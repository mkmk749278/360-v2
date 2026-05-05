#!/usr/bin/env bash
# Lumin app v0.0.9 — Data wiring: history survives restarts, per-agent
# drill-down, status sub-filters, format helpers.
#
# Pairs with engine PR #299 ("persist signal history + per-evaluator
# filter + agent lifecycle stats") — engine should be deployed first
# so the new ?setup_class= and lifecycle fields are populated.  If the
# engine is on the old API the app still works (filter param is
# ignored server-side; lifecycle fields default to 0 / null).
#
# Changes vs v0.0.8:
#   1. Repository contract extended:
#        - fetchSignals(setupClass: ...) and fetchActivity(setupClass: ...)
#          accept an optional UPPER_SNAKE setup-class filter.
#        - AgentStat schema gains closedToday / tpHits / slHits /
#          invalidated / lastSignalAgeMinutes.
#   2. Agents tab — bottom sheet redo.  Tapping an agent now fetches that
#      evaluator's stats AND its 10 most-recent signals from the engine.
#      Subscribers can finally see WHAT each agent has actually shipped,
#      not just metadata about the evaluator class.
#   3. Signals tab — when "Closed" filter is active a second row of
#      sub-filter chips appears (All / TP / SL / Invalidated / Expired)
#      so historical state diversity is visible at a glance instead of
#      being smeared into one bucket.
#   4. New `lib/shared/format.dart` — pure-Dart formatters for price,
#      P&L, percentage, age.  No `intl` package dep.  Wires the global-
#      audience-readiness foundation; a follow-up retrofits pulse/trade
#      pages to use them (deferred to v0.0.10 to keep this PR scoped).
#
# Termux-safe: bash + GNU sed/awk only, no jq/python.
#
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v009.sh
#   bash lumin-v009.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

if grep -q "^version: 0.0.9" pubspec.yaml; then
  echo "→ Already on v0.0.9 — nothing to do."
  exit 0
fi

if ! grep -q "^version: 0.0.8" pubspec.yaml; then
  echo "ERROR: expected v0.0.8 baseline; found:"
  grep "^version:" pubspec.yaml
  echo "Run lumin-v008.sh first, then re-run this script."
  exit 1
fi

echo "→ Updating Lumin app to v0.0.9 (data wiring + per-agent drill-down)…"

mkdir -p lib/shared

# ── lib/shared/format.dart (NEW) ──────────────────────────────────────
echo "  ✓ writing lib/shared/format.dart"
cat > lib/shared/format.dart <<'EOF_FORMAT'
/// Number / time formatting for global-audience rendering.
///
/// Pure-Dart helpers — no `intl` package dep.  Crypto + financial
/// surfaces should route through these so we don't accumulate
/// locale-hostile patterns ($-hardcoded, no thousands separators) that
/// will need unwinding when subscriber localisation lands.

String _withSeparators(String integerPart) {
  return integerPart.replaceAllMapped(
    RegExp(r'(\d)(?=(\d{3})+$)'),
    (m) => '${m[1]},',
  );
}

/// Auto-precision price.  $1,234.56 for liquid pairs; preserves precision
/// on micro-cap altcoins (down to 7 decimals) so $0.0000123 doesn't
/// collapse to $0.00.  No currency symbol — that's the caller's job.
String formatPrice(num value) {
  if (value == 0) return '0.00';
  final absV = value.abs().toDouble();
  int decimals;
  if (absV >= 100) {
    decimals = 2;
  } else if (absV >= 1) {
    decimals = 4;
  } else if (absV >= 0.01) {
    decimals = 5;
  } else {
    decimals = 7;
  }
  final s = absV.toStringAsFixed(decimals);
  final parts = s.split('.');
  final integer = _withSeparators(parts[0]);
  final body = parts.length > 1 ? '$integer.${parts[1]}' : integer;
  return value < 0 ? '-$body' : body;
}

/// P&L in USD with explicit sign and currency symbol.  '+\$12.84' / '-\$3.20'.
String formatPnl(num usd) {
  final absV = usd.abs().toDouble();
  final s = absV.toStringAsFixed(2);
  final parts = s.split('.');
  final integer = _withSeparators(parts[0]);
  final body = '\$$integer.${parts[1]}';
  return usd >= 0 ? '+$body' : '-$body';
}

/// Percentage with explicit sign.  '+1.28%' / '-0.45%'.
String formatPct(num pct, {int decimals = 2}) {
  final sign = pct >= 0 ? '+' : '-';
  return '$sign${pct.abs().toStringAsFixed(decimals)}%';
}

/// Short relative-age label.  '5m' / '2h' / '3d'.  Caller appends 'ago'
/// where needed — most card layouts already have that suffix baked into
/// adjacent copy.
String formatAge(int minutes) {
  if (minutes < 0) return '';
  if (minutes < 60) return '${minutes}m';
  if (minutes < 1440) return '${(minutes / 60).round()}h';
  return '${(minutes / 1440).round()}d';
}
EOF_FORMAT

# ── lib/data/repository.dart (full rewrite) ───────────────────────────
echo "  ✓ rewriting lib/data/repository.dart"
cat > lib/data/repository.dart <<'EOF_REPO'
/// Repository abstraction — the single seam between UI and data source.
///
/// Pages call ``LuminRepository`` methods.  The concrete implementation
/// (``MockRepository`` for offline/preview, ``HttpRepository`` for live
/// engine) is chosen at app startup based on user preference.  Adding a
/// new data source (websocket, on-device cache, …) means writing a new
/// implementation; no page has to change.
import 'package:flutter/material.dart';

import '../shared/tokens.dart';
import 'api_client.dart';
import 'mock_data.dart';

class AutoModeStatus {
  const AutoModeStatus({
    required this.mode,
    required this.openPositions,
    required this.dailyPnlUsd,
    required this.dailyLossPct,
    required this.dailyKillTripped,
    required this.manualPaused,
    required this.currentEquityUsd,
    this.simulatedPnlUsd,
  });

  final String mode;
  final int openPositions;
  final double dailyPnlUsd;
  final double dailyLossPct;
  final bool dailyKillTripped;
  final bool manualPaused;
  final double currentEquityUsd;
  final double? simulatedPnlUsd;

