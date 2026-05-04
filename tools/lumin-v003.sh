#!/usr/bin/env bash
# Lumin app v0.0.3 — mock-data dashboards on Pulse / Signals / Trade tabs.
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v003.sh
#   bash lumin-v003.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

echo "→ Updating Lumin app to v0.0.3 (real-looking dashboards on Pulse / Signals / Trade)…"

mkdir -p lib/data lib/shared/widgets lib/features/pulse lib/features/signals lib/features/trade

# pubspec.yaml ----------------------------------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.3+3

environment:
  sdk: ">=3.4.0 <4.0.0"
  flutter: ">=3.24.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
EOF_PUBSPEC

# ── lib/data/mock_data.dart ──────────────────────────────────────────────
cat > lib/data/mock_data.dart <<'EOF_MOCK_DATA'
/// Mock data — sample engine state, signals, and positions.
///
/// Replaced by repository implementations once the FastAPI backend
/// lands.  Until then the UI consumes these constants so users get a
/// real-looking app instead of "Coming soon" placeholders.  Each tab's
/// page passes ``isPreview: true`` to the preview banner so the data
/// is clearly marked as sample.
import 'package:flutter/material.dart';

class MockEngineSnapshot {
  const MockEngineSnapshot({
    required this.status,
    required this.regime,
    required this.regimePctTrending,
    required this.todayPnlUsd,
    required this.todayPnlPct,
    required this.dailyLossBudgetUsd,
    required this.dailyLossUsedUsd,
    required this.openPositions,
    required this.signalsToday,
    required this.uptime,
  });

  final String status;
  final String regime;
  final double regimePctTrending;
  final double todayPnlUsd;
  final double todayPnlPct;
  final double dailyLossBudgetUsd;
  final double dailyLossUsedUsd;
  final int openPositions;
  final int signalsToday;
  final String uptime;
}

const mockEngine = MockEngineSnapshot(
  status: 'Healthy',
  regime: 'TRENDING_UP',
  regimePctTrending: 54.4,
  todayPnlUsd: 12.84,
  todayPnlPct: 1.28,
  dailyLossBudgetUsd: 30.00,
  dailyLossUsedUsd: 0.00,
  openPositions: 1,
  signalsToday: 3,
  uptime: '2d 14h',
);

class MockSignal {
  const MockSignal({
    required this.id,
    required this.symbol,
    required this.direction,
    required this.setupName,
    required this.agentName,
    required this.entry,
    required this.sl,
    required this.tp1,
    required this.tp2,
    required this.tp3,
    required this.confidence,
    required this.tier,
    required this.status,
    required this.pnlPct,
    required this.minutesAgo,
  });

  final String id;
  final String symbol;
  final String direction; // LONG / SHORT
  final String setupName;
  final String agentName;
  final double entry;
  final double sl;
  final double tp1;
  final double tp2;
  final double tp3;
  final double confidence;
  final String tier; // A+ / B
  final String status; // ACTIVE / TP1_HIT / TP2_HIT / TP3_HIT / SL_HIT / INVALIDATED
  final double pnlPct;
  final int minutesAgo;
}

