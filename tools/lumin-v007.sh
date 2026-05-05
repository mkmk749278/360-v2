#!/usr/bin/env bash
# Lumin app v0.0.7 — Pages on live data.
#
# Refactors Pulse / Signals / Trade pages to FutureBuilder against the
# repository.  When the app's data source is Live, every render hits
# the engine through the auto-authenticated client (v0.0.6 plumbing).
# Pull-to-refresh on every page; mode toggle on Trade actually flips
# the engine's auto-execution mode via /api/auto-mode POST.
#
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v007.sh
#   bash lumin-v007.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

echo "→ Updating Lumin app to v0.0.7 (Pulse / Signals / Trade on live data)…"

mkdir -p lib/features/pulse lib/features/signals lib/features/trade

# pubspec.yaml ----------------------------------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.7+7

environment:
  sdk: ">=3.4.0 <4.0.0"
  flutter: ">=3.24.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8
  http: ^1.2.0
  shared_preferences: ^2.3.0
  flutter_secure_storage: ^9.2.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
EOF_PUBSPEC

# ── lib/features/pulse/pulse_page.dart ──────────────────────────────────────────
cat > lib/features/pulse/pulse_page.dart <<'EOF_PULSE'
/// Pulse — engine status dashboard.
///
/// FutureBuilder against the live repo (or MockRepository when offline).
/// Pull-to-refresh re-fetches; tier-conditional rendering hooks added so
/// v0.0.8+ can hide paid-only widgets without restructuring the page.
import 'package:flutter/material.dart';

import '../../data/app_config.dart';
import '../../data/mock_data.dart';
import '../../data/repository.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import '../../shared/widgets/preview_badge.dart';
import '../../shared/widgets/stat_pill.dart';

class _PulseBundle {
  const _PulseBundle({required this.engine, required this.recent});
  final MockEngineSnapshot engine;
  final List<MockSignal> recent;
}

class PulsePage extends StatefulWidget {
  const PulsePage({super.key});

  @override
  State<PulsePage> createState() => _PulsePageState();
}

class _PulsePageState extends State<PulsePage> {
  late Future<_PulseBundle> _future;
  LuminRepository? _lastRepo;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final repo = AppConfigScope.of(context).repo;
    if (repo != _lastRepo) {
      _lastRepo = repo;
      _future = _load(repo);
    }
  }

  Future<_PulseBundle> _load(LuminRepository repo) async {
    final results = await Future.wait([
      repo.fetchPulse(),
      repo.fetchSignals(status: 'all', limit: 3),
    ]);
    return _PulseBundle(
      engine: results[0] as MockEngineSnapshot,
      recent: (results[1] as List).cast<MockSignal>(),
    );
  }

  Future<void> _refresh() async {
    final repo = AppConfigScope.of(context).repo;
    setState(() => _future = _load(repo));
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppConfigScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Pulse')),
      body: RefreshIndicator(
        color: LuminColors.accent,
        onRefresh: _refresh,
        child: FutureBuilder<_PulseBundle>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState == ConnectionState.waiting &&
                !snap.hasData) {
              return const _PulseSkeleton();
            }
            if (snap.hasError) {
              return _ErrorView(
                error: snap.error.toString(),
                onRetry: _refresh,
                isLive: scope.repo.isLive,
              );
            }
            final data = snap.data!;
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              children: [
                if (!scope.repo.isLive) const PreviewBadge(),
                _EngineStatusCard(engine: data.engine),
                const SizedBox(height: LuminSpacing.md),
                _RegimeAndPnlRow(engine: data.engine),
                const SizedBox(height: LuminSpacing.md),
                _DailyLossBudgetCard(engine: data.engine),
                const SizedBox(height: LuminSpacing.md),
                _RecentSignalsCard(recent: data.recent),
                const SizedBox(height: LuminSpacing.xl),
              ],
            );
          },
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Cards (data-driven via constructor)
// ---------------------------------------------------------------------------

class _EngineStatusCard extends StatelessWidget {
  const _EngineStatusCard({required this.engine});
  final MockEngineSnapshot engine;

  @override
  Widget build(BuildContext context) {
    final isHealthy = engine.status == 'Healthy';
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Row(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: isHealthy ? LuminColors.success : LuminColors.warn,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: (isHealthy ? LuminColors.success : LuminColors.warn)
                        .withOpacity(0.4),
                    blurRadius: 8,
                  ),
                ],
              ),
            ),
            const SizedBox(width: LuminSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Engine ${engine.status.toLowerCase()}',
                    style: const TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Up ${engine.uptime} • scanning 75 pairs',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.flash_on, color: LuminColors.accent, size: 18),
          ],
        ),
      ),
    );
  }
}