  factory AutoModeStatus.fromJson(Map<String, dynamic> j) => AutoModeStatus(
        mode: j['mode'] as String,
        openPositions: (j['open_positions'] as num?)?.toInt() ?? 0,
        dailyPnlUsd: (j['daily_pnl_usd'] as num?)?.toDouble() ?? 0.0,
        dailyLossPct: (j['daily_loss_pct'] as num?)?.toDouble() ?? 0.0,
        dailyKillTripped: j['daily_kill_tripped'] as bool? ?? false,
        manualPaused: j['manual_paused'] as bool? ?? false,
        currentEquityUsd:
            (j['current_equity_usd'] as num?)?.toDouble() ?? 0.0,
        simulatedPnlUsd: (j['simulated_pnl_usd'] as num?)?.toDouble(),
      );
}

class AgentStat {
  const AgentStat({
    required this.evaluator,
    required this.setupClass,
    required this.displayName,
    required this.enabled,
    required this.attempts,
    required this.generated,
    required this.noSignal,
    this.closedToday = 0,
    this.tpHits = 0,
    this.slHits = 0,
    this.invalidated = 0,
    this.lastSignalAgeMinutes,
  });
  final String evaluator;
  final String setupClass;
  final String displayName;
  final bool enabled;
  // Telemetry counters (reset per scan-cycle window):
  final int attempts;
  final int generated;
  final int noSignal;
  // Lifecycle counters (rolling 24h):
  final int closedToday;
  final int tpHits;
  final int slHits;
  final int invalidated;
  // Minutes since this agent's most recent emission, or null if it has
  // never fired since the engine's history window started.
  final int? lastSignalAgeMinutes;

  factory AgentStat.fromJson(Map<String, dynamic> j) => AgentStat(
        evaluator: j['evaluator'] as String? ?? '',
        setupClass: j['setup_class'] as String? ?? '',
        displayName: j['display_name'] as String? ?? '',
        enabled: j['enabled'] as bool? ?? true,
        attempts: (j['attempts'] as num?)?.toInt() ?? 0,
        generated: (j['generated'] as num?)?.toInt() ?? 0,
        noSignal: (j['no_signal'] as num?)?.toInt() ?? 0,
        closedToday: (j['closed_today'] as num?)?.toInt() ?? 0,
        tpHits: (j['tp_hits'] as num?)?.toInt() ?? 0,
        slHits: (j['sl_hits'] as num?)?.toInt() ?? 0,
        invalidated: (j['invalidated'] as num?)?.toInt() ?? 0,
        lastSignalAgeMinutes: (j['last_signal_age_minutes'] as num?)?.toInt(),
      );
}

abstract class LuminRepository {
  /// True when the underlying source is the live engine (vs. mocks).
  bool get isLive;

  Future<MockEngineSnapshot> fetchPulse();
  Future<List<MockSignal>> fetchSignals({
    String status = 'all',
    int limit = 50,
    String? setupClass,
  });
  Future<List<MockPosition>> fetchPositions();
  Future<List<MockActivityEvent>> fetchActivity({
    int limit = 50,
    String? setupClass,
  });
  Future<AutoModeStatus> fetchAutoMode();
  Future<AutoModeStatus> setAutoMode(String mode);
  Future<List<AgentStat>> fetchAgents();
  Future<bool> healthCheck();
}

// ---------------------------------------------------------------------------
// MockRepository — wraps the constants in ``mock_data.dart``.
// ---------------------------------------------------------------------------

class MockRepository implements LuminRepository {
  const MockRepository();

  @override
  bool get isLive => false;

  @override
  Future<MockEngineSnapshot> fetchPulse() async => mockEngine;

  @override
  Future<List<MockSignal>> fetchSignals({
    String status = 'all',
    int limit = 50,
    String? setupClass,
  }) async {
    // setupClass is ignored in mock mode — the 4-signal fixture isn't
    // worth filtering and Live mode is the canonical path for drill-down.
    final all = mockSignals;
    Iterable<MockSignal> filtered;
    switch (status) {
      case 'open':
        filtered = all.where((s) => s.status == 'ACTIVE');
        break;
      case 'closed':
        filtered = all.where((s) => s.status != 'ACTIVE');
        break;
      default:
        filtered = all;
    }
    return filtered.take(limit).toList();
  }

  @override
  Future<List<MockPosition>> fetchPositions() async => mockPositions;

  @override
  Future<List<MockActivityEvent>> fetchActivity({
    int limit = 50,
    String? setupClass,
  }) async =>
      mockActivity.take(limit).toList();

  @override
  Future<AutoModeStatus> fetchAutoMode() async => const AutoModeStatus(
        mode: 'paper',
        openPositions: 1,
        dailyPnlUsd: 12.84,
        dailyLossPct: 0.0,
        dailyKillTripped: false,
        manualPaused: false,
        currentEquityUsd: 1012.84,
        simulatedPnlUsd: 12.84,
      );

  @override
  Future<AutoModeStatus> setAutoMode(String mode) async =>
      // Mock can't actually switch — return a status with the requested mode
      // so the UI feedback feels right.
      AutoModeStatus(
        mode: mode,
        openPositions: 0,
        dailyPnlUsd: 0.0,
        dailyLossPct: 0.0,
        dailyKillTripped: false,
        manualPaused: false,
        currentEquityUsd: 1000.0,
      );

  @override
  Future<List<AgentStat>> fetchAgents() async {
    // Synthesise 14 agents with zero lifecycle counters — preview mode
    // doesn't simulate fired-signal history.
    final names = <String, String>{
      'SR_FLIP_RETEST': 'The Architect',
      'LIQUIDITY_SWEEP_REVERSAL': 'The Counter-Puncher',
      'FAILED_AUCTION_RECLAIM': 'The Reclaimer',
      'QUIET_COMPRESSION_BREAK': 'The Coil Hunter',
      'VOLUME_SURGE_BREAKOUT': 'The Tracker',
      'BREAKDOWN_SHORT': 'The Crusher',
      'FUNDING_EXTREME_SIGNAL': 'The Contrarian',
      'WHALE_MOMENTUM': 'The Whale Hunter',
      'LIQUIDATION_REVERSAL': 'The Cascade Catcher',
      'CONTINUATION_LIQUIDITY_SWEEP': 'The Continuation Specialist',
      'DIVERGENCE_CONTINUATION': 'The Divergence Reader',
      'TREND_PULLBACK_EMA': 'The Pullback Sniper',
      'POST_DISPLACEMENT_CONTINUATION': 'The Aftermath Trader',
      'OPENING_RANGE_BREAKOUT': 'The Range Breaker',
    };
    return names.entries
        .map((e) => AgentStat(
              evaluator: e.key,
              setupClass: e.key,
              displayName: e.value,
              enabled: true,
              attempts: 0,
              generated: 0,
              noSignal: 0,
            ))
        .toList();
  }

