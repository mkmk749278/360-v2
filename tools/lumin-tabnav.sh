#!/usr/bin/env bash
# Lumin app v0.0.2 — 5-tab navigation skeleton + 14 AI agent personas.
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-tabnav.sh
#   bash lumin-tabnav.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ]; then
  echo "ERROR: not in a git repo. Run from inside ~/lumin-app"
  exit 1
fi

if [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: this doesn't look like the lumin-app repo (no pubspec.yaml or wrong name)."
  exit 1
fi

echo "→ Updating Lumin app to v0.0.2 (5-tab navigation + 14 agents)…"

# Wipe old single-file main and rebuild the lib tree.
rm -f lib/main.dart
mkdir -p lib/app lib/features/pulse lib/features/signals lib/features/agents \
         lib/features/trade lib/features/settings lib/shared/widgets

# pubspec.yaml — version bump + comment ----------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.2+2

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

# lib/shared/tokens.dart -------------------------------------------------
cat > lib/shared/tokens.dart <<'EOF_TOKENS'
/// Brand tokens — Lumin design system.
import 'package:flutter/material.dart';

class LuminColors {
  LuminColors._();

  static const Color bgDeep = Color(0xFF0A0E1A);
  static const Color bgCard = Color(0xFF0F1729);
  static const Color bgElevated = Color(0xFF131C32);
  static const Color accent = Color(0xFF7BD3F7);
  static const Color accentMuted = Color(0xFF4A8DAA);
  static const Color textPrimary = Color(0xFFF8FAFC);
  static const Color textSecondary = Color(0xFF94A3B8);
  static const Color textMuted = Color(0xFF64748B);
  static const Color success = Color(0xFF4ADE80);
  static const Color warn = Color(0xFFF59E0B);
  static const Color loss = Color(0xFFF87171);

  static Color cardBorder = const Color(0xFF7BD3F7).withOpacity(0.10);
}

class LuminSpacing {
  LuminSpacing._();
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;
}

class LuminRadii {
  LuminRadii._();
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double pill = 999;
}
EOF_TOKENS

# lib/theme.dart ---------------------------------------------------------
cat > lib/theme.dart <<'EOF_THEME'
import 'package:flutter/material.dart';
import 'shared/tokens.dart';

ThemeData buildLuminTheme() {
  const accent = LuminColors.accent;
  const bg = LuminColors.bgDeep;
  const surface = LuminColors.bgCard;

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: bg,
    colorScheme: const ColorScheme.dark(
      primary: accent,
      secondary: accent,
      surface: surface,
      onPrimary: bg,
      onSecondary: bg,
      onSurface: LuminColors.textPrimary,
      error: LuminColors.loss,
    ),
    textTheme: const TextTheme(
      displayLarge: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w300, letterSpacing: 1.5),
      displayMedium: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w300, letterSpacing: 1.0),
      headlineLarge: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w400),
      headlineMedium: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w500),
      titleLarge: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w500),
      bodyLarge: TextStyle(color: LuminColors.textPrimary),
      bodyMedium: TextStyle(color: LuminColors.textSecondary),
      labelLarge: TextStyle(color: LuminColors.textPrimary, fontWeight: FontWeight.w500, letterSpacing: 0.5),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: surface,
      indicatorColor: accent.withOpacity(0.15),
      surfaceTintColor: surface,
      elevation: 0,
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: accent, fontSize: 12, fontWeight: FontWeight.w500);
        }
        return const TextStyle(color: LuminColors.textSecondary, fontSize: 12);
      }),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: accent, size: 24);
        }
        return const IconThemeData(color: LuminColors.textSecondary, size: 24);
      }),
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: bg,
      foregroundColor: LuminColors.textPrimary,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(color: LuminColors.textPrimary, fontSize: 24, fontWeight: FontWeight.w300, letterSpacing: 1.5),
    ),
    iconTheme: const IconThemeData(color: LuminColors.textPrimary),
  );
}
EOF_THEME

