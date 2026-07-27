"""Layer G — autonomous emission-policy controller (pure decision core).

Closes the outer loop the system was missing: the ``suppression_audit`` gate
verdicts (KEEP / TUNE / DROP) and the ``strategy_edge`` matrix are measured every
cycle but nothing *acts* on them — exactly where the edge matrix sat before PR 752.
This module consumes those measurements and moves the ``context_emission_policy``
parameters **per strategy**, inside a bounded envelope, with **no human in the
loop** (owner directive, S72: autonomous, dark-first, self-promoting).

Design + envelope: ``docs/PLAN_AUTONOMOUS_EMISSION_CONTROLLER.md``.

**Pure by construction** — every input is a parameter (plain dicts mapped from the
live stores by the integration layer), no I/O, so the whole controller is unit-
tested deterministically. The integration layer (loop + Firestore store + policy
override read + liveness probe) applies only the adjustments this core marks
``applied=True`` and stamps *all* candidates (promoted + pending) to the ledger.

**Autonomy with guardrails** (the safety is the envelope, not a human):
* action space is *only* the two per-strategy knobs below, hard-clamped to bounds;
* nothing promotes on first sight — a candidate must be stable across K cycles,
  each with a sufficiently-sampled verdict, and (for suppress toggles) clear an EV
  magnitude bar, and survive a global boot-grace of pure observation;
* at most ``max_changes_per_cycle`` promotions per cycle (blast radius);
* on promotion the (strategy, param) history is cleared so a reversal needs K
  fresh opposite cycles → no oscillation;
* the master kill (``emission_controller_enabled``) lives in the integration layer:
  when off it simply never calls this core and the policy reads global params.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Set

# Verdict tokens (mirror src/suppression_audit.py) + our own history tokens.
V_KEEP = "KEEP"
V_DROP = "DROP"
V_TUNE = "TUNE"
V_INSUFF = "INSUFFICIENT_SAMPLE"

# min_samples history tokens
T_LOWER = "LOWER"
T_RAISE = "RAISE"
T_HOLD = "HOLD"
T_SKIP = "SKIP"  # verdict/sample not actionable this cycle (does not advance stability)

PARAM_SUPPRESS = "suppress_negative"
PARAM_MIN_SAMPLES = "min_samples"

STATUS_PROMOTED = "PROMOTED"
STATUS_PENDING = "PENDING"
STATUS_PRUNED = "PRUNED"

# ---------------------------------------------------------------------------
# Routability — the controller's action space vs what the policy can read
# ---------------------------------------------------------------------------
# The controller's *inputs* are keyed by **matrix** strategy, which includes the
# measurement arms (``X@ATR``/``X@FIXED``/``X@SAREXIT``/…) and the shadow-only
# units (``SHADOW_*``).  Its *output* is read by
# ``context_emission_policy.PolicyParams.resolve_min_samples`` /
# ``resolve_suppress_negative``, which the scanner only ever calls with a live
# ``SetupClass`` value.  So an override stored under any other key is
# **unreachable by construction**: persisted, logged ``[APPLY]``, rendered in ops
# as an "active override" — and read by nothing.
#
# Measured on production 2026-07-27 (controller cycle 279): 9 of 18 persisted
# overrides were dead keys and 23 of 40 lifetime promotions had gone to them.
# Worse, the phantoms *outcompete* the real rows for a 2-per-cycle budget:
#
#   * the auto-tighten brake cannot fire on them — an arm never emits, so
#     ``n_emitted`` stays 0, ``strategy_health`` never reaches ``health_min_n``,
#     and ``losing`` is permanently False, making an arm unconditionally
#     promotable in the LOWER direction where a real strategy would be held;
#   * ties in the blast-radius sort resolve in their favour — every min_samples
#     candidate has ``ev_per_suppression_r=None`` → sort key 0.0, so the stable
#     sort falls through to ``sorted(strategies)`` (alphabetical) and e.g.
#     ``QUIET_COMPRESSION_BREAK@ATR`` precedes ``RANGE_FADE``.
#
# **This is measured live, not dark.** ``routable`` is always classified and
# always reported (``ControllerDecision.routability``), including the
# counterfactual: *which live candidates would have promoted had the action space
# been closed*. That is the number an activation decision needs, and it cannot be
# obtained by shipping the measurement switched off — a dark path that stamps
# nothing produces an empty ops panel and a decision that keeps being deferred
# (§ Project Phase; the SAR arm paid for that lesson on 2026-07-25).
#
# ``enforce_routable`` is the separate, default-OFF switch that actually closes
# the action space and prunes the dead keys. Measurement ON, effect OFF.
#
# ``routable`` is a **parameter**, never an import: this module is pure by
# construction and ``geometry_ab`` does file/env I/O at import time. The
# integration layer supplies the live ``SetupClass`` set. ``routable=None``
# disables classification entirely (legacy behaviour, unchanged).


def _routable_set(routable: Optional[Iterable[str]]) -> Optional[Set[str]]:
    if routable is None:
        return None
    return {str(s).upper() for s in routable}


@dataclass(frozen=True)
class RoutabilityReport:
    """What the controller's un-closed action space is costing, per cycle.

    Always populated when ``routable`` is supplied, whether or not enforcement
    is on — this is the evidence the activation decision reads.

    ``promoted_unroutable``/``starved_routable`` are the decision-relevant pair:
    the promotions this cycle spent on keys nothing reads, and the live
    candidates that would have taken those slots instead. Both are ``"S|param"``.
    """

    enforced: bool
    routable_candidates: int
    unroutable_candidates: int
    unroutable_strategies: List[str] = field(default_factory=list)
    dead_overrides: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    promoted_unroutable: List[str] = field(default_factory=list)
    starved_routable: List[str] = field(default_factory=list)
    pruned: List[str] = field(default_factory=list)

    @property
    def wasted_promotions(self) -> int:
        return len(self.promoted_unroutable)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enforced": self.enforced,
            "routable_candidates": self.routable_candidates,
            "unroutable_candidates": self.unroutable_candidates,
            "unroutable_strategies": list(self.unroutable_strategies),
            "dead_overrides": {k: dict(v) for k, v in self.dead_overrides.items()},
            "promoted_unroutable": list(self.promoted_unroutable),
            "starved_routable": list(self.starved_routable),
            "pruned": list(self.pruned),
            "wasted_promotions": self.wasted_promotions,
        }


@dataclass(frozen=True)
class ControllerBounds:
    stability_cycles: int = 3          # K
    boot_grace_cycles: int = 3         # pure-observation cycles after (re)start
    min_gate_n: int = 40               # min gate sample for a verdict to count
    promote_ev_r: float = 0.25         # min |EV/suppression| to flip a suppress toggle
    max_changes_per_cycle: int = 2     # blast radius
    min_samples_floor: int = 15        # lower clamp for the per-strategy relax floor
    min_samples_ceiling: int = 30      # never raise an override above the global default
    min_samples_step: int = 5
    health_raise_ev_r: float = -0.10   # emitted edge below this → undo a min_samples loosening
    health_min_n: int = 20             # min emitted trades before the health signal is trusted


@dataclass
class StrategyOverride:
    """Per-strategy override on top of the global PolicyParams. ``None`` = follow global."""
    suppress_negative: Optional[bool] = None
    min_samples: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"suppress_negative": self.suppress_negative, "min_samples": self.min_samples}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StrategyOverride":
        return cls(
            suppress_negative=d.get("suppress_negative"),
            min_samples=d.get("min_samples"),
        )


@dataclass
class ControllerState:
    overrides: Dict[str, StrategyOverride] = field(default_factory=dict)
    history: Dict[str, List[str]] = field(default_factory=dict)   # "S|param" -> recent tokens
    last_change_cycle: Dict[str, int] = field(default_factory=dict)
    cycle: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overrides": {s: o.to_dict() for s, o in self.overrides.items()},
            "history": {k: list(v) for k, v in self.history.items()},
            "last_change_cycle": dict(self.last_change_cycle),
            "cycle": self.cycle,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ControllerState":
        if not isinstance(d, dict):
            return cls()
        return cls(
            overrides={
                s: StrategyOverride.from_dict(o)
                for s, o in (d.get("overrides") or {}).items()
                if isinstance(o, dict)
            },
            history={k: list(v) for k, v in (d.get("history") or {}).items() if isinstance(v, list)},
            last_change_cycle=dict(d.get("last_change_cycle") or {}),
            cycle=int(d.get("cycle") or 0),
        )


@dataclass
class _Candidate:
    """Internal, mutable — carries the override store value + promote flag while the
    cycle is being decided. Converted to a frozen ``Adjustment`` on the way out."""
    strategy: str
    param: str
    old: Any
    new: Any
    store_val: Any            # value to write to the override if promoted (None = follow global)
    promotable: bool
    reason: str
    verdict: str
    ev_per_suppression_r: Optional[float]
    n: int
    routable: Optional[bool] = None   # None = not classified (routable not supplied)


@dataclass(frozen=True)
class Adjustment:
    strategy: str
    param: str
    old: Any
    new: Any
    applied: bool
    status: str            # PROMOTED | PENDING | PRUNED
    reason: str
    verdict: str = ""
    ev_per_suppression_r: Optional[float] = None
    n: int = 0
    # Whether the emission policy can actually read this strategy key. Stamped by
    # the engine so **ops renders it rather than re-deriving it** — a mirrored
    # suffix list in the dashboard is the drift class that silently inflated the
    # Strategy Lab rollup for a week. ``None`` = not classified.
    routable: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "param": self.param,
            "old": self.old,
            "new": self.new,
            "applied": self.applied,
            "status": self.status,
            "reason": self.reason,
            "verdict": self.verdict,
            "ev_per_suppression_r": self.ev_per_suppression_r,
            "n": self.n,
            "routable": self.routable,
        }


@dataclass(frozen=True)
class ControllerDecision:
    state: ControllerState
    adjustments: List[Adjustment]   # promoted + pending candidates (HOLD not listed)
    routability: Optional[RoutabilityReport] = None

    @property
    def applied(self) -> List[Adjustment]:
        return [a for a in self.adjustments if a.applied]


def _push(history: Dict[str, List[str]], key: str, token: str, k: int) -> List[str]:
    seq = list(history.get(key, []))
    seq.append(token)
    seq = seq[-k:]
    history[key] = seq
    return seq


def _stable(seq: List[str], token: str, k: int) -> bool:
    """True when the last K tokens exist and all equal ``token``."""
    return len(seq) >= k and all(t == token for t in seq[-k:])


def _effective(override: Optional[bool | int], global_value: Any) -> Any:
    return global_value if override is None else override


def run_cycle(
    *,
    gate_metrics: Dict[str, Dict[str, Any]],
    best_strong_cell: Dict[str, Dict[str, Any]],
    strategy_health: Dict[str, Dict[str, Any]],
    global_params: Dict[str, Any],
    prior: ControllerState,
    bounds: ControllerBounds,
    cycles_since_start: int,
    unlocked_cell_r: Optional[Dict[str, float]] = None,
    routable: Optional[Iterable[str]] = None,
    enforce_routable: bool = False,
) -> ControllerDecision:
    """Advance the controller one cycle.

    ``gate_metrics``:  strategy -> {n, ev_per_suppression_r, verdict}  (context_floor:S gate)
    ``best_strong_cell``: strategy -> {n, edge}  (largest-n cell at/above STRONG edge)
    ``unlocked_cell_r``:  strategy -> edge_r of the cell a prior min_samples-lower unlocked
                          (optional; per-cell tighten signal, precise auto-revert)
    ``strategy_health``:  strategy -> {emitted_avg_r, emitted_n}
    ``global_params``:    {suppress_negative: bool, min_samples: int}  (the PolicyParams defaults)
    ``cycles_since_start``: in-process cycles since boot (resets on restart → boot grace)
    ``routable``:      the strategy keys the emission policy can actually look up
                       (live ``SetupClass`` values). Supplying it turns on
                       **measurement**: every candidate is classified, the dead
                       overrides are reported, and the counterfactual is computed.
                       It changes no behaviour on its own. ``None`` = no
                       classification (legacy).
    ``enforce_routable``: apply what the measurement shows — exclude unroutable
                       keys from the action space and prune the dead overrides.
                       **Default OFF**; flip only after owner sign-off on the
                       measured result (§ Project Phase). Ignored without
                       ``routable``.

    Returns the new state, the candidate adjustments, and (when ``routable`` is
    given) the ``RoutabilityReport``. An adjustment with ``applied=True`` should be
    written to the override store; every adjustment is stamped to the ledger.
    """
    k = max(1, bounds.stability_cycles)
    state = ControllerState(
        overrides={s: StrategyOverride(o.suppress_negative, o.min_samples) for s, o in prior.overrides.items()},
        history={key: list(seq) for key, seq in prior.history.items()},
        last_change_cycle=dict(prior.last_change_cycle),
        cycle=prior.cycle + 1,
    )
    g_suppress = bool(global_params.get("suppress_negative", True))
    g_min = int(global_params.get("min_samples", 30))
    past_grace = cycles_since_start > bounds.boot_grace_cycles

    strategies = set(gate_metrics) | set(best_strong_cell) | set(state.overrides)

    allowed = _routable_set(routable)
    enforcing = allowed is not None and enforce_routable

    def _is_routable(strategy: str) -> Optional[bool]:
        return None if allowed is None else (strategy.upper() in allowed)

    # The unroutable keys in play this cycle, resolved once: both the report and
    # the prune walk the same list, so they can never disagree about what is dead.
    unroutable_now: List[str] = (
        [] if allowed is None
        else sorted(s for s in strategies if s.upper() not in allowed)
    )

    # Dead overrides — persisted entries under keys the policy never looks up.
    # Reported every cycle whether or not we enforce, so the ops panel shows the
    # standing footprint rather than only the moment it is cleaned up.
    dead_overrides: Dict[str, Dict[str, Any]] = {}
    for strategy in unroutable_now:
        ov = state.overrides.get(strategy)
        if ov is None:
            continue
        live_vals = {k: v for k, v in ov.to_dict().items() if v is not None}
        if live_vals:
            dead_overrides[strategy] = live_vals

    # Enforcement: close the action space and prune. Pruning is derived from
    # ``routable`` every cycle rather than run as a one-shot migration, so the
    # invariant re-establishes itself on every run and needs no schema stamp or
    # deploy-date gate (cf. #802 — never date-gate a migration).
    prunes: List[Adjustment] = []
    if enforcing:
        unroutable_set = set(unroutable_now)
        for strategy in unroutable_now:
            ov = state.overrides.pop(strategy, None)
            for param in (PARAM_SUPPRESS, PARAM_MIN_SAMPLES):
                key = f"{strategy}|{param}"
                state.history.pop(key, None)
                state.last_change_cycle.pop(key, None)
                old = getattr(ov, param, None) if ov is not None else None
                if old is None:
                    continue
                prunes.append(Adjustment(
                    strategy=strategy, param=param, old=old, new=None, applied=True,
                    status=STATUS_PRUNED, routable=False,
                    reason="unroutable: the emission policy never looks this key up "
                           "(measurement arm or shadow-only unit) — override was dead",
                ))
        strategies = strategies - unroutable_set

    candidates: List[_Candidate] = []

    for strategy in sorted(strategies):
        ov = state.overrides.get(strategy) or StrategyOverride()

        # ---- suppress_negative, driven by the context_floor:S gate verdict ----
        gm = gate_metrics.get(strategy) or {}
        gn = int(gm.get("n", 0) or 0)
        gev = gm.get("ev_per_suppression_r")
        gverdict = str(gm.get("verdict") or "")
        token = gverdict if (gn >= bounds.min_gate_n and gverdict in (V_KEEP, V_DROP)) else T_SKIP
        seq = _push(state.history, f"{strategy}|{PARAM_SUPPRESS}", token, k)
        cur_suppress = _effective(ov.suppress_negative, g_suppress)

        desired_suppress: Optional[bool] = None
        if _stable(seq, V_DROP, k):
            desired_suppress = False            # gate is killing winners → stop suppressing
        elif _stable(seq, V_KEEP, k):
            desired_suppress = True             # gate protects → keep suppressing (global default)
        if desired_suppress is not None and desired_suppress != cur_suppress:
            # The EV-magnitude bar gates only the RISKY direction — turning
            # suppression OFF (more emissions). Returning to the protective
            # default (suppress ON) is safety-positive and needs stability only.
            evmag = (abs(float(gev)) if gev is not None else 0.0) if desired_suppress is False else None
            reason, ok = _gate_change_ok(
                past_grace=past_grace, evmag=evmag, bounds=bounds,
                key=f"{strategy}|{PARAM_SUPPRESS}", state=state, k=k,
            )
            candidates.append(_Candidate(
                strategy=strategy, param=PARAM_SUPPRESS, old=cur_suppress, new=desired_suppress,
                # store None when reverting to the global default, else the explicit value
                store_val=None if desired_suppress == g_suppress else desired_suppress,
                promotable=ok, reason=reason, verdict=gverdict, ev_per_suppression_r=gev, n=gn,
                routable=_is_routable(strategy),
            ))

        # ---- min_samples, driven by a thin STRONG cell + emitted health ----
        cur_min = int(_effective(ov.min_samples, g_min))
        cell = best_strong_cell.get(strategy) or {}
        cell_n = int(cell.get("n", 0) or 0)
        health = strategy_health.get(strategy) or {}
        h_avg_r = health.get("emitted_avg_r")
        h_n = int(health.get("emitted_n", 0) or 0)
        # Strategy-aggregate health (coarse) OR the specific unlocked cell's own
        # edge going negative (precise) triggers a min_samples tighten. The
        # per-cell signal closes the gap where one losing unlocked cell hides
        # inside an otherwise-healthy strategy average and never self-corrects
        # (ported from the closed #762, review #1).
        losing = h_avg_r is not None and float(h_avg_r) < bounds.health_raise_ev_r and h_n >= bounds.health_min_n
        if unlocked_cell_r is not None:
            _cell_r = unlocked_cell_r.get(strategy)
            if _cell_r is not None and float(_cell_r) < bounds.health_raise_ev_r:
                losing = True

        has_unlock = bounds.min_samples_floor <= cell_n < cur_min
        if cur_min < bounds.min_samples_ceiling and losing:
            mtoken = T_RAISE                    # a prior loosening soured → tighten back
        elif has_unlock and not losing:
            mtoken = T_LOWER                    # thin STRONG cell + emissions not losing → unlock
        else:
            mtoken = T_HOLD
        mseq = _push(state.history, f"{strategy}|{PARAM_MIN_SAMPLES}", mtoken, k)

        desired_min: Optional[int] = None
        if _stable(mseq, T_LOWER, k):
            desired_min = max(bounds.min_samples_floor, cur_min - bounds.min_samples_step)
        elif _stable(mseq, T_RAISE, k):
            desired_min = min(bounds.min_samples_ceiling, cur_min + bounds.min_samples_step)
        if desired_min is not None and desired_min != cur_min:
            reason, ok = _gate_change_ok(
                past_grace=past_grace, evmag=None, bounds=bounds,
                key=f"{strategy}|{PARAM_MIN_SAMPLES}", state=state, k=k,
            )
            candidates.append(_Candidate(
                strategy=strategy, param=PARAM_MIN_SAMPLES, old=cur_min, new=desired_min,
                store_val=None if desired_min == g_min else desired_min,
                promotable=ok, reason=reason + f" (strong_cell_n={cell_n})",
                verdict=mtoken, ev_per_suppression_r=None, n=cell_n,
                routable=_is_routable(strategy),
            ))

    # ---- blast radius: promote at most max_changes_per_cycle, prefer measured harm ----
    budget = max(0, bounds.max_changes_per_cycle)

    def _rank(pool: List[_Candidate]) -> List[_Candidate]:
        return sorted(pool, key=lambda c: abs(c.ev_per_suppression_r or 0.0), reverse=True)

    promotable = _rank([c for c in candidates if c.promotable])
    promote_ids = {id(c) for c in promotable[:budget]}

    # The counterfactual, computed whenever classification is on: re-run the exact
    # same bounded selection over routable candidates only, and diff. This is what
    # makes the cost readable instead of inferred — "these two dead keys took the
    # budget; these two live strategies would have moved instead." Under
    # enforcement the pools are identical and both lists come out empty.
    promoted_unroutable: List[str] = []
    starved_routable: List[str] = []
    if allowed is not None:
        routable_only = _rank([c for c in promotable if c.routable])
        would_ids = {id(c) for c in routable_only[:budget]}
        promoted_unroutable = [
            f"{c.strategy}|{c.param}" for c in promotable
            if id(c) in promote_ids and not c.routable
        ]
        starved_routable = [
            f"{c.strategy}|{c.param}" for c in routable_only
            if id(c) in would_ids and id(c) not in promote_ids
        ]

    # Prunes remove dead state rather than change live policy, so they are audited
    # but deliberately do not consume the promotion budget.
    final: List[Adjustment] = list(prunes)
    for c in candidates:
        if id(c) in promote_ids:
            ov = state.overrides.setdefault(c.strategy, StrategyOverride())
            if c.param == PARAM_SUPPRESS:
                ov.suppress_negative = c.store_val
            else:
                ov.min_samples = c.store_val
            state.last_change_cycle[f"{c.strategy}|{c.param}"] = state.cycle
            state.history[f"{c.strategy}|{c.param}"] = []  # reset → K fresh cycles before reversal
            final.append(Adjustment(
                strategy=c.strategy, param=c.param, old=c.old, new=c.new, applied=True,
                status=STATUS_PROMOTED, reason=c.reason, verdict=c.verdict,
                ev_per_suppression_r=c.ev_per_suppression_r, n=c.n, routable=c.routable,
            ))
        else:
            reason = c.reason if not c.promotable else c.reason + " | deferred:blast_radius"
            final.append(Adjustment(
                strategy=c.strategy, param=c.param, old=c.old, new=c.new, applied=False,
                status=STATUS_PENDING, reason=reason, verdict=c.verdict,
                ev_per_suppression_r=c.ev_per_suppression_r, n=c.n, routable=c.routable,
            ))

    report: Optional[RoutabilityReport] = None
    if allowed is not None:
        report = RoutabilityReport(
            enforced=enforcing,
            routable_candidates=sum(1 for c in candidates if c.routable),
            unroutable_candidates=sum(1 for c in candidates if c.routable is False),
            unroutable_strategies=sorted(
                {c.strategy for c in candidates if c.routable is False} | set(dead_overrides)
            ),
            dead_overrides=dead_overrides,
            promoted_unroutable=promoted_unroutable,
            starved_routable=starved_routable,
            pruned=[f"{a.strategy}|{a.param}" for a in prunes],
        )

    return ControllerDecision(state=state, adjustments=final, routability=report)


def build_inputs(
    *,
    by_gate: Dict[str, Dict[str, Any]],
    matrix: Dict[str, Dict[str, Any]],
    strong_verdict: str = "STRONG",
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Map the live stores into ``run_cycle`` inputs (pure).

    ``by_gate``: ``suppression_audit.compute_gate_suppression_metrics`` output
        (gate_name -> {n, ev_per_suppression_r, verdict}).
    ``matrix``:  ``StrategyEdgeStore.matrix`` output ("S|ctx" -> per-cell stats).

    Returns ``{"gate_metrics", "best_strong_cell", "strategy_health"}``. The
    ``strategy_health`` R is the per-strategy sample-weighted ``avg_r`` across its
    cells (an all-source proxy — the emitted arm alone is too thin to trust) used
    only for the conservative min_samples auto-tighten; the suppress loop runs off
    the clean per-gate EV.
    """
    gate_metrics: Dict[str, Dict[str, Any]] = {}
    for gate_name, m in (by_gate or {}).items():
        if not isinstance(m, dict) or not str(gate_name).startswith("context_floor:"):
            continue
        strategy = str(gate_name).split("context_floor:", 1)[1]
        gate_metrics[strategy] = {
            "n": int(m.get("n", 0) or 0),
            "ev_per_suppression_r": m.get("ev_per_suppression_r"),
            "verdict": str(m.get("verdict") or ""),
        }

    best_strong_cell: Dict[str, Dict[str, Any]] = {}
    health_acc: Dict[str, Dict[str, float]] = {}
    for cell in (matrix or {}).values():
        if not isinstance(cell, dict):
            continue
        strat = str(cell.get("strategy") or "")
        if not strat:
            continue
        n = int(cell.get("n", 0) or 0)
        if str(cell.get("verdict") or "") == strong_verdict and n > 0:
            edge = cell.get("edge_r")
            prev = best_strong_cell.get(strat)
            if prev is None or n > prev["n"]:
                best_strong_cell[strat] = {"n": n, "edge": float(edge) if edge is not None else None}
        acc = health_acc.setdefault(strat, {"r_weight": 0.0, "n": 0.0, "emitted_n": 0.0})
        avg_r = cell.get("avg_r")
        if avg_r is not None and n > 0:
            acc["r_weight"] += float(avg_r) * n
            acc["n"] += n
        acc["emitted_n"] += int(cell.get("n_emitted", 0) or 0)

    strategy_health: Dict[str, Dict[str, Any]] = {}
    for strat, acc in health_acc.items():
        strategy_health[strat] = {
            "emitted_avg_r": (acc["r_weight"] / acc["n"]) if acc["n"] else None,
            "emitted_n": int(acc["emitted_n"]),
        }

    return {
        "gate_metrics": gate_metrics,
        "best_strong_cell": best_strong_cell,
        "strategy_health": strategy_health,
    }


def _gate_change_ok(
    *, past_grace: bool, evmag: Optional[float], bounds: ControllerBounds,
    key: str, state: ControllerState, k: int,
) -> tuple[str, bool]:
    """Return (reason, promote_ok). Encodes boot-grace, EV bar (suppress only),
    and the rate limit. Stability is already established by the caller."""
    if not past_grace:
        return ("boot_grace: observe-only", False)
    if evmag is not None and evmag < bounds.promote_ev_r:
        return (f"ev_below_bar |{evmag:.2f}|<{bounds.promote_ev_r}", False)
    last = state.last_change_cycle.get(key)
    if last is not None and (state.cycle - last) < k:
        return (f"rate_limited since_cycle={state.cycle - last}<{k}", False)
    return ("stable+bar+grace → promote", True)