class _RegimeAndPnlRow extends StatelessWidget {
  const _RegimeAndPnlRow({required this.engine});
  final MockEngineSnapshot engine;

  @override
  Widget build(BuildContext context) {
    final pnlPositive = engine.todayPnlUsd >= 0;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Row(
        children: [
          Expanded(
            child: LuminCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  StatPill(
                    label: 'Regime',
                    value: engine.regime,
                    icon: Icons.bar_chart_outlined,
                    valueColor: LuminColors.accent,
                  ),
                  const SizedBox(height: LuminSpacing.sm),
                  Text(
                    '${engine.regimePctTrending.toStringAsFixed(1)}% of cycles',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: LuminSpacing.md),
          Expanded(
            child: LuminCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  StatPill(
                    label: "Today's P&L",
                    value:
                        '${pnlPositive ? '+' : ''}\$${engine.todayPnlUsd.toStringAsFixed(2)}',
                    valueColor: pnlPositive
                        ? LuminColors.success
                        : LuminColors.loss,
                    icon: pnlPositive
                        ? Icons.trending_up
                        : Icons.trending_down,
                  ),
                  const SizedBox(height: LuminSpacing.sm),
                  Text(
                    '${pnlPositive ? '+' : ''}${engine.todayPnlPct.toStringAsFixed(2)}% on margin',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _DailyLossBudgetCard extends StatelessWidget {
  const _DailyLossBudgetCard({required this.engine});
  final MockEngineSnapshot engine;

  @override
  Widget build(BuildContext context) {
    final used = engine.dailyLossUsedUsd.abs();
    final budget = engine.dailyLossBudgetUsd;
    final pct = budget == 0 ? 0.0 : (used / budget).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.shield_outlined,
                    color: LuminColors.accent, size: 16),
                const SizedBox(width: LuminSpacing.xs),
                const Text(
                  'DAILY LOSS BUDGET',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 10,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                Text(
                  '\$${used.toStringAsFixed(2)} / \$${budget.toStringAsFixed(2)}',
                  style: const TextStyle(
                    color: LuminColors.textPrimary,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
            const SizedBox(height: LuminSpacing.sm),
            ClipRRect(
              borderRadius: BorderRadius.circular(LuminRadii.pill),
              child: LinearProgressIndicator(
                value: pct,
                minHeight: 6,
                backgroundColor: LuminColors.bgElevated,
                valueColor: AlwaysStoppedAnimation(
                  pct < 0.7
                      ? LuminColors.success
                      : pct < 0.95
                          ? LuminColors.warn
                          : LuminColors.loss,
                ),
              ),
            ),
            const SizedBox(height: LuminSpacing.xs),
            Text(
              pct < 0.01
                  ? 'No losses today — budget intact'
                  : '${(pct * 100).toStringAsFixed(0)}% of daily budget used',
              style: const TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RecentSignalsCard extends StatelessWidget {
  const _RecentSignalsCard({required this.recent});
  final List<MockSignal> recent;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.history, color: LuminColors.accent, size: 16),
                SizedBox(width: LuminSpacing.xs),
                Text(
                  'RECENT SIGNALS',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 10,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            if (recent.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: LuminSpacing.lg),
                child: Center(
                  child: Text(
                    'No signals yet',
                    style: TextStyle(
                      color: LuminColors.textMuted,
                      fontSize: 13,
                    ),
                  ),
                ),
              )
            else
              for (final sig in recent) _RecentSignalRow(sig: sig),
          ],
        ),
      ),
    );
  }
}

class _RecentSignalRow extends StatelessWidget {
  const _RecentSignalRow({required this.sig});
  final MockSignal sig;

  Color _statusColor() {
    switch (sig.status) {
      case 'TP1_HIT':
      case 'TP2_HIT':
      case 'TP3_HIT':
        return LuminColors.success;
      case 'SL_HIT':
        return LuminColors.loss;
      case 'INVALIDATED':
        return LuminColors.textMuted;
      default:
        return LuminColors.accent;
    }
  }

  String _agoLabel() {
    if (sig.minutesAgo < 60) return '${sig.minutesAgo}m ago';
    if (sig.minutesAgo < 1440) return '${(sig.minutesAgo / 60).round()}h ago';
    return '${(sig.minutesAgo / 1440).round()}d ago';
  }

  @override
  Widget build(BuildContext context) {
    final pnlPositive = sig.pnlPct >= 0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: LuminSpacing.sm),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 40,
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
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: LuminSpacing.xs),
                    Text(
                      sig.direction,
                      style: TextStyle(
                        color: sig.direction == 'LONG'
                            ? LuminColors.success
                            : LuminColors.loss,
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(width: LuminSpacing.xs),
                    Text(
                      '• ${sig.status}',
                      style: TextStyle(
                        color: _statusColor(),
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  '${sig.agentName} • ${_agoLabel()}',
                  style: const TextStyle(
                    color: LuminColors.textSecondary,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          Text(
            '${pnlPositive ? '+' : ''}${sig.pnlPct.toStringAsFixed(2)}%',
            style: TextStyle(
              color: pnlPositive ? LuminColors.success : LuminColors.loss,
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Loading + error views (shared across pages)
// ---------------------------------------------------------------------------

class _PulseSkeleton extends StatelessWidget {
  const _PulseSkeleton();

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
        SizedBox(height: LuminSpacing.md),
        Center(
          child: Text(
            'Connecting to engine…',
            style: TextStyle(color: LuminColors.textSecondary, fontSize: 12),
          ),
        ),
      ],
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({
    required this.error,
    required this.onRetry,
    required this.isLive,
  });
  final String error;
  final Future<void> Function() onRetry;
  final bool isLive;

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(
        parent: BouncingScrollPhysics(),
      ),
      padding: const EdgeInsets.all(LuminSpacing.lg),
      children: [
        const SizedBox(height: LuminSpacing.xxl),
        const Icon(Icons.cloud_off, color: LuminColors.loss, size: 48),
        const SizedBox(height: LuminSpacing.md),
        const Text(
          'Could not reach engine',
          textAlign: TextAlign.center,
          style: TextStyle(
            color: LuminColors.textPrimary,
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: LuminSpacing.sm),
        Text(
          error,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: LuminColors.textSecondary,
            fontSize: 12,
            height: 1.4,
          ),
        ),
        const SizedBox(height: LuminSpacing.lg),
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
        if (isLive) ...[
          const SizedBox(height: LuminSpacing.sm),
          const Center(
            child: Text(
              'Pull down to refresh, or check Menu → API keys.',
              textAlign: TextAlign.center,
              style: TextStyle(color: LuminColors.textMuted, fontSize: 11),
            ),
          ),
        ],
      ],
    );
  }
}
EOF_PULSE

# ── lib/features/signals/signals_page.dart ──────────────────────────────────────────
cat > lib/features/signals/signals_page.dart <<'EOF_SIGNALS'
/// Signals — live + closed feed.
///
/// Filter chips trigger a re-fetch via the repository.  Pull-to-refresh
/// reloads.  Bottom-sheet detail unchanged from v0.0.3.
import 'package:flutter/material.dart';

import '../../data/app_config.dart';
import '../../data/mock_data.dart';
import '../../data/repository.dart';
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

class SignalsPage extends StatefulWidget {
  const SignalsPage({super.key});

  @override
  State<SignalsPage> createState() => _SignalsPageState();
}

class _SignalsPageState extends State<SignalsPage> {
  _SignalFilter _filter = _SignalFilter.all;
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
    });
    _refetch();
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
                  final items = snap.data ?? const <MockSignal>[];
                  if (items.isEmpty) {
                    return _SignalsEmpty(filter: _filter);
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
            _FilterChip(
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

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

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
          padding: const EdgeInsets.symmetric(
            horizontal: LuminSpacing.md,
            vertical: LuminSpacing.xs + 2,
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
              fontSize: 12,
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
  const _SignalsEmpty({required this.filter});
  final _SignalFilter filter;

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
          filter == _SignalFilter.open
              ? 'No open signals right now'
              : filter == _SignalFilter.closed
                  ? 'No closed signals yet'
                  : 'No signals yet',
          style: Theme.of(context).textTheme.bodyMedium,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: LuminSpacing.xs),
        const Text(
          'Pull down to refresh.',
          textAlign: TextAlign.center,
          style: TextStyle(color: LuminColors.textMuted, fontSize: 11),
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
        return LuminColors.success;
      case 'SL_HIT':
        return LuminColors.loss;
      case 'INVALIDATED':
        return LuminColors.textMuted;
      default:
        return LuminColors.accent;
    }
  }

  String _agoLabel() {
    if (sig.minutesAgo < 60) return '${sig.minutesAgo}m';
    if (sig.minutesAgo < 1440) return '${(sig.minutesAgo / 60).round()}h';
    return '${(sig.minutesAgo / 1440).round()}d';
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
                  value: sig.entry.toStringAsFixed(2),
                ),
              ),
              Expanded(
                child: _PriceCol(
                  label: 'SL',
                  value: sig.sl.toStringAsFixed(2),
                  color: LuminColors.loss,
                ),
              ),
              Expanded(
                child: _PriceCol(
                  label: 'TP1',
                  value: sig.tp1.toStringAsFixed(2),
                  color: LuminColors.success,
                ),
              ),
              Expanded(
                child: _PriceCol(
                  label: 'TP3',
                  value: sig.tp3.toStringAsFixed(2),
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
                '• ${_agoLabel()} ago',
                style: const TextStyle(
                  color: LuminColors.textMuted,
                  fontSize: 11,
                ),
              ),
              const Spacer(),
              Text(
                '${pnlPositive ? '+' : ''}${sig.pnlPct.toStringAsFixed(2)}%',
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
                  'Chart preview — coming with v0.0.8',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 12,
                  ),
                ),
              ),
            ),
            const SizedBox(height: LuminSpacing.lg),
            _DetailRow('TP2', sig.tp2.toStringAsFixed(2)),
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

# ── lib/features/trade/trade_page.dart ──────────────────────────────────────────
cat > lib/features/trade/trade_page.dart <<'EOF_TRADE'
/// Trade — auto-execution control + activity log.
///
/// FutureBuilder against the live repo.  Mode toggle calls
/// ``repo.setAutoMode(...)`` against the engine; on success the page
/// refetches positions and activity.  The engine refuses mode changes
/// with open positions or missing creds — those refusals surface as a
/// SnackBar with the engine's reason.
import 'package:flutter/material.dart';

import '../../data/app_config.dart';
import '../../data/mock_data.dart';
import '../../data/repository.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import '../../shared/widgets/preview_badge.dart';

class _TradeBundle {
  const _TradeBundle({
    required this.autoMode,
    required this.positions,
    required this.activity,
  });
  final AutoModeStatus autoMode;
  final List<MockPosition> positions;
  final List<MockActivityEvent> activity;
}

class TradePage extends StatefulWidget {
  const TradePage({super.key});

  @override
  State<TradePage> createState() => _TradePageState();
}

class _TradePageState extends State<TradePage> {
  late Future<_TradeBundle> _future;
  LuminRepository? _lastRepo;
  bool _switchingMode = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final repo = AppConfigScope.of(context).repo;
    if (repo != _lastRepo) {
      _lastRepo = repo;
      _future = _load(repo);
    }
  }

  Future<_TradeBundle> _load(LuminRepository repo) async {
    final results = await Future.wait([
      repo.fetchAutoMode(),
      repo.fetchPositions(),
      repo.fetchActivity(limit: 30),
    ]);
    return _TradeBundle(
      autoMode: results[0] as AutoModeStatus,
      positions: (results[1] as List).cast<MockPosition>(),
      activity: (results[2] as List).cast<MockActivityEvent>(),
    );
  }

  Future<void> _refresh() async {
    final repo = AppConfigScope.of(context).repo;
    setState(() => _future = _load(repo));
    await _future;
  }

  Future<void> _changeMode(String newMode) async {
    if (_switchingMode) return;
    final repo = AppConfigScope.of(context).repo;
    setState(() => _switchingMode = true);
    try {
      await repo.setAutoMode(newMode);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Mode → ${newMode.toUpperCase()}'),
          duration: const Duration(seconds: 2),
        ),
      );
      await _refresh();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Refused: $e'),
          duration: const Duration(seconds: 4),
          backgroundColor: LuminColors.loss,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _switchingMode = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final scope = AppConfigScope.of(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Trade')),
      body: RefreshIndicator(
        color: LuminColors.accent,
        onRefresh: _refresh,
        child: FutureBuilder<_TradeBundle>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState == ConnectionState.waiting &&
                !snap.hasData) {
              return const _TradeLoading();
            }
            if (snap.hasError) {
              return _TradeError(error: snap.error.toString(), onRetry: _refresh);
            }
            final data = snap.data!;
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(
                parent: BouncingScrollPhysics(),
              ),
              children: [
                if (!scope.repo.isLive) const PreviewBadge(),
                _ModeToggle(
                  mode: _modeIndex(data.autoMode.mode),
                  switching: _switchingMode,
                  onChanged: (i) => _changeMode(_modeName(i)),
                ),
                const SizedBox(height: LuminSpacing.md),
                _OpenPositionsCard(positions: data.positions),
                const SizedBox(height: LuminSpacing.md),
                _ActivityCard(events: data.activity),
                const SizedBox(height: LuminSpacing.xl),
              ],
            );
          },
        ),
      ),
    );
  }

  static int _modeIndex(String mode) {
    switch (mode) {
      case 'paper':
        return 1;
      case 'live':
        return 2;
      default:
        return 0;
    }
  }

  static String _modeName(int idx) {
    switch (idx) {
      case 1:
        return 'paper';
      case 2:
        return 'live';
      default:
        return 'off';
    }
  }
}

class _ModeToggle extends StatelessWidget {
  const _ModeToggle({
    required this.mode,
    required this.switching,
    required this.onChanged,
  });