# lib/shared/widgets/lumin_card.dart -------------------------------------
cat > lib/shared/widgets/lumin_card.dart <<'EOF_CARD'
import 'package:flutter/material.dart';
import '../tokens.dart';

class LuminCard extends StatelessWidget {
  const LuminCard({super.key, required this.child, this.padding = const EdgeInsets.all(LuminSpacing.lg), this.onTap});

  final Widget child;
  final EdgeInsetsGeometry padding;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final card = Container(
      padding: padding,
      decoration: BoxDecoration(
        color: LuminColors.bgCard,
        borderRadius: BorderRadius.circular(LuminRadii.lg),
        border: Border.all(color: LuminColors.cardBorder),
      ),
      child: child,
    );
    if (onTap == null) return card;
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(LuminRadii.lg),
      child: InkWell(
        borderRadius: BorderRadius.circular(LuminRadii.lg),
        onTap: onTap,
        child: card,
      ),
    );
  }
}
EOF_CARD

# lib/shared/widgets/coming_soon.dart ------------------------------------
cat > lib/shared/widgets/coming_soon.dart <<'EOF_COMING'
import 'package:flutter/material.dart';
import '../tokens.dart';
import 'lumin_card.dart';

class ComingSoon extends StatelessWidget {
  const ComingSoon({super.key, required this.title, required this.icon, required this.description});

