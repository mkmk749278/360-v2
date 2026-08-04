"""Each setup's own trigger timeframe — one declaration, several readers.

The defect
----------
``Scanner._get_primary_timeframe`` returned the literal string ``"5m"`` for
every channel:

    @staticmethod
    def _get_primary_timeframe(chan_name: str) -> str:
        \"\"\"Return the primary timeframe interval string for a given channel.\"\"\"
        return "5m"

A docstring describing a lookup, over a function that is a constant.  Six
money-path consumers read it, and every one of them is therefore computed on 5m
bars for setups that do not trade 5m:

* continuation-sweep evidence  → ``has_sweep`` → the 25-point SMC dimension
* VWAP extension rejection     → soft penalty
* OI + funding gate            → soft penalty, and ``_funding_rate``
* cross-timeframe volume divergence → soft penalty
* chart + candlestick patterns → ``sig.confidence`` bonus and the 10-point
  Patterns dimension
* the volume inputs to ``score_signal_components`` → the composite score

``MOVER_TREND_PULLBACK`` is ~59% of the enqueued book and trades **15m**.
``MOVER_AVWAP_SCALP``, ``MEAN_REVERT`` and ``RANGE_FADE`` also trade 15m;
``MA_CROSS_TREND_SHIFT`` is a 1h/4h cross; ``WHALE_MOMENTUM`` is 1m.  So for the
majority of the book, every one of those six readings has been taken on the
wrong series — not missing, not crashing, just describing a different chart
than the one the trade is on.

Why this module exists at all
------------------------------
The map was first written for ``structural_snap`` (a 5m swing and a 15m swing
are different levels).  A second consumer means a second copy, and a second copy
is the drift that inflated the Strategy Lab rollup for a week.  So the
declaration lives here, alone, and both subsystems import it — one writer, one
reader, the rule this repo already lives by.

Every entry was read off the evaluator's own ``candles.get(...)`` in
``channels/scalp.py``.  A setup absent from the map is **not** defaulted: callers
get ``None`` and decide what that means for them, and
``tests/test_structural_snap.py`` derives the required keys by parsing the
evaluators' own ``setup_class=`` arguments, so tomorrow's evaluator fails CI
rather than silently inheriting 5m.

Shipping posture
----------------
Correcting this changes what scores and therefore what emits, so it ships
**dark**: ``SETUP_TF_CORRECTION_LIVE`` defaults **off** and
``_get_primary_timeframe`` keeps returning ``"5m"`` byte-identically, while the
mismatch is counted from the moment it deploys.  The flag is the money-path
half; the counting is not.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

#: The timeframe each evaluator actually triggers on.
#:
#: Read off ``channels/scalp.py``. ``MOVER_AVWAP_SCALP`` follows the
#: ``MOVER_AVWAP_TF`` env default ("15m"); ``MA_CROSS_TREND_SHIFT`` fires on a
#: 1h EMA21/50 or 4h EMA50/200 cross and takes the faster of the two.
TF_BY_SETUP: Dict[str, str] = {
    "WHALE_MOMENTUM": "1m",
    "LIQUIDITY_SWEEP_REVERSAL": "5m",
    "TREND_PULLBACK_EMA": "5m",
    "LIQUIDATION_REVERSAL": "5m",
    "VOLUME_SURGE_BREAKOUT": "5m",
    "BREAKDOWN_SHORT": "5m",
    "OPENING_RANGE_BREAKOUT": "5m",
    "SR_FLIP_RETEST": "5m",
    "FUNDING_EXTREME_SIGNAL": "5m",
    "QUIET_COMPRESSION_BREAK": "5m",
    "DIVERGENCE_CONTINUATION": "5m",
    "CONTINUATION_LIQUIDITY_SWEEP": "5m",
    "POST_DISPLACEMENT_CONTINUATION": "5m",
    "FAILED_AUCTION_RECLAIM": "5m",
    "MOVER_TREND_PULLBACK": "15m",
    "MOVER_AVWAP_SCALP": "15m",
    "MEAN_REVERT": "15m",
    "RANGE_FADE": "15m",
    "MA_CROSS_TREND_SHIFT": "1h",
}

#: What the scanner has always used, and still uses while the flag is off.
LEGACY_TF = "5m"


def declared_for(setup_class: str) -> Optional[str]:
    """The setup's own trigger timeframe, or ``None`` if it declares none.

    ``None`` is deliberately not ``"5m"``: a caller that cannot tell "declares
    5m" from "declares nothing" cannot report a new evaluator as unmapped, and
    an unmapped path would inherit the exact defect this module exists to fix.
    """
    return TF_BY_SETUP.get(str(setup_class or "").upper())


@dataclass
class TfCounters:
    """In-process census of **resolutions**, not of signals.

    Read from a counter the engine itself increments — a ``docker exec``
    one-shot reads the boot default of a tunable and has already misled one
    diagnosis (2026-08-02).

    **The denominator is not the signal count.** Six consumers call
    :func:`resolve` per candidate, so a candidate contributes ~6 rows here.
    That is right for the question this object answers — "is the resolver
    being called at all, and on what" — and wrong for "what fraction of the
    book would a flip move".  The per-signal fact is stamped once, on the
    structural-snap row (``score_tf_used`` / ``score_tf_mismatch``), and that
    is what the ops panel divides by.  Do not compute a book fraction from
    here; the two denominators differ by a factor nobody would notice on a
    plausible-looking percentage.
    """

    resolved: int = 0
    #: Declared TF == the legacy 5m. No behaviour change either way.
    agreed: int = 0
    #: Declared TF differs from 5m — these are the rows a flip would move.
    mismatched: int = 0
    #: No declared timeframe: a setup absent from the map.
    unmapped: int = 0
    #: Correction actually applied (flag on).
    applied: int = 0
    by_setup: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def record(self, setup_class: str, declared: Optional[str], used: str,
               applied: bool) -> None:
        key = str(setup_class or "UNKNOWN").upper()
        with self._lock:
            self.resolved += 1
            slot = self.by_setup.setdefault(
                key, {"n": 0, "declared": declared, "mismatched": 0, "applied": 0}
            )
            slot["n"] += 1
            slot["declared"] = declared
            if declared is None:
                self.unmapped += 1
            elif declared == used:
                self.agreed += 1
            else:
                self.mismatched += 1
                slot["mismatched"] += 1
            if applied:
                self.applied += 1
                slot["applied"] += 1

    def as_dict(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "resolved": self.resolved,
                "agreed": self.agreed,
                "mismatched": self.mismatched,
                "unmapped": self.unmapped,
                "applied": self.applied,
                "by_setup": {k: dict(v) for k, v in self.by_setup.items()},
            }


_counters = TfCounters()


def get_counters() -> TfCounters:
    return _counters


def reset_counters() -> None:
    global _counters
    _counters = TfCounters()


def correction_live() -> bool:
    """Whether the corrected timeframe is actually handed to the six consumers.

    Default **off**. This is the money-path half: flipping it changes what
    ``has_sweep``, the VWAP/OI/volume-divergence gates, the pattern bonus and
    the composite score's volume inputs are computed on, for ~59% of the book
    at once. Owner-sign-off item.
    """
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("setup_tf_correction_live"))
    except Exception:  # noqa: BLE001 — a tunable read must never block emission
        return False


def resolve(setup_class: str, *, live: Optional[bool] = None) -> str:
    """The timeframe the scanner should use, and the census entry for it.

    Returns ``LEGACY_TF`` unchanged while the correction is dark, so live
    behaviour is byte-identical to before this module existed — and counts the
    mismatch either way, which is what makes the flip decidable.
    """
    declared = declared_for(setup_class)
    is_live = correction_live() if live is None else bool(live)
    use_corrected = bool(is_live and declared is not None and declared != LEGACY_TF)
    used = declared if (use_corrected and declared is not None) else LEGACY_TF
    _counters.record(setup_class, declared, used, applied=use_corrected)
    return used


def summary() -> Dict[str, Any]:
    out = _counters.as_dict()
    out["correction_live"] = correction_live()
    return out