  @override
  Future<bool> healthCheck() async => true;
}

// ---------------------------------------------------------------------------
// HttpRepository — talks to FastAPI backend.
// ---------------------------------------------------------------------------

class HttpRepository implements LuminRepository {
  HttpRepository(this.client);

  final LuminApiClient client;

  @override
  bool get isLive => true;

  @override
  Future<MockEngineSnapshot> fetchPulse() async {
    final j = (await client.get('/api/pulse')) as Map<String, dynamic>;
    return MockEngineSnapshot(
      status: j['status'] as String? ?? 'Healthy',
      regime: j['regime'] as String? ?? 'RANGING',
      regimePctTrending:
          (j['regime_pct_trending'] as num?)?.toDouble() ?? 0.0,
      todayPnlUsd: (j['today_pnl_usd'] as num?)?.toDouble() ?? 0.0,
      todayPnlPct: (j['today_pnl_pct'] as num?)?.toDouble() ?? 0.0,
      dailyLossBudgetUsd:
          (j['daily_loss_budget_usd'] as num?)?.toDouble() ?? 0.0,
      dailyLossUsedUsd:
          (j['daily_loss_used_usd'] as num?)?.toDouble() ?? 0.0,
      openPositions: (j['open_positions'] as num?)?.toInt() ?? 0,
      signalsToday: (j['signals_today'] as num?)?.toInt() ?? 0,
      uptime: _formatUptime((j['uptime_seconds'] as num?)?.toDouble() ?? 0.0),
    );
  }

  @override
  Future<List<MockSignal>> fetchSignals({
    String status = 'all',
    int limit = 50,
    String? setupClass,
  }) async {
    final query = <String, dynamic>{'status': status, 'limit': limit};
    if (setupClass != null && setupClass.isNotEmpty) {
      query['setup_class'] = setupClass;
    }
    final j = (await client.get('/api/signals', query: query))
        as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(_signalFromJson).toList();
  }

  @override
  Future<List<MockPosition>> fetchPositions() async {
    final j = (await client.get('/api/positions')) as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(_positionFromJson).toList();
  }

  @override
  Future<List<MockActivityEvent>> fetchActivity({
    int limit = 50,
    String? setupClass,
  }) async {
    final query = <String, dynamic>{'limit': limit};
    if (setupClass != null && setupClass.isNotEmpty) {
      query['setup_class'] = setupClass;
    }
    final j = (await client.get('/api/activity', query: query))
        as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(_activityFromJson).toList();
  }

  @override
  Future<AutoModeStatus> fetchAutoMode() async {
    final j = (await client.get('/api/auto-mode')) as Map<String, dynamic>;
    return AutoModeStatus.fromJson(j);
  }

  @override
  Future<AutoModeStatus> setAutoMode(String mode) async {
    await client.post('/api/auto-mode', body: {'mode': mode});
    // Re-fetch so the UI sees the post-change risk-gate state in one shot.
    return fetchAutoMode();
  }

  @override
  Future<List<AgentStat>> fetchAgents() async {
    final j = (await client.get('/api/agents')) as Map<String, dynamic>;
    final items = (j['items'] as List? ?? []).cast<Map<String, dynamic>>();
    return items.map(AgentStat.fromJson).toList();
  }

  @override
  Future<bool> healthCheck() async {
    try {
      final j = await client.get('/api/health');
      return j is Map && j['ok'] == true;
    } catch (_) {
      return false;
    }
  }

  // ---- json → mock-class adapters --------------------------------------

  MockSignal _signalFromJson(Map<String, dynamic> j) => MockSignal(
        id: j['signal_id'] as String? ?? '',
        symbol: j['symbol'] as String? ?? '',
        direction: j['direction'] as String? ?? 'LONG',
        setupName: (j['setup_class'] as String? ?? '').replaceAll('_', ' '),
        agentName: j['agent_name'] as String? ?? '',
        entry: (j['entry'] as num?)?.toDouble() ?? 0.0,
        sl: (j['stop_loss'] as num?)?.toDouble() ?? 0.0,
        tp1: (j['tp1'] as num?)?.toDouble() ?? 0.0,
        tp2: (j['tp2'] as num?)?.toDouble() ?? 0.0,
        tp3: (j['tp3'] as num?)?.toDouble() ?? 0.0,
        confidence: (j['confidence'] as num?)?.toDouble() ?? 0.0,
        tier: j['quality_tier'] as String? ?? 'B',
        status: j['status'] as String? ?? 'ACTIVE',
        pnlPct: (j['pnl_pct'] as num?)?.toDouble() ?? 0.0,
        minutesAgo: (j['minutes_ago'] as num?)?.toInt() ?? 0,
      );

  MockPosition _positionFromJson(Map<String, dynamic> j) => MockPosition(
        symbol: j['symbol'] as String? ?? '',
        direction: j['direction'] as String? ?? 'LONG',
        entry: (j['entry'] as num?)?.toDouble() ?? 0.0,
        currentPrice: (j['current_price'] as num?)?.toDouble() ?? 0.0,
        qty: (j['qty'] as num?)?.toDouble() ?? 0.0,
        pnlUsd: (j['pnl_usd'] as num?)?.toDouble() ?? 0.0,
        pnlPct: (j['pnl_pct'] as num?)?.toDouble() ?? 0.0,
        minutesOpen: (j['minutes_open'] as num?)?.toInt() ?? 0,
      );

  MockActivityEvent _activityFromJson(Map<String, dynamic> j) {
    final kind = j['kind'] as String? ?? 'OPEN';
    return MockActivityEvent(
      kind: kind,
      title: j['title'] as String? ?? '',
      subtitle: j['subtitle'] as String? ?? '',
      minutesAgo: (j['minutes_ago'] as num?)?.toInt() ?? 0,
      color: _colorForKind(kind),
    );
  }

