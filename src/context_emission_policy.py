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

from dataclasses import dataclass
from typing import Optional

from src.strategy_edge import (
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

    @staticmethod
    def from_config() -> "PolicyParams":
        """Effective params: ops runtime tunables overlaid on the env/config defaults.

        Every knob is live-controllable from ops (Control → Signal gating); a
        tunable read that fails (registry not built, e.g. in a unit test) falls
        back to the frozen config default, so the policy is always well-defined.
        """
        from config import (
            CONTEXT_EMISSION_LIVE,
            CONTEXT_EMISSION_MIN_SAMPLES,
            CONTEXT_EMISSION_POLICY_ENABLED,
            CONTEXT_EMISSION_POSITIVE_RELAX,
            CONTEXT_EMISSION_QUALITY_ANCHOR,
            CONTEXT_EMISSION_STRONG_RELAX,
            CONTEXT_EMISSION_SUPPRESS_NEGATIVE,
        )

        def _rt(key: str, default: object) -> object:
            try:
                from src import runtime_tunables as _r

                val = _r.get(key)
                return val if val is not None else default
            except Exception:
                return default

        return PolicyParams(
            enabled=bool(_rt("context_emission_enabled", CONTEXT_EMISSION_POLICY_ENABLED)),
            live=bool(_rt("context_emission_live", CONTEXT_EMISSION_LIVE)),
            quality_anchor=float(_rt("context_emission_quality_anchor", CONTEXT_EMISSION_QUALITY_ANCHOR)),  # type: ignore[arg-type]
            strong_relax=max(0.0, float(_rt("context_emission_strong_relax", CONTEXT_EMISSION_STRONG_RELAX))),  # type: ignore[arg-type]
            positive_relax=max(0.0, float(_rt("context_emission_positive_relax", CONTEXT_EMISSION_POSITIVE_RELAX))),  # type: ignore[arg-type]
            min_samples=max(1, int(_rt("context_emission_min_samples", CONTEXT_EMISSION_MIN_SAMPLES))),  # type: ignore[call-overload]
            suppress_negative=bool(_rt("context_emission_suppress_negative", CONTEXT_EMISSION_SUPPRESS_NEGATIVE)),
        )


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


def effective_floor(
    strategy: str,
    context_key: str,
    base_floor: float,
    *,
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
    matrix_strategy = _resolve_matrix_strategy(strategy, store)
    # Prefer the strategy's own cell; fall back to the shadow control arm only
    # when own data is thin (INSUFFICIENT), so a path with real emitted outcomes
    # is judged on itself.
    own_verdict = store.verdict(strategy, context_key)  # type: ignore[attr-defined]
    if matrix_strategy != strategy and own_verdict == "INSUFFICIENT_DATA":
        lookup = matrix_strategy
    else:
        lookup = strategy
    verdict = store.verdict(lookup, context_key)  # type: ignore[attr-defined]
    edge_r = store.edge_r(lookup, context_key)  # type: ignore[attr-defined]
    n = store.sample_count(lookup, context_key)  # type: ignore[attr-defined]

    if verdict == VERDICT_NEGATIVE:
        if p.suppress_negative:
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
        if n < p.min_samples:
            return _base(f"{verdict.lower()}_thin n={n}<{p.min_samples}", verdict, lookup)
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

    # FLAT / INSUFFICIENT / unknown → global floor, unchanged.
    return _base(f"neutral n={n}", verdict, lookup)


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
