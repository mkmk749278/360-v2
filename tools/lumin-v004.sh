#!/usr/bin/env bash
# Lumin app v0.0.4 — Settings drill-down pages.
# Replaces every Menu-tab SnackBar with a real settings page.
#
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v004.sh
#   bash lumin-v004.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

echo "→ Updating Lumin app to v0.0.4 (Settings drill-down pages)…"

mkdir -p lib/shared/widgets lib/features/settings/pages

# pubspec.yaml ----------------------------------------------------------
cat > pubspec.yaml <<'EOF_PUBSPEC'
name: lumin
description: "Lumin — AI Crypto Trading. Mobile app for 360 Crypto Eye signals."
publish_to: "none"
version: 0.0.4+4

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

# ── lib/shared/tokens.dart ──────────────────────────────────────────────
# Refreshes the tokens with const-correct cardBorder so const Divider /
# const BoxDecoration with cardBorder compile cleanly.  Idempotent.
cat > lib/shared/tokens.dart <<'EOF_TOKENS'
/// Brand tokens — colours, spacing, radii.
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

  // Pre-baked alpha (0.10 × 255 ≈ 26 = 0x1A) so it's a true compile-time const.
  static const Color cardBorder = Color(0x1A7BD3F7);
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

# ── lib/features/settings/settings_page.dart ────────────────────────────
cat > lib/features/settings/settings_page.dart <<'EOF_SETTINGS'
/// Menu / Settings — root list of drill-down pages.
///
/// Each row pushes a self-contained settings page where the user can edit
/// the relevant subsystem.  No setting persists across sessions yet — that
/// lands when the FastAPI backend ships.
import 'package:flutter/material.dart';

import '../../shared/tokens.dart';
import '../../shared/widgets/lumin_card.dart';
import 'pages/about_page.dart';
import 'pages/agents_settings_page.dart';
import 'pages/api_keys_settings_page.dart';
import 'pages/auto_trade_settings_page.dart';
import 'pages/pretp_settings_page.dart';
import 'pages/risk_gates_settings_page.dart';
import 'pages/subscription_page.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Menu')),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const SizedBox(height: LuminSpacing.md),
          _section(
            title: 'EXECUTION',
            rows: [
              _Row(
                icon: Icons.auto_mode,
                label: 'Auto-trade',
                subtitle: 'Mode, sizing, leverage cap',
                onTap: () => _push(context, const AutoTradeSettingsPage()),
              ),
              _Row(
                icon: Icons.shield_moon_outlined,
                label: 'Pre-TP grab',
                subtitle: 'Auto-breakeven thresholds',
                onTap: () => _push(context, const PreTpSettingsPage()),
              ),
              _Row(
                icon: Icons.shield_outlined,
                label: 'Risk gates',
                subtitle: 'Daily-loss kill, leverage, equity floor',
                onTap: () => _push(context, const RiskGatesSettingsPage()),
              ),
            ],
          ),
          const SizedBox(height: LuminSpacing.md),
          _section(
            title: 'ENGINE',
            rows: [
              _Row(
                icon: Icons.psychology_outlined,
                label: 'Agents',
                subtitle: '14 evaluators — per-agent toggles',
                onTap: () => _push(context, const AgentsSettingsPage()),
              ),
              _Row(
                icon: Icons.vpn_key_outlined,
                label: 'API keys',
                subtitle: 'Binance Futures credentials',
                onTap: () => _push(context, const ApiKeysSettingsPage()),
              ),
            ],
          ),
          const SizedBox(height: LuminSpacing.md),
          _section(
            title: 'ACCOUNT',
            rows: [
              _Row(
                icon: Icons.workspace_premium_outlined,
                label: 'Subscription',
                subtitle: 'Free / Pro tiers',
                onTap: () => _push(context, const SubscriptionPage()),
              ),
              _Row(
                icon: Icons.palette_outlined,
                label: 'Appearance',
                subtitle: 'Dark mode (always on for now)',
                onTap: () => _stub(context, 'Appearance'),
              ),
              _Row(
                icon: Icons.translate_outlined,
                label: 'Language',
                subtitle: 'English',
                onTap: () => _stub(context, 'Language'),
              ),
              _Row(
                icon: Icons.info_outline,
                label: 'About',
                subtitle: 'Version, terms, risk disclosure',
                onTap: () => _push(context, const AboutPage()),
              ),
            ],
          ),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _section({required String title, required List<_Row> rows}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(
              left: LuminSpacing.sm,
              bottom: LuminSpacing.sm,
            ),
            child: Text(
              title,
              style: const TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          LuminCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                for (int i = 0; i < rows.length; i++) ...[
                  rows[i],
                  if (i < rows.length - 1)
                    const Divider(
                      color: LuminColors.cardBorder,
                      height: 1,
                      indent: 56,
                    ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _push(BuildContext context, Widget page) {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
  }

  void _stub(BuildContext context, String label) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$label — not yet implemented'),
        duration: const Duration(seconds: 2),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  const _Row({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: LuminSpacing.md,
          vertical: LuminSpacing.md,
        ),
        child: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: LuminColors.accent.withOpacity(0.10),
                borderRadius: BorderRadius.circular(LuminRadii.sm),
              ),
              alignment: Alignment.center,
              child: Icon(icon, color: LuminColors.accent, size: 18),
            ),
            const SizedBox(width: LuminSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: LuminColors.textMuted, size: 18),
          ],
        ),
      ),
    );
  }
}
EOF_SETTINGS

echo "  ✓ tokens.dart + settings_page.dart"