  /// Brand-token mapping for activity event glyphs.  Mirrors the colours
  /// used by ``mock_data.dart`` so the live feed renders identically to
  /// the offline preview.
  static Color _colorForKind(String kind) {
    switch (kind) {
      case 'OPEN':
        return LuminColors.accent;
      case 'PRE_TP':
        return LuminColors.warn;
      case 'TP1':
      case 'TP2':
      case 'TP3':
        return LuminColors.success;
      case 'SL':
        return LuminColors.loss;
      case 'INVAL':
        return LuminColors.textMuted;
      default:
        return LuminColors.accent;
    }
  }

  static String _formatUptime(double seconds) {
    if (seconds <= 0) return '0s';
    final d = seconds ~/ 86400;
    final h = (seconds % 86400) ~/ 3600;
    if (d > 0) return '${d}d ${h}h';
    final m = (seconds % 3600) ~/ 60;
    return h > 0 ? '${h}h ${m}m' : '${m}m';
  }

}
EOF_REPO

# ── lib/features/agents/agents_page.dart (full rewrite) ───────────────
echo "  ✓ rewriting lib/features/agents/agents_page.dart"
cat > lib/features/agents/agents_page.dart <<'EOF_AGENTS'
/// Agents — 14 evaluator personas + per-agent drill-down.
///
/// The detail bottom sheet fetches that agent's lifecycle stats and
/// recent signals from the live engine (or mock repo offline) so users
/// see WHAT each evaluator has actually shipped, not just what the
/// evaluator class is supposed to do.
import 'package:flutter/material.dart';

import '../../data/app_config.dart';
import '../../data/mock_data.dart';
import '../../data/repository.dart';
import '../../shared/format.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import 'agent_data.dart';

class AgentsPage extends StatelessWidget {
  const AgentsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agents'),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline),
            tooltip: 'About the agents',
            onPressed: () => _showAboutDialog(context),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
              child: Text(
                '${kAgents.length} AI specialists',
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: LuminSpacing.md),
              child: Text(
                'Each agent watches markets for a specific setup family. '
                'Tap an agent to see its live stats and recent signals.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
            ),
            Expanded(
              child: ListView.separated(
                physics: const BouncingScrollPhysics(),
                itemCount: kAgents.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(height: LuminSpacing.md),
                itemBuilder: (_, i) => _AgentCard(agent: kAgents[i]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: LuminColors.bgCard,
        title: const Text("Lumin's 14 AI agents"),
        content: const Text(
          "Each agent corresponds to one of the engine's evaluator paths. "
          'They scan 75 USDT-M futures pairs continuously, looking for their '
          "specific setup type. When an agent's confidence clears the paid "
          'threshold (65+), the signal is dispatched.\n\n'
          'Per-agent toggles and custom thresholds coming with a future '
          'subscription tier. Live stats are populated as soon as that '
          'evaluator emits a signal.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}

class _AgentCard extends StatelessWidget {
  const _AgentCard({required this.agent});
  final Agent agent;

  @override
  Widget build(BuildContext context) {
    return LuminCard(
      onTap: () => _openDetail(context, agent),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: LuminColors.accent.withOpacity(0.10),
              borderRadius: BorderRadius.circular(LuminRadii.md),
              border: Border.all(color: LuminColors.cardBorder),
            ),
            child: Icon(agent.icon, color: LuminColors.accent, size: 28),
          ),
          const SizedBox(width: LuminSpacing.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(agent.name,
                    style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: LuminSpacing.xs),
                Text(agent.tagline,
                    style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          const Icon(Icons.chevron_right, color: LuminColors.textMuted),
        ],
      ),
    );
  }

  void _openDetail(BuildContext context, Agent agent) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: LuminColors.bgCard,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(LuminRadii.lg)),
      ),
      builder: (_) => _AgentDetailSheet(agent: agent),
    );
  }
}

// ---------------------------------------------------------------------------
// Detail bottom sheet — async-fetches stats + recent signals.
// ---------------------------------------------------------------------------

class _AgentDetailBundle {
  const _AgentDetailBundle({required this.stat, required this.signals});
  final AgentStat stat;
  final List<MockSignal> signals;
}

class _AgentDetailSheet extends StatefulWidget {
  const _AgentDetailSheet({required this.agent});
  final Agent agent;

  @override
  State<_AgentDetailSheet> createState() => _AgentDetailSheetState();
}

class _AgentDetailSheetState extends State<_AgentDetailSheet> {
  late Future<_AgentDetailBundle> _future;

  @override
  void initState() {
    super.initState();
    // We must read AppConfigScope after the first frame; doing so here is
    // safe because showModalBottomSheet is called with a context that
    // sits below AppConfigScope.
    _future = _load();
  }

  Future<_AgentDetailBundle> _load() async {
    final repo = AppConfigScope.of(context).repo;
    final results = await Future.wait([
      repo.fetchAgents(),
      repo.fetchSignals(
        status: 'all',
        limit: 10,
        setupClass: widget.agent.id,
      ),
    ]);
    final allAgents = results[0] as List<AgentStat>;
    final signals = (results[1] as List).cast<MockSignal>();
    final stat = allAgents.firstWhere(
      (a) => a.setupClass == widget.agent.id,
      orElse: () => AgentStat(
        evaluator: widget.agent.id,
        setupClass: widget.agent.id,
        displayName: widget.agent.name,
        enabled: true,
        attempts: 0,
        generated: 0,
        noSignal: 0,
      ),
    );
    return _AgentDetailBundle(stat: stat, signals: signals);
  }

  Future<void> _refresh() async {
    setState(() => _future = _load());
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) {
        return SingleChildScrollView(
          controller: scrollController,
          padding: const EdgeInsets.fromLTRB(
            LuminSpacing.xl,
            LuminSpacing.lg,
            LuminSpacing.xl,
            LuminSpacing.xl,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 36,
                  height: 4,
                  decoration: BoxDecoration(
                    color: LuminColors.textMuted,
                    borderRadius: BorderRadius.circular(LuminRadii.pill),
                  ),
                ),
              ),
              const SizedBox(height: LuminSpacing.lg),
              _Hero(agent: widget.agent),
              const SizedBox(height: LuminSpacing.lg),
              Text(
                widget.agent.specialty,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: LuminSpacing.lg),
              FutureBuilder<_AgentDetailBundle>(
                future: _future,
                builder: (context, snap) {
                  if (snap.connectionState == ConnectionState.waiting &&
                      !snap.hasData) {
                    return const Padding(
                      padding: EdgeInsets.symmetric(vertical: LuminSpacing.xl),
                      child: Center(
                        child: SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: LuminColors.accent,
                          ),
                        ),
                      ),
                    );
                  }
                  if (snap.hasError) {
                    return _ErrorBlock(
                      error: snap.error.toString(),
                      onRetry: _refresh,
                    );
                  }
                  final bundle = snap.data!;
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _StatsCard(stat: bundle.stat),
                      const SizedBox(height: LuminSpacing.lg),
                      _RecentSignalsBlock(signals: bundle.signals),
                    ],
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }
}