  final String title;
  final IconData icon;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(LuminSpacing.lg),
      child: LuminCard(
        padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.xl, vertical: LuminSpacing.xxl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: LuminColors.accent),
            const SizedBox(height: LuminSpacing.lg),
            Text(title, style: Theme.of(context).textTheme.titleLarge, textAlign: TextAlign.center),
            const SizedBox(height: LuminSpacing.sm),
            Text(description, style: Theme.of(context).textTheme.bodyMedium, textAlign: TextAlign.center),
            const SizedBox(height: LuminSpacing.lg),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.md, vertical: LuminSpacing.xs),
              decoration: BoxDecoration(
                color: LuminColors.bgElevated,
                borderRadius: BorderRadius.circular(LuminRadii.pill),
                border: Border.all(color: LuminColors.cardBorder),
              ),
              child: const Text(
                'Coming soon',
                style: TextStyle(color: LuminColors.textSecondary, fontSize: 11, letterSpacing: 1.2, fontWeight: FontWeight.w500),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
EOF_COMING

# lib/features/agents/agent_data.dart ------------------------------------
cat > lib/features/agents/agent_data.dart <<'EOF_AGENT_DATA'
import 'package:flutter/material.dart';

class Agent {
  const Agent({required this.id, required this.name, required this.tagline, required this.specialty, required this.icon});
  final String id;
  final String name;
  final String tagline;
  final String specialty;
  final IconData icon;
}

const List<Agent> kAgents = [
  Agent(id: 'SR_FLIP_RETEST', name: 'The Architect', tagline: 'Structural levels & flip retests',
    specialty: 'Watches support / resistance levels that flip and retest cleanly. Enters on the retest with structural confluence — the highest-quality setup family in the engine. Currently the top emitter.',
    icon: Icons.architecture_outlined),
  Agent(id: 'LIQUIDITY_SWEEP_REVERSAL', name: 'The Counter-Puncher', tagline: 'Reversal hunter after liquidity grabs',
    specialty: 'Fades the move when price sweeps liquidity (stop-runs above swing highs / below swing lows) and reverses. Counter-trend by design — thrives on traps set against the obvious move.',
    icon: Icons.swap_horiz_outlined),
  Agent(id: 'FAILED_AUCTION_RECLAIM', name: 'The Reclaimer', tagline: 'Trapped traders → reversal',
    specialty: 'Spots failed auction attempts (price breaks a level, fails to follow through, reclaims back). Trapped breakout traders fuel the reversal — clean R:R when the pattern triggers.',
    icon: Icons.replay_outlined),
  Agent(id: 'QUIET_COMPRESSION_BREAK', name: 'The Coil Hunter', tagline: 'Pre-volatility expansion',
    specialty: 'Identifies tight Bollinger-band compression in QUIET regime, then enters on the first directional break. The market\'s spring releasing — high R:R, low fire rate.',
    icon: Icons.compress_outlined),
  Agent(id: 'VOLUME_SURGE_BREAKOUT', name: 'The Tracker', tagline: 'Momentum-confirmed breakouts',
    specialty: 'Catches breakouts validated by a strong volume spike. Filters out fakeouts that lack participation. Built for trending markets where breakout follow-through matters.',
    icon: Icons.trending_up_outlined),
  Agent(id: 'BREAKDOWN_SHORT', name: 'The Crusher', tagline: 'Bearish twin of breakout',
    specialty: 'The short-side mirror of The Tracker. Hunts breakdowns through support with volume confirmation. Rare in current markets but high-conviction when it fires.',
    icon: Icons.trending_down_outlined),
  Agent(id: 'FUNDING_EXTREME_SIGNAL', name: 'The Contrarian', tagline: 'Funding-rate squeeze plays',
    specialty: 'Reads perpetual funding rates. When one side gets crowded (extreme funding), takes the other side — squeezing trapped longs / shorts. Pure order-flow contrarian.',
    icon: Icons.percent_outlined),
  Agent(id: 'WHALE_MOMENTUM', name: 'The Whale Hunter', tagline: 'Large-order chaser',
    specialty: 'Detects whale-sized order flow imbalances and rides the momentum until the impulse exhausts. Tape-driven — direction comes from real-time tick data, not technicals.',
    icon: Icons.waves_outlined),
  Agent(id: 'LIQUIDATION_REVERSAL', name: 'The Cascade Catcher', tagline: 'Post-liquidation reversal',
    specialty: 'Waits for liquidation cascades to finish, then enters the snapback. Forced selling exhaustion creates clean reversals — but cascades are rare, so this agent is patient.',
    icon: Icons.bolt_outlined),
  Agent(id: 'CONTINUATION_LIQUIDITY_SWEEP', name: 'The Continuation Specialist', tagline: 'Trend-resume after pullback sweep',
    specialty: 'Finds liquidity sweeps that occur DURING a trend (mid-trend stop runs that reset positioning). Enters on the trend resumption — cleaner than fresh-trend entries.',
    icon: Icons.timeline_outlined),
  Agent(id: 'DIVERGENCE_CONTINUATION', name: 'The Divergence Reader', tagline: 'CVD / price divergence plays',
    specialty: 'Reads cumulative volume delta against price action. When CVD diverges from price during a continuation, signals a high-prob move in the direction of the underlying flow.',
    icon: Icons.show_chart_outlined),
  Agent(id: 'TREND_PULLBACK_EMA', name: 'The Pullback Sniper', tagline: 'Pullback entries to EMAs in trend',
    specialty: 'Waits for clean pullbacks to the EMA stack during a confirmed trend, then enters on the reclaim. Classic trend-following with tight invalidation if the EMA fails.',
    icon: Icons.timeline),
  Agent(id: 'POST_DISPLACEMENT_CONTINUATION', name: 'The Aftermath Trader', tagline: 'Post-impulse continuation',
    specialty: 'After a strong directional displacement, waits for consolidation and enters on re-acceleration. Captures the back half of institutional moves.',
    icon: Icons.airline_seat_recline_normal_outlined),
  Agent(id: 'OPENING_RANGE_BREAKOUT', name: 'The Range Breaker', tagline: 'Session open-range breakouts',
    specialty: 'Tracks the opening range of major sessions and enters on the directional break with volume confirmation. Currently disabled pending session-anchored range logic rebuild.',
    icon: Icons.start_outlined),
];
EOF_AGENT_DATA

# lib/features/agents/agents_page.dart -----------------------------------
# (copied from the local generation tree)
EOF_AGENTS_HEADER_PLACEHOLDER=true

cat > lib/features/agents/agents_page.dart <<'EOF_AGENTS_PAGE'
import 'package:flutter/material.dart';
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
          IconButton(icon: const Icon(Icons.info_outline), tooltip: 'About the agents', onPressed: () => _showAboutDialog(context)),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
              child: Text('${kAgents.length} AI specialists', style: Theme.of(context).textTheme.titleMedium),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: LuminSpacing.md),
              child: Text('Each agent watches markets for a specific setup family.  Live stats land when the backend wires up.', style: Theme.of(context).textTheme.bodyMedium),
            ),
            Expanded(
              child: ListView.separated(
                physics: const BouncingScrollPhysics(),
                itemCount: kAgents.length,
                separatorBuilder: (_, __) => const SizedBox(height: LuminSpacing.md),
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
        title: const Text('Lumin\'s 14 AI agents'),
        content: const Text(
          'Each agent corresponds to one of the engine\'s evaluator paths.  They scan 75 USDT-M futures pairs continuously, looking for their specific setup type.  When an agent\'s confidence clears the paid threshold (65+), the signal is dispatched.\n\nPer-agent toggles, custom thresholds, and live stats coming with the next backend ship.',
        ),
        actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
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
      onTap: () => _showAgentDetail(context, agent),
      child: Row(
        children: [
          Container(
            width: 56, height: 56,
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
                Text(agent.name, style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: LuminSpacing.xs),
                Text(agent.tagline, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          const Icon(Icons.chevron_right, color: LuminColors.textMuted),
        ],
      ),
    );
  }

  void _showAgentDetail(BuildContext context, Agent agent) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: LuminColors.bgCard,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(LuminRadii.lg))),
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(LuminSpacing.xl, LuminSpacing.lg, LuminSpacing.xl, LuminSpacing.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(child: Container(width: 36, height: 4, decoration: BoxDecoration(color: LuminColors.textMuted, borderRadius: BorderRadius.circular(LuminRadii.pill)))),
            const SizedBox(height: LuminSpacing.lg),
            Row(children: [
              Icon(agent.icon, size: 32, color: LuminColors.accent),
              const SizedBox(width: LuminSpacing.md),
              Expanded(child: Text(agent.name, style: Theme.of(context).textTheme.headlineMedium)),
            ]),
            const SizedBox(height: LuminSpacing.xs),
            Text(agent.tagline, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: LuminColors.accent)),
            const SizedBox(height: LuminSpacing.lg),
            Text(agent.specialty, style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: LuminSpacing.lg),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.md, vertical: LuminSpacing.sm),
              decoration: BoxDecoration(color: LuminColors.bgElevated, borderRadius: BorderRadius.circular(LuminRadii.sm)),
              child: Row(children: [
                const Icon(Icons.tag, size: 14, color: LuminColors.textMuted),
                const SizedBox(width: LuminSpacing.xs),
                Text(agent.id, style: const TextStyle(color: LuminColors.textMuted, fontFamily: 'monospace', fontSize: 11, letterSpacing: 1.0)),
              ]),
            ),
          ],
        ),
      ),
    );
  }
}
EOF_AGENTS_PAGE