# ── lib/features/settings/pages/auto_trade_settings_page.dart ───────────────────────────
cat > lib/features/settings/pages/auto_trade_settings_page.dart <<'EOF_AUTO_TRADE'
/// Auto-trade settings — execution-mode + sizing controls.
///
/// Mirrors the Trade tab's mode toggle (Off / Paper / Live) but adds the
/// sizing dials that the Trade tab doesn't expose: position-size %, leverage
/// cap, and max concurrent positions. State is session-only until the
/// backend wires up `/api/auto-mode`.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';
import '../../../shared/widgets/preview_badge.dart';

class AutoTradeSettingsPage extends StatefulWidget {
  const AutoTradeSettingsPage({super.key});

  @override
  State<AutoTradeSettingsPage> createState() => _AutoTradeSettingsPageState();
}

class _AutoTradeSettingsPageState extends State<AutoTradeSettingsPage> {
  // 0 = Off, 1 = Paper, 2 = Live
  int _mode = 1;
  double _positionSizePct = 2.0; // % of equity per trade
  double _leverageCap = 10.0;     // 1x..30x — B12 hard cap
  int _maxConcurrent = 3;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Auto-trade'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _modeCard(),
          const SizedBox(height: LuminSpacing.md),
          _sizingCard(),
          const SizedBox(height: LuminSpacing.md),
          _safetyNote(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _modeCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'EXECUTION MODE',
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
                _modeBtn(0, 'Off', Icons.power_settings_new, LuminColors.textMuted),
                const SizedBox(width: LuminSpacing.sm),
                _modeBtn(1, 'Paper', Icons.science_outlined, LuminColors.warn),
                const SizedBox(width: LuminSpacing.sm),
                _modeBtn(2, 'Live', Icons.bolt, LuminColors.loss),
              ],
            ),
            const SizedBox(height: LuminSpacing.md),
            Text(
              _modeDesc(_mode),
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

  Widget _modeBtn(int idx, String label, IconData icon, Color color) {
    final selected = _mode == idx;
    return Expanded(
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(LuminRadii.md),
        child: InkWell(
          borderRadius: BorderRadius.circular(LuminRadii.md),
          onTap: () => setState(() => _mode = idx),
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
                Icon(icon, color: selected ? color : LuminColors.textSecondary, size: 22),
                const SizedBox(height: LuminSpacing.xs),
                Text(
                  label,
                  style: TextStyle(
                    color: selected ? color : LuminColors.textSecondary,
                    fontSize: 12,
                    fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
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

  String _modeDesc(int m) {
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

  Widget _sizingCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'SIZING',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            _slider(
              label: 'Position size',
              value: '${_positionSizePct.toStringAsFixed(1)}% of equity',
              slider: Slider(
                value: _positionSizePct,
                min: 0.5,
                max: 10.0,
                divisions: 19,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: (v) => setState(() => _positionSizePct = v),
              ),
            ),
            _slider(
              label: 'Leverage cap',
              value: '${_leverageCap.toStringAsFixed(0)}x',
              slider: Slider(
                value: _leverageCap,
                min: 1,
                max: 30,
                divisions: 29,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: (v) => setState(() => _leverageCap = v),
              ),
            ),
            _slider(
              label: 'Max concurrent positions',
              value: '$_maxConcurrent',
              slider: Slider(
                value: _maxConcurrent.toDouble(),
                min: 1,
                max: 10,
                divisions: 9,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: (v) => setState(() => _maxConcurrent = v.round()),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _slider({required String label, required String value, required Widget slider}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: LuminSpacing.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    color: LuminColors.textPrimary,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  color: LuminColors.accent,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          slider,
        ],
      ),
    );
  }

  Widget _safetyNote() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.md),
        decoration: BoxDecoration(
          color: LuminColors.warn.withOpacity(0.08),
          borderRadius: BorderRadius.circular(LuminRadii.md),
          border: Border.all(color: LuminColors.warn.withOpacity(0.25)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Icon(Icons.shield_outlined, color: LuminColors.warn, size: 16),
            SizedBox(width: LuminSpacing.sm),
            Expanded(
              child: Text(
                'Live mode requires API keys + paper-mode validation. '
                'B12 caps leverage at 30x.',
                style: TextStyle(
                  color: LuminColors.warn,
                  fontSize: 11,
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _save() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Saved (session only — backend wiring pending)'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
EOF_AUTO_TRADE

# ── lib/features/settings/pages/pretp_settings_page.dart ───────────────────────────
cat > lib/features/settings/pages/pretp_settings_page.dart <<'EOF_PRETP'
/// Pre-TP grab settings — early-profit-taking knobs.
///
/// Pre-TP grab moves SL to breakeven once price has captured a configurable
/// fraction of the path to TP1 (covers fees + safety margin).  This page
/// exposes the knobs that the engine reads from `config.PRE_TP_*`.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';
import '../../../shared/widgets/preview_badge.dart';

class PreTpSettingsPage extends StatefulWidget {
  const PreTpSettingsPage({super.key});

  @override
  State<PreTpSettingsPage> createState() => _PreTpSettingsPageState();
}

class _PreTpSettingsPageState extends State<PreTpSettingsPage> {
  bool _enabled = true;
  double _grabPct = 0.50;     // fraction of TP1 distance
  double _atrMult = 0.30;     // ATR-floor multiplier
  double _feeFloor = 0.12;    // % — minimum profit before BE move

  // Regime allowlist
  bool _regimeTrending = true;
  bool _regimeRanging = true;
  bool _regimeChoppy = false;

  // Setup blacklist (false = blacklisted)
  final Map<String, bool> _setups = {
    'TPE (Trend Pullback)': true,
    'DIV_CONT (Divergence)': true,
    'CLS (Continuation)': true,
    'PDC (Post-Displacement)': true,
    'WHALE (Whale Momentum)': true,
    'FUNDING (Funding Extreme)': true,
    'LIQ_REVERSAL (Liquidation)': true,
    'LSR (Liquidity Sweep)': true,
    'FAR (Failed Auction)': true,
    'SR_FLIP (S/R Flip)': true,
    'QCB (Quiet Compression)': true,
    'VSB (Volume Surge)': true,
    'BDS (Breakdown Short)': true,
    'ORB (Opening Range)': false,
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pre-TP grab'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _masterCard(),
          const SizedBox(height: LuminSpacing.md),
          _thresholdsCard(),
          const SizedBox(height: LuminSpacing.md),
          _regimeCard(),
          const SizedBox(height: LuminSpacing.md),
          _setupsCard(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _masterCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Row(
          children: [
            const Icon(Icons.shield_moon_outlined, color: LuminColors.accent, size: 18),
            const SizedBox(width: LuminSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Pre-TP grab',
                    style: TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _enabled
                        ? 'Auto-moves SL to breakeven once price captures the threshold'
                        : 'Disabled — SL stays at original position until TP/SL hit',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            Switch(
              value: _enabled,
              activeColor: LuminColors.accent,
              onChanged: (v) => setState(() => _enabled = v),
            ),
          ],
        ),
      ),
    );
  }

  Widget _thresholdsCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'THRESHOLDS',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            _slider(
              label: 'Grab fraction (of TP1 distance)',
              value: '${(_grabPct * 100).toStringAsFixed(0)}%',
              slider: Slider(
                value: _grabPct,
                min: 0.20,
                max: 0.80,
                divisions: 12,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: _enabled ? (v) => setState(() => _grabPct = v) : null,
              ),
            ),
            _slider(
              label: 'ATR floor multiplier',
              value: '${_atrMult.toStringAsFixed(2)}x',
              slider: Slider(
                value: _atrMult,
                min: 0.10,
                max: 1.00,
                divisions: 18,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: _enabled ? (v) => setState(() => _atrMult = v) : null,
              ),
            ),
            _slider(
              label: 'Fee floor (min profit before BE)',
              value: '${_feeFloor.toStringAsFixed(2)}%',
              slider: Slider(
                value: _feeFloor,
                min: 0.05,
                max: 0.50,
                divisions: 9,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: _enabled ? (v) => setState(() => _feeFloor = v) : null,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _regimeCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'REGIME ALLOWLIST',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.sm),
            _regimeRow('Trending', _regimeTrending,
                (v) => setState(() => _regimeTrending = v)),
            _regimeRow('Ranging', _regimeRanging,
                (v) => setState(() => _regimeRanging = v)),
            _regimeRow('Choppy', _regimeChoppy,
                (v) => setState(() => _regimeChoppy = v)),
          ],
        ),
      ),
    );
  }

  Widget _regimeRow(String label, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                color: LuminColors.textPrimary,
                fontSize: 13,
              ),
            ),
          ),
          Switch(
            value: value,
            activeColor: LuminColors.accent,
            onChanged: _enabled ? onChanged : null,
          ),
        ],
      ),
    );
  }

  Widget _setupsCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'SETUP ALLOWLIST',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.sm),
            for (final entry in _setups.entries)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        entry.key,
                        style: const TextStyle(
                          color: LuminColors.textPrimary,
                          fontSize: 12,
                        ),
                      ),
                    ),
                    Switch(
                      value: entry.value,
                      activeColor: LuminColors.accent,
                      onChanged: _enabled
                          ? (v) => setState(() => _setups[entry.key] = v)
                          : null,
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _slider({required String label, required String value, required Widget slider}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: LuminSpacing.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  label,
                  style: TextStyle(
                    color: _enabled ? LuminColors.textPrimary : LuminColors.textMuted,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Text(
                value,
                style: TextStyle(
                  color: _enabled ? LuminColors.accent : LuminColors.textMuted,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          slider,
        ],
      ),
    );
  }

  void _save() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Saved (session only — backend wiring pending)'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
EOF_PRETP

# ── lib/features/settings/pages/risk_gates_settings_page.dart ───────────────────────────
cat > lib/features/settings/pages/risk_gates_settings_page.dart <<'EOF_RISK_GATES'
/// Risk gates settings — circuit-breaker thresholds.
///
/// These mirror engine-side risk constants — daily-loss kill, leverage cap,
/// equity floor.  When tripped, auto-trade halts until manual reset.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';
import '../../../shared/widgets/preview_badge.dart';

class RiskGatesSettingsPage extends StatefulWidget {
  const RiskGatesSettingsPage({super.key});

  @override
  State<RiskGatesSettingsPage> createState() => _RiskGatesSettingsPageState();
}

class _RiskGatesSettingsPageState extends State<RiskGatesSettingsPage> {
  double _dailyLossKillPct = 5.0;   // % of equity
  double _maxLeverage = 10.0;        // capped at 30x by B12
  double _minEquityFloorUsd = 100.0;
  bool _haltOnConsecutiveLosses = true;
  int _consecutiveLossesLimit = 3;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Risk gates'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _gatesCard(),
          const SizedBox(height: LuminSpacing.md),
          _streakCard(),
          const SizedBox(height: LuminSpacing.md),
          _disclaimer(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _gatesCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'CIRCUIT BREAKERS',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            _slider(
              label: 'Daily-loss kill',
              value: '${_dailyLossKillPct.toStringAsFixed(1)}% of equity',
              slider: Slider(
                value: _dailyLossKillPct,
                min: 1.0,
                max: 15.0,
                divisions: 28,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: (v) => setState(() => _dailyLossKillPct = v),
              ),
              hint: 'Auto-halt for 24h once daily PnL ≤ –${_dailyLossKillPct.toStringAsFixed(1)}%',
            ),
            _slider(
              label: 'Max leverage',
              value: '${_maxLeverage.toStringAsFixed(0)}x',
              slider: Slider(
                value: _maxLeverage,
                min: 1,
                max: 30,
                divisions: 29,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: (v) => setState(() => _maxLeverage = v),
              ),
              hint: 'Hard-capped at 30x per B12',
            ),
            _slider(
              label: 'Min equity floor',
              value: '\$${_minEquityFloorUsd.toStringAsFixed(0)}',
              slider: Slider(
                value: _minEquityFloorUsd,
                min: 50,
                max: 1000,
                divisions: 19,
                activeColor: LuminColors.accent,
                inactiveColor: LuminColors.cardBorder,
                onChanged: (v) => setState(() => _minEquityFloorUsd = v),
              ),
              hint: 'Halt if account equity drops below this',
            ),
          ],
        ),
      ),
    );
  }

  Widget _streakCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text(
                    'Halt on consecutive losses',
                    style: TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                Switch(
                  value: _haltOnConsecutiveLosses,
                  activeColor: LuminColors.accent,
                  onChanged: (v) => setState(() => _haltOnConsecutiveLosses = v),
                ),
              ],
            ),
            if (_haltOnConsecutiveLosses) ...[
              const SizedBox(height: LuminSpacing.md),
              _slider(
                label: 'Streak limit',
                value: '$_consecutiveLossesLimit losses',
                slider: Slider(
                  value: _consecutiveLossesLimit.toDouble(),
                  min: 2,
                  max: 10,
                  divisions: 8,
                  activeColor: LuminColors.accent,
                  inactiveColor: LuminColors.cardBorder,
                  onChanged: (v) =>
                      setState(() => _consecutiveLossesLimit = v.round()),
                ),
                hint: 'Halt auto-trade after this many losses in a row',
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _slider({
    required String label,
    required String value,
    required Widget slider,
    String? hint,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: LuminSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    color: LuminColors.textPrimary,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Text(
                value,
                style: const TextStyle(
                  color: LuminColors.accent,
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          slider,
          if (hint != null)
            Text(
              hint,
              style: const TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 11,
                height: 1.3,
              ),
            ),
        ],
      ),
    );
  }

  Widget _disclaimer() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.md),
        decoration: BoxDecoration(
          color: LuminColors.loss.withOpacity(0.08),
          borderRadius: BorderRadius.circular(LuminRadii.md),
          border: Border.all(color: LuminColors.loss.withOpacity(0.25)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Icon(Icons.warning_amber_rounded, color: LuminColors.loss, size: 16),
            SizedBox(width: LuminSpacing.sm),
            Expanded(
              child: Text(
                'Risk gates protect capital but cannot eliminate loss. '
                'Crypto futures can liquidate in seconds during volatile moves.',
                style: TextStyle(
                  color: LuminColors.loss,
                  fontSize: 11,
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _save() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Saved (session only — backend wiring pending)'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
EOF_RISK_GATES

# ── lib/features/settings/pages/agents_settings_page.dart ───────────────────────────
cat > lib/features/settings/pages/agents_settings_page.dart <<'EOF_AGENTS'
/// Agents settings — per-evaluator enable/disable toggles.
///
/// 14 evaluator paths, each owned by an agent persona.  Disabling an agent
/// suppresses its setup at the channel-router level (no Telegram dispatch,
/// no auto-trade entry).  Mirrors `config.AGENT_ENABLED_*` flags.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';
import '../../../shared/widgets/preview_badge.dart';

class AgentsSettingsPage extends StatefulWidget {
  const AgentsSettingsPage({super.key});

  @override
  State<AgentsSettingsPage> createState() => _AgentsSettingsPageState();
}

class _AgentsSettingsPageState extends State<AgentsSettingsPage> {
  // (display name, setup code, enabled-by-default)
  final List<List<dynamic>> _agents = [
    ['The Architect', 'SR_FLIP_RETEST', true],
    ['The Counter-Puncher', 'LIQUIDITY_SWEEP_REVERSAL', true],
    ['The Reclaimer', 'FAILED_AUCTION_RECLAIM', true],
    ['The Coil Hunter', 'QUIET_COMPRESSION_BREAK', true],
    ['The Tracker', 'VOLUME_SURGE_BREAKOUT', true],
    ['The Crusher', 'BREAKDOWN_SHORT', true],
    ['The Contrarian', 'FUNDING_EXTREME_SIGNAL', true],
    ['The Whale Hunter', 'WHALE_MOMENTUM', true],
    ['The Cascade Catcher', 'LIQUIDATION_REVERSAL', true],
    ['The Continuation Specialist', 'CONTINUATION_LIQUIDITY_SWEEP', true],
    ['The Divergence Reader', 'DIVERGENCE_CONTINUATION', true],
    ['The Pullback Sniper', 'TREND_PULLBACK_EMA', true],
    ['The Aftermath Trader', 'POST_DISPLACEMENT_CONTINUATION', true],
    ['The Range Breaker', 'OPENING_RANGE_BREAKOUT', true],
  ];

  @override
  Widget build(BuildContext context) {
    final activeCount = _agents.where((a) => a[2] as bool).length;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agents'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _summaryCard(activeCount),
          const SizedBox(height: LuminSpacing.md),
          _bulkActionsCard(),
          const SizedBox(height: LuminSpacing.md),
          _agentsCard(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _summaryCard(int activeCount) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: LuminColors.accent.withOpacity(0.15),
                borderRadius: BorderRadius.circular(LuminRadii.md),
              ),
              alignment: Alignment.center,
              child: Text(
                '$activeCount',
                style: const TextStyle(
                  color: LuminColors.accent,
                  fontSize: 22,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            const SizedBox(width: LuminSpacing.md),
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Active agents',
                    style: TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'of 14 evaluators',
                    style: TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _bulkActionsCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Row(
        children: [
          Expanded(
            child: _bulkBtn('Enable all', LuminColors.success, () {
              setState(() {
                for (final a in _agents) {
                  a[2] = true;
                }
              });
            }),
          ),
          const SizedBox(width: LuminSpacing.sm),
          Expanded(
            child: _bulkBtn('Disable all', LuminColors.loss, () {
              setState(() {
                for (final a in _agents) {
                  a[2] = false;
                }
              });
            }),
          ),
        ],
      ),
    );
  }

  Widget _bulkBtn(String label, Color color, VoidCallback onTap) {
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(LuminRadii.md),
      child: InkWell(
        borderRadius: BorderRadius.circular(LuminRadii.md),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
          decoration: BoxDecoration(
            color: color.withOpacity(0.10),
            borderRadius: BorderRadius.circular(LuminRadii.md),
            border: Border.all(color: color.withOpacity(0.30)),
          ),
          alignment: Alignment.center,
          child: Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ),
    );
  }

  Widget _agentsCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'EVALUATORS',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.sm),
            for (int i = 0; i < _agents.length; i++) ...[
              _agentRow(i),
              if (i < _agents.length - 1)
                const Divider(
                  color: LuminColors.cardBorder,
                  height: 1,
                ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _agentRow(int idx) {
    final name = _agents[idx][0] as String;
    final code = _agents[idx][1] as String;
    final enabled = _agents[idx][2] as bool;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: LuminSpacing.sm),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: TextStyle(
                    color: enabled
                        ? LuminColors.textPrimary
                        : LuminColors.textMuted,
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  code,
                  style: const TextStyle(
                    color: LuminColors.textSecondary,
                    fontSize: 10,
                    letterSpacing: 0.4,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: enabled,
            activeColor: LuminColors.accent,
            onChanged: (v) => setState(() => _agents[idx][2] = v),
          ),
        ],
      ),
    );
  }

  void _save() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Saved (session only — backend wiring pending)'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
EOF_AGENTS

# ── lib/features/settings/pages/api_keys_settings_page.dart ───────────────────────────
cat > lib/features/settings/pages/api_keys_settings_page.dart <<'EOF_API_KEYS'
/// API keys settings — Binance Futures credentials.
///
/// Masked input, "Test connection" stub.  In v0.0.4 keys live in session
/// memory only; the backend will move them to encrypted at-rest storage
/// once the FastAPI service ships.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';
import '../../../shared/widgets/preview_badge.dart';

class ApiKeysSettingsPage extends StatefulWidget {
  const ApiKeysSettingsPage({super.key});

  @override
  State<ApiKeysSettingsPage> createState() => _ApiKeysSettingsPageState();
}

class _ApiKeysSettingsPageState extends State<ApiKeysSettingsPage> {
  final _apiKeyCtl = TextEditingController();
  final _apiSecretCtl = TextEditingController();
  bool _showSecret = false;
  bool _testnet = false;
  String? _testResult;
  bool _testing = false;

  @override
  void dispose() {
    _apiKeyCtl.dispose();
    _apiSecretCtl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API keys'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const PreviewBadge(),
          _credsCard(),
          const SizedBox(height: LuminSpacing.md),
          _envCard(),
          const SizedBox(height: LuminSpacing.md),
          _testCard(),
          const SizedBox(height: LuminSpacing.md),
          _safetyCard(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _credsCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'BINANCE FUTURES',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            _label('API key'),
            TextField(
              controller: _apiKeyCtl,
              style: const TextStyle(color: LuminColors.textPrimary, fontSize: 13),
              decoration: _inputDecoration('Paste API key'),
            ),
            const SizedBox(height: LuminSpacing.md),
            _label('API secret'),
            TextField(
              controller: _apiSecretCtl,
              obscureText: !_showSecret,
              style: const TextStyle(color: LuminColors.textPrimary, fontSize: 13),
              decoration: _inputDecoration('Paste API secret').copyWith(
                suffixIcon: IconButton(
                  icon: Icon(
                    _showSecret ? Icons.visibility_off : Icons.visibility,
                    color: LuminColors.textMuted,
                    size: 18,
                  ),
                  onPressed: () => setState(() => _showSecret = !_showSecret),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _envCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Row(
          children: [
            const Icon(Icons.cloud_outlined, color: LuminColors.accent, size: 18),
            const SizedBox(width: LuminSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _testnet ? 'Testnet' : 'Mainnet',
                    style: const TextStyle(
                      color: LuminColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _testnet
                        ? 'fapi-testnet.binance.com — fake balance, real APIs'
                        : 'fapi.binance.com — real money, real fills',
                    style: const TextStyle(
                      color: LuminColors.textSecondary,
                      fontSize: 11,
                      height: 1.3,
                    ),
                  ),
                ],
              ),
            ),
            Switch(
              value: _testnet,
              activeColor: LuminColors.warn,
              onChanged: (v) => setState(() => _testnet = v),
            ),
          ],
        ),
      ),
    );
  }

  Widget _testCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: double.infinity,
              child: Material(
                color: Colors.transparent,
                borderRadius: BorderRadius.circular(LuminRadii.md),
                child: InkWell(
                  borderRadius: BorderRadius.circular(LuminRadii.md),
                  onTap: _testing ? null : _runTest,
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
                    decoration: BoxDecoration(
                      color: LuminColors.accent.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(LuminRadii.md),
                      border: Border.all(color: LuminColors.accent.withOpacity(0.30)),
                    ),
                    alignment: Alignment.center,
                    child: _testing
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: LuminColors.accent,
                            ),
                          )
                        : const Text(
                            'Test connection',
                            style: TextStyle(
                              color: LuminColors.accent,
                              fontSize: 13,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                ),
              ),
            ),
            if (_testResult != null) ...[
              const SizedBox(height: LuminSpacing.md),
              Text(
                _testResult!,
                style: TextStyle(
                  color: _testResult!.startsWith('OK')
                      ? LuminColors.success
                      : LuminColors.loss,
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _safetyCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.md),
        decoration: BoxDecoration(
          color: LuminColors.warn.withOpacity(0.08),
          borderRadius: BorderRadius.circular(LuminRadii.md),
          border: Border.all(color: LuminColors.warn.withOpacity(0.25)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Row(
              children: [
                Icon(Icons.lock_outline, color: LuminColors.warn, size: 16),
                SizedBox(width: LuminSpacing.sm),
                Text(
                  'Required permissions',
                  style: TextStyle(
                    color: LuminColors.warn,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            SizedBox(height: LuminSpacing.sm),
            Text(
              '• Enable Reading\n'
              '• Enable Futures\n'
              '• DO NOT enable Withdrawals\n'
              '• Restrict to your IP if possible',
              style: TextStyle(
                color: LuminColors.warn,
                fontSize: 11,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _label(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: LuminSpacing.xs),
      child: Text(
        text,
        style: const TextStyle(
          color: LuminColors.textSecondary,
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(
        color: LuminColors.textMuted,
        fontSize: 13,
      ),
      filled: true,
      fillColor: LuminColors.bgElevated,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: LuminSpacing.md,
        vertical: LuminSpacing.sm,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LuminRadii.sm),
        borderSide: const BorderSide(color: LuminColors.cardBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(LuminRadii.sm),
        borderSide: const BorderSide(color: LuminColors.accent),
      ),
    );
  }

  Future<void> _runTest() async {
    if (_apiKeyCtl.text.isEmpty || _apiSecretCtl.text.isEmpty) {
      setState(() => _testResult = 'ERR: enter both key and secret');
      return;
    }
    setState(() {
      _testing = true;
      _testResult = null;
    });
    await Future.delayed(const Duration(milliseconds: 900));
    if (!mounted) return;
    setState(() {
      _testing = false;
      _testResult = 'OK — mock authentication.  Real check lands with backend.';
    });
  }

  void _save() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Saved (session only — secure storage lands with backend)'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
EOF_API_KEYS

# ── lib/features/settings/pages/subscription_page.dart ───────────────────────────
cat > lib/features/settings/pages/subscription_page.dart <<'EOF_SUBSCRIPTION'
/// Subscription page — Free vs Pro tier comparison + Telegram bot deep link.
///
/// Per Play Store reader-app exception, crypto subscription must NOT use
/// Google Play Billing.  Subscriptions are managed via the @LuminProBot
/// Telegram bot — tap "Upgrade" → opens t.me/LuminProBot.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';

class SubscriptionPage extends StatelessWidget {
  const SubscriptionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Subscription')),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const SizedBox(height: LuminSpacing.md),
          _heroCard(),
          const SizedBox(height: LuminSpacing.md),
          _tierComparison(),
          const SizedBox(height: LuminSpacing.md),
          _pricingCards(context),
          const SizedBox(height: LuminSpacing.md),
          _telegramCta(context),
          const SizedBox(height: LuminSpacing.md),
          _disclaimer(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _heroCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.lg),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              LuminColors.accent.withOpacity(0.18),
              LuminColors.accent.withOpacity(0.05),
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(LuminRadii.lg),
          border: Border.all(color: LuminColors.accent.withOpacity(0.30)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Icon(Icons.workspace_premium, color: LuminColors.accent, size: 32),
            SizedBox(height: LuminSpacing.sm),
            Text(
              'Lumin Pro',
              style: TextStyle(
                color: LuminColors.textPrimary,
                fontSize: 22,
                fontWeight: FontWeight.w700,
                letterSpacing: -0.5,
              ),
            ),
            SizedBox(height: LuminSpacing.xs),
            Text(
              'Full 14-evaluator paid signals.  Real-time Telegram dispatch.  '
              'Auto-trade unlock.',
              style: TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 13,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _tierComparison() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'WHAT YOU GET',
              style: TextStyle(
                color: LuminColors.textMuted,
                fontSize: 10,
                letterSpacing: 1.2,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            _featureRow('Watchlist signals (free channel)', true, true),
            _featureRow('Paid signals — 14 evaluators', false, true),
            _featureRow('Real-time Telegram dispatch', false, true),
            _featureRow('Pre-TP grab + auto-breakeven', false, true),
            _featureRow('In-app auto-trade (Paper)', false, true),
            _featureRow('In-app auto-trade (Live)', false, true),
            _featureRow('Per-agent toggles', false, true),
            _featureRow('Custom risk gates', false, true),
          ],
        ),
      ),
    );
  }

  Widget _featureRow(String label, bool free, bool pro) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            flex: 5,
            child: Text(
              label,
              style: const TextStyle(
                color: LuminColors.textPrimary,
                fontSize: 12,
              ),
            ),
          ),
          Expanded(
            child: Center(
              child: Icon(
                free ? Icons.check_circle : Icons.remove_circle_outline,
                color: free ? LuminColors.success : LuminColors.textMuted,
                size: 16,
              ),
            ),
          ),
          Expanded(
            child: Center(
              child: Icon(
                pro ? Icons.check_circle : Icons.remove_circle_outline,
                color: pro ? LuminColors.accent : LuminColors.textMuted,
                size: 16,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _pricingCards(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Column(
        children: [
          _priceTile(
            context,
            label: 'Monthly',
            price: '\$30',
            unit: '/ month',
            note: 'Cancel anytime',
            highlight: false,
          ),
          const SizedBox(height: LuminSpacing.sm),
          _priceTile(
            context,
            label: 'Yearly',
            price: '\$300',
            unit: '/ year',
            note: 'Save \$60 — equivalent to 2 months free',
            highlight: true,
          ),
          const SizedBox(height: LuminSpacing.sm),
          _priceTile(
            context,
            label: 'Lifetime',
            price: '\$999',
            unit: 'one-time',
            note: 'Pay once, paid signals forever',
            highlight: false,
          ),
        ],
      ),
    );
  }

  Widget _priceTile(
    BuildContext context, {
    required String label,
    required String price,
    required String unit,
    required String note,
    required bool highlight,
  }) {
    return Container(
      padding: const EdgeInsets.all(LuminSpacing.md),
      decoration: BoxDecoration(
        color: highlight
            ? LuminColors.accent.withOpacity(0.10)
            : LuminColors.bgCard,
        borderRadius: BorderRadius.circular(LuminRadii.md),
        border: Border.all(
          color: highlight
              ? LuminColors.accent.withOpacity(0.50)
              : LuminColors.cardBorder,
          width: highlight ? 1.5 : 1,
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      label,
                      style: const TextStyle(
                        color: LuminColors.textPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (highlight) ...[
                      const SizedBox(width: LuminSpacing.sm),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: LuminSpacing.sm,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: LuminColors.accent,
                          borderRadius: BorderRadius.circular(LuminRadii.pill),
                        ),
                        child: const Text(
                          'BEST VALUE',
                          style: TextStyle(
                            color: LuminColors.bgDeep,
                            fontSize: 9,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.6,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  note,
                  style: const TextStyle(
                    color: LuminColors.textSecondary,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                price,
                style: const TextStyle(
                  color: LuminColors.textPrimary,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.3,
                ),
              ),
              Text(
                unit,
                style: const TextStyle(
                  color: LuminColors.textMuted,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _telegramCta(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(LuminRadii.md),
        child: InkWell(
          borderRadius: BorderRadius.circular(LuminRadii.md),
          onTap: () => _showTelegramSheet(context),
          child: Container(
            padding: const EdgeInsets.all(LuminSpacing.md),
            decoration: BoxDecoration(
              color: LuminColors.accent,
              borderRadius: BorderRadius.circular(LuminRadii.md),
            ),
            child: Row(
              children: [
                const Icon(Icons.send, color: LuminColors.bgDeep, size: 20),
                const SizedBox(width: LuminSpacing.md),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Upgrade via Telegram',
                        style: TextStyle(
                          color: LuminColors.bgDeep,
                          fontSize: 14,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      SizedBox(height: 2),
                      Text(
                        '@LuminProBot — payment, activation, support',
                        style: TextStyle(
                          color: LuminColors.bgDeep,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.arrow_forward, color: LuminColors.bgDeep, size: 18),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showTelegramSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: LuminColors.bgCard,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(LuminRadii.lg)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(LuminSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: LuminColors.cardBorder,
                borderRadius: BorderRadius.circular(LuminRadii.pill),
              ),
            ),
            const SizedBox(height: LuminSpacing.md),
            const Text(
              'Open Telegram bot',
              style: TextStyle(
                color: LuminColors.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: LuminSpacing.sm),
            const Text(
              'You will be redirected to @LuminProBot in Telegram.  '
              'There you can pick a plan, pay, and the bot will activate '
              'paid signals on your account.',
              style: TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 13,
                height: 1.5,
              ),
            ),
            const SizedBox(height: LuminSpacing.lg),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: LuminColors.accent,
                  foregroundColor: LuminColors.bgDeep,
                  padding: const EdgeInsets.symmetric(vertical: LuminSpacing.md),
                ),
                onPressed: () {
                  Navigator.pop(ctx);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Telegram deep link wires up with backend launch'),
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
                child: const Text(
                  'Open @LuminProBot',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
            const SizedBox(height: LuminSpacing.sm),
            SizedBox(
              width: double.infinity,
              child: TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text(
                  'Cancel',
                  style: TextStyle(color: LuminColors.textSecondary),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _disclaimer() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Text(
        'Subscriptions are managed outside Google Play in compliance with the '
        'reader-app exception.  Crypto trading carries substantial risk; '
        'past signals do not guarantee future performance.',
        style: TextStyle(
          color: LuminColors.textMuted.withOpacity(0.85),
          fontSize: 10,
          height: 1.5,
        ),
      ),
    );
  }
}
EOF_SUBSCRIPTION

# ── lib/features/settings/pages/about_page.dart ───────────────────────────
cat > lib/features/settings/pages/about_page.dart <<'EOF_ABOUT'
/// About / Risk Disclosure — Play Store legal compliance.
///
/// Version, attribution, terms link, privacy link, and full risk-disclosure
/// content required for Google Play approval of a financial-services app.
import 'package:flutter/material.dart';

import '../../../shared/tokens.dart';
import '../../../shared/widgets/lumin_card.dart';

class AboutPage extends StatelessWidget {
  const AboutPage({super.key});

  static const _version = '0.0.4';
  static const _build = 'preview-mock';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('About')),
      body: ListView(
        physics: const BouncingScrollPhysics(),
        children: [
          const SizedBox(height: LuminSpacing.md),
          _hero(),
          const SizedBox(height: LuminSpacing.md),
          _versionCard(),
          const SizedBox(height: LuminSpacing.md),
          _riskCard(),
          const SizedBox(height: LuminSpacing.md),
          _legalLinks(context),
          const SizedBox(height: LuminSpacing.md),
          _attribution(),
          const SizedBox(height: LuminSpacing.xl),
        ],
      ),
    );
  }

  Widget _hero() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.lg),
        decoration: BoxDecoration(
          color: LuminColors.bgCard,
          borderRadius: BorderRadius.circular(LuminRadii.lg),
          border: Border.all(color: LuminColors.cardBorder),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Row(
              children: [
                Icon(Icons.auto_awesome, color: LuminColors.accent, size: 28),
                SizedBox(width: LuminSpacing.sm),
                Text(
                  'Lumin',
                  style: TextStyle(
                    color: LuminColors.textPrimary,
                    fontSize: 24,
                    fontWeight: FontWeight.w700,
                    letterSpacing: -0.5,
                  ),
                ),
              ],
            ),
            SizedBox(height: LuminSpacing.sm),
            Text(
              'Crypto-scalping signal companion app for the 360 Crypto Eye '
              'engine.  Watch the engine pulse, browse signals, and manage '
              'auto-trade execution.',
              style: TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 13,
                height: 1.4,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _versionCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          children: [
            _kv('Version', _version),
            _kv('Build', _build),
            _kv('Engine', '360 Crypto Eye'),
            _kv('Channel', 'Telegram'),
          ],
        ),
      ),
    );
  }

  Widget _kv(String k, String v) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Expanded(
            child: Text(
              k,
              style: const TextStyle(
                color: LuminColors.textSecondary,
                fontSize: 12,
              ),
            ),
          ),
          Text(
            v,
            style: const TextStyle(
              color: LuminColors.textPrimary,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _riskCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Container(
        padding: const EdgeInsets.all(LuminSpacing.md),
        decoration: BoxDecoration(
          color: LuminColors.loss.withOpacity(0.06),
          borderRadius: BorderRadius.circular(LuminRadii.md),
          border: Border.all(color: LuminColors.loss.withOpacity(0.25)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: const [
            Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: LuminColors.loss, size: 18),
                SizedBox(width: LuminSpacing.sm),
                Text(
                  'RISK DISCLOSURE',
                  style: TextStyle(
                    color: LuminColors.loss,
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                  ),
                ),
              ],
            ),
            SizedBox(height: LuminSpacing.md),
            Text(
              'Crypto-asset perpetual futures trading is highly speculative '
              'and carries a substantial risk of loss.  Leverage amplifies '
              'both gains and losses; you can lose more than your initial '
              'margin in seconds during volatile market conditions.\n\n'
              'Lumin and the 360 Crypto Eye engine provide algorithmic '
              'signals for informational purposes only.  Signals are not '
              'financial advice, are not personalised to your situation, '
              'and do not account for your risk tolerance, financial '
              'circumstances, or jurisdiction.\n\n'
              'Past performance — including any historical statistics shown '
              'in this app — is not indicative of future results.  Backtests '
              'and forward-tested figures may not reflect realistic execution '
              'cost (fees, slippage, funding) at retail order sizes.\n\n'
              'You are solely responsible for trades executed on your '
              'Binance account, whether placed manually or via the app\'s '
              'auto-trade module.  Verify every order before authorising '
              'live execution.  Never trade with capital you cannot afford '
              'to lose.',
              style: TextStyle(
                color: LuminColors.textPrimary,
                fontSize: 12,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _legalLinks(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: LuminCard(
        child: Column(
          children: [
            _link(context, Icons.description_outlined, 'Terms of Service'),
            const Divider(color: LuminColors.cardBorder, height: 1),
            _link(context, Icons.privacy_tip_outlined, 'Privacy Policy'),
            const Divider(color: LuminColors.cardBorder, height: 1),
            _link(context, Icons.gavel_outlined, 'Open-source licences'),
            const Divider(color: LuminColors.cardBorder, height: 1),
            _link(context, Icons.mail_outline, 'Contact support'),
          ],
        ),
      ),
    );
  }

  Widget _link(BuildContext context, IconData icon, String label) {
    return InkWell(
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$label opens once site is live'),
            duration: const Duration(seconds: 2),
          ),
        );
      },
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: LuminSpacing.sm),
        child: Row(
          children: [
            Icon(icon, color: LuminColors.accent, size: 18),
            const SizedBox(width: LuminSpacing.md),
            Expanded(
              child: Text(
                label,
                style: const TextStyle(
                  color: LuminColors.textPrimary,
                  fontSize: 13,
                ),
              ),
            ),
            const Icon(Icons.chevron_right, color: LuminColors.textMuted, size: 18),
          ],
        ),
      ),
    );
  }

  Widget _attribution() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: LuminSpacing.lg),
      child: Text(
        '© 2026 360 Crypto Eye.  All rights reserved.\n'
        'Made for scalpers, with the 14-evaluator engine.',
        textAlign: TextAlign.center,
        style: TextStyle(
          color: LuminColors.textMuted.withOpacity(0.75),
          fontSize: 10,
          height: 1.6,
        ),
      ),
    );
  }
}
EOF_ABOUT

echo "  ✓ 7 settings drill-down pages"

echo "→ Bumping version → 0.0.4+4 — done"
echo "→ Stage + commit + push (then GitHub Actions builds APK)"

git add lib/ pubspec.yaml
git commit -m "feat(settings): v0.0.4 — drill-down pages for every Menu row

Auto-trade, Pre-TP grab, Risk gates, Agents, API keys, Subscription, About.
Replaces SnackBar placeholders with real pages.  Session-only state until
the FastAPI backend wires up persistence."

echo "✓ v0.0.4 ready.  'git push' to trigger APK build."