class _Hero extends StatelessWidget {
  const _Hero({required this.agent});
  final Agent agent;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(agent.icon, size: 32, color: LuminColors.accent),
        const SizedBox(width: LuminSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(agent.name,
                  style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 2),
              Text(
                agent.tagline,
                style: Theme.of(context)
                    .textTheme
                    .bodyMedium
                    ?.copyWith(color: LuminColors.accent),
              ),
              const SizedBox(height: LuminSpacing.xs),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: LuminSpacing.sm,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: LuminColors.bgElevated,
                  borderRadius: BorderRadius.circular(LuminRadii.sm),
                ),
                child: Text(
                  agent.id,
                  style: const TextStyle(
                    color: LuminColors.textMuted,
                    fontFamily: 'monospace',
                    fontSize: 10,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _StatsCard extends StatelessWidget {
  const _StatsCard({required this.stat});
  final AgentStat stat;

  @override
  Widget build(BuildContext context) {
    final lastFired = stat.lastSignalAgeMinutes;
    final lastFiredLabel = lastFired == null
        ? 'never'
        : lastFired < 1
            ? 'just now'
            : '${formatAge(lastFired)} ago';
    return LuminCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'STATS — LAST 24h',
            style: TextStyle(
              color: LuminColors.textMuted,
              fontSize: 10,
              letterSpacing: 1.2,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: LuminSpacing.md),
          Row(
            children: [
              Expanded(
                child: _Stat(
                  label: 'TP hits',
                  value: '${stat.tpHits}',
                  color: LuminColors.success,
                ),
              ),
              Expanded(
                child: _Stat(
                  label: 'SL hits',
                  value: '${stat.slHits}',
                  color: LuminColors.loss,
                ),
              ),
              Expanded(
                child: _Stat(
                  label: 'Invalidated',
                  value: '${stat.invalidated}',
                  color: LuminColors.textMuted,
                ),
              ),
            ],
          ),
          const SizedBox(height: LuminSpacing.md),
          Row(
            children: [
              Expanded(
                child: _Stat(
                  label: 'Closed',
                  value: '${stat.closedToday}',
                  color: LuminColors.textPrimary,
                ),
              ),
              Expanded(
                child: _Stat(
                  label: 'Last fired',
                  value: lastFiredLabel,
                  color: LuminColors.accent,
                ),
              ),
              Expanded(
                child: _Stat(
                  label: 'Generated',
                  value: '${stat.generated}',
                  color: LuminColors.accent,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  const _Stat({
    required this.label,
    required this.value,
    required this.color,
  });
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            color: LuminColors.textMuted,
            fontSize: 9,
            letterSpacing: 1.0,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: -0.3,
          ),
        ),
      ],
    );
  }
}

class _RecentSignalsBlock extends StatelessWidget {
  const _RecentSignalsBlock({required this.signals});
  final List<MockSignal> signals;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'RECENT SIGNALS',
          style: TextStyle(
            color: LuminColors.textMuted,
            fontSize: 10,
            letterSpacing: 1.2,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: LuminSpacing.md),
        if (signals.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: LuminSpacing.lg),
            child: Center(
              child: Text(
                'No signals from this agent yet.\n'
                'Will appear here as soon as it fires.',
                textAlign: TextAlign.center,
                style: TextStyle(color: LuminColors.textMuted, fontSize: 12),
              ),
            ),
          )
        else
          for (int i = 0; i < signals.length; i++) ...[
            _AgentSignalRow(sig: signals[i]),
            if (i < signals.length - 1)
              const Divider(
                color: LuminColors.cardBorder,
                height: LuminSpacing.lg,
              ),
          ],
      ],
    );
  }
}

class _AgentSignalRow extends StatelessWidget {
  const _AgentSignalRow({required this.sig});
  final MockSignal sig;

  Color _statusColor() {
    switch (sig.status) {
      case 'TP1_HIT':
      case 'TP2_HIT':
      case 'TP3_HIT':
      case 'FULL_TP_HIT':
        return LuminColors.success;
      case 'SL_HIT':
        return LuminColors.loss;
      case 'INVALIDATED':
      case 'EXPIRED':
      case 'CANCELLED':
        return LuminColors.textMuted;
      default:
        return LuminColors.accent;
    }
  }