const List<MockSignal> mockSignals = [
  MockSignal(
    id: 'SIG-2841',
    symbol: 'ETHUSDT',
    direction: 'LONG',
    setupName: 'SR FLIP RETEST',
    agentName: 'The Architect',
    entry: 2329.0,
    sl: 2310.0,
    tp1: 2351.0,
    tp2: 2360.0,
    tp3: 2394.0,
    confidence: 83.5,
    tier: 'A+',
    status: 'ACTIVE',
    pnlPct: 0.42,
    minutesAgo: 18,
  ),
  MockSignal(
    id: 'SIG-2840',
    symbol: 'BTCUSDT',
    direction: 'SHORT',
    setupName: 'LIQUIDITY SWEEP REVERSAL',
    agentName: 'The Counter-Puncher',
    entry: 78240.0,
    sl: 78850.0,
    tp1: 77800.0,
    tp2: 77400.0,
    tp3: 76900.0,
    confidence: 71.2,
    tier: 'B',
    status: 'TP1_HIT',
    pnlPct: 0.56,
    minutesAgo: 142,
  ),
  MockSignal(
    id: 'SIG-2839',
    symbol: 'SOLUSDT',
    direction: 'LONG',
    setupName: 'FAILED AUCTION RECLAIM',
    agentName: 'The Reclaimer',
    entry: 142.85,
    sl: 141.20,
    tp1: 144.50,
    tp2: 145.80,
    tp3: 148.00,
    confidence: 68.4,
    tier: 'B',
    status: 'INVALIDATED',
    pnlPct: -0.04,
    minutesAgo: 421,
  ),
  MockSignal(
    id: 'SIG-2838',
    symbol: 'BNBUSDT',
    direction: 'LONG',
    setupName: 'QUIET COMPRESSION BREAK',
    agentName: 'The Coil Hunter',
    entry: 612.40,
    sl: 607.50,
    tp1: 618.20,
    tp2: 622.10,
    tp3: 628.50,
    confidence: 82.5,
    tier: 'A+',
    status: 'TP3_HIT',
    pnlPct: 2.78,
    minutesAgo: 880,
  ),
];

class MockPosition {
  const MockPosition({
    required this.symbol,
    required this.direction,
    required this.entry,
    required this.currentPrice,
    required this.qty,
    required this.pnlPct,
    required this.pnlUsd,
    required this.minutesOpen,
  });

  final String symbol;
  final String direction;
  final double entry;
  final double currentPrice;
  final double qty;
  final double pnlPct;
  final double pnlUsd;
  final int minutesOpen;
}

const List<MockPosition> mockPositions = [
  MockPosition(
    symbol: 'ETHUSDT',
    direction: 'LONG',
    entry: 2329.0,
    currentPrice: 2338.80,
    qty: 0.0429,
    pnlPct: 0.42,
    pnlUsd: 0.42,
    minutesOpen: 18,
  ),
];

class MockActivityEvent {
  const MockActivityEvent({
    required this.kind,
    required this.title,
    required this.subtitle,
    required this.minutesAgo,
    required this.color,
  });

  final String kind;
  final String title;
  final String subtitle;
  final int minutesAgo;
  final Color color;
}

const mockActivity = <MockActivityEvent>[
  MockActivityEvent(
    kind: 'OPEN',
    title: 'ETHUSDT LONG opened',
    subtitle: 'qty 0.0429 @ 2,329.00 — The Architect',
    minutesAgo: 18,
    color: Color(0xFF7BD3F7),
  ),
  MockActivityEvent(
    kind: 'TP1',
    title: 'BTCUSDT SHORT — TP1 hit',
    subtitle: '+0.56% on 33% partial — SL → breakeven',
    minutesAgo: 96,
    color: Color(0xFF4ADE80),
  ),
  MockActivityEvent(
    kind: 'OPEN',
    title: 'BTCUSDT SHORT opened',
    subtitle: 'qty 0.0009 @ 78,240.00 — The Counter-Puncher',
    minutesAgo: 142,
    color: Color(0xFF7BD3F7),
  ),
  MockActivityEvent(
    kind: 'INVAL',
    title: 'SOLUSDT LONG invalidated',
    subtitle: 'momentum_loss — closed at 142.79 (-0.04%)',
    minutesAgo: 421,
    color: Color(0xFF94A3B8),
  ),
  MockActivityEvent(
    kind: 'TP3',
    title: 'BNBUSDT LONG — TP3 hit',
    subtitle: '+2.78% — full close, signal lifecycle complete',
    minutesAgo: 880,
    color: Color(0xFF4ADE80),
  ),
];
EOF_MOCK_DATA

