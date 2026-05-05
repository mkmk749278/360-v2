#!/usr/bin/env bash
# Lumin app v0.0.8 — Cosmetic + UX honesty fixes.
#
# Surgical patches (no full-file replacements) so the script can be re-run
# safely on a clean repo and does the same thing each time.  Termux-safe:
# bash + GNU sed/awk only, no jq/python.
#
# What changes vs v0.0.7:
#   1. API keys page no longer shows the orange "Preview — sample data"
#      banner when Live engine is enabled (was rendering unconditionally).
#   2. About page version constants bumped to 0.0.8 / 'live' (was stuck at
#      0.0.4 / 'preview-mock' from v0.0.4 — drifted across 3 releases).
#   3. Pulse regime card subtitle relabelled "X.X% trending" instead of
#      "X.X% of cycles" — the metric is the % of cycles in TRENDING regime,
#      so pairing it with the current-regime label produced confusing reads
#      like "RANGING / 0.0% of cycles".
#   4. Signals empty state shows honest copy in Live mode: "Engine is
#      scanning 75 pairs. New paid signals appear here when they fire." —
#      so paid subscribers don't see a blank "No signals yet" and assume
#      the app is broken when the engine simply hasn't fired anything yet.
#
# Run from inside the cloned lumin-app repo:
#   cd ~/lumin-app
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/lumin-v008.sh
#   bash lumin-v008.sh
#   git push
set -euo pipefail

if [ ! -d ".git" ] || [ ! -f "pubspec.yaml" ] || ! grep -q "name: lumin" pubspec.yaml; then
  echo "ERROR: run from inside ~/lumin-app"
  exit 1
fi

if grep -q "^version: 0.0.8" pubspec.yaml; then
  echo "→ Already on v0.0.8 — nothing to do."
  exit 0
fi

if ! grep -q "^version: 0.0.7" pubspec.yaml; then
  echo "ERROR: expected v0.0.7 baseline; found:"
  grep "^version:" pubspec.yaml
  echo "Aborting — re-run only on a v0.0.7 install."
  exit 1
fi

echo "→ Updating Lumin app to v0.0.8 (cosmetic + UX honesty fixes)…"

API_KEYS="lib/features/settings/pages/api_keys_settings_page.dart"
ABOUT="lib/features/settings/pages/about_page.dart"
PULSE="lib/features/pulse/pulse_page.dart"
SIGNALS="lib/features/signals/signals_page.dart"

for f in "$API_KEYS" "$ABOUT" "$PULSE" "$SIGNALS"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: missing $f — repo state inconsistent"
    exit 1
  fi
done

# ── Patch 1: API keys page — wrap PreviewBadge in conditional ──────────
# All other pages (pulse/signals/trade) gate the badge on isLive; this one
# was missed.  Use _liveMode (the page's local UI state) so the banner
# tracks the Switch instantly, not just after Save.
echo "  ✓ patch 1/4: api_keys banner conditional"
sed -i 's|^          const PreviewBadge(),$|          if (!_liveMode) const PreviewBadge(),|' "$API_KEYS"
grep -q "if (!_liveMode) const PreviewBadge()" "$API_KEYS" || {
  echo "ERROR: patch 1 failed — anchor not matched in $API_KEYS"
  exit 1
}

# ── Patch 2: About page — bump hardcoded version constants ─────────────
# These have drifted since v0.0.4.  Long-term fix is reading from
# pubspec.yaml at build time via package_info_plus, but that's a v0.1.0
# concern.  For now just keep them in sync at install time.
echo "  ✓ patch 2/4: about page version constants"
sed -i "s|static const _version = '0.0.4';|static const _version = '0.0.8';|" "$ABOUT"
sed -i "s|static const _build = 'preview-mock';|static const _build = 'live';|" "$ABOUT"
grep -q "_version = '0.0.8'" "$ABOUT" || {
  echo "ERROR: patch 2 failed — version constant not bumped"
  exit 1
}

# ── Patch 3: Pulse regime card label ───────────────────────────────────
# regimePctTrending is the % of cycles in TRENDING regime over the window,
# not the % of cycles in the *current* regime.  Pairing it with the live
# regime label produces nonsense like "RANGING / 0.0% of cycles".  Re-label
# so the meaning is unambiguous regardless of current regime.
echo "  ✓ patch 3/4: pulse regime label"
sed -i "s|.toStringAsFixed(1)}% of cycles|.toStringAsFixed(1)}% trending|" "$PULSE"
grep -q "% trending" "$PULSE" || {
  echo "ERROR: patch 3 failed — pulse label not updated"
  exit 1
}

