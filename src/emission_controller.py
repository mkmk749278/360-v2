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

import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("emission_controller")

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


@dataclass(frozen=True)
class Adjustment:
    strategy: str
    param: str
    old: Any
    new: Any
    applied: bool
    status: str            # PROMOTED | PENDING
    reason: str
    verdict: str = ""
    ev_per_suppression_r: Optional[float] = None
    n: int = 0

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
        }


@dataclass(frozen=True)
class ControllerDecision:
    state: ControllerState
    adjustments: List[Adjustment]   # promoted + pending candidates (HOLD not listed)

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
) -> ControllerDecision:
    """Advance the controller one cycle.

    ``gate_metrics``:  strategy -> {n, ev_per_suppression_r, verdict}  (context_floor:S gate)
    ``best_strong_cell``: strategy -> {n, edge}  (largest-n cell at/above STRONG edge)
    ``strategy_health``:  strategy -> {emitted_avg_r, emitted_n}
    ``global_params``:    {suppress_negative: bool, min_samples: int}  (the PolicyParams defaults)
    ``cycles_since_start``: in-process cycles since boot (resets on restart → boot grace)

    Returns the new state + the candidate adjustments. An adjustment with
    ``applied=True`` should be written to the override store; every adjustment
    (applied or pending) is stamped to the shadow ledger.
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
            ))

        # ---- min_samples, driven by a thin STRONG cell + emitted health ----
        cur_min = int(_effective(ov.min_samples, g_min))
        cell = best_strong_cell.get(strategy) or {}
        cell_n = int(cell.get("n", 0) or 0)
        health = strategy_health.get(strategy) or {}
        h_avg_r = health.get("emitted_avg_r")
        h_n = int(health.get("emitted_n", 0) or 0)
        # Strategy-aggregate health (coarse) OR the specific unlocked cell's own
        # edge going negative (precise) triggers a tighten.  The per-cell signal
        # closes the gap where a single losing unlocked cell hides inside an
        # otherwise-healthy strategy average and never self-corrects (review #1).
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
            ))

    # ---- blast radius: promote at most max_changes_per_cycle, prefer measured harm ----
    promotable = sorted(
        (c for c in candidates if c.promotable),
        key=lambda c: abs(c.ev_per_suppression_r or 0.0), reverse=True,
    )
    promote_ids = {id(c) for c in promotable[: max(0, bounds.max_changes_per_cycle)]}

    final: List[Adjustment] = []
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
                ev_per_suppression_r=c.ev_per_suppression_r, n=c.n,
            ))
        else:
            reason = c.reason if not c.promotable else c.reason + " | deferred:blast_radius"
            final.append(Adjustment(
                strategy=c.strategy, param=c.param, old=c.old, new=c.new, applied=False,
                status=STATUS_PENDING, reason=reason, verdict=c.verdict,
                ev_per_suppression_r=c.ev_per_suppression_r, n=c.n,
            ))

    return ControllerDecision(state=state, adjustments=final)


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


# ---------------------------------------------------------------------------
# Persistence store + hot-path override accessor
# ---------------------------------------------------------------------------
#
# The decision core above is pure.  This store gives it a home: it persists the
# ``ControllerState`` (overrides + verdict history + cycle index) across
# restarts, exposes an O(1) in-memory ``get_override(strategy)`` for the scanner
# hot path (never touches disk), and appends every adjustment to an audit
# ledger.  Thread-safe: the background loop writes under a lock while the
# scanner reads the (immutable-per-cycle) override snapshot lock-free-ish.


class EmissionControllerStore:
    """State home for the emission controller.

    * ``get_override(strategy)`` — hot-path read (scanner, per candidate). Returns
      the per-strategy :class:`StrategyOverride`; ``None`` fields follow global.
      In-memory dict lookup — no disk, no network (Cost Discipline).
    * ``load`` / ``save`` — JSON persistence of the full state.
    * ``apply_decision`` — swap in the new state, persist, and append every
      adjustment (applied *and* shadow/pending) to the JSONL ledger.
    """

    def __init__(self, path: str, ledger_path: str = "") -> None:
        self._path = path
        self._ledger_path = ledger_path
        self._lock = threading.Lock()
        self._state: ControllerState = ControllerState()
        # A plain dict snapshot of overrides for lock-free-ish hot reads. Replaced
        # atomically (single reference assignment) whenever the state changes.
        self._override_snapshot: Dict[str, StrategyOverride] = {}

    # ---- lifecycle -------------------------------------------------------

    def load(self) -> "EmissionControllerStore":
        try:
            if os.path.exists(self._path):
                with open(self._path, "r", encoding="utf-8") as fh:
                    self._state = ControllerState.from_dict(json.load(fh))
        except Exception as exc:  # corrupt/partial file → start clean, don't crash boot
            log.warning("emission_controller: state load failed ({}), starting clean", exc)
            self._state = ControllerState()
        self._override_snapshot = dict(self._state.overrides)
        return self

    def save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            tmp = f"{self._path}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(self._state.to_dict(), fh)
            os.replace(tmp, self._path)  # atomic
        except Exception as exc:
            log.warning("emission_controller: state save failed ({})", exc)

    # ---- hot path (scanner, per candidate) -------------------------------

    def get_override(self, strategy: str) -> StrategyOverride:
        """O(1) in-memory read. Empty override (all ``None`` → follow global)
        when the strategy has none."""
        return self._override_snapshot.get(strategy) or StrategyOverride()

    @property
    def state(self) -> ControllerState:
        return self._state

    # ---- background loop (per cycle) -------------------------------------

    def apply_decision(self, decision: "ControllerDecision") -> None:
        """Persist the new state, refresh the hot-path snapshot, ledger every
        adjustment. Applied adjustments change emission; pending/shadow ones are
        recorded for the owner to review but change nothing."""
        with self._lock:
            self._state = decision.state
            # Atomic reference swap so a concurrent hot-path reader sees either
            # the old or the new full snapshot, never a half-updated dict.
            self._override_snapshot = dict(decision.state.overrides)
            self.save()
            self._append_ledger(decision.adjustments)

    def _append_ledger(self, adjustments: "List[Adjustment]") -> None:
        if not self._ledger_path or not adjustments:
            return
        try:
            os.makedirs(os.path.dirname(self._ledger_path) or ".", exist_ok=True)
            ts = time.time()
            with open(self._ledger_path, "a", encoding="utf-8") as fh:
                for a in adjustments:
                    row = a.to_dict()
                    row["ts"] = ts
                    row["cycle"] = self._state.cycle
                    fh.write(json.dumps(row) + "\n")
        except Exception as exc:
            log.warning("emission_controller: ledger append failed ({})", exc)


# Module-level singleton (mirrors src.strategy_edge / src.api.users pattern).
_store: Optional[EmissionControllerStore] = None
_store_lock = threading.Lock()


def get_default_store(
    path: Optional[str] = None, ledger_path: Optional[str] = None
) -> EmissionControllerStore:
    """Return (and lazily build) the process-global controller store."""
    global _store
    with _store_lock:
        if _store is None:
            import config
            _store = EmissionControllerStore(
                path or config.EMISSION_CONTROLLER_PERSIST_PATH,
                ledger_path if ledger_path is not None else config.EMISSION_CONTROLLER_LEDGER_PATH,
            ).load()
        return _store


def _reset_default_store() -> None:
    """Test hook — drop the singleton so a test can inject a fresh path."""
    global _store
    with _store_lock:
        _store = None


def bounds_from_config() -> ControllerBounds:
    """Build the envelope from config (owner-tunable). The controller can never
    act outside these bounds."""
    import config
    return ControllerBounds(
        stability_cycles=int(config.EMISSION_CONTROLLER_STABILITY_CYCLES),
        boot_grace_cycles=int(config.EMISSION_CONTROLLER_BOOT_GRACE_CYCLES),
        min_gate_n=int(config.EMISSION_CONTROLLER_MIN_GATE_N),
        promote_ev_r=float(config.EMISSION_CONTROLLER_PROMOTE_EV_R),
        max_changes_per_cycle=int(config.EMISSION_CONTROLLER_MAX_CHANGES_PER_CYCLE),
        min_samples_floor=int(config.EMISSION_CONTROLLER_MIN_SAMPLES_FLOOR),
        min_samples_ceiling=int(config.CONTEXT_EMISSION_MIN_SAMPLES),
        min_samples_step=int(config.EMISSION_CONTROLLER_MIN_SAMPLES_STEP),
    )