# lib/features/pulse/pulse_page.dart -------------------------------------
cat > lib/features/pulse/pulse_page.dart <<'EOF_PULSE'
import 'package:flutter/material.dart';
import '../../shared/widgets/coming_soon.dart';

class PulsePage extends StatelessWidget {
  const PulsePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Pulse')),
      body: const ComingSoon(
        title: 'Engine Pulse',
        icon: Icons.monitor_heart_outlined,
        description: 'Engine status, regime snapshot, today\'s P&L, daily-loss budget, and the last 5 closes — all live, in one place.',
      ),
    );
  }
}
EOF_PULSE

# lib/features/signals/signals_page.dart ---------------------------------
cat > lib/features/signals/signals_page.dart <<'EOF_SIGNALS'
import 'package:flutter/material.dart';
import '../../shared/widgets/coming_soon.dart';

class SignalsPage extends StatelessWidget {
  const SignalsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Signals')),
      body: const ComingSoon(
        title: 'Signal Feed',
        icon: Icons.bolt_outlined,
        description: 'Live and closed signals with chart preview, agent attribution, and net-of-fees PnL at your leverage.  Tap to drill in.',
      ),
    );
  }
}
EOF_SIGNALS

# lib/features/trade/trade_page.dart -------------------------------------
cat > lib/features/trade/trade_page.dart <<'EOF_TRADE'
import 'package:flutter/material.dart';
import '../../shared/widgets/coming_soon.dart';