# ── Patch 4: Signals empty state ───────────────────────────────────────
# In Live mode, "No signals yet / Pull down to refresh" reads as broken
# from the subscriber POV.  Add an isLive-conditional second line that
# tells them the engine is scanning and signals appear when they fire.
# Three coordinated edits: constructor signature, field declaration,
# call site; plus an awk pass for the multi-line empty-state body.
echo "  ✓ patch 4/4: signals empty state"

# 4a — constructor signature
sed -i 's|const _SignalsEmpty({required this.filter});|const _SignalsEmpty({required this.filter, required this.isLive});|' "$SIGNALS"

# 4b — field declaration (insert `final bool isLive;` after `final _SignalFilter filter;`)
sed -i 's|^  final _SignalFilter filter;$|  final _SignalFilter filter;\n  final bool isLive;|' "$SIGNALS"

# 4c — call site (pass isLive: scope.repo.isLive)
sed -i 's|return _SignalsEmpty(filter: _filter);|return _SignalsEmpty(filter: _filter, isLive: scope.repo.isLive);|' "$SIGNALS"

# 4d — empty-state body (multi-line via awk state machine)
awk '
  BEGIN { state = 0; buffered = "" }

  # State 1: just saw `        const Text(`; lookahead to confirm it is
  # the empty-state body and not some other Text widget.
  state == 1 {
    if (/Pull down to refresh/) {
      # Confirmed.  Emit patched header + conditional message; transition
      # to state 2 so the subsequent style line gets `const` re-added.
      print "        Text("
      print "          isLive"
      print "              ? '"'"'Engine is scanning 75 pairs.\\nNew paid signals appear here when they fire.'"'"'"
      print "              : '"'"'Pull down to refresh.'"'"',"
      state = 2
      buffered = ""
      next
    } else {
      # Not our target.  Flush original line and continue normally.
      print buffered
      buffered = ""
      state = 0
      print
      next
    }
  }

  # State 2: after replacement; the style: TextStyle(...) is no longer
  # inside a `const Text(...)` so the const moves down to the TextStyle.
  state == 2 && /style: TextStyle/ {
    sub(/style: TextStyle/, "style: const TextStyle")
    print
    state = 0
    next
  }

  # Anchor: a `        const Text(` opens a candidate block.  Buffer
  # without printing yet so we can swap the const off if confirmed.
  /^        const Text\(/ && state == 0 {
    buffered = $0
    state = 1
    next
  }

  { print }

  END {
    if (state != 0) {
      print "ERROR: signals_page.dart format unexpected — patch incomplete" > "/dev/stderr"
      exit 1
    }
  }
' "$SIGNALS" > "$SIGNALS.tmp" && mv "$SIGNALS.tmp" "$SIGNALS"

grep -q "Engine is scanning 75 pairs" "$SIGNALS" || {
  echo "ERROR: patch 4d failed — empty-state body not patched"
  exit 1
}
grep -q "required this.isLive" "$SIGNALS" || {
  echo "ERROR: patch 4a failed — constructor not updated"
  exit 1
}
grep -q "isLive: scope.repo.isLive" "$SIGNALS" || {
  echo "ERROR: patch 4c failed — call site not updated"
  exit 1
}

# ── pubspec.yaml version bump ──────────────────────────────────────────
echo "→ Bumping version → 0.0.8+8"
sed -i 's|^version: 0.0.7+7$|version: 0.0.8+8|' pubspec.yaml
grep -q "^version: 0.0.8+8$" pubspec.yaml || {
  echo "ERROR: pubspec version bump failed"
  exit 1
}

# ── git stage + commit ─────────────────────────────────────────────────
echo "→ Stage + commit (then 'git push' triggers APK build)"
git add pubspec.yaml "$API_KEYS" "$ABOUT" "$PULSE" "$SIGNALS"
git commit -m "fix(ui): v0.0.8 — banner conditional, About version, regime label, Signals empty copy

- API keys page: PreviewBadge now hidden when Live engine is enabled
  (was unconditional render — contradicted Test connection's green OK)
- About page: version bumped 0.0.4 → 0.0.8, build 'preview-mock' → 'live'
  (had drifted across three releases)
- Pulse regime card: subtitle re-labelled '% trending' (was '% of cycles',
  read as nonsense when paired with non-TRENDING current regime)
- Signals empty state: in Live mode shows honest 'Engine is scanning'
  copy so paid subscribers don't read 'No signals yet' as a broken app"

echo
echo "✓ v0.0.8 ready.  'git push' to trigger APK build."
