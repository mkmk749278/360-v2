"""What this trade REQUIRED, and what those requirements read now.

The governor's system prompt asks the model whether *reality still supports the
original premise*. Until this module existed the payload carried `setup_class`
as a bare name and nothing else about it, so the model was being asked to check
a premise it had never been told. Measured 2026-09-10: the whole world one
position was described by was 27 scalar fields and 1,042 bytes, and none of them
said what `MOVER_TREND_PULLBACK` means.

Three rules shape what is and is not in here.

**The thesis is engine-authored, and a path without one is refused.**
`THESIS_BY_SETUP` is a constant this repo owns — never external text, never a
model-written summary. A setup missing from it is `no_thesis`, counted and
named, rather than defaulted to a generic sentence: `SNAP_TF_BY_SETUP` learned
that a hand-maintained per-setup map is a floor and the miss has to be a
refusal, and a test derives the required keys from the evaluators' own
`setup_class=` arguments so tomorrow's path fails CI instead of landing
silently in a fallback.

**The condition list is DERIVED from the feature registry, not typed twice.**
`entry_features.features_for(setup)` already decides which readings a path turns
on, and the entry stamp already records them. A second hand-kept list here is
the drift this repo has paid for under six names.

**Nothing here judges. It reports.**
There is deliberately no `still_true` boolean on a numeric condition. Deciding
that RSI 47 at entry against RSI 41 now means the premise has broken needs a
threshold, and any threshold picked today would come from the window it is about
to be measured on — the defect `entry_quality` was built to avoid ("does its
threshold come from code that already exists, or from this window?"). So both
values are published, `moved` states the change in the feature's own units, and
the model does the reading. Where the evaluator itself gated on a BOOLEAN, that
boolean is reported as it stands, because there the threshold is the engine's
and already exists.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence

from src import fail_open
from src.utils import get_logger

log = get_logger("ai_governor_premise")

#: A path with no thesis is refused rather than given a generic sentence.
REFUSE_NO_THESIS = "no_thesis"
#: We hold the entry stamp but the trigger series will not support a recompute.
WHY_NOT_RECOMPUTABLE = "not_recomputable_in_monitor"
#: The entry-feature lane never stamped this signal (it predates the lane, or
#: the stamp was refused). Named apart from "the feature is unknown": one is a
#: missing row and the other is a missing reading.
WHY_NO_ENTRY_STAMP = "no_entry_stamp"
#: The stamp exists and this feature is not in it — the entry-quality lane
#: refused or could not compute that one reading. Named apart from a missing
#: row: one means the lane never saw this signal, the other means it saw it and
#: could not read this column, and the fixes differ.
WHY_FEATURE_NOT_STAMPED = "feature_not_stamped"


#: One sentence per live path, written from the evaluator's own mechanism.
#:
#: These are descriptions of what the code requires, not opinions about whether
#: it works. Each was read off `src/channels/scalp.py` rather than off a doc,
#: because a doc describing an evaluator is a claim about it and this repo has
#: found four of those false in one session.
THESIS_BY_SETUP: Dict[str, str] = {
    "MOVER_TREND_PULLBACK": (
        "A pair promoted for its own 24h move, in an established trend on the "
        "15m, pulled back into its SMA7/25/99 stack and resumed. It requires "
        "the stack to stay ordered in the trade's direction and the pullback to "
        "remain a pullback rather than becoming the reversal."
    ),
    "MOVER_AVWAP_SCALP": (
        "A promoted mover trading with its anchored VWAP, gated on volume and "
        "on the slope of that VWAP. It requires the anchor to still be the "
        "right anchor: the move it is measured from has not ended, and price "
        "has not spent the leg it was entered for."
    ),
    "TREND_PULLBACK_EMA": (
        "A 1H EMA21/EMA50 trend, entered on a 5m pullback that tagged EMA21 and "
        "closed back above both EMAs with RSI in 40-60 and rising, on a close "
        "above the previous high. It requires the 1H trend to hold; every 5m "
        "trigger condition was a boolean and is already spent."
    ),
    "FAILED_AUCTION_RECLAIM": (
        "Price swept a level, failed to accept beyond it, and reclaimed. It "
        "requires the reclaim to hold — a second failure back through the level "
        "is the premise inverting, not a drawdown."
    ),
    "LIQUIDITY_SWEEP_REVERSAL": (
        "A stop run through an obvious level that immediately reversed. It "
        "requires the reversal to keep going: this setup pays quickly or not at "
        "all, and time spent near entry is itself evidence against it."
    ),
    "QUIET_COMPRESSION_BREAK": (
        "Volatility compressed into a range and broke out. It requires the "
        "expansion to continue; a return inside the compressed range is the "
        "break having failed."
    ),
    "BREAKDOWN_SHORT": (
        "A structural breakdown through support with participation. It requires "
        "the broken level to hold as resistance."
    ),
    "MEAN_REVERT": (
        "Price stretched far enough from its mean, in a range, to snap back. It "
        "requires the range to still be a range — a trend starting is the "
        "premise being wrong rather than the trade being early."
    ),
    "RANGE_FADE": (
        "A fade of a range extreme. It requires the range boundary to hold; "
        "acceptance beyond it is a breakout and this trade is on the wrong side "
        "of it."
    ),
    "DIVERGENCE_CONTINUATION": (
        "Order-flow divergence against a move, taken as continuation of the "
        "prior trend. It requires that divergence to resolve in the trade's "
        "direction rather than the price move to keep winning."
    ),
    "SR_FLIP_RETEST": (
        "A broken support/resistance level retested from the other side, "
        "confirmed on the 1H close. It requires the flip to hold: price back "
        "through the level is the flip having failed."
    ),
    "VOLUME_SURGE_BREAKOUT": (
        "A breakout carried by a volume surge. It requires the participation to "
        "persist; a breakout on volume that dries up is a trap."
    ),
    "WHALE_MOMENTUM": (
        "A large-order momentum impulse on the 1m. It requires the impulse to "
        "still be running — this is the shortest-lived premise in the book."
    ),
    "FUNDING_EXTREME_SIGNAL": (
        "A contrarian entry against extreme funding, with price/RSI/CVD "
        "confluence. It requires the funding extreme to still be there; funding "
        "normalising is the reason for the trade going away."
    ),
    "LIQUIDATION_REVERSAL": (
        "A reversal off a liquidation cascade. It requires the cascade to be "
        "finished rather than paused."
    ),
    "MA_CROSS_TREND_SHIFT": (
        "A 1H moving-average cross marking a trend shift. It requires the new "
        "trend to establish; a cross that immediately reverts is noise."
    ),
    # Both disabled evaluators (ORB + CLS). They still declare a `setup_class`,
    # so they are still in the derived requirement — and a path that is off
    # today is exactly the one that would land silently in `no_thesis` the day
    # somebody turns it on.
    "OPENING_RANGE_BREAKOUT": (
        "A break of the session's opening range. It requires the break to hold "
        "beyond the range rather than revert into it."
    ),
    "CONTINUATION_LIQUIDITY_SWEEP": (
        "A sweep of liquidity taken as continuation rather than reversal. It "
        "requires the prior trend to reassert after the sweep."
    ),
    "POST_DISPLACEMENT_CONTINUATION": (
        "Continuation after a displacement leg. It requires the displacement to "
        "be respected on the retrace."
    ),
}


def thesis_for(setup_class: str) -> Optional[str]:
    """The path's thesis, or ``None`` — never a generic sentence."""
    return THESIS_BY_SETUP.get(str(setup_class or "").upper())