# ── lib/shared/widgets/preview_badge.dart ──────────────────────────────────────────────
cat > lib/shared/widgets/preview_badge.dart <<'EOF_PREVIEW_BADGE'
/// Preview banner — sits at the top of any tab showing mocked data.
///
/// Honest framing: clearly tells the user this is sample data while the
/// FastAPI backend wires up.  Without this badge a user could mistake
/// the mocked numbers for real engine state.
import 'package:flutter/material.dart';
import '../tokens.dart';

class PreviewBadge extends StatelessWidget {
  const PreviewBadge({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.fromLTRB(
        LuminSpacing.lg,
        LuminSpacing.sm,
        LuminSpacing.lg,
        LuminSpacing.md,
      ),
      padding: const EdgeInsets.symmetric(
        horizontal: LuminSpacing.md,
        vertical: LuminSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: LuminColors.warn.withOpacity(0.10),
        borderRadius: BorderRadius.circular(LuminRadii.sm),
        border: Border.all(color: LuminColors.warn.withOpacity(0.30)),
      ),
      child: Row(
        children: const [
          Icon(Icons.info_outline, color: LuminColors.warn, size: 16),
          SizedBox(width: LuminSpacing.sm),
          Expanded(
            child: Text(
              'Preview — sample data.  Live engine data lands when the backend wires up.',
              style: TextStyle(
                color: LuminColors.warn,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
EOF_PREVIEW_BADGE

# ── lib/shared/widgets/stat_pill.dart ──────────────────────────────────────────────
cat > lib/shared/widgets/stat_pill.dart <<'EOF_STAT_PILL'
/// Compact label-value pill for dashboard stats.
import 'package:flutter/material.dart';
import '../tokens.dart';

class StatPill extends StatelessWidget {
  const StatPill({
    super.key,
    required this.label,
    required this.value,
    this.valueColor,
    this.icon,
  });

  final String label;
  final String value;
  final Color? valueColor;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            if (icon != null) ...[
              Icon(icon, size: 14, color: LuminColors.textMuted),
              const SizedBox(width: LuminSpacing.xs),
            ],
            Text(
              label.toUpperCase(),
              style: const TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: LuminSpacing.xs),
        Text(
          value,
          style: TextStyle(
            color: valueColor ?? LuminColors.textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.w500,
            letterSpacing: -0.5,
          ),
        ),
      ],
    );
  }
}
EOF_STAT_PILL

# ── lib/features/pulse/pulse_page.dart ──────────────────────────────────────────────
cat > lib/features/pulse/pulse_page.dart <<'EOF_PULSE_PAGE'
/// Pulse — engine status dashboard.
///
/// Real-looking dashboard built against [mockEngine] + [mockSignals].
/// When the FastAPI backend lands, swap the mock-data imports for a
/// repository call — UI components don't change.
import 'package:flutter/material.dart';

import '../../data/mock_data.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import '../../shared/widgets/preview_badge.dart';
import '../../shared/widgets/stat_pill.dart';

class PulsePage extends StatelessWidget {
  const PulsePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pulse')),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _EngineStatusCard(),
          const SizedBox(height: LuminSpacing.md),
          _RegimeAndPnlRow(),
          const SizedBox(height: LuminSpacing.md),
          _DailyLossBudgetCard(),
          const SizedBox(height: LuminSpacing.md),
          _RecentSignalsCard(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }
}

class _EngineStatusCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final isHealthy = mockEngine.status == 'Healthy';
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
                    'Engine ${mockEngine.status.toLowerCase()}',
                    style: const TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'Up ${mockEngine.uptime} • scanning 75 pairs',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.flash_on,
              color: LuminColors.accent,
              size: 18,
            ),
          ],
        ),
      ),
    );
  }
}