class TradePage extends StatelessWidget {
  const TradePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Trade')),
      body: const ComingSoon(
        title: 'Auto-Trade Control',
        icon: Icons.swap_vert,
        description: 'Live / Demo toggle, open positions, daily-loss budget, and the order activity log.  All from your phone, no manual exchange browsing.',
      ),
    );
  }
}
EOF_TRADE

# lib/features/settings/settings_page.dart -------------------------------
cat > lib/features/settings/settings_page.dart <<'EOF_SETTINGS'
import 'package:flutter/material.dart';
import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: const EdgeInsets.all(LuminSpacing.lg),
        physics: const BouncingScrollPhysics(),
        children: [
          LuminCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: const [
                  Icon(Icons.account_circle_outlined, color: LuminColors.accent),
                  SizedBox(width: LuminSpacing.md),
                  Text('Mulakapati Kishore Kumar', style: TextStyle(color: LuminColors.textPrimary, fontSize: 16, fontWeight: FontWeight.w500)),
                ]),
                const SizedBox(height: LuminSpacing.sm),
                Padding(padding: const EdgeInsets.only(left: 32), child: Text('Telegram identity • Free tier', style: Theme.of(context).textTheme.bodyMedium)),
              ],
            ),
          ),
          const SizedBox(height: LuminSpacing.lg),
          _SectionHeader('Trading'),
          _SettingsRow(icon: Icons.swap_horiz_outlined, title: 'Auto-trade', subtitle: 'Off / Paper / Live mode'),
          _SettingsRow(icon: Icons.bolt_outlined, title: 'Pre-TP grab', subtitle: 'Threshold, ATR multiplier, fee floor'),
          _SettingsRow(icon: Icons.shield_outlined, title: 'Risk gates', subtitle: 'Daily-loss kill, leverage cap, exposure'),
          _SettingsRow(icon: Icons.code_outlined, title: 'Agents', subtitle: 'Per-path enable / custom thresholds'),
          const SizedBox(height: LuminSpacing.lg),
          _SectionHeader('Account'),
          _SettingsRow(icon: Icons.key_outlined, title: 'API keys', subtitle: 'Binance Futures (encrypted)'),
          _SettingsRow(icon: Icons.subscriptions_outlined, title: 'Subscription', subtitle: 'Free → Pro via Telegram bot'),
          const SizedBox(height: LuminSpacing.lg),
          _SectionHeader('App'),
          _SettingsRow(icon: Icons.dark_mode_outlined, title: 'Appearance', subtitle: 'Dark (default)'),
          _SettingsRow(icon: Icons.translate_outlined, title: 'Language', subtitle: 'English'),
          _SettingsRow(icon: Icons.info_outline, title: 'About', subtitle: 'Lumin v0.0.2 — Powered by 360 Crypto Eye'),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader(this.text);
  final String text;
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: LuminSpacing.sm, bottom: LuminSpacing.sm),
      child: Text(text.toUpperCase(), style: const TextStyle(color: LuminColors.textMuted, fontSize: 11, fontWeight: FontWeight.w600, letterSpacing: 1.5)),
    );
  }
}

