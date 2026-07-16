"""CI guard: the numpy-truthiness pattern class must not re-enter src/.

2026-07-14 incident (PRs #726/#727): ``arr or []`` / ``if not arr`` /
``and arr`` on OHLCV values raises ``ValueError`` when the value is a
multi-element numpy array (the shape ``HistoricalDataStore.get_candles``
returns), and fail-open handlers turned those raises into eight silently
dead features.  The runtime defense is src/fail_open.py + the
feature-liveness watchdog; THIS test is the build-time defense — it scans
the source for the dangerous shapes so the bug class fails CI before it can
ship.

If this test fails on your new code: use ``v = cd.get("close")`` +
``if v is None or len(v) == 0`` instead of truthiness.  If your site is
GENUINELY list-fed (a ``_normalize_candle_dict`` boundary, a JSON payload),
add it to the allowlist below WITH a comment proving the source — see
tests/test_incident_2026_07_14_numpy_truthiness.py for why "the fixture
passed lists" is not proof.
"""
from __future__ import annotations

import pathlib
import re

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
# 2026-07-16 audit: the guard only scanned src/ — scripts/, tools/ and
# config/ consume the same stores (diag scripts read candles directly) and
# were unguarded against regression.  All three are clean today; this pins them.
_SCAN_DIRS = [_SRC, _ROOT / "scripts", _ROOT / "tools", _ROOT / "config"]

_OHLCV = r"(?:open|high|low|close|volume)"

# The shapes that killed us: boolean coercion of a maybe-ndarray OHLCV value.
_PATTERNS = [
    # x.get("close") or []   /   x.get("close", []) or []
    re.compile(rf"\.get\(\s*[\"']{_OHLCV}[\"'][^)]*\)\s+or\s"),
    # if not x.get("close")  /  ... and not cd.get("high")
    re.compile(rf"not\s+\w+\.get\(\s*[\"']{_OHLCV}[\"']"),
    # if candles["close"]:   /   and candles["close"]
    re.compile(rf"(?:if|and|or)\s+\w+\[\s*[\"']{_OHLCV}[\"']\s*\]\s*(?::|and\b|or\b|\)|$)"),
    # float(x[-1]) if closes else ...
    re.compile(r"if\s+(?:closes|highs|lows|opens|volumes|\w+_arr|\w+_array)\s+else\b"),
    # if not closes: (bare named series; _arr/_array suffixes added 2026-07-16
    # — the original OHLCV-name-bound regex missed `if not mom_arr:` shapes)
    re.compile(r"(?:if|and|or)\s+not\s+(?:closes|highs|lows|opens|volumes|\w+_arr|\w+_array)\s*(?::|and\b|or\b|\)|$)"),
    # if cd.get("close"):  (truthy .get — the 2026-07-16 audit found the
    # original patterns only caught `not …get()` and `…get() or`, not the
    # plain truthy test).  A trailing `is`/comparison does NOT match.
    re.compile(rf"(?:if|and|or)\s+\w+\.get\(\s*[\"']{_OHLCV}[\"'][^)]*\)\s*(?::|and\b|or\b|\)|$)"),
    # if mom_arr: (bare truthy _arr/_array-suffixed series)
    re.compile(r"(?:if|and|or)\s+(?:\w+_arr|\w+_array)\s*(?::|and\b|or\b|$)"),
    # arr or [] / series or [] / closes or [] — the bare-name fallback form
    # (2026-07-16 audit: the original .get()-bound regex missed it entirely).
    # `candles` is deliberately absent: by codebase convention that name holds
    # the per-symbol DICT (get_candles output), whose truthiness is safe.
    re.compile(
        r"\b(?:arr|series|closes|highs|lows|opens|volumes|ohlc\w*|\w+_arr|\w+_array)"
        r"\s+or\s+\[",
    ),
    # if not arr: / if not series: / if not ohlcv: (bare series names — the
    # docstring always claimed this coverage; the regex never had it).
    re.compile(r"(?:if|and|or)\s+not\s+(?:arr|series|ohlc\w*)\s*(?::|and\b|or\b|\)|$)"),
]