# ---------------------------------------------------------------------------
# Recomputing "now" — only from the series the sweep already holds
# ---------------------------------------------------------------------------
#
# The monitor loop resolves ONE timeframe (the trigger tf) for the menu, and
# that is the whole budget. A feature needing 1H bars, the order book, the
# LevelBook at entry or the scanner's smc_data is not recomputable here and says
# so by name rather than arriving as a plausible-looking zero.


def _closes(series: Mapping[str, Any]) -> List[float]:
    try:
        return [float(c) for c in (series or {}).get("close", [])]
    except Exception:  # noqa: BLE001
        return []


def _sma(values: Sequence[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None
    return sum(values[-period:]) / float(period)


def _rsi_now(series: Mapping[str, Any], period: int = 14) -> Optional[float]:
    closes = _closes(series)
    if len(closes) < period + 1:
        return None
    gains: List[float] = []
    losses: List[float] = []
    for i in range(len(closes) - period, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0.0))
        losses.append(max(-diff, 0.0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss <= 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _vol_ratio_now(series: Mapping[str, Any], lookback: int = 20) -> Optional[float]:
    try:
        vols = [float(v) for v in (series or {}).get("volume", [])]
    except Exception:  # noqa: BLE001
        return None
    if len(vols) < lookback + 1:
        return None
    base = sum(vols[-lookback - 1:-1]) / float(lookback)
    return (vols[-1] / base) if base > 0 else None


def _stack_sep_now(series: Mapping[str, Any]) -> Optional[float]:
    """Separation of the SMA7/SMA99 stack, in percent — MVRTP's own geometry."""
    closes = _closes(series)
    fast, slow = _sma(closes, 7), _sma(closes, 99)
    if fast is None or slow is None or slow <= 0:
        return None
    return (fast - slow) / slow * 100.0


def _extension_now(series: Mapping[str, Any]) -> Optional[float]:
    """How far the last close sits from the slow MA, in percent."""
    closes = _closes(series)
    slow = _sma(closes, 25)
    # `len(closes) == 0`, never `not closes`: the data store holds numpy arrays
    # and truthiness on one RAISES. That killed eight features silently on
    # 2026-07-14 and is a hard limit in this repo, enforced by
    # tests/test_no_numpy_truthiness_regression.py — which is what caught this
    # line.
    if slow is None or slow <= 0 or len(closes) == 0:
        return None
    return (closes[-1] - slow) / slow * 100.0


#: Feature name → how to read it NOW off the trigger series. Keyed by the
#: registry's own names so the two cannot drift: a feature renamed in
#: `entry_features` simply stops matching and reports `not_recomputable`, which
#: is visible, rather than silently reading the wrong column.
_RECOMPUTE: Dict[str, Callable[[Mapping[str, Any]], Optional[float]]] = {
    "rsi_at_entry": _rsi_now,
    "pullback_vol_ratio": _vol_ratio_now,
    "vol_ratio_at_trigger": _vol_ratio_now,
    "stack_sep_pct": _stack_sep_now,
    "sep_15m_pct": _stack_sep_now,
    "extension_pct": _extension_now,
}


def _moved(at_entry: Any, now: Any) -> Optional[float]:
    """Change in the feature's own units. Descriptive, never a verdict.

    Returns ``None`` unless BOTH sides are numeric — a bool is not a number
    here, because "True moved to False" is a fact the model should read as a
    fact rather than as ``-1.0``.
    """
    if isinstance(at_entry, bool) or isinstance(now, bool):
        return None
    try:
        return round(float(now) - float(at_entry), 6)
    except Exception:  # noqa: BLE001
        return None


def build(
    *,
    setup_class: str,
    signal: Any,
    entry_row: Optional[Mapping[str, Any]],
    series: Optional[Mapping[str, Any]],
) -> Dict[str, Any]:
    """The premise block for one position, or a named refusal.

    ``entry_row`` is the `entry_features` stamp for this signal — the record of
    what was true when the trade was taken. It is looked up rather than
    recomputed for the reason that lane exists: the entry regime, the entry
    order book and the entry level book are knowable only at entry, and this
    module must never hand the model a present-tense reading wearing an
    entry-time label.
    """
    try:
        from src import entry_features as _ef

        setup = str(setup_class or "").upper()
        thesis = thesis_for(setup)
        if not thesis:
            # Refused, not defaulted. A generic sentence over an unknown path is
            # the fallback that makes a miss invisible.
            return {"refusal": REFUSE_NO_THESIS, "setup_class": setup}

        declared = _ef.features_for(setup)
        stamped = dict(entry_row or {})
        conditions: List[Dict[str, Any]] = []
        for name in declared:
            key = f"ef_{name}" if f"ef_{name}" in stamped else name
            at_entry = stamped.get(key) if stamped else None
            recompute = _RECOMPUTE.get(name)
            now: Any = None
            now_reason: Optional[str] = None
            if recompute is not None and series is not None:
                try:
                    now = recompute(series)
                except Exception as exc:  # noqa: BLE001
                    fail_open.record(f"ai_governor_premise.recompute:{name}", exc)
                    now = None
                if now is None:
                    now_reason = WHY_NOT_RECOMPUTABLE
                else:
                    now = round(float(now), 6)
            else:
                now_reason = WHY_NOT_RECOMPUTABLE
            # Three states, not two. The first cut set a reason only when the
            # whole stamp was missing, so a feature simply absent from a stamp
            # that exists came out as `null` with no cause — a blank with no
            # caption, in the block whose entire job is telling the model what
            # it can and cannot see.
            if at_entry is not None:
                entry_reason = None
            elif not stamped:
                entry_reason = WHY_NO_ENTRY_STAMP
            else:
                entry_reason = WHY_FEATURE_NOT_STAMPED
            conditions.append({
                "name": name,
                "at_entry": at_entry,
                "at_entry_reason": entry_reason,
                "now": now,
                "now_reason": now_reason,
                "moved": _moved(at_entry, now),
            })

        recomputed = sum(1 for c in conditions if c["now"] is not None)
        return {
            "thesis": thesis,
            "conditions": conditions,
            # Coverage beside the block, never instead of it. A premise where
            # nothing could be re-read is still worth publishing — the model
            # learns what the trade required — but it must not read as a live
            # check when it is an entry-time record.
            "conditions_n": len(conditions),
            "conditions_recomputed_now": recomputed,
            "entry_stamp": bool(stamped),
            "note": (
                "at_entry is the entry-feature stamp; now is recomputed from the "
                "trigger series where that is possible and is null with a reason "
                "where it is not. `moved` is the change in the feature's own "
                "units and is NOT a judgement: no threshold here was chosen from "
                "this window."
            ),
        }
    except Exception as exc:  # noqa: BLE001 — a premise is never worth a raise
        fail_open.record("ai_governor_premise.build", exc)
        return {"refusal": "error"}