  final int mode;
  final bool switching;
  final ValueChanged<int> onChanged;

  static const _labels = ['Off', 'Paper', 'Live'];
  static const _icons = [
    Icons.power_settings_new,
    Icons.science_outlined,
    Icons.bolt,
  ];

  Color _modeColor(int i) {
    switch (i) {
      case 0:
        return LuminColors.textMuted;
      case 1:
        return LuminColors.warn;
      case 2:
        return LuminColors.loss;
      default:
        return LuminColors.textPrimary;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Text(
                  'AUTO-EXECUTION MODE',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 10,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                if (switching) ...[
                  const SizedBox(width: LuminSpacing.sm),
                  const SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(
                      strokeWidth: 1.5,
                      color: LuminColors.accent,
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            Row(
              children: [
                for (int i = 0; i < 3; i++) ...[
                  Expanded(
                    child: _ModeButton(
                      label: _labels[i],
                      icon: _icons[i],
                      selected: mode == i,
                      color: _modeColor(i),
                      onTap: switching ? null : () => onChanged(i),
                    ),
                  ),
                  if (i < 2) const SizedBox(width: LuminSpacing.sm),
                ],
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            Text(
              _description(mode),
              style: const TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _description(int m) {
    switch (m) {
      case 0:
        return 'Auto-trade disabled. Signals still publish to Telegram.';
      case 1:
        return 'Paper mode — fills are simulated, no real orders. Zero risk.';
      case 2:
        return 'Live — real orders on Binance Futures. Risk gates active.';
      default:
        return '';
    }
  }
}

class _ModeButton extends StatelessWidget {
  const _ModeButton({
    required this.label,
    required this.icon,
    required this.selected,
    required this.color,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final bool selected;
  final Color color;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final disabled = onTap == null;
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(LuminRadii.md),
      child: InkWell(
        borderRadius: BorderRadius.circular(LuminRadii.md),
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
          decoration: BoxDecoration(
            color: selected ? color.withOpacity(0.15) : LuminColors.bgElevated,
            borderRadius: BorderRadius.circular(LuminRadii.md),
            border: Border.all(
              color: selected ? color.withOpacity(0.50) : LuminColors.cardBorder,
            ),
          ),
          child: Opacity(
            opacity: disabled ? 0.6 : 1.0,
            child: Column(
              children: [
                Icon(
                  icon,
                  color: selected ? color : LuminColors.textSecondary,
                  size: 22,
                ),
                const SizedBox(height: LuminSpacing.xs),
                Text(
                  label,
                  style: TextStyle(
                    color: selected ? color : LuminColors.textSecondary,
                    fontSize: 12,
                    fontWeight:
                        selected ? FontWeight.w600 : FontWeight.w500,
                    letterSpacing: 0.3,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _OpenPositionsCard extends StatelessWidget {
  const _OpenPositionsCard({required this.positions});
  final List<MockPosition> positions;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.account_balance_wallet_outlined,
                    color: LuminColors.accent, size: 16),
                SizedBox(width: LuminSpacing.xs),
                Text(
                  'OPEN POSITIONS',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 10,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            if (positions.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: LuminSpacing.lg),
                child: Center(
                  child: Text(
                    'No open positions',
                    style: TextStyle(
                      color: LuminColors.textMuted,
                      fontSize: 13,
                    ),
                  ),
                ),
              )
            else
              for (int i = 0; i < positions.length; i++) ...[
                _PositionRow(p: positions[i]),
                if (i < positions.length - 1)
                  const Divider(
                    color: LuminColors.cardBorder,
                    height: LuminSpacing.lg,
                  ),
              ],
          ],
        ),
      ),
    );
  }
}

class _PositionRow extends StatelessWidget {
  const _PositionRow({required this.p});
  final MockPosition p;

  @override
  Widget build(BuildContext context) {
    final isLong = p.direction == 'LONG';
    final pnlPositive = p.pnlPct >= 0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              p.symbol,
              style: const TextStyle(
                color: LuminColors.textPrimary,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(width: LuminSpacing.xs),
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
                p.direction,
                style: TextStyle(
                  color: isLong ? LuminColors.success : LuminColors.loss,
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
              ),
            ),
            const Spacer(),
            Text(
              '${pnlPositive ? '+' : ''}\$${p.pnlUsd.toStringAsFixed(2)}',
              style: TextStyle(
                color: pnlPositive ? LuminColors.success : LuminColors.loss,
                fontSize: 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: LuminSpacing.xs),
        Text(
          'qty ${p.qty} @ ${p.entry.toStringAsFixed(2)} → ${p.currentPrice.toStringAsFixed(2)}',
          style: const TextStyle(
            color: LuminColors.textSecondary,
            fontSize: 11,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          '${p.minutesOpen}m open • ${pnlPositive ? '+' : ''}${p.pnlPct.toStringAsFixed(2)}%',
          style: TextStyle(
            color: pnlPositive ? LuminColors.success : LuminColors.loss,
            fontSize: 11,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _ActivityCard extends StatelessWidget {
  const _ActivityCard({required this.events});
  final List<MockActivityEvent> events;

  String _agoLabel(int m) {
    if (m < 60) return '${m}m';
    if (m < 1440) return '${(m / 60).round()}h';
    return '${(m / 1440).round()}d';
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: const [
                Icon(Icons.list_alt_outlined,
                    color: LuminColors.accent, size: 16),
                SizedBox(width: LuminSpacing.xs),
                Text(
                  'ACTIVITY',
                  style: TextStyle(
                    color: LuminColors.textMuted,
                    fontSize: 10,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            if (events.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: LuminSpacing.lg),
                child: Center(
                  child: Text(
                    'No activity yet',
                    style: TextStyle(
                      color: LuminColors.textMuted,
                      fontSize: 13,
                    ),
                  ),
                ),
              )
            else
              for (int i = 0; i < events.length; i++) ...[
                _ActivityRow(
                  event: events[i],
                  ago: _agoLabel(events[i].minutesAgo),
                ),
                if (i < events.length - 1)
                  const SizedBox(height: LuminSpacing.md),
              ],
          ],
        ),
      ),
    );
  }
}

class _ActivityRow extends StatelessWidget {
  const _ActivityRow({required this.event, required this.ago});
  final MockActivityEvent event;
  final String ago;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: event.color.withOpacity(0.15),
            borderRadius: BorderRadius.circular(LuminRadii.sm),
          ),
          alignment: Alignment.center,
          child: Text(
            event.kind,
            style: TextStyle(
              color: event.color,
              fontSize: 9,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.5,
            ),
          ),
        ),
        const SizedBox(width: LuminSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                event.title,
                style: const TextStyle(
                  color: LuminColors.textPrimary,
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                event.subtitle,
                style: const TextStyle(
                  color: LuminColors.textSecondary,
                  fontSize: 11,
                ),
              ),
            ],
          ),
        ),
        Text(
          ago,
          style: const TextStyle(
            color: LuminColors.textMuted,
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}

class _TradeLoading extends StatelessWidget {
  const _TradeLoading();

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

class _TradeError extends StatelessWidget {
  const _TradeError({required this.error, required this.onRetry});
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
          'Could not load Trade state',
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
EOF_TRADE

echo "  ✓ Pulse + Signals + Trade now use FutureBuilder against the live repo"

echo "→ Bumping version → 0.0.7+7 — done"
echo "→ Stage + commit + push (then GitHub Actions builds APK)"

git add lib/ pubspec.yaml
git commit -m "feat(pages): v0.0.7 — Pulse / Signals / Trade on live data

All three data-driven pages now FutureBuilder against the repository.
Pull-to-refresh on every page.  Trade mode toggle calls /api/auto-mode.
Loading skeleton + error view + Retry button on every page."

echo "✓ v0.0.7 ready.  'git push' to trigger APK build."
