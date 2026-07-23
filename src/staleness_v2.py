"""Dispatch-staleness V2 — geometry-aware drift evaluation (2026-07-23).

Why V1 is being re-derived: the flat ``DISPATCH_STALENESS_MAX_DRIFT_PCT``
(0.5% either way) is the highest-volume dispatch suppressor and carries a
measured-negative verdict in the suppression audit (1225 suppressions, 49.7%
would-win, EV −0.19R, 318R missed).  A flat percentage ignores the two things
that actually decide whether a drifted entry is still tradeable:

* **The candidate's own geometry.**  0.5% of drift consumes most of a tight
  scalp stop but is noise against a wide mover stop.  V2 measures drift in the
  candidate's own R-space: as a fraction of the entry→SL distance (adverse
  side) or of the entry→TP1 distance (favourable side).  Because every
  evaluator owns its SL/TP geometry (B7) and most stops are ATR/structure
  scaled, this makes the gate volatility-aware with zero new data reads.
* **The drift's direction.**  Drift toward the stop compresses the remaining
  risk room — the original 2026-05-07 pathology ("entry says 626.85, price
  already at the 631.86 SL") is the extreme of this side.  Drift toward the
  target is a *chase*: the trade still fills, but the remaining reward no
  longer pays for the full risk.  The two failure modes deserve separate
  bounds; V1 conflated them.

Pure functions only — the scanner owns wiring, price lookup, counters and the
shadow stamping.  Dark-first per production doctrine: ``ENABLED`` turns on
shadow evaluation (V1 keeps deciding), ``LIVE`` (default OFF, owner sign-off)
lets V2 replace V1 as the deciding gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Drift-direction labels (also used in scanner counters / logs).
DRIFT_NONE = "none"
DRIFT_TOWARD_SL = "toward_sl"
DRIFT_TOWARD_TP = "toward_tp"


@dataclass(frozen=True)
class StalenessV2Params:
    """Tunable envelope, mirroring ``context_emission_policy.PolicyParams``."""

    enabled: bool
    live: bool
    toward_sl_max_frac: float
    toward_tp_max_frac: float

    @staticmethod
    def from_config() -> "StalenessV2Params":
        """Effective params: ops runtime tunables overlaid on config defaults."""
        from config import (
            DISPATCH_STALENESS_V2_ENABLED,
            DISPATCH_STALENESS_V2_LIVE,
            DISPATCH_STALENESS_V2_TOWARD_SL_MAX_FRAC,
            DISPATCH_STALENESS_V2_TOWARD_TP_MAX_FRAC,
        )

        def _rt(key: str, default: object) -> object:
            try:
                from src import runtime_tunables as _r

                val = _r.get(key)
                return val if val is not None else default
            except Exception:
                return default

        return StalenessV2Params(
            enabled=bool(_rt("dispatch_staleness_v2_enabled", DISPATCH_STALENESS_V2_ENABLED)),
            live=bool(_rt("dispatch_staleness_v2_live", DISPATCH_STALENESS_V2_LIVE)),
            toward_sl_max_frac=max(
                0.0,
                float(_rt("dispatch_staleness_v2_toward_sl_max_frac", DISPATCH_STALENESS_V2_TOWARD_SL_MAX_FRAC)),  # type: ignore[arg-type]
            ),
            toward_tp_max_frac=max(
                0.0,
                float(_rt("dispatch_staleness_v2_toward_tp_max_frac", DISPATCH_STALENESS_V2_TOWARD_TP_MAX_FRAC)),  # type: ignore[arg-type]
            ),
        )


@dataclass(frozen=True)
class StalenessV2Decision:
    """One candidate's V2 verdict at dispatch time.

    ``fresh=True`` means V2 would let the dispatch proceed.  ``drift_frac`` is
    the drift expressed in the bound's own denominator (entry→SL distance for
    adverse drift, entry→TP1 distance for favourable drift), so a value of 1.0
    always reads "the full budget of that side is consumed".
    """

    fresh: bool
    drift_direction: str
    drift_frac: float
    reason: str


def evaluate(
    *,
    side: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    current_price: float,
    params: Optional[StalenessV2Params] = None,
) -> StalenessV2Decision:
    """Geometry-aware freshness verdict for one candidate at dispatch time.

    Fail-open by construction: degenerate geometry (missing / inverted SL or
    TP, non-positive prices) yields ``fresh=True`` with a diagnostic reason —
    identical to V1's behaviour on unreadable inputs, so V2 can never be
    *stricter* than V1 merely because a field was unparseable.
    """
    p = params or StalenessV2Params.from_config()
    side_u = str(side or "").upper()
    entry = float(entry or 0.0)
    stop_loss = float(stop_loss or 0.0)
    tp1 = float(tp1 or 0.0)
    current_price = float(current_price or 0.0)

    if side_u not in ("LONG", "SHORT") or min(entry, current_price) <= 0:
        return StalenessV2Decision(True, DRIFT_NONE, 0.0, "unreadable_inputs")

    sl_distance = abs(entry - stop_loss)
    tp_distance = abs(tp1 - entry)
    sl_valid = stop_loss > 0 and sl_distance > 0 and (
        (side_u == "LONG" and stop_loss < entry) or (side_u == "SHORT" and stop_loss > entry)
    )
    tp_valid = tp1 > 0 and tp_distance > 0 and (
        (side_u == "LONG" and tp1 > entry) or (side_u == "SHORT" and tp1 < entry)
    )

    # Signed drift: positive = toward the target, negative = toward the stop.
    drift = current_price - entry if side_u == "LONG" else entry - current_price
    if drift == 0.0:
        return StalenessV2Decision(True, DRIFT_NONE, 0.0, "no_drift")

    if drift < 0:
        if not sl_valid:
            return StalenessV2Decision(True, DRIFT_TOWARD_SL, 0.0, "degenerate_sl_geometry")
        frac = -drift / sl_distance
        if frac > p.toward_sl_max_frac:
            return StalenessV2Decision(
                False, DRIFT_TOWARD_SL, frac,
                f"stop_room_consumed {frac:.2f}>{p.toward_sl_max_frac:.2f}",
            )
        return StalenessV2Decision(True, DRIFT_TOWARD_SL, frac, "within_sl_budget")

    if not tp_valid:
        return StalenessV2Decision(True, DRIFT_TOWARD_TP, 0.0, "degenerate_tp_geometry")
    frac = drift / tp_distance
    if frac > p.toward_tp_max_frac:
        return StalenessV2Decision(
            False, DRIFT_TOWARD_TP, frac,
            f"chased_toward_target {frac:.2f}>{p.toward_tp_max_frac:.2f}",
        )
    return StalenessV2Decision(True, DRIFT_TOWARD_TP, frac, "within_tp_budget")
