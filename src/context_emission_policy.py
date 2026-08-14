"""Context-adaptive emission policy — the Layer-C → emission consumer.

The engine already *measures* every strategy per market context (Layer C,
``strategy_edge.py``) and the allocator (Layer D, ``strategy_allocator.py``)
already computes which strategies it would run in the current context — but that
recommendation is ``RECOMMENDATION_ONLY``, consumed by nothing.  Meanwhile the
single, context-blind confidence floor (``min_confidence`` in the scanner) decides
emission for *every* strategy, so the two highest-scoring paths (MTP, FAR)
dominate emission while paths with a measured STRONG edge in a specific context
(QUIET_COMPRESSION_BREAK +2.21R OVERLAP/QUIET/COMPRESSED, SR_FLIP_RETEST +1.29R
LONDON/VOLATILE_EXPANSION/CASCADE) emit ~zero because they rarely clear 65.

This module is the wire that closes that gap.  It turns the global floor into a
**per-``(strategy × context)`` floor driven live by the measured edge matrix**:

  * STRONG cell   → *relax* the floor toward the quality anchor (emit the path's
                    best setups in the context where it is measured to win);
  * POSITIVE cell → relax half as much;
  * NEGATIVE cell → *hard-suppress* (never emit this path in a context it loses);
  * cold/thin/FLAT→ leave the global floor untouched — today's proven behaviour,
                    never guess on an unmeasured cell.

It is the two-sided generalisation of the S67 RANGE_FADE context gate: that gate
is exactly the NEGATIVE/thin *suppress* side of this policy for one strategy.

**DARK by default** (production doctrine).  ``CONTEXT_EMISSION_POLICY_ENABLED``
turns on measurement (a cheap O(1) stamp that changes nothing);
``CONTEXT_EMISSION_LIVE`` (the ``context_emission_live`` runtime tunable) turns on
live application after owner sign-off on a shadow window.

Pure functions over the already-warm ``StrategyEdgeStore`` — no I/O, no new
Firestore/network read on any hot path (Cost Discipline).  Fail-open toward the
base floor: any lookup error yields *today's* behaviour (no relaxation, no
suppression) and is surfaced by the caller via ``fail_open.record``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from src.strategy_edge import (
    VERDICT_INSUFFICIENT,
    VERDICT_NEGATIVE,
    VERDICT_POSITIVE,
    VERDICT_STRONG,
)

# Live→matrix control-arm aliases.  Freshly-graduated paths (RANGE_FADE,
# MEAN_REVERT) emit too rarely to have their own emitted stats, so their richer
# ungated shadow arm is the measurement source — identical to how the S67
# RANGE_FADE gate reads SHADOW_RANGE_FADE.  Every other strategy is measured
# under its own name (its suppressed counterfactuals + emitted outcomes populate
# the cell directly).
_CONTROL_ARM = {
    "RANGE_FADE": "SHADOW_RANGE_FADE",
    "MEAN_REVERT": "SHADOW_MEAN_REVERT",
}

# Divergence classes — how the policy's decision compares to today's global floor.
DIV_AGREE_EMIT = "agree_emit"
DIV_AGREE_SUPPRESS = "agree_suppress"
DIV_RELAX = "relax"       # policy would emit; the global floor suppresses (missed edge)
DIV_TIGHTEN = "tighten"   # policy would suppress; the global floor emits (a losing cell)

# W5 — the only dispatch gates the edge matrix may override.  Both carry a
# measured-negative suppression verdict (2026-07-23 audit: dispatch_staleness
# EV −0.19R n=1225 · level_still_in_play EV −0.06R n=989).  Safety gates
# (kill switch, blast radius, data_stale, dispatch_cooldown) are deliberately
# NOT in this tuple and must never be added without owner sign-off.
OVERRIDABLE_GATES = ("dispatch_staleness", "level_still_in_play")


@dataclass(frozen=True)
class PolicyParams:
    """Tunable envelope for the emission policy (mirrors ``AllocatorLimits``)."""

    enabled: bool
    live: bool
    quality_anchor: float
    strong_relax: float
    positive_relax: float
    min_samples: int
    suppress_negative: bool
    cohort_aware: bool = False
    # W5 — edge-matrix authority over the audited-negative dispatch gates
    # (OVERRIDABLE_GATES).  ``gate_override_enabled`` turns on the shadow
    # measurement; ``gate_override_live`` (dark, owner sign-off) applies it.
    gate_override_enabled: bool = False
    gate_override_live: bool = False
    # Layer-G per-strategy overrides: {STRATEGY -> {suppress_negative, min_samples}}.
    # Set by the autonomous emission controller; each key may be None (follow the
    # global value above). Loaded once per params build from the in-memory
    # controller store (O(1), no hot-path I/O); empty when the controller is off.
    per_strategy: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # Warmup allowance — see ``_warmup_take`` and the INSUFFICIENT branch of
    # ``evaluate_emission``.  Breaks the absorbing state where an unmeasured
    # cell cannot emit, so never accumulates the samples that would measure it.
    warmup_enabled: bool = True
    warmup_target: int = 30
    warmup_daily_cap: int = 12

    @staticmethod
    def from_config() -> "PolicyParams":
        """Effective params: ops runtime tunables overlaid on the env/config defaults.

        Every knob is live-controllable from ops (Control → Signal gating); a
        tunable read that fails (registry not built, e.g. in a unit test) falls
        back to the frozen config default, so the policy is always well-defined.
        """
        from config import (
            CONTEXT_EMISSION_COHORT_AWARE,
            CONTEXT_EMISSION_GATE_OVERRIDE_ENABLED,
            CONTEXT_EMISSION_GATE_OVERRIDE_LIVE,
            CONTEXT_EMISSION_LIVE,
            CONTEXT_EMISSION_MIN_SAMPLES,
            CONTEXT_EMISSION_POLICY_ENABLED,
            CONTEXT_EMISSION_POSITIVE_RELAX,
            CONTEXT_EMISSION_QUALITY_ANCHOR,
            CONTEXT_EMISSION_STRONG_RELAX,
            CONTEXT_EMISSION_WARMUP_DAILY_CAP,
            CONTEXT_EMISSION_WARMUP_ENABLED,
            CONTEXT_EMISSION_WARMUP_TARGET,
            CONTEXT_EMISSION_SUPPRESS_NEGATIVE,
        )

        def _rt(key: str, default: object) -> object:
            try:
                from src import runtime_tunables as _r

                val = _r.get(key)
                return val if val is not None else default
            except Exception:
                return default

        # Layer-G per-strategy overrides — only when the controller is enabled
        # (master switch). In-memory read; failures fall back to no overrides
        # (i.e. today's global-only behaviour), never to a guess.
        per_strategy: Dict[str, Dict[str, Any]] = {}
        try:
            if bool(_rt("emission_controller_enabled", True)):
                from src.emission_controller_store import get_emission_controller_store

                per_strategy = get_emission_controller_store().overrides_snapshot()
        except Exception:
            per_strategy = {}

        return PolicyParams(
            enabled=bool(_rt("context_emission_enabled", CONTEXT_EMISSION_POLICY_ENABLED)),
            live=bool(_rt("context_emission_live", CONTEXT_EMISSION_LIVE)),
            quality_anchor=float(_rt("context_emission_quality_anchor", CONTEXT_EMISSION_QUALITY_ANCHOR)),  # type: ignore[arg-type]
            strong_relax=max(0.0, float(_rt("context_emission_strong_relax", CONTEXT_EMISSION_STRONG_RELAX))),  # type: ignore[arg-type]
            positive_relax=max(0.0, float(_rt("context_emission_positive_relax", CONTEXT_EMISSION_POSITIVE_RELAX))),  # type: ignore[arg-type]
            min_samples=max(1, int(_rt("context_emission_min_samples", CONTEXT_EMISSION_MIN_SAMPLES))),  # type: ignore[call-overload]
            suppress_negative=bool(_rt("context_emission_suppress_negative", CONTEXT_EMISSION_SUPPRESS_NEGATIVE)),
            cohort_aware=bool(_rt("context_emission_cohort_aware", CONTEXT_EMISSION_COHORT_AWARE)),
            gate_override_enabled=bool(
                _rt("context_emission_gate_override_enabled", CONTEXT_EMISSION_GATE_OVERRIDE_ENABLED)
            ),
            gate_override_live=bool(
                _rt("context_emission_gate_override_live", CONTEXT_EMISSION_GATE_OVERRIDE_LIVE)
            ),
            per_strategy=per_strategy,
            warmup_enabled=bool(_rt("context_emission_warmup_enabled", CONTEXT_EMISSION_WARMUP_ENABLED)),
            warmup_target=max(1, int(_rt("context_emission_warmup_target", CONTEXT_EMISSION_WARMUP_TARGET))),  # type: ignore[call-overload]
            warmup_daily_cap=max(0, int(_rt("context_emission_warmup_daily_cap", CONTEXT_EMISSION_WARMUP_DAILY_CAP))),  # type: ignore[call-overload]
        )

    def resolve_suppress_negative(self, strategy: str) -> bool:
        """Effective suppress-NEGATIVE for ``strategy`` — the controller's per-
        strategy override when set, else the global value."""
        ov = self.per_strategy.get((strategy or "").upper()) or {}
        v = ov.get("suppress_negative")
        return self.suppress_negative if v is None else bool(v)

    def resolve_min_samples(self, strategy: str) -> int:
        """Effective relax sample-floor for ``strategy`` — controller override when
        set, else the global value."""
        ov = self.per_strategy.get((strategy or "").upper()) or {}
        v = ov.get("min_samples")
        return self.min_samples if v is None else int(v)


#: Warmup grants issued today, per strategy: ``{"day": "YYYY-MM-DD", "counts": {}}``.
#: In-memory and O(1) — this is consulted on the scanner hot path, so it must add
#: no I/O (Cost Discipline).  Losing it on restart is deliberate and safe: the
#: cap re-arms, which can only ever *grant* more, and the grant is already
#: bounded by ``warmup_target`` on the cell's own sample count.
_WARMUP_GRANTS: Dict[str, Any] = {"day": "", "counts": {}}


def _warmup_take(strategy: str, cap: int) -> bool:
    """Consume one warmup grant for ``strategy`` today. False when capped.

    The cap counts **floor relaxations granted**, not signals delivered — the
    router drops most of what it dequeues, so grants over-count delivery.  That
    is the conservative direction for a blast-radius bound (it caps sooner than
    a delivery count would) and it is the number this module can actually
    observe: "emitted means DELIVERED, and only the router knows that".
    """
    if cap <= 0:
        return False
    from datetime import datetime, timezone

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if _WARMUP_GRANTS.get("day") != day:
        _WARMUP_GRANTS["day"] = day
        _WARMUP_GRANTS["counts"] = {}
    key = (strategy or "").upper()
    counts = _WARMUP_GRANTS["counts"]
    used = int(counts.get(key, 0))
    if used >= cap:
        return False
    counts[key] = used + 1
    return True


@dataclass(frozen=True)
class EmissionDecision:
    """What the policy would do for one candidate.

    ``effective_floor`` is the confidence bar to apply *when the policy is live*;
    ``suppressed`` overrides it (a NEGATIVE cell never emits regardless of score).
    In dark mode the scanner reads these fields only to stamp the would-be
    decision — live output is unchanged.
    """

    effective_floor: float
    verdict: str
    edge_r: Optional[float]
    n: int
    matrix_strategy: str
    suppressed: bool
    relaxed: float
    reason: str


def _resolve_matrix_strategy(strategy: str, store: object) -> str:
    """Own name, or the richer shadow control arm if the own cell is thin.

    The alias is only consulted when the strategy has a mapped shadow arm; a
    strategy measured under its own name always uses it.
    """
    alias = _CONTROL_ARM.get(strategy.upper())
    return alias if alias else strategy


def _lookup_cell(
    strategy: str,
    context_key: str,
    cohort: str,
    store: object,
    p: "PolicyParams",
) -> tuple:
    """Resolve the measurement cell for ``strategy`` in ``context_key``.

    Applies the Phase-5 cohort refinement and the shadow-control-arm fallback
    exactly as ``effective_floor`` always has; returns
    ``(lookup_name, effective_context, verdict, edge_r, n)``.
    """
    effective_ctx = context_key
    if p.cohort_aware and cohort:
        from src.pair_cohort import cohort_context_key

        cohort_ctx = cohort_context_key(context_key, cohort)
        alias = _CONTROL_ARM.get(strategy.upper())
        cohort_has_data = (
            store.verdict(strategy, cohort_ctx) != "INSUFFICIENT_DATA"  # type: ignore[attr-defined]
            or (
                alias is not None
                and store.verdict(alias, cohort_ctx) != "INSUFFICIENT_DATA"  # type: ignore[attr-defined]
            )
        )
        if cohort_has_data:
            effective_ctx = cohort_ctx

    matrix_strategy = _resolve_matrix_strategy(strategy, store)
    # Prefer the strategy's own cell; fall back to the shadow control arm only
    # when own data is thin (INSUFFICIENT), so a path with real emitted outcomes
    # is judged on itself.
    own_verdict = store.verdict(strategy, effective_ctx)  # type: ignore[attr-defined]
    if matrix_strategy != strategy and own_verdict == "INSUFFICIENT_DATA":
        lookup = matrix_strategy
    else:
        lookup = strategy
    verdict = store.verdict(lookup, effective_ctx)  # type: ignore[attr-defined]
    edge_r = store.edge_r(lookup, effective_ctx)  # type: ignore[attr-defined]
    n = store.sample_count(lookup, effective_ctx)  # type: ignore[attr-defined]
    return lookup, effective_ctx, verdict, edge_r, n


def effective_floor(
    strategy: str,
    context_key: str,
    base_floor: float,
    *,
    cohort: str = "",
    store: Optional[object] = None,
    params: Optional[PolicyParams] = None,
) -> EmissionDecision:
    """Compute the edge-matrix-driven emission floor for ``strategy`` in ``context_key``.

    Missing inputs (no strategy / no context) return a base-floor decision.  A
    store error propagates so the scanner caller fails open to the base floor and
    records it via ``fail_open.record`` (the S67 RANGE_FADE-gate pattern) — an
    unverifiable edge must page, not silently relax or suppress.
    """
    p = params or PolicyParams.from_config()
    base = float(base_floor)
    anchor = min(p.quality_anchor, base)  # never *raise* the floor via the anchor

    def _base(reason: str, verdict: str = "UNKNOWN", matrix_strategy: str = "") -> EmissionDecision:
        return EmissionDecision(
            effective_floor=base,
            verdict=verdict,
            edge_r=None,
            n=0,
            matrix_strategy=matrix_strategy or strategy,
            suppressed=False,
            relaxed=0.0,
            reason=reason,
        )

    if not strategy or not context_key:
        return _base("no_context")

    if store is None:
        from src.strategy_edge import get_strategy_edge_store

        store = get_strategy_edge_store()

    lookup, context_key, verdict, edge_r, n = _lookup_cell(
        strategy, context_key, cohort, store, p
    )

    if verdict == VERDICT_NEGATIVE:
        if p.resolve_suppress_negative(strategy):
            return EmissionDecision(
                effective_floor=base,
                verdict=verdict,
                edge_r=edge_r,
                n=n,
                matrix_strategy=lookup,
                suppressed=True,
                relaxed=0.0,
                reason=f"negative_suppress edge={edge_r:+.3f}R n={n}"
                if edge_r is not None
                else f"negative_suppress n={n}",
            )
        return _base(f"negative_no_suppress n={n}", verdict, lookup)

    if verdict in (VERDICT_STRONG, VERDICT_POSITIVE):
        eff_min_samples = p.resolve_min_samples(strategy)
        if n < eff_min_samples:
            return _base(f"{verdict.lower()}_thin n={n}<{eff_min_samples}", verdict, lookup)
        relax_cap = p.strong_relax if verdict == VERDICT_STRONG else p.positive_relax
        relaxed = min(relax_cap, max(0.0, base - anchor))
        return EmissionDecision(
            effective_floor=base - relaxed,
            verdict=verdict,
            edge_r=edge_r,
            n=n,
            matrix_strategy=lookup,
            suppressed=False,
            relaxed=relaxed,
            reason=f"{verdict.lower()}_relax {relaxed:.1f}pts edge={edge_r:+.3f}R n={n}"
            if edge_r is not None
            else f"{verdict.lower()}_relax {relaxed:.1f}pts n={n}",
        )

    # ------------------------------------------------------------------ #
    # Warmup: let an UNMEASURED cell deliver, so it can become a measured one.
    #
    # Owner, 2026-08-14: *"let them deliver first, don't wait for 20 to 30,
    # after reaching desirable count then start sort out."*
    #
    # The absorbing state this breaks: ``strategy_edge`` returns INSUFFICIENT
    # while ``edge is None``, and edge is None until the sample floor is met.
    # So a starved path carries no verdict, never earns the relax, rarely
    # clears the floor, rarely delivers — and therefore never accumulates the
    # samples that would give it a verdict.  LSR sat at ~1 delivered row in 7
    # days against MOVER_TREND_PULLBACK's 134 while reading +0.984%/row in the
    # dark lane.  Same shape as ``cohort_edge`` (#816's sibling): a gate whose
    # evidence only arrives from what it lets through can never release.
    #
    # Three bounds, and each one is load-bearing:
    #   * **INSUFFICIENT only.**  FLAT is a *measured* neutral — it has a
    #     verdict and the samples behind it, so it is not owed a warmup.  And
    #     NEGATIVE returned above, so this can never resurrect a cell that was
    #     measured bad: warmup is for the unmeasured, never for the disproven.
    #   * **``warmup_target``** — the "desirable count".  Past it the cell is
    #     on its own; the edge rules above take over and start sorting out.
    #   * **``warmup_daily_cap``** — per strategy per day, because without it
    #     this is an unbounded loosening of what subscribers receive, on a book
    #     whose 30d result is not distinguishable from zero.
    #
    # A capped grant is its OWN reason string, never folded into ``neutral``:
    # "the allowance is spent" and "this cell is not owed one" are different
    # facts with different next moves.
    if verdict == VERDICT_INSUFFICIENT and p.warmup_enabled and n < p.warmup_target:
        if _warmup_take(strategy, p.warmup_daily_cap):
            relaxed = min(p.positive_relax, max(0.0, base - anchor))
            return EmissionDecision(
                effective_floor=base - relaxed,
                verdict=verdict,
                edge_r=edge_r,
                n=n,
                matrix_strategy=lookup,
                suppressed=False,
                relaxed=relaxed,
                reason=f"warmup_relax {relaxed:.1f}pts n={n}<{p.warmup_target}",
            )
        return _base(f"warmup_capped n={n}<{p.warmup_target}", verdict, lookup)

    # FLAT / measured-but-neutral / unknown → global floor, unchanged.
    return _base(f"neutral n={n}", verdict, lookup)


@dataclass(frozen=True)
class GateOverrideDecision:
    """W5 — whether measured cell evidence outranks an OVERRIDABLE_GATES block.

    ``would_override=True`` means: this candidate's (strategy, context) cell is
    measured STRONG on adequate sample, so the audited-negative heuristic gate
    should yield.  In shadow mode the scanner stamps the would-be rescue as an
    ``X@GOV`` arm; in live mode (``gate_override_live``) it emits.
    """

    would_override: bool
    verdict: str
    edge_r: Optional[float]
    n: int
    matrix_strategy: str
    reason: str


def gate_override(
    strategy: str,
    context_key: str,
    *,
    cohort: str = "",
    store: Optional[object] = None,
    params: Optional[PolicyParams] = None,
) -> GateOverrideDecision:
    """Should measured cell evidence override an OVERRIDABLE_GATES suppression?

    The bar is deliberately higher than the confidence-floor relax: STRONG only
    (never POSITIVE), positive measured edge, and the same per-strategy sample
    floor the relax side uses.  A store error propagates so the scanner caller
    fails open to the gate's own decision and records it via ``fail_open`` —
    an unverifiable edge must never override a live gate.
    """
    p = params or PolicyParams.from_config()

    def _no(reason: str, verdict: str = "UNKNOWN", edge: Optional[float] = None, n: int = 0,
            matrix_strategy: str = "") -> GateOverrideDecision:
        return GateOverrideDecision(
            would_override=False,
            verdict=verdict,
            edge_r=edge,
            n=n,
            matrix_strategy=matrix_strategy or strategy,
            reason=reason,
        )

    if not p.gate_override_enabled:
        return _no("disabled")
    if not strategy or not context_key:
        return _no("no_context")

    if store is None:
        from src.strategy_edge import get_strategy_edge_store

        store = get_strategy_edge_store()

    lookup, _ctx, verdict, edge_r, n = _lookup_cell(strategy, context_key, cohort, store, p)

    if verdict != VERDICT_STRONG:
        return _no(f"not_strong verdict={verdict}", verdict, edge_r, n, lookup)
    eff_min_samples = p.resolve_min_samples(strategy)
    if n < eff_min_samples:
        return _no(f"strong_thin n={n}<{eff_min_samples}", verdict, edge_r, n, lookup)
    if edge_r is None or edge_r <= 0:
        return _no(f"non_positive_edge edge={edge_r}", verdict, edge_r, n, lookup)
    return GateOverrideDecision(
        would_override=True,
        verdict=verdict,
        edge_r=edge_r,
        n=n,
        matrix_strategy=lookup,
        reason=f"strong_override edge={edge_r:+.3f}R n={n}",
    )


def classify_divergence(
    confidence: float,
    base_floor: float,
    decision: EmissionDecision,
    *,
    components_ok: bool = True,
) -> str:
    """How the policy decision compares to today's global-floor decision.

    ``components_ok`` folds in the non-confidence component floors (market /
    execution / risk) so a candidate the component floors already block is never
    counted as a policy divergence.
    """
    live_emit = components_ok and confidence >= base_floor
    policy_emit = (
        components_ok
        and (not decision.suppressed)
        and confidence >= decision.effective_floor
    )
    if live_emit and policy_emit:
        return DIV_AGREE_EMIT
    if (not live_emit) and (not policy_emit):
        return DIV_AGREE_SUPPRESS
    if policy_emit and not live_emit:
        return DIV_RELAX
    return DIV_TIGHTEN