class _SettingsRow extends StatelessWidget {
  const _SettingsRow({required this.icon, required this.title, required this.subtitle});
  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: LuminSpacing.sm),
      child: LuminCard(
        padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg, vertical: LuminSpacing.md),
        onTap: () => _showComingSoon(context),
        child: Row(
          children: [
            Icon(icon, color: LuminColors.accent, size: 22),
            const SizedBox(width: LuminSpacing.lg),
            Expanded(child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: LuminColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w500)),
                const SizedBox(height: 2),
                Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
              ],
            )),
            const Icon(Icons.chevron_right, color: LuminColors.textMuted, size: 20),
          ],
        ),
      ),
    );
  }

  void _showComingSoon(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: LuminColors.bgElevated,
        content: Text('$title — coming with the next backend ship.', style: const TextStyle(color: LuminColors.textPrimary)),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
EOF_SETTINGS

# lib/app/nav_shell.dart -------------------------------------------------
cat > lib/app/nav_shell.dart <<'EOF_NAV'
import 'package:flutter/material.dart';
import '../features/agents/agents_page.dart';
import '../features/pulse/pulse_page.dart';
import '../features/settings/settings_page.dart';
import '../features/signals/signals_page.dart';
import '../features/trade/trade_page.dart';

class NavShell extends StatefulWidget {
  const NavShell({super.key});

  @override
  State<NavShell> createState() => _NavShellState();
}

class _NavShellState extends State<NavShell> {
  int _index = 0;

  static const _pages = <Widget>[
    PulsePage(),
    SignalsPage(),
    AgentsPage(),
    TradePage(),
    SettingsPage(),
  ];

  static const _destinations = <NavigationDestination>[
    NavigationDestination(icon: Icon(Icons.monitor_heart_outlined), selectedIcon: Icon(Icons.monitor_heart), label: 'Pulse'),
    NavigationDestination(icon: Icon(Icons.bolt_outlined), selectedIcon: Icon(Icons.bolt), label: 'Signals'),
    NavigationDestination(icon: Icon(Icons.psychology_outlined), selectedIcon: Icon(Icons.psychology), label: 'Agents'),
    NavigationDestination(icon: Icon(Icons.swap_vert_outlined), selectedIcon: Icon(Icons.swap_vert), label: 'Trade'),
    NavigationDestination(icon: Icon(Icons.menu), selectedIcon: Icon(Icons.menu_open), label: 'Menu'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: _destinations,
      ),
    );
  }
}
EOF_NAV

# lib/main.dart ----------------------------------------------------------
cat > lib/main.dart <<'EOF_MAIN'
import 'package:flutter/material.dart';
import 'app/nav_shell.dart';
import 'theme.dart';

void main() {
  runApp(const LuminApp());
}

class LuminApp extends StatelessWidget {
  const LuminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Lumin',
      debugShowCheckedModeBanner: false,
      theme: buildLuminTheme(),
      home: const NavShell(),
    );
  }
}
EOF_MAIN

echo "→ Files written:"
find lib -type f | sort
echo
echo "→ Staging + committing…"
git add pubspec.yaml lib/

# Commit with a clear message; preserve user identity if set, else use a placeholder.
git -c user.email="$(git config user.email || echo bot@lumin.local)" \
    -c user.name="$(git config user.name || echo Lumin Bootstrap)" \
    commit -m "feat: 5-tab navigation + 14 AI agent personas (v0.0.2)

- Bottom nav: Pulse / Signals / Agents / Trade / Menu
- Brand theme tokens centralised in lib/shared/tokens.dart
- 14 agent personas with names, taglines, specialties, icons:
  The Architect, Counter-Puncher, Reclaimer, Coil Hunter, Tracker,
  Crusher, Contrarian, Whale Hunter, Cascade Catcher, Continuation
  Specialist, Divergence Reader, Pullback Sniper, Aftermath Trader,
  Range Breaker
- Settings tab shows Profile + Trading / Account / App rows (placeholder
  taps surface a 'coming with backend ship' SnackBar)
- Pulse / Signals / Trade tabs show ComingSoon placeholders
- Agents tab is fully populated — tap a card → modal sheet with full
  specialty description + engine-side agent ID

Pushes from existing GitHub Actions APK pipeline; no workflow changes."

echo
echo "→ Done.  Push to trigger the APK build:"
echo
echo "  git push"
echo
echo "Watch:  https://github.com/mkmk749278/lumin-app/actions"
echo "APK in artifacts as lumin-apk-<run_number>"