class _RegimeAndPnlRow extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final pnlPositive = mockEngine.todayPnlUsd >= 0;
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
                    value: mockEngine.regime,
                    icon: Icons.bar_chart_outlined,
                    valueColor: LuminColors.accent,
                  ),
                  const SizedBox(height: LuminSpacing.sm),
                  Text(
                    '${mockEngine.regimePctTrending.toStringAsFixed(1)}% of cycles',
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
                        '${pnlPositive ? '+' : ''}\$${mockEngine.todayPnlUsd.toStringAsFixed(2)}',
                    valueColor:
                        pnlPositive ? LuminColors.success : LuminColors.loss,
                    icon: pnlPositive
                        ? Icons.trending_up
                        : Icons.trending_down,
                  ),
                  const SizedBox(height: LuminSpacing.sm),
                  Text(
                    '${pnlPositive ? '+' : ''}${mockEngine.todayPnlPct.toStringAsFixed(2)}% on margin',
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
  @override
  Widget build(BuildContext context) {
    final used = mockEngine.dailyLossUsedUsd.abs();
    final budget = mockEngine.dailyLossBudgetUsd;
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
  @override
  Widget build(BuildContext context) {
    final recent = mockSignals.take(3).toList();
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
EOF_PULSE_PAGE

# ── lib/features/signals/signals_page.dart ──────────────────────────────────────────────
cat > lib/features/signals/signals_page.dart <<'EOF_SIGNALS_PAGE'
/// Signals — live + closed feed.
///
/// Filter chips (All / Open / Closed) toggle the visible subset.  Each
/// signal renders as a card with symbol, direction, agent, entry/SL/TP,
/// confidence tier, and live PnL.  Tap → detail bottom sheet (placeholder
/// for now; real chart preview lands when backend ships).
import 'package:flutter/material.dart';

import '../../data/mock_data.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import '../../shared/widgets/preview_badge.dart';

enum _SignalFilter { all, open, closed }

class SignalsPage extends StatefulWidget {
  const SignalsPage({super.key});

  @override
  State<SignalsPage> createState() => _SignalsPageState();
}

class _SignalsPageState extends State<SignalsPage> {
  _SignalFilter _filter = _SignalFilter.all;

  bool _isOpen(MockSignal s) => s.status == 'ACTIVE';

  List<MockSignal> get _filtered {
    switch (_filter) {
      case _SignalFilter.open:
        return mockSignals.where(_isOpen).toList();
      case _SignalFilter.closed:
        return mockSignals.where((s) => !_isOpen(s)).toList();
      case _SignalFilter.all:
        return mockSignals;
    }
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filtered;
    return Scaffold(
      appBar: AppBar(title: const Text('Signals')),
      body: Column(
        children: [
          const PreviewBadge(),
          _FilterRow(
            current: _filter,
            onChanged: (f) => setState(() => _filter = f),
          ),
          const SizedBox(height: LuminSpacing.sm),
          if (filtered.isEmpty)
            _EmptyState(filter: _filter)
          else
            Expanded(
              child: ListView.separated(
                physics: const BouncingScrollPhysics(),
                padding: const EdgeInsets.symmetric(
                  horizontal: LuminSpacing.lg,
                ),
                itemCount: filtered.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(height: LuminSpacing.md),
                itemBuilder: (_, i) => _SignalCard(sig: filtered[i]),
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
              label: f.name[0].toUpperCase() + f.name.substring(1),
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

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.filter});
  final _SignalFilter filter;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(LuminSpacing.xl),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.inbox_outlined,
                size: 48,
                color: LuminColors.textMuted,
              ),
              const SizedBox(height: LuminSpacing.md),
              Text(
                filter == _SignalFilter.open
                    ? 'No open signals right now'
                    : 'No closed signals yet',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
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
          // Header row.
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
          // Agent + setup
          Text(
            '${sig.agentName} • ${sig.setupName}',
            style: const TextStyle(
              color: LuminColors.textSecondary,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: LuminSpacing.md),
          // Price levels row.
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
          // Status footer.
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
                  color:
                      pnlPositive ? LuminColors.success : LuminColors.loss,
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
                  'Chart preview — coming with backend',
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
EOF_SIGNALS_PAGE

# ── lib/features/trade/trade_page.dart ──────────────────────────────────────────────
cat > lib/features/trade/trade_page.dart <<'EOF_TRADE_PAGE'
/// Trade — auto-execution control + activity log.
///
/// Live / Demo mode toggle at the top, open positions list, and a
/// time-ordered activity log of opens / TP hits / SL hits / invalidations.
/// Wires to `/api/auto-mode` + `/api/trades` once the backend ships.
import 'package:flutter/material.dart';

import '../../data/mock_data.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import '../../shared/widgets/preview_badge.dart';

class TradePage extends StatefulWidget {
  const TradePage({super.key});

  @override
  State<TradePage> createState() => _TradePageState();
}

class _TradePageState extends State<TradePage> {
  // 0 = Off, 1 = Paper, 2 = Live
  int _mode = 1;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Trade')),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _ModeToggle(
            mode: _mode,
            onChanged: (m) => setState(() => _mode = m),
          ),
          const SizedBox(height: LuminSpacing.md),
          _OpenPositionsCard(),
          const SizedBox(height: LuminSpacing.md),
          _ActivityCard(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }
}

class _ModeToggle extends StatelessWidget {
  const _ModeToggle({required this.mode, required this.onChanged});

  final int mode;
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
            const Text(
              'AUTO-EXECUTION MODE',
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
                for (int i = 0; i < 3; i++) ...[
                  Expanded(
                    child: _ModeButton(
                      label: _labels[i],
                      icon: _icons[i],
                      selected: mode == i,
                      color: _modeColor(i),
                      onTap: () => onChanged(i),
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
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
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
    );
  }
}

class _OpenPositionsCard extends StatelessWidget {
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
            if (mockPositions.isEmpty)
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
              for (int i = 0; i < mockPositions.length; i++) ...[
                _PositionRow(p: mockPositions[i]),
                if (i < mockPositions.length - 1)
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
            for (int i = 0; i < mockActivity.length; i++) ...[
              _ActivityRow(
                event: mockActivity[i],
                ago: _agoLabel(mockActivity[i].minutesAgo),
              ),
              if (i < mockActivity.length - 1)
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
EOF_TRADE_PAGE


echo "→ Files written:"
find lib/data lib/shared/widgets/preview_badge.dart lib/shared/widgets/stat_pill.dart \
     lib/features/pulse/pulse_page.dart lib/features/signals/signals_page.dart \
     lib/features/trade/trade_page.dart -type f | sort
echo
echo "→ Staging + committing…"
git add pubspec.yaml lib/

git -c user.email="$(git config user.email || echo bot@lumin.local)" \
    -c user.name="$(git config user.name || echo Lumin Bootstrap)" \
    commit -m "feat: real-looking dashboards on Pulse / Signals / Trade (v0.0.3)

- Pulse: engine status pill (green/red dot), regime + today P&L row,
  daily-loss budget bar with progress, recent signals list with status
  bars and color-coded PnL
- Signals: filter chips (All / Open / Closed), signal cards with
  symbol/direction/agent/setup/Entry/SL/TP1/TP3/confidence-tier/PnL,
  tap → bottom sheet with chart-preview placeholder + detail rows
- Trade: 3-button mode toggle (Off / Paper / Live) with color coding,
  open positions card, time-ordered activity feed (OPEN / TP1 / TP3 /
  INVAL events with colored badges)
- New shared widgets: PreviewBadge (warn-styled banner), StatPill
  (label + value column)
- All mocked data lives in lib/data/mock_data.dart — single swap
  point when the FastAPI backend wires up
- PreviewBadge clearly marks every dashboard as sample data so users
  don't mistake mocked numbers for live engine state

Pushes via existing GitHub Actions APK pipeline; no workflow changes."

echo
echo "→ Done.  Push to trigger the APK build:"
echo
echo "  git push"
echo
echo "Watch:  https://github.com/mkmk749278/lumin-app/actions"