  @override
  Widget build(BuildContext context) {
    final pnlPositive = sig.pnlPct >= 0;
    final isLong = sig.direction == 'LONG';
    return Row(
      children: [
        Container(
          width: 6,
          height: 36,
          decoration: BoxDecoration(
            color: _statusColor(),
            borderRadius: BorderRadius.circular(LuminRadii.pill),
          ),
        ),
        const SizedBox(width: LuminSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    sig.symbol,
                    style: const TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(width: LuminSpacing.xs),
                  Text(
                    sig.direction,
                    style: TextStyle(
                      color:
                          isLong ? LuminColors.success : LuminColors.loss,
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Text(
                '${sig.status} • ${formatAge(sig.minutesAgo)} ago',
                style: TextStyle(
                  color: _statusColor(),
                  fontSize: 10,
                  letterSpacing: 0.3,
                ),
              ),
            ],
          ),
        ),
        Text(
          formatPct(sig.pnlPct),
          style: TextStyle(
            color: pnlPositive ? LuminColors.success : LuminColors.loss,
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

class _ErrorBlock extends StatelessWidget {
  const _ErrorBlock({required this.error, required this.onRetry});
  final String error;
  final Future<void> Function() onRetry;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: LuminSpacing.lg),
      child: Column(
        children: [
          const Icon(Icons.cloud_off, color: LuminColors.loss, size: 32),
          const SizedBox(height: LuminSpacing.sm),
          const Text(
            'Could not load agent stats',
            style: TextStyle(
              color: LuminColors.textPrimary,
              fontSize: 14,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: LuminSpacing.xs),
          Text(
            error,
            textAlign: TextAlign.center,
            style: const TextStyle(
              color: LuminColors.textSecondary,
              fontSize: 11,
            ),
          ),
          const SizedBox(height: LuminSpacing.md),
          FilledButton.icon(
            style: FilledButton.styleFrom(
              backgroundColor: LuminColors.accent,
              foregroundColor: LuminColors.bgDeep,
            ),
            onPressed: onRetry,
            icon: const Icon(Icons.refresh, size: 18),
            label: const Text('Retry'),
          ),
        ],
      ),
    );
  }
}
EOF_AGENTS

# ── lib/features/signals/signals_page.dart (full rewrite) ─────────────
echo "  ✓ rewriting lib/features/signals/signals_page.dart"
cat > lib/features/signals/signals_page.dart <<'EOF_SIGNALS'
/// Signals — live + closed feed.
///
/// Filter chips trigger a re-fetch via the repository.  When the
/// "Closed" filter is active, a second row of sub-filter chips appears
/// (All / TP / SL / Invalidated / Expired) and is applied client-side
/// so we don't multiply API requests for what is essentially a status
/// projection of the same closed-pool.
import 'package:flutter/material.dart';

import '../../data/app_config.dart';
import '../../data/mock_data.dart';
import '../../data/repository.dart';
import '../../shared/format.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import '../../shared/widgets/preview_badge.dart';

enum _SignalFilter { all, open, closed }

extension _FilterStr on _SignalFilter {
  String get apiValue {
    switch (this) {
      case _SignalFilter.open:
        return 'open';
      case _SignalFilter.closed:
        return 'closed';
      case _SignalFilter.all:
        return 'all';
    }
  }

  String get label =>
      '${name[0].toUpperCase()}${name.substring(1)}';
}

enum _ClosedSubFilter { all, tp, sl, invalidated, expired }

extension _SubFilterStr on _ClosedSubFilter {
  String get label {
    switch (this) {
      case _ClosedSubFilter.all:
        return 'All';
      case _ClosedSubFilter.tp:
        return 'TP';
      case _ClosedSubFilter.sl:
        return 'SL';
      case _ClosedSubFilter.invalidated:
        return 'Invalidated';
      case _ClosedSubFilter.expired:
        return 'Expired';
    }
  }
}

bool _matchesSubFilter(MockSignal s, _ClosedSubFilter f) {
  switch (f) {
    case _ClosedSubFilter.all:
      return true;
    case _ClosedSubFilter.tp:
      return s.status == 'TP1_HIT' ||
          s.status == 'TP2_HIT' ||
          s.status == 'TP3_HIT' ||
          s.status == 'FULL_TP_HIT';
    case _ClosedSubFilter.sl:
      return s.status == 'SL_HIT';
    case _ClosedSubFilter.invalidated:
      return s.status == 'INVALIDATED' || s.status == 'CANCELLED';
    case _ClosedSubFilter.expired:
      return s.status == 'EXPIRED';
  }
}

class SignalsPage extends StatefulWidget {
  const SignalsPage({super.key});

  @override
  State<SignalsPage> createState() => _SignalsPageState();
}

class _SignalsPageState extends State<SignalsPage> {
  _SignalFilter _filter = _SignalFilter.all;
  _ClosedSubFilter _subFilter = _ClosedSubFilter.all;
  late Future<List<MockSignal>> _future;
  LuminRepository? _lastRepo;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final repo = AppConfigScope.of(context).repo;
    if (repo != _lastRepo) {
      _lastRepo = repo;
      _refetch();
    }
  }

  void _refetch() {
    final repo = AppConfigScope.of(context).repo;
    setState(() {
      _future = repo.fetchSignals(status: _filter.apiValue, limit: 100);
    });
  }

  Future<void> _refresh() async {
    _refetch();
    await _future;
  }

  void _setFilter(_SignalFilter f) {
    if (f == _filter) return;
    setState(() {
      _filter = f;
      // Reset sub-filter when switching primary chip — hidden when not Closed.
      _subFilter = _ClosedSubFilter.all;
    });
    _refetch();
  }

  void _setSubFilter(_ClosedSubFilter f) {
    if (f == _subFilter) return;
    setState(() => _subFilter = f);
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppConfigScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Signals')),
      body: Column(
        children: [
          if (!scope.repo.isLive) const PreviewBadge(),
          _FilterRow(current: _filter, onChanged: _setFilter),
          if (_filter == _SignalFilter.closed) ...[
            const SizedBox(height: LuminSpacing.sm),
            _SubFilterRow(current: _subFilter, onChanged: _setSubFilter),
          ],
          const SizedBox(height: LuminSpacing.sm),
          Expanded(
            child: RefreshIndicator(
              color: LuminColors.accent,
              onRefresh: _refresh,
              child: FutureBuilder<List<MockSignal>>(
                future: _future,
                builder: (context, snap) {
                  if (snap.connectionState == ConnectionState.waiting &&
                      !snap.hasData) {
                    return const _SignalsLoading();
                  }
                  if (snap.hasError) {
                    return _SignalsError(
                      error: snap.error.toString(),
                      onRetry: _refresh,
                    );
                  }
                  var items = snap.data ?? const <MockSignal>[];
                  if (_filter == _SignalFilter.closed &&
                      _subFilter != _ClosedSubFilter.all) {
                    items = items
                        .where((s) => _matchesSubFilter(s, _subFilter))
                        .toList(growable: false);
                  }
                  if (items.isEmpty) {
                    return _SignalsEmpty(
                      filter: _filter,
                      subFilter: _subFilter,
                      isLive: scope.repo.isLive,
                    );
                  }
                  return ListView.separated(
                    physics: const AlwaysScrollableScrollPhysics(
                      parent: BouncingScrollPhysics(),
                    ),
                    padding: const EdgeInsets.symmetric(
                      horizontal: LuminSpacing.lg,
                    ),
                    itemCount: items.length,
                    separatorBuilder: (_, __) =>
                        const SizedBox(height: LuminSpacing.md),
                    itemBuilder: (_, i) => _SignalCard(sig: items[i]),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterRow extends StatelessWidget {
  const _FilterRow({required this.current, required this.onChanged});

  final _SignalFilter current;
  final ValueChanged<_SignalFilter> onChanged;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Row(
        children: [
          for (final f in _SignalFilter.values) ...[
            _Chip(
              label: f.label,
              selected: current == f,
              onTap: () => onChanged(f),
            ),
            if (f != _SignalFilter.values.last)
              const SizedBox(width: LuminSpacing.sm),
          ],
        ],
      ),
    );
  }
}

class _SubFilterRow extends StatelessWidget {
  const _SubFilterRow({required this.current, required this.onChanged});

  final _ClosedSubFilter current;
  final ValueChanged<_ClosedSubFilter> onChanged;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 32,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding:
            const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
        itemCount: _ClosedSubFilter.values.length,
        separatorBuilder: (_, __) => const SizedBox(width: LuminSpacing.sm),
        itemBuilder: (_, i) {
          final f = _ClosedSubFilter.values[i];
          return _Chip(
            label: f.label,
            selected: current == f,
            onTap: () => onChanged(f),
            compact: true,
          );
        },
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  const _Chip({
    required this.label,
    required this.selected,
    required this.onTap,
    this.compact = false,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(LuminRadii.pill),
      child: InkWell(
        borderRadius: BorderRadius.circular(LuminRadii.pill),
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: EdgeInsets.symmetric(
            horizontal: compact ? LuminSpacing.sm : LuminSpacing.md,
            vertical: compact ? LuminSpacing.xs : LuminSpacing.xs + 2,
          ),
          decoration: BoxDecoration(
            color: selected
                ? LuminColors.accent.withOpacity(0.15)
                : LuminColors.bgCard,
            borderRadius: BorderRadius.circular(LuminRadii.pill),
            border: Border.all(
              color: selected
                  ? LuminColors.accent.withOpacity(0.40)
                  : LuminColors.cardBorder,
            ),
          ),
          child: Text(
            label,
            style: TextStyle(
              color: selected ? LuminColors.accent : LuminColors.textSecondary,
              fontSize: compact ? 11 : 12,
              fontWeight: FontWeight.w500,
              letterSpacing: 0.3,
            ),
          ),
        ),
      ),
    );
  }
}

class _SignalsEmpty extends StatelessWidget {
  const _SignalsEmpty({
    required this.filter,
    required this.subFilter,
    required this.isLive,
  });
  final _SignalFilter filter;
  final _ClosedSubFilter subFilter;
  final bool isLive;

  String _heading() {
    if (filter == _SignalFilter.open) return 'No open signals right now';
    if (filter == _SignalFilter.closed) {
      switch (subFilter) {
        case _ClosedSubFilter.all:
          return 'No closed signals yet';
        case _ClosedSubFilter.tp:
          return 'No TP hits yet';
        case _ClosedSubFilter.sl:
          return 'No SL hits yet';
        case _ClosedSubFilter.invalidated:
          return 'No invalidated signals';
        case _ClosedSubFilter.expired:
          return 'No expired signals';
      }
    }
    return 'No signals yet';
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(
        parent: BouncingScrollPhysics(),
      ),
      children: [
        const SizedBox(height: LuminSpacing.xxl),
        const Icon(Icons.inbox_outlined,
            size: 48, color: LuminColors.textMuted),
        const SizedBox(height: LuminSpacing.md),
        Text(
          _heading(),
          style: Theme.of(context).textTheme.bodyMedium,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: LuminSpacing.xs),
        Text(
          isLive
              ? 'Engine is scanning 75 pairs.\nNew paid signals appear here when they fire.'
              : 'Pull down to refresh.',
          textAlign: TextAlign.center,
          style: const TextStyle(color: LuminColors.textMuted, fontSize: 11),
        ),
      ],
    );
  }
}

class _SignalsLoading extends StatelessWidget {
  const _SignalsLoading();

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(
        parent: BouncingScrollPhysics(),
      ),
      children: const [
        SizedBox(height: LuminSpacing.xxl),
        Center(
          child: SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: LuminColors.accent,
            ),
          ),
        ),
      ],
    );
  }
}

class _SignalsError extends StatelessWidget {
  const _SignalsError({required this.error, required this.onRetry});
  final String error;
  final Future<void> Function() onRetry;

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(
        parent: BouncingScrollPhysics(),
      ),
      padding: const EdgeInsets.all(LuminSpacing.lg),
      children: [
        const SizedBox(height: LuminSpacing.xxl),
        const Icon(Icons.cloud_off, color: LuminColors.loss, size: 40),
        const SizedBox(height: LuminSpacing.md),
        const Text(
          'Could not load signals',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: LuminColors.textPrimary,
            fontSize: 15,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: LuminSpacing.sm),
        Text(
          error,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: LuminColors.textSecondary,
            fontSize: 11,
            height: 1.4,
          ),
        ),
        const SizedBox(height: LuminSpacing.md),
        Center(
          child: FilledButton.icon(
            style: FilledButton.styleFrom(
              backgroundColor: LuminColors.accent,
              foregroundColor: LuminColors.bgDeep,
            ),
            onPressed: onRetry,
            icon: const Icon(Icons.refresh, size: 18),
            label: const Text('Retry'),
          ),
        ),
      ],
    );
  }
}

class _SignalCard extends StatelessWidget {
  const _SignalCard({required this.sig});
  final MockSignal sig;