# Verified list-fed or len-guarded sites (file suffix, line substring).
# Every entry must carry the proof in the comment.
_ALLOWLIST = [
    # ctx.candles values are plain lists — normalized at the store boundary
    # by scanner._normalize_candle_dict (the shadow path proved this live).
    ("scanner/__init__.py", "highs = c15.get(\"high\") or []"),
    ("scanner/__init__.py", "lows = c15.get(\"low\") or []"),
    ("scanner/__init__.py", "closes = c15.get(\"close\") or []"),
    # Evaluator-side candle dicts are the scanner's normalized list dicts.
    ("channels/scalp.py", "h1_highs = cd_1h.get(\"high\") or []"),
    ("channels/scalp.py", "h1_lows = cd_1h.get(\"low\") or []"),
    ("channels/scalp.py", "_h1_closes = _h1.get(\"close\") or []"),
    ("channels/scalp.py", "_h1_highs = _h1.get(\"high\") or []"),
    ("channels/scalp.py", "_h1_lows = _h1.get(\"low\") or []"),
    ("channels/scalp.py", "closes_15m = candles_15m.get(\"close\") or []"),
    # cd is _atr_pct_from_candles input — every caller passes ctx.candles
    # sub-dicts (lists); verified in the 2026-07-14 sweep.
    ("scanner/__init__.py", "highs = cd.get(\"high\") or []"),
    ("scanner/__init__.py", "lows = cd.get(\"low\") or []"),
    ("scanner/__init__.py", "closes = cd.get(\"close\") or []"),
    # btc_direction fallback list check runs AFTER the 2026-07-14 fix
    # normalised `closes` to None-or-sequence with len() checks.
    ("order_flow.py", "if not closes or not buy_volumes or not sell_volumes:"),
    # bin_volumes is `.tolist()` output two lines above — always a list.
    ("volume_profile.py", "if not bin_volumes or all(v == 0 for v in bin_volumes):"),
    # `zone` is an FVG/OB zone DICT of scalar floats (gap_high/top/level/…),
    # never a candle series — scalar `or`-chaining is the intended fallback.
    ("channels/scalp.py", "or zone.get(\"high\")"),
    ("channels/scalp.py", "or zone.get(\"low\")"),
    # Documentation text inside a docstring (describes the banned pattern);
    # the scanner strips `#` comments but not docstrings.
    ("btc_state.py", "Avoids ``arr or []`` (ambiguous truth value on numpy arrays)."),
    # `ohlc` here is fetch_ohlc_since's return: a DICT of lists per its
    # documented contract (invalidation_audit.py:251) — `if not ohlc:` is
    # dict-emptiness; the inner values get None/len checks two lines below.
    ("invalidation_audit.py", "if not ohlc:"),
    ("suppression_audit.py", "if not ohlc:"),
]


def _allowed(rel: str, line: str) -> bool:
    stripped = line.strip()
    return any(rel.endswith(sfx) and frag in stripped for sfx, frag in _ALLOWLIST)


def test_no_new_numpy_truthiness_patterns_in_src():
    violations = []
    paths = []
    for base in _SCAN_DIRS:
        if base.is_dir():
            paths.extend(sorted(base.rglob("*.py")))
    for path in paths:
        rel = str(path.relative_to(_ROOT))
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("#", 1)[0]
            if not code.strip():
                continue
            for pat in _PATTERNS:
                if pat.search(code) and not _allowed(rel, line):
                    violations.append(f"{rel}:{lineno}: {line.strip()}")
                    break
    assert not violations, (
        "Boolean-context OHLCV access — the numpy-truthiness class that "
        "silently killed 8 features (2026-07-14, PRs #726/#727). Use "
        "`v is None or len(v) == 0`, or add a PROVEN list-fed site to the "
        "allowlist in this file:\n  " + "\n  ".join(violations)
    )
