"""Entry-time features for MOVER_TREND_PULLBACK — stamped, never applied.

Owner, 2026-08-01: *"taking entry is matter, how we are taking entry based on
only EMA or what, what if we add some more data to that"*.

The answer to the first half is: essentially yes.  ``_evaluate_mover_trend_pullback``
decides direction from ``SMA25 vs SMA99`` on 15m, triggers on the previous bar
tagging ``SMA7`` within a band while this bar closes back above it, and sizes the
stop from ``min(SMA25, prev_low) - ATR×buffer``.  Price against three simple
moving averages plus one ATR.  It reads ``vols`` but hands them only to
``_mover_consol_break`` — the two triggers that produce almost all the volume,
``fast_pullback`` and ``deep_pullback``, never look at volume at all.  A pullback
on collapsing bid into a liquidation cluster is, to this path, the same object as
a pullback being absorbed at a level.

Meanwhile ``smc_data`` is built once per symbol per scan and handed to every
evaluator carrying ``cvd`` / ``cvd_15m``, ``order_book``, ``funding_rate``,
``liquidation_clusters``, ``orderblocks``, ``sweeps``, ``mss``, ``fvg``,
``level_book_levels`` and ``recent_ticks``.  MOVER_TREND_PULLBACK touches two
keys from it — ``pair_profile`` and ``regime_context`` — and uses both only for
display stamps on the outgoing signal.

This module records what those inputs *said* at the moment each MVRTP signal was
created, and applies none of it.

Why stamping rather than filtering
----------------------------------
The 2026-07-29→08-01 window is 46 closed MVRTP signals.  Nineteen cells were
tested across six candidate discriminators; exactly one 95% CI excluded zero, in
the *backwards* direction, against a ~62% familywise probability of at least one
doing so by chance.  That window cannot choose a filter, and choosing one from it
would be the FAILED_AUCTION_RECLAIM mistake at larger n (``CLAUDE.md``: *two
winners are not a promotion*).  So: stamp every candidate input, wait for a
population that can decide, and let the measurement pick.

Design decisions worth keeping
------------------------------
**No second resolver.**  Every other measurement lane in this repo carries its
own forward-resolution machinery, and each one has cost a session to
``INSUFFICIENT`` rows, stalled arms, stale anchors or undatable windows.  This
lane has no resolver at all: it stamps a row keyed by ``signal_id``, and the
outcome is joined from ``signal_performance.json`` — the closed-signal record
``trade_monitor`` already writes at the terminal transition, which since #848
carries the entry risk the trade was actually sized for.  A row that never
delivered simply never joins, and the surface says how many did not rather than
quietly shrinking its own denominator.

**Free by construction.**  Every value here is already in memory at the call
site.  No Firestore read, no network call, no extra candle fetch — the cost rules
forbid adding any of those to a per-scan path, and this adds none.

**Refuse, don't clamp.**  A feature whose inputs are absent is ``None`` with its
reason recorded in ``missing``, never a zero or a midpoint.  A zero here would be
a *reading*, and a reading nobody took is worse than an admitted gap: it would
make an absent order book look like perfectly balanced depth.

Nothing here changes what emits, what a subscriber sees, or what any order does.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

from src import fail_open
from src.utils import get_logger

log = get_logger("entry_features")

#: Ledger schema. Readers gate on this, never on a date (#802) — a migration
#: keyed on a timestamp that predicts a future deploy trusted 88 rows of
#: old-code stamps once already.
SCHEMA = 1

_DEFAULT_PATH: str = os.getenv("ENTRY_FEATURES_PATH", "data/entry_features_v1.json")

#: Ring size. A storage bound, not a cap on what stamps.
_MAX_ROWS: int = int(os.getenv("ENTRY_FEATURES_MAX_ROWS", "4000"))

#: Bars of pullback context to measure over. The trigger looks at exactly two
#: bars (``prev`` and ``close``); the pullback that produced them is longer, and
#: its shape is the thing we have never recorded.
_PULLBACK_LOOKBACK: int = int(os.getenv("ENTRY_FEATURES_PULLBACK_BARS", "6"))

#: Baseline window for the volume ratio — what "normal" volume is for this pair
#: right now, so the ratio is self-normalising across pairs of any size.
_VOL_BASELINE_BARS: int = int(os.getenv("ENTRY_FEATURES_VOL_BASELINE_BARS", "20"))


# --------------------------------------------------------------------------- #
# Feature extraction
# --------------------------------------------------------------------------- #


def _f(value: Any) -> Optional[float]:
    """Coerce to float, or None. Never raises, never invents a default."""
    try:
        if value is None:
            return None
        out = float(value)
        if out != out or out in (float("inf"), float("-inf")):  # NaN / inf
            return None
        return out
    except (TypeError, ValueError):
        return None


def _series(tf: Any, key: str) -> Optional[List[float]]:
    """A candle series as floats, or None.

    Never boolean-tests the array: the data store holds numpy arrays and their
    truthiness raises (``CLAUDE.md`` hard limit — eight features died silently
    to this on 2026-07-14).
    """
    if tf is None:
        return None
    raw = tf.get(key) if isinstance(tf, dict) else None
    if raw is None:
        return None
    try:
        if len(raw) == 0:
            return None
        return [float(v) for v in raw]
    except (TypeError, ValueError):
        return None


def pullback_volume_ratio(
    volumes: Optional[List[float]],
    *,
    lookback: int = _PULLBACK_LOOKBACK,
    baseline: int = _VOL_BASELINE_BARS,
) -> Optional[float]:
    """Volume across the pullback, against this pair's own recent baseline.

    The question the trigger never asks: was the dip sold, or did it just drift?
    A pullback on 0.4× normal volume is participants stepping back; the same
    shape on 2× is distribution. Both currently emit identically.

    Returns mean(pullback bars) / mean(baseline bars). ``None`` when either
    window is short or the baseline is zero — a ratio against no baseline is
    not a small number, it is not a number.
    """
    if volumes is None or len(volumes) < baseline + lookback:
        return None
    recent = volumes[-lookback:]
    prior = volumes[-(baseline + lookback):-lookback]
    if len(prior) == 0 or len(recent) == 0:
        return None
    base = sum(prior) / len(prior)
    if base <= 0:
        return None
    return (sum(recent) / len(recent)) / base


def cvd_slope(cvd: Any, *, lookback: int = _PULLBACK_LOOKBACK) -> Optional[float]:
    """Net cumulative-volume-delta change across the pullback window.

    Sign is what matters: on a LONG pullback a *positive* slope means the dip
    was being absorbed, a negative one means it was being sold into. The
    evaluator has never distinguished those.

    Deliberately returns the raw delta, not a normalised score — normalising
    would need a scale nobody has measured yet, and inventing one now would bake
    an unexamined assumption into the first population this lane ever produces.
    """
    if cvd is None:
        return None
    try:
        if len(cvd) < lookback + 1:
            return None
        head = _f(cvd[-(lookback + 1)])
        tail = _f(cvd[-1])
    except (TypeError, ValueError, IndexError):
        return None
    if head is None or tail is None:
        return None
    return tail - head


def pullback_depth_atr(
    closes: Optional[List[float]],
    lows: Optional[List[float]],
    highs: Optional[List[float]],
    atr: Optional[float],
    is_long: bool,
    *,
    lookback: int = _PULLBACK_LOOKBACK,
) -> Optional[float]:
    """How far the pullback actually retraced, in ATR.

    A one-ATR dip and a three-ATR dip both "tag SMA7 and reclaim". They are not
    the same trade, and nothing downstream can tell them apart today.
    """
    if atr is None or atr <= 0 or closes is None or len(closes) < lookback + 1:
        return None
    ref = closes[-(lookback + 1)]
    if is_long:
        arr = lows
        if arr is None or len(arr) < lookback:
            return None
        extreme = min(arr[-lookback:])
        return (ref - extreme) / atr
    arr = highs
    if arr is None or len(arr) < lookback:
        return None
    extreme = max(arr[-lookback:])
    return (extreme - ref) / atr


def extension_pct(close: Optional[float], ma_slow: Optional[float]) -> Optional[float]:
    """How far price sits from its own slow MA, signed, in percent.

    ``consol_break`` guards against chasing an extended move; ``fast_pullback``
    and ``deep_pullback`` — the two that carry the volume — do not.
    """
    if close is None or ma_slow is None or ma_slow <= 0:
        return None
    return (close - ma_slow) / ma_slow * 100.0


def level_distance_r(
    levels: Any,
    entry: Optional[float],
    tp1: Optional[float],
    sl_dist: Optional[float],
    is_long: bool,
) -> Optional[float]:
    """Distance to the nearest opposing level, in units of the trade's own risk.

    TP1 sits at exactly 1.0R by construction. If a resistance level sits at
    0.4R above a long's entry, that target is behind a wall and the geometry
    never knew. Expressed in R so it is directly comparable to the target.

    ``None`` when the level book has nothing for this symbol — an empty book is
    "we do not know what is overhead", which must not read as "nothing is".
    """
    if entry is None or sl_dist is None or sl_dist <= 0 or not levels:
        return None
    want = "resistance" if is_long else "support"
    best: Optional[float] = None
    for lvl in levels:
        price = _f(getattr(lvl, "price", None) if not isinstance(lvl, dict) else lvl.get("price"))
        ltype = (
            getattr(lvl, "type", "") if not isinstance(lvl, dict) else lvl.get("type", "")
        )
        if price is None or str(ltype) != want:
            continue
        gap = (price - entry) if is_long else (entry - price)
        if gap <= 0:
            continue  # already behind us
        if best is None or gap < best:
            best = gap
    if best is None:
        return None
    return best / sl_dist


def book_imbalance(order_book: Any) -> Optional[float]:
    """Top-of-book depth imbalance: (bids - asks) / (bids + asks), in [-1, 1].

    Positive favours the bid. ``None`` when either side is absent — a missing
    book is not a balanced one, and returning 0.0 would say the opposite of
    what we know.
    """
    if not isinstance(order_book, dict):
        return None
    bids, asks = order_book.get("bids"), order_book.get("asks")
    if not bids or not asks:
        return None
    try:
        b = sum(float(lvl[1]) for lvl in bids[:10])
        a = sum(float(lvl[1]) for lvl in asks[:10])
    except (TypeError, ValueError, IndexError):
        return None
    if b + a <= 0:
        return None
    return (b - a) / (b + a)


def capture(
    *,
    symbol: str,
    direction_is_long: bool,
    entry: float,
    sl_dist: float,
    tp1: float,
    trigger: str,
    ma_fast: float,
    ma_mid: float,
    ma_slow: float,
    stack_sep_pct: float,
    atr: Optional[float],
    tf_15m: Any,
    smc_data: Optional[Dict[str, Any]],
    profile_would_reject: Optional[bool] = None,
) -> Dict[str, Any]:
    """Every entry-time input the path currently ignores, read once.

    Pure: no I/O, no mutation of anything passed in. Each feature independently
    degrades to ``None`` with a reason in ``missing`` rather than failing the
    whole capture — one absent order book must not cost us the volume reading
    beside it.
    """
    smc = smc_data or {}
    closes = _series(tf_15m, "close")
    highs = _series(tf_15m, "high")
    lows = _series(tf_15m, "low")
    vols = _series(tf_15m, "volume")

    feats: Dict[str, Any] = {
        "pullback_vol_ratio": pullback_volume_ratio(vols),
        "cvd_slope": cvd_slope(smc.get("cvd_15m") or smc.get("cvd")),
        "pullback_depth_atr": pullback_depth_atr(
            closes, lows, highs, _f(atr), direction_is_long
        ),
        "extension_pct": extension_pct(_f(entry), _f(ma_slow)),
        "level_dist_r": level_distance_r(
            smc.get("level_book_levels"), _f(entry), _f(tp1), _f(sl_dist), direction_is_long
        ),
        "book_imbalance": book_imbalance(smc.get("order_book")),
        "funding_rate": _f(smc.get("funding_rate")),
        "liq_clusters_n": (
            len(smc["liquidation_clusters"])
            if isinstance(smc.get("liquidation_clusters"), (list, tuple))
            else None
        ),
    }
    feats["missing"] = sorted(k for k, v in feats.items() if v is None)
    feats.update(
        {
            "symbol": str(symbol),
            "side": "LONG" if direction_is_long else "SHORT",
            "entry_trigger": str(trigger or ""),
            "stack_sep_pct": _f(stack_sep_pct),
            "sl_dist_pct": (
                (_f(sl_dist) / _f(entry) * 100.0)
                if _f(entry) and _f(sl_dist) and _f(entry) > 0
                else None
            ),
            # The shadow of the argument nineteen of twenty call sites omit:
            # would the pair-tier-aware spread/volume thresholds have rejected
            # this candidate? Recorded, never enforced.
            "profile_would_reject": profile_would_reject,
        }
    )
    return feats


# --------------------------------------------------------------------------- #
# Ledger — stamp only; outcomes are joined from the closed-signal record
# --------------------------------------------------------------------------- #


class EntryFeatureLedger:
    """Append-only ring of entry stamps, keyed by ``signal_id``."""

    def __init__(self, path: Optional[str] = None, max_rows: Optional[int] = None) -> None:
        self._path = _DEFAULT_PATH if path is None else path
        self._rows: Deque[dict] = deque(maxlen=max_rows or _MAX_ROWS)
        self._seen: set = set()
        self._lock = threading.RLock()
        self._dirty = False
        self.duplicate_skips = 0

    def add(self, row: dict) -> bool:
        sid = str(row.get("signal_id") or "")
        if not sid:
            return False
        with self._lock:
            if sid in self._seen:
                # A signal is stamped exactly once, at creation. A second stamp
                # would mean the evaluator ran twice on one signal_id, which is
                # a fault worth counting rather than silently overwriting.
                self.duplicate_skips += 1
                return False
            self._seen.add(sid)
            self._rows.append(row)
            self._dirty = True
            return True

    def rows(self) -> List[dict]:
        with self._lock:
            return list(self._rows)

    def flush(self, force: bool = False) -> bool:
        """Persist. ``force`` writes even when unchanged, so an idle lane still
        proves it is alive — a heartbeat that only fires on change is not a
        heartbeat, and an ops page cannot tell "quiet" from "stopped" without it.
        """
        with self._lock:
            if not (self._dirty or force):
                return False
            # ``path=""`` means in-memory (what tests construct with). Return
            # BEFORE the side effect: a no-op that touches the disk wrote a
            # stray .tmp into the repo root for two months, and its failure
            # raised into fail_open on every test run.
            if not self._path:
                self._dirty = False
                return False
            rows = list(self._rows)
            self._dirty = False
        payload = {"schema": SCHEMA, "written_at": time.time(), "rows": rows}
        tmp = f"{self._path}.tmp"
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:  # noqa: BLE001 — measurement must never break a scan
            fail_open.record("entry_features.flush", exc)
            return False

    def load(self) -> None:
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            if int(payload.get("schema") or 0) != SCHEMA:
                log.info(
                    "entry_features: ledger schema {} != {}, starting fresh",
                    payload.get("schema"), SCHEMA,
                )
                return
            with self._lock:
                for row in payload.get("rows") or []:
                    sid = str(row.get("signal_id") or "")
                    if sid and sid not in self._seen:
                        self._seen.add(sid)
                        self._rows.append(row)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("entry_features.load", exc)


_ledger: Optional[EntryFeatureLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> EntryFeatureLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = EntryFeatureLedger()
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[EntryFeatureLedger] = None) -> None:
    global _ledger
    with _ledger_lock:
        _ledger = ledger


def enabled() -> bool:
    """Measurement flag — ON by default.

    ``CLAUDE.md`` § Project Phase: a measurement shipped default-OFF produces an
    empty panel and a decision that keeps being deferred, which is exactly what
    happened to the SAR exit arm. This cannot reach a subscriber or the money
    path, so it runs from the moment it ships.
    """
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("entry_features_enabled"))
    except Exception:
        return os.getenv("ENTRY_FEATURES_ENABLED", "true").strip().lower() != "false"


def stamp(
    sig: Any,
    features: Dict[str, Any],
    now_ts: Optional[float] = None,
    regime: str = "",
) -> bool:
    """Record one signal's entry-time features. Never raises into the scanner.

    ``regime`` is passed in rather than read off ``sig``, and that is not a
    style choice. ``sig.entry_regime`` is written by
    ``scanner._populate_signal_context``, which runs **after** the evaluator has
    returned — so at stamp time the attribute is still ``""``. Reading it here
    put an empty regime on every row and would have bucketed the whole page into
    one group (caught 2026-08-01, immediately after shipping).

    That is #817's class one caller earlier, and the comment above
    ``_populate_signal_context``'s call site already warns about it: the
    market-context stamp *"previously ran with these fields still empty, so the
    Wyckoff phase always classified AMBIGUOUS"*. The evaluator receives the
    regime as a parameter, which is where it is genuinely known at this point.

    The closed-signal record's ``entry_regime`` remains authoritative — it is
    what the scanner finalised — and ops prefers it on the join. This value is
    the evaluator's own view; where the two disagree, the scanner reclassified
    between evaluation and dispatch, and that is information rather than a
    conflict.
    """
    if not enabled():
        return False
    try:
        sid = str(getattr(sig, "signal_id", "") or "")
        if not sid:
            return False
        row = dict(features)
        row.update(
            {
                "signal_id": sid,
                "setup_class": str(getattr(sig, "setup_class", "") or ""),
                "confidence": _f(getattr(sig, "confidence", None)),
                "entry_regime": str(
                    regime or getattr(sig, "entry_regime", "") or ""
                ),
                "stamped_at": time.time() if now_ts is None else float(now_ts),
                "schema": SCHEMA,
            }
        )
        return get_ledger().add(row)
    except Exception as exc:  # noqa: BLE001 — a measurement must never kill a scan
        fail_open.record("entry_features.stamp", exc)
        return False


# --------------------------------------------------------------------------- #
# "As of now" vs "later" — the split this lane exists to produce
# --------------------------------------------------------------------------- #

#: Features where a LOWER value is the suspected problem, so a candidate rule
#: would keep rows ABOVE the threshold. Everything else keeps rows below.
_KEEP_ABOVE = frozenset({"pullback_vol_ratio", "level_dist_r", "cvd_slope"})


def split_by_feature(
    joined: List[Dict[str, Any]],
    feature: str,
    threshold: float,
) -> Dict[str, Any]:
    """What the delivered book looks like now, versus under one candidate rule.

    *now* is every joined row — the book as it actually shipped. *keep* is the
    subset a rule on this feature would have let through; *drop* is what it
    would have removed. ``unknown`` is rows whose feature never computed, and it
    is reported rather than folded into either side: a rule cannot be credited
    with an outcome it could not have seen, and silently binning the unknowns
    with "keep" is how a filter takes credit for rows it never filtered.

    Every row carries ``r`` from the closed-signal record — the engine's
    ``sl_distance_pct_at_entry`` denominator (#848), not the stop the trade
    exited on.
    """
    keep_above = feature in _KEEP_ABOVE
    buckets: Dict[str, List[Dict[str, Any]]] = {"keep": [], "drop": [], "unknown": []}
    for row in joined or []:
        val = _f(row.get(feature))
        if val is None:
            buckets["unknown"].append(row)
        elif (val >= threshold) if keep_above else (val <= threshold):
            buckets["keep"].append(row)
        else:
            buckets["drop"].append(row)

    def _agg(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        rs = [_f(r.get("r")) for r in rows]
        rs = [v for v in rs if v is not None]
        pnls = [_f(r.get("pnl_pct")) for r in rows]
        pnls = [v for v in pnls if v is not None]
        return {
            "n": len(rows),
            "scored": len(rs),
            "win_rate": (sum(1 for v in rs if v > 0) / len(rs)) if rs else None,
            "avg_r": (sum(rs) / len(rs)) if rs else None,
            "total_r": sum(rs) if rs else None,
            # Quoted beside every R because the R-scored subset is not a random
            # sample of the book — rows closed before #848 carry no denominator.
            "avg_pnl_pct": (sum(pnls) / len(pnls)) if pnls else None,
            "total_pnl_pct": sum(pnls) if pnls else None,
        }

    now = _agg(list(joined or []))
    keep = _agg(buckets["keep"])
    delta_r = (
        keep["avg_r"] - now["avg_r"]
        if keep["avg_r"] is not None and now["avg_r"] is not None
        else None
    )
    return {
        "feature": feature,
        "threshold": threshold,
        "direction": "keep >= threshold" if keep_above else "keep <= threshold",
        "now": now,
        "keep": keep,
        "drop": _agg(buckets["drop"]),
        "unknown": _agg(buckets["unknown"]),
        "delta_avg_r": delta_r,
        # A rule that keeps almost everything has not been tested by this window,
        # whatever its delta reads.
        "kept_fraction": (keep["n"] / now["n"]) if now["n"] else None,
    }


def join_outcomes(
    stamps: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Join entry stamps to closed-signal records on ``signal_id``.

    Returns ``(joined, coverage)``. Coverage is not decoration: a stamp with no
    record is a signal the router dropped or one still open, and a record with
    no stamp predates this lane. Both populations must be visible, because a
    join that silently keeps only what matched reports a book that is not the
    book.
    """
    by_id = {str(r.get("signal_id") or ""): r for r in records or []}
    joined: List[Dict[str, Any]] = []
    unmatched = 0
    for s in stamps or []:
        rec = by_id.get(str(s.get("signal_id") or ""))
        if rec is None:
            unmatched += 1
            continue
        pnl = _f(rec.get("pnl_pct"))
        sl_pct = _f(rec.get("sl_distance_pct_at_entry"))
        row = dict(s)
        row.update(
            {
                "pnl_pct": pnl,
                "sl_distance_pct_at_entry": sl_pct,
                "r": (pnl / sl_pct) if (pnl is not None and sl_pct and sl_pct > 0) else None,
                "outcome_label": str(rec.get("outcome_label") or ""),
                "hit_sl": bool(rec.get("hit_sl")),
            }
        )
        joined.append(row)
    return joined, {
        "stamps": len(stamps or []),
        "records": len(records or []),
        "joined": len(joined),
        "stamped_not_closed": unmatched,
        "scored": sum(1 for r in joined if r.get("r") is not None),
    }


def summary(ledger: Optional[EntryFeatureLedger] = None) -> Dict[str, Any]:
    """Liveness-facing shape: is this lane stamping, and how complete is it?"""
    led = ledger if ledger is not None else get_ledger()
    rows = led.rows()
    newest = max((_f(r.get("stamped_at")) or 0.0 for r in rows), default=0.0)
    per_feature_missing: Dict[str, int] = {}
    for r in rows:
        for k in r.get("missing") or []:
            per_feature_missing[k] = per_feature_missing.get(k, 0) + 1
    return {
        "schema": SCHEMA,
        "rows": len(rows),
        "newest_stamp_ts": newest or None,
        "age_sec": (time.time() - newest) if newest else None,
        "duplicate_skips": led.duplicate_skips,
        # Which inputs are absent, and how often. A feature missing on every row
        # is a dead upstream, and it looks identical to a feature nobody uses
        # unless the count is on screen.
        "missing_by_feature": per_feature_missing,
    }
