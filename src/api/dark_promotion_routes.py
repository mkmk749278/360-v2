"""Dark → live promotion rules — the owner's control surface for the lane.

Three owner-gated endpoints behind ops Control → Promotions:

* ``GET  /api/admin/dark-promotions``    — every rule, plus the vocabulary the
  form needs (which gates, regimes and sessions the ledger has actually seen)
  and the live counters.
* ``POST /api/admin/dark-promotions``    — create or replace one path's rule.
* ``DELETE /api/admin/dark-promotions/{setup_class}`` — remove one.

The read endpoint is deliberately more than a dump of the registry. A control
that offers a free-text regime box invites a rule keyed on a label the engine
never emits — enabled, plausible-looking, matching nothing forever, and
indistinguishable on screen from a rule that is simply waiting for a setup to
appear. So the vocabulary comes from **the rows themselves**: ops renders the
options this engine has actually stamped, and a value the ledger has never
produced cannot be selected by accident.

That also settles where the option list lives. It is derived from the dark
ledger on each read, not enumerated here and not mirrored in ops — the fix for
a drifting mirror is not a second mirror, and a hand-kept list of regimes is
silent by construction on the next label the detector learns.

Not a hot path: owner-initiated, at ops page-load rates, so no caching is
needed (Cost Discipline). The engine-side read that *is* hot — ``decide`` at
the divert site — goes through ``dark_promotion``'s in-memory registry and
never touches this module.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from src import dark_promotion
from src.utils import get_logger

log = get_logger("api.dark_promotion_routes")


class DarkPromotionRuleRequest(BaseModel):
    """One path's promotion conditions.

    Every list is an explicit allow-list. ``["*"]`` means "any value of this
    dimension"; ``[]`` means the rule matches nothing and is inert. The
    permissive case has to be typed, so it is always somebody's decision rather
    than a field left blank.
    """

    setup_class: str = Field(..., description="Path this rule governs, e.g. LIQUIDITY_SWEEP_REVERSAL")
    enabled: bool = Field(False, description="The per-path master switch")
    gates: List[str] = Field(default_factory=list, description="Dark gates that may be carried into the live feed")
    regimes: List[str] = Field(default_factory=lambda: [dark_promotion.ANY])
    sessions: List[str] = Field(default_factory=lambda: [dark_promotion.ANY])
    direction: str = Field(dark_promotion.DIR_ANY, description="any | long | short | with_trend | counter_trend")
    min_confidence: Optional[float] = None
    max_per_day: int = Field(
        dark_promotion.DEFAULT_MAX_PER_DAY,
        description="Blast-radius cap: promotions per UTC day for this rule",
    )
    note: str = ""
    updated_by: str = ""


def _vocabulary(ledger_rows: List[dict]) -> Dict[str, List[str]]:
    """The dimension values this engine has actually produced.

    Read off the ledger rather than declared, so a rule can only ever be built
    from labels that exist. Sorted for a stable form; the counts ride along
    because "this gate has 20 rows" and "this gate has 1" should not look the
    same in a dropdown the owner is about to act on.
    """
    gates: Dict[str, int] = {}
    regimes: Dict[str, int] = {}
    sessions: Dict[str, int] = {}
    setups: Dict[str, int] = {}
    for row in ledger_rows:
        gate = str(row.get("dark_gate") or "")
        if gate:
            gates[gate] = gates.get(gate, 0) + 1
        regime = str(row.get("regime") or "")
        if regime:
            regimes[regime] = regimes.get(regime, 0) + 1
        ctx = str(row.get("context_key") or "")
        if ctx:
            # `session/phase/volatility/rotation` — the session is the first
            # component and the only one this control filters on. Parsed rather
            # than stored separately because `market_context` owns the key's
            # shape and a second copy of it here would be one more mirror.
            session = ctx.split("/")[0].strip()
            if session:
                sessions[session] = sessions.get(session, 0) + 1
        setup = str(row.get("setup_class") or "")
        if setup:
            setups[setup] = setups.get(setup, 0) + 1
    return {
        "gates": sorted(gates),
        "regimes": sorted(regimes),
        "sessions": sorted(sessions),
        "setups": sorted(setups),
        "counts": {
            "gates": gates,
            "regimes": regimes,
            "sessions": sessions,
            "setups": setups,
        },
    }


def register(app: FastAPI, *, owner_required: Callable) -> None:
    """Register the promotion-rule routes."""

    def _ledger_rows() -> List[dict]:
        try:
            from src import dark_emission

            return dark_emission.get_ledger().rows()
        except Exception as exc:  # pragma: no cover - defensive
            log.warning("dark ledger unreadable for promotion vocabulary: {}", exc)
            return []

    @app.get(
        "/api/admin/dark-promotions",
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def get_dark_promotions() -> Dict[str, Any]:
        """Every rule, the vocabulary a rule can be built from, and the counters.

        ``master_enabled`` and ``dark_lane_enabled`` are published together
        because a rule is inert if either is off, for entirely different
        reasons — the first means promotion is disarmed, the second means the
        rows it would promote are being killed by the gate upstream and never
        reach the decision at all. An operator seeing one switch without the
        other cannot tell which half is missing.
        """
        snap = dark_promotion.snapshot()
        snap["vocabulary"] = _vocabulary(_ledger_rows())
        # Path retirement rides the same payload deliberately: it is the same
        # decision pointing the other way (live -> dark, where promotion is
        # dark -> live), and an operator who can arm one without seeing the
        # other cannot tell why a path produces nothing. Two endpoints would be
        # two places for the next reader to forget about.
        try:
            from src import path_retirement

            snap["path_retirement"] = path_retirement.snapshot()
        except Exception as exc:  # noqa: BLE001
            snap["path_retirement"] = {"error": str(exc)}
        return snap

    @app.post(
        "/api/admin/dark-promotions",
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def set_dark_promotion(req: DarkPromotionRuleRequest) -> Dict[str, Any]:
        """Create or replace one path's rule.

        Returns the **stored** rule, not the request. The normaliser upper-cases
        tokens, drops an unrecognised direction and clamps the cap, so echoing
        the request would report a setting the engine will not enforce — the
        exact defect ``/api/admin/users/exit-mechanism`` was written to avoid,
        and the reason its companion lookup had to learn to return the field.
        """
        if not str(req.setup_class or "").strip():
            raise HTTPException(status_code=422, detail="setup_class is required")
        if req.direction not in dark_promotion.DIRECTIONS:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"direction must be one of {list(dark_promotion.DIRECTIONS)}"
                ),
            )
        try:
            stored = dark_promotion.set_rule(
                dark_promotion.PromotionRule(
                    setup_class=req.setup_class,
                    enabled=req.enabled,
                    gates=req.gates,
                    regimes=req.regimes,
                    sessions=req.sessions,
                    direction=req.direction,
                    min_confidence=req.min_confidence,
                    max_per_day=req.max_per_day,
                    note=req.note,
                    updated_by=req.updated_by,
                )
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return {
            "ok": True,
            "rule": stored.to_dict(),
            "master_enabled": dark_promotion.master_enabled(),
            "dark_lane_enabled": dark_promotion.snapshot()["dark_lane_enabled"],
        }

    @app.delete(
        "/api/admin/dark-promotions/{setup_class}",
        tags=["admin"],
        dependencies=[Depends(owner_required)],
    )
    async def delete_dark_promotion(setup_class: str) -> Dict[str, Any]:
        removed = dark_promotion.delete_rule(setup_class)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"no promotion rule for {setup_class}",
            )
        return {"ok": True, "removed": setup_class.upper()}