  Color _statusColor() {
    switch (sig.status) {
      case 'TP1_HIT':
      case 'TP2_HIT':
      case 'TP3_HIT':
      case 'FULL_TP_HIT':
        return LuminColors.success;
      case 'SL_HIT':
        return LuminColors.loss;
      case 'INVALIDATED':
      case 'EXPIRED':
      case 'CANCELLED':
        return LuminColors.textMuted;
      default:
        return LuminColors.accent;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLong = sig.direction == 'LONG';
    final pnlPositive = sig.pnlPct >= 0;
    return LuminCard(
      onTap: () => _showDetail(context),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                sig.symbol,
                style: const TextStyle(
                  color: LuminColors.textPrimary,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(width: LuminSpacing.sm),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: LuminSpacing.sm,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: (isLong ? LuminColors.success : LuminColors.loss)
                      .withOpacity(0.15),
                  borderRadius: BorderRadius.circular(LuminRadii.sm),
                ),
                child: Text(
                  sig.direction,
                  style: TextStyle(
                    color: isLong ? LuminColors.success : LuminColors.loss,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5,
                  ),
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: LuminSpacing.sm,
                  vertical: 2,
                ),
                decoration: BoxDecoration(
                  color: LuminColors.accent.withOpacity(0.10),
                  borderRadius: BorderRadius.circular(LuminRadii.sm),
                ),
                child: Text(
                  '${sig.confidence.toStringAsFixed(1)} ${sig.tier}',
                  style: const TextStyle(
                    color: LuminColors.accent,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: LuminSpacing.xs),
          Text(
            '${sig.agentName} • ${sig.setupName}',
            style: const TextStyle(
              color: LuminColors.textSecondary,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: LuminSpacing.md),
          Row(
            children: [
              Expanded(
                child: _PriceCol(
                  label: 'Entry',
                  value: formatPrice(sig.entry),
                ),
              ),
              Expanded(
                child: _PriceCol(
                  label: 'SL',
                  value: formatPrice(sig.sl),
                  color: LuminColors.loss,
                ),
              ),
              Expanded(
                child: _PriceCol(
                  label: 'TP1',
                  value: formatPrice(sig.tp1),
                  color: LuminColors.success,
                ),
              ),
              Expanded(
                child: _PriceCol(
                  label: 'TP3',
                  value: formatPrice(sig.tp3),
                  color: LuminColors.success,
                ),
              ),
            ],
          ),
          const SizedBox(height: LuminSpacing.md),
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: _statusColor(),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: LuminSpacing.xs),
              Text(
                sig.status,
                style: TextStyle(
                  color: _statusColor(),
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.3,
                ),
              ),
              const SizedBox(width: LuminSpacing.sm),
              Text(
                '• ${formatAge(sig.minutesAgo)} ago',
                style: const TextStyle(
                  color: LuminColors.textMuted,
                  fontSize: 11,
                ),
              ),
              const Spacer(),
              Text(
                formatPct(sig.pnlPct),
                style: TextStyle(
                  color: pnlPositive ? LuminColors.success : LuminColors.loss,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showDetail(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: LuminColors.bgCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(LuminRadii.lg),
        ),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(LuminSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: LuminColors.textMuted,
                  borderRadius: BorderRadius.circular(LuminRadii.pill),
                ),
              ),
            ),
            const SizedBox(height: LuminSpacing.lg),
            Text(
              '${sig.symbol} ${sig.direction}',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: LuminSpacing.xs),
            Text(
              'Signal ${sig.id} • ${sig.agentName}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: LuminSpacing.lg),
            Container(
              height: 120,
              decoration: BoxDecoration(
                color: LuminColors.bgElevated,
                borderRadius: BorderRadius.circular(LuminRadii.md),
                border: Border.all(color: LuminColors.cardBorder),
              ),
              child: const Center(
                child: Text(
                  'Chart preview — coming with v0.1.0',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
            const SizedBox(height: LuminSpacing.lg),
            _DetailRow('TP2', formatPrice(sig.tp2)),
            _DetailRow('Confidence',
                '${sig.confidence.toStringAsFixed(1)} (${sig.tier})'),
            _DetailRow('Status', sig.status),
          ],
        ),
      ),
    );
  }
}

class _PriceCol extends StatelessWidget {
  const _PriceCol({required this.label, required this.value, this.color});
  final String label;
  final String value;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            color: LuminColors.textMuted,
            fontSize: 9,
            letterSpacing: 1.2,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            color: color ?? LuminColors.textPrimary,
            fontSize: 13,
            fontWeight: FontWeight.w500,
            letterSpacing: -0.3,
          ),
        ),
      ],
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow(this.label, this.value);
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: LuminSpacing.xs),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: const TextStyle(
                color: LuminColors.textMuted,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: LuminColors.textPrimary,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
EOF_SIGNALS

# ── pubspec.yaml version bump ──────────────────────────────────────────
echo "→ Bumping version → 0.0.9+9"
sed -i 's|^version: 0.0.8+8$|version: 0.0.9+9|' pubspec.yaml
grep -q "^version: 0.0.9+9$" pubspec.yaml || {
  echo "ERROR: pubspec version bump failed"
  exit 1
}

# ── Verify everything landed ───────────────────────────────────────────
echo "→ Verifying patches"
grep -q "formatPrice" lib/shared/format.dart || {
  echo "ERROR: format.dart missing"
  exit 1
}
grep -q "lastSignalAgeMinutes" lib/data/repository.dart || {
  echo "ERROR: AgentStat lifecycle fields missing"
  exit 1
}
grep -q "setup_class" lib/data/repository.dart || {
  echo "ERROR: setupClass query plumbing missing"
  exit 1
}
grep -q "_AgentDetailSheet" lib/features/agents/agents_page.dart || {
  echo "ERROR: agents detail sheet missing"
  exit 1
}
grep -q "_SubFilterRow" lib/features/signals/signals_page.dart || {
  echo "ERROR: signals sub-filter row missing"
  exit 1
}

# ── git stage + commit ─────────────────────────────────────────────────
echo "→ Stage + commit (then 'git push' triggers APK build)"
git add pubspec.yaml \
        lib/shared/format.dart \
        lib/data/repository.dart \
        lib/features/agents/agents_page.dart \
        lib/features/signals/signals_page.dart
git commit -m "feat(data): v0.0.9 — per-agent drill-down + status sub-filters + format helpers

- Repository contract: fetchSignals(setupClass:) and fetchActivity(setupClass:)
  pass an optional UPPER_SNAKE setup-class filter to /api/{signals,activity};
  AgentStat schema gains closedToday / tpHits / slHits / invalidated /
  lastSignalAgeMinutes (populated by engine PR #299).
- Agents tab: tap any agent → bottom sheet fetches that evaluator's
  lifecycle stats AND its 10 most-recent signals.  Subscribers see what
  each agent has actually shipped, not just metadata.
- Signals tab: 'Closed' chip now reveals a sub-filter row (All / TP /
  SL / Invalidated / Expired) so historical state diversity is visible
  at a glance instead of mashed into one bucket.
- New lib/shared/format.dart — pure-Dart formatters for price / P&L /
  pct / age.  Wired into signals page; pulse + trade retrofit deferred
  to v0.0.10 to keep this release scoped.

Pairs with engine PR #299.  App still works against old API (filter is
ignored server-side, lifecycle fields default to 0)."

echo
echo "✓ v0.0.9 ready.  'git push' to trigger APK build."
