"""Dark → live promotion, under owner-set conditions.

The dark lane (``dark_emission``) carries a candidate past one loosened gate,
measures it forward on real candles, and diverts it at the single
``signal_queue.put`` site so it reaches nobody.  That answers *"was this
setup worth sending"* and gives the owner no way to act on the answer except
by editing a compatibility matrix in this repo and shipping a deploy.

This module is the act.  A rule names a path and the conditions under which
its dark rows stop being diverted:

    LIQUIDITY_SWEEP_REVERSAL
      gates    setup_compat:regime_STRONG_TREND, execution:overextended
      regimes  TRENDING_DOWN, TRENDING_UP
      sessions *
      side     with_trend
      cap      25 / day

Everything else about the candidate is unchanged.  A promoted signal has
already cleared every gate in the chain except the loosened one — scoring,
MTF, min_confidence, the context floors, ``level_still_in_play``, dispatch
cooldown, staleness — and it still meets the router's second layer
(correlation lock, cooldowns, concurrency caps, same-direction throttle)
before anything reaches a subscriber.  Promotion removes exactly one gate,
for exactly the rows the rule describes, and nothing else.

**Measurement does not stop when a rule is switched on.**  A promoted row is
still written to the dark ledger and still walked by the dark resolver, with
``promoted: true`` and its delivery outcome stamped on it.  That is the whole
point: the population that justified the promotion keeps arriving after the
promotion, so the decision can be re-read against fresh rows rather than
frozen at the moment it was made.  Ops never pools the two — a promoted row
reached the router and a dark row did not, and averaging them would report a
feed size that never existed.

Six design rules, each one paid for elsewhere in this repo:

* **Fail closed, everywhere.**  Every dimension is an explicit allow-list and
  an empty list matches nothing, so a half-configured rule is inert rather
  than permissive.  ``decide`` catches every exception and answers "stay
  dark".  Absence of knowledge is not permission (``crypto_perp_admission``),
  and here the open path is a paid subscriber's feed.
* **Two flags, not one.**  ``dark_promotion_enabled`` is the engine-wide
  master switch and every rule carries its own ``enabled``.  The first is a
  kill switch for the mechanism; the second is the owner's per-path decision.
  Neither implies the other.
* **A bound you cannot compute in advance is a blast-radius cap, and it is
  counted.**  Nobody knows how many rows a rule will promote until it runs —
  the ledger is on the VPS and the router layer has never been applied to
  this population.  ``max_per_day`` bounds it, a candidate over the cap stays
  dark under its own reason (``daily_cap``), and the count is on screen.  A
  silent cap is a population shrinking for a reason the reader cannot see.
* **A refusal names its dimension.**  ``decide`` returns every unmet
  condition, not a bare False, so the ops panel can say *"matched the gate and
  the session, failed the regime"* instead of leaving the owner to guess which
  half of his rule is wrong.
* **The registry is read off one writer.**  Ops renders the rules this module
  returns; it holds no copy and mirrors no enum.  The fix for a drifting
  mirror is not a second mirror (``MEASUREMENT_SUFFIXES``).
* **Not a hot-path read.**  The rule set lives in memory behind a generation
  counter and is re-read from disk only when a write bumps it.  ``decide``
  runs per diverted candidate, which is a scan-rate path (Cost Discipline).

Direction alignment is the condition this module was built around, and it is
worth stating because the obvious rule is the wrong one.
``REGIME_SETUP_COMPATIBILITY`` blocks ``LIQUIDITY_SWEEP_REVERSAL`` in
``STRONG_TREND`` because a sweep-reversal *against* a strong trend is the
setup's known failure mode.  That reasoning is sound and the matrix cannot
express it: it blocks the setup class, not the direction, so it also blocks a
sweep of a high in a downtrend — which is with-trend and is 20 of the 43
measured rows, at +1.354% each.  ``with_trend`` is how a rule keeps the
doctrine and admits the rows it was never meant to exclude.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional, Tuple

from src import fail_open
from src import ledger_schema
from src.utils import get_logger

log = get_logger("dark_promotion")

#: Registry schema. Readers gate on this, never on a date (#802).
REGISTRY_SCHEMA = 1

#: Older schemas this build reads unchanged. EMPTY, and that is a decision
#: rather than an oversight: there has only ever been one schema, so there is
#: nothing older to accept. When this is bumped, ask the question
#: ``ledger_schema`` exists to force — does the change only ADD fields, or does
#: it redefine one? Additive belongs here; redefining does not, because old and
#: new rules would then disagree about what a condition *means*, and a rule
#: reinterpreted rather than dropped is a promotion nobody authorised.
ADDITIVE_FROM_SCHEMAS: frozenset = frozenset()

#: Wildcard token. ``["*"]`` on a dimension means "any value of this
#: dimension"; ``[]`` means "nothing matches" and makes the rule inert.
#:
#: Both are deliberate. An empty list *could* have meant "unrestricted" — it
#: reads that way in most config — and that is exactly the reading that turns
#: a half-finished rule into a live promotion of everything the path emits.
#: The owner has to type the wildcard, so the permissive case is a choice
#: somebody made rather than a field somebody forgot.
ANY = "*"

#: Direction conditions. ``with_trend`` / ``counter_trend`` are resolved
#: against the row's own entry regime, and abstain (no promotion) when that
#: regime names no trend — an unknown trend is not an aligned one.
DIR_ANY = "any"
DIR_LONG = "long"
DIR_SHORT = "short"
DIR_WITH_TREND = "with_trend"
DIR_COUNTER_TREND = "counter_trend"
DIRECTIONS: Tuple[str, ...] = (
    DIR_ANY,
    DIR_LONG,
    DIR_SHORT,
    DIR_WITH_TREND,
    DIR_COUNTER_TREND,
)

#: Dimension names, used for the ``unmet`` list and by the ops form. Order is
#: the order a reader should check them in: the gate is what the rule is
#: *about*, the rest narrow it.
DIM_GATE = "gate"
DIM_REGIME = "regime"
DIM_SESSION = "session"
DIM_DIRECTION = "direction"
DIM_CONFIDENCE = "confidence"
DIM_CAP = "daily_cap"
DIM_MASTER = "master_switch"
DIM_RULE = "rule_enabled"
DIM_NO_RULE = "no_rule"

#: Where the registry is persisted. On the engine's data volume, which ops
#: mounts read-only — but ops reads the rules through the API rather than off
#: this file, because a control surface must read its state back from the
#: thing that enforces it (control doctrine), not from a file beside it.
REGISTRY_PATH = os.getenv(
    "DARK_PROMOTION_REGISTRY", "data/dark_promotions_v1.json"
)

#: Default blast-radius cap for a new rule, per UTC day, per rule.
DEFAULT_MAX_PER_DAY = int(os.getenv("DARK_PROMOTION_DEFAULT_CAP", "25"))


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _norm_list(values: Optional[Iterable[Any]]) -> List[str]:
    """Normalise an allow-list, preserving the wildcard and dropping blanks."""
    out: List[str] = []
    for raw in values or ():
        token = str(raw or "").strip()
        if not token:
            continue
        token = token if token == ANY else token.upper()
        if token not in out:
            out.append(token)
    return out


def _matches(allowed: List[str], value: str) -> bool:
    if not allowed:
        return False
    if ANY in allowed:
        return True
    return _norm(value) in allowed


def trend_of(regime: Any) -> Optional[str]:
    """The trend direction a regime label names, or ``None``.

    Deliberately substring-based rather than an enumeration of labels. The
    regime vocabulary is the detector's to own and it has gained labels
    before; a list kept here would be silent by construction on the next one,
    which is the ``is_tradfi_perp`` deny-list wearing yet another hat. What
    this needs is narrower than the label set — *does this word say up or
    down* — and that survives a new label.

    ``None`` for a range, and ``None`` is not "no". A caller asking for
    with-trend alignment must abstain here, never assume: an unknown trend is
    the case the doctrine is most worried about.
    """
    token = _norm(regime)
    if not token:
        return None
    up = "UP" in token or "BULL" in token or "MARKUP" in token
    down = "DOWN" in token or "BEAR" in token or "MARKDOWN" in token
    if up and not down:
        return "UP"
    if down and not up:
        return "DOWN"
    return None


@dataclass
class PromotionRule:
    """One path's promotion conditions.

    ``enabled`` is the master switch the owner flips; every other field
    narrows *which* of the path's dark rows it applies to. A rule with
    ``enabled`` true and an empty ``gates`` list promotes nothing, and the ops
    panel says so rather than showing a switch that appears to be on.
    """

    setup_class: str
    enabled: bool = False
    gates: List[str] = field(default_factory=list)
    regimes: List[str] = field(default_factory=lambda: [ANY])
    sessions: List[str] = field(default_factory=lambda: [ANY])
    direction: str = DIR_ANY
    min_confidence: Optional[float] = None
    max_per_day: int = DEFAULT_MAX_PER_DAY
    note: str = ""
    updated_at: Optional[float] = None
    updated_by: str = ""

    def normalised(self) -> "PromotionRule":
        direction = str(self.direction or DIR_ANY).strip().lower()
        if direction not in DIRECTIONS:
            direction = DIR_ANY
        conf: Optional[float]
        try:
            conf = None if self.min_confidence is None else float(self.min_confidence)
        except (TypeError, ValueError):
            conf = None
        try:
            cap = max(0, int(self.max_per_day))
        except (TypeError, ValueError):
            cap = DEFAULT_MAX_PER_DAY
        return replace(
            self,
            setup_class=_norm(self.setup_class),
            enabled=bool(self.enabled),
            gates=_norm_list(self.gates),
            regimes=_norm_list(self.regimes),
            sessions=_norm_list(self.sessions),
            direction=direction,
            min_confidence=conf,
            max_per_day=cap,
            note=str(self.note or ""),
        )

    @property
    def inert(self) -> bool:
        """Enabled, and yet incapable of promoting anything.

        A real state and its own word. An operator looking at a switch in the
        on position is entitled to assume it does something; this is what the
        panel badges when it does not.
        """
        return bool(self.enabled) and not (
            self.gates and self.regimes and self.sessions
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "setup_class": self.setup_class,
            "enabled": bool(self.enabled),
            "gates": list(self.gates),
            "regimes": list(self.regimes),
            "sessions": list(self.sessions),
            "direction": self.direction,
            "min_confidence": self.min_confidence,
            "max_per_day": int(self.max_per_day),
            "note": self.note,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
            "inert": self.inert,
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "PromotionRule":
        return cls(
            setup_class=str(raw.get("setup_class") or ""),
            enabled=bool(raw.get("enabled")),
            gates=list(raw.get("gates") or []),
            regimes=list(raw.get("regimes") or []),
            sessions=list(raw.get("sessions") or []),
            direction=str(raw.get("direction") or DIR_ANY),
            min_confidence=raw.get("min_confidence"),
            max_per_day=raw.get("max_per_day", DEFAULT_MAX_PER_DAY),
            note=str(raw.get("note") or ""),
            updated_at=raw.get("updated_at"),
            updated_by=str(raw.get("updated_by") or ""),
        ).normalised()


@dataclass
class PromotionDecision:
    """Why a diverted candidate is, or is not, being promoted.

    ``unmet`` carries every dimension that failed, not the first one. A rule
    is a conjunction and an owner debugging it wants to know whether he missed
    one condition or four — reporting only the first turns one edit into a
    sequence of them, each revealing the next failure.
    """

    promote: bool
    setup_class: str = ""
    gate: str = ""
    unmet: List[str] = field(default_factory=list)
    matched: List[str] = field(default_factory=list)
    rule: Optional[PromotionRule] = None
    detail: str = ""

    def to_row(self) -> Dict[str, Any]:
        """The block stamped onto the dark ledger row."""
        return {
            "promoted": bool(self.promote),
            "promotion_gate": self.gate,
            "promotion_unmet": list(self.unmet),
            "promotion_direction": (self.rule.direction if self.rule else None),
            "promotion_note": self.detail or None,
        }


# --------------------------------------------------------------------------- #
# Registry — in memory, generation-gated, persisted on write
# --------------------------------------------------------------------------- #

_lock = RLock()
_rules: Dict[str, PromotionRule] = {}
_generation: int = 0
_loaded: bool = False
#: ``{(setup_class, utc_day): count}`` — the blast-radius cap's counter.
_promoted_today: Dict[Tuple[str, str], int] = {}
#: Cumulative, since process start. Cheap and honest: a low number after a
#: deploy is a young process, not a quiet market, and the ops panel says so.
_counters: Dict[str, int] = {}

#: ``{setup_class: {"total", "by_dimension", "sole_blocker"}}`` — which
#: condition is actually refusing, cumulative since process start.
#:
#: This exists because the module's own docstring promised it and the code did
#: not deliver it (2026-08-17). ``decide`` has always computed the full
#: ``unmet`` list — *"so the ops panel can say 'matched the gate and the
#: session, failed the regime' instead of leaving the owner to guess which half
#: of his rule is wrong"* — and then every caller threw it away: the scanner's
#: refusal branch calls ``dark_emission.publish(sig)`` with no decision, and
#: the only counter was ``unmet:{setup_class}``, one integer over five
#: dimensions. So the owner armed two rules against 610 diverted
#: `LIQUIDITY_SWEEP_REVERSAL` candidates in one window, got zero promotions,
#: and neither he nor this engine could say which condition was responsible.
#: A docstring asserting a property the code beneath it does not have, checkable
#: in one command — the shape this repo has now paid for under five names.
_refusals: Dict[str, Dict[str, Any]] = {}

#: Recent refusals, with the values that failed. The counters say how *much*;
#: this says *what* — a rule wanting `with_trend` against rows stamped
#: `RANGING` is obvious in one sample and invisible in any total.
#:
#: Bounded, and the bound is published beside it: a capped ring makes every
#: verdict on it a sample, and the cap is invisible unless printed.
NEAR_MISS_RING = int(os.getenv("DARK_PROMOTION_NEAR_MISS_RING", "60"))
_near_misses: List[Dict[str, Any]] = []
#: Unbounded, beside the bounded ring, so the newest few cannot read as the
#: whole population.
_near_miss_seen: int = 0

#: Every dimension ``decide`` can refuse on, in the order a reader checks them.
#: Derived from the ``DIM_*`` constants rather than retyped, so a dimension
#: added to the rule cannot be silently absent from the census that explains it.
REFUSAL_DIMENSIONS: Tuple[str, ...] = (
    DIM_GATE,
    DIM_REGIME,
    DIM_SESSION,
    DIM_DIRECTION,
    DIM_CONFIDENCE,
    DIM_CAP,
)


def _utc_day(now: Optional[float] = None) -> str:
    ts = time.time() if now is None else float(now)
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _count(key: str) -> None:
    _counters[key] = _counters.get(key, 0) + 1


def _record_refusal(
    sig: Any,
    setup_class: str,
    gate: str,
    unmet: List[str],
    matched: List[str],
    detail: str,
    now: Optional[float] = None,
) -> None:
    """Record which condition refused this candidate, and on what values.

    Two numbers per dimension, and they answer different questions:

    * ``by_dimension`` — how often this condition failed *at all*. A rule is a
      conjunction, so several dimensions can fail on one candidate and these
      deliberately sum to more than ``total``.
    * ``sole_blocker`` — how often it was the **only** thing standing in the
      way. That is the actionable number: relax this one condition and exactly
      this many candidates promote. The marginal count cannot say that, and the
      ops promotions panel offers its evidence marginally — one table per
      dimension — while the rule it builds is a conjunction. A reader picking
      the best-looking cell of each table can select an intersection that is
      empty, and nothing on that page could tell him.

    In-memory dict work on a scan-rate path: no I/O, no allocation beyond one
    small dict per refusal (Cost Discipline).

    Taken under the registry lock, and that is not belt-and-braces: ``decide``
    runs on the scanner's event loop while :func:`runtime_report` is called from
    the snapshot writer's **thread pool**, so an unguarded dict would eventually
    raise *"dictionary changed size during iteration"* in the reader — and the
    block would then silently stop publishing, which is the failure this whole
    change exists to remove. The lock is already on this path (``decide`` →
    ``get_rule`` → ``load`` takes it), so it costs nothing new.
    """
    global _near_miss_seen
    sample = {
        "ts": time.time() if now is None else float(now),
        "symbol": str(getattr(sig, "symbol", "") or ""),
        "setup_class": setup_class,
        "side": str(
            getattr(getattr(sig, "direction", None), "value", None)
            or getattr(sig, "direction", "")
            or ""
        ),
        "gate": gate,
        # The observed values, not the rule's — the owner is comparing what he
        # asked for against what the engine actually stamped, and only one of
        # those two is already on his screen.
        "regime": str(getattr(sig, "entry_regime", "") or ""),
        "regime_15m": str(getattr(sig, "entry_regime_15m", "") or ""),
        "session": str(getattr(sig, "mc_session", "") or ""),
        "confidence": float(getattr(sig, "confidence", 0.0) or 0.0),
        "unmet": list(unmet),
        "matched": list(matched),
        "detail": detail or "",
    }
    try:
        with _lock:
            cell = _refusals.setdefault(
                setup_class,
                {"total": 0, "by_dimension": {}, "sole_blocker": {}},
            )
            cell["total"] += 1
            by_dim = cell["by_dimension"]
            for dim in unmet:
                by_dim[dim] = by_dim.get(dim, 0) + 1
            if len(unmet) == 1:
                sole = cell["sole_blocker"]
                sole[unmet[0]] = sole.get(unmet[0], 0) + 1

            _near_miss_seen += 1
            _near_misses.append(sample)
            if len(_near_misses) > max(1, NEAR_MISS_RING):
                del _near_misses[:-max(1, NEAR_MISS_RING)]
    except Exception as exc:  # pragma: no cover - defensive
        # A census failing must never be the reason a candidate is mishandled,
        # and it must never be silent either.
        fail_open.record("dark_promotion.record_refusal", exc)


def master_enabled() -> bool:
    """The engine-wide switch, read live from the tunables store.

    Fail-closed on any error, which is the opposite of ``dark_emission.enabled``
    and deliberately so: that switch decides whether a measurement runs, this
    one decides whether a candidate reaches a subscriber.
    """
    try:
        from src import runtime_tunables as _rt

        return bool(_rt.get("dark_promotion_enabled"))
    except Exception as exc:
        fail_open.record("dark_promotion.master_enabled", exc)
        return False


def _registry_path() -> Path:
    return Path(REGISTRY_PATH)


def load(force: bool = False) -> None:
    """Read the registry from disk.

    Called once at first use and again after a write. A missing file is an
    empty registry and not an error — no rule has ever been created — while an
    unreadable one is counted and leaves the in-memory set untouched, because
    *could not read* and *there is nothing here* have different fixes and only
    one of them should quietly disarm every rule.
    """
    global _loaded
    with _lock:
        if _loaded and not force:
            return
        path = _registry_path()
        try:
            if not path.exists():
                _loaded = True
                return
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail_open.record("dark_promotion.load", exc)
            _loaded = True
            return
        if not isinstance(raw, dict):
            _loaded = True
            return
        # Through `ledger_schema`, never a bare `!=` — the comparison that cost
        # this repo 371 SAR arms. Forward-reading is refused there for the
        # reason that matters most here: an older build meeting a newer file
        # would be guessing what a condition it has never seen means, and the
        # guess would decide which rows reach subscribers.
        _ok, _why = ledger_schema.accepts(
            raw.get("schema"), REGISTRY_SCHEMA, ADDITIVE_FROM_SCHEMAS
        )
        if not _ok:
            log.warning(
                "dark_promotion registry refused ({}) — no rule is armed, so "
                "every dark row stays diverted", _why,
            )
            _loaded = True
            return
        rules: Dict[str, PromotionRule] = {}
        for item in raw.get("rules") or []:
            try:
                rule = PromotionRule.from_dict(item)
            except Exception as exc:  # pragma: no cover - defensive
                fail_open.record("dark_promotion.load_rule", exc)
                continue
            if rule.setup_class:
                rules[rule.setup_class] = rule
        _rules.clear()
        _rules.update(rules)
        _loaded = True


def _persist() -> None:
    path = _registry_path()
    payload = {
        "schema": REGISTRY_SCHEMA,
        "written_at": time.time(),
        "rules": [r.to_dict() for r in _rules.values()],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, path)
    except Exception as exc:
        fail_open.record("dark_promotion.persist", exc)


def generation() -> int:
    """Bumped on every write. A consumer caching a decision gates on this."""
    return _generation


def get_rule(setup_class: Any) -> Optional[PromotionRule]:
    load()
    with _lock:
        return _rules.get(_norm(setup_class))


def all_rules() -> List[PromotionRule]:
    load()
    with _lock:
        return sorted(_rules.values(), key=lambda r: r.setup_class)


def set_rule(rule: PromotionRule) -> PromotionRule:
    """Create or replace one path's rule, and persist it.

    Returns the **stored** rule rather than the argument. The normaliser drops
    an unrecognised direction and clamps the cap, so echoing the request would
    report a setting that is not what the engine will enforce — the defect
    ``/api/admin/users/exit-mechanism`` avoided by reading its value back
    (#911), arriving one control over.
    """
    global _generation
    load()
    stored = rule.normalised()
    if not stored.setup_class:
        raise ValueError("setup_class is required")
    stored.updated_at = time.time()
    with _lock:
        _rules[stored.setup_class] = stored
        _generation += 1
        _persist()
    log.info(
        "[PROMOTION] {} enabled={} gates={} regimes={} sessions={} dir={} cap={}",
        stored.setup_class, stored.enabled, stored.gates, stored.regimes,
        stored.sessions, stored.direction, stored.max_per_day,
    )
    return stored


def delete_rule(setup_class: Any) -> bool:
    global _generation
    load()
    key = _norm(setup_class)
    with _lock:
        if key not in _rules:
            return False
        del _rules[key]
        _generation += 1
        _persist()
    log.info("[PROMOTION] {} rule removed", key)
    return True


def reset_for_test(path: Optional[str] = None) -> None:
    """Drop all in-memory state. Tests only; never called by the engine."""
    global _rules, _generation, _loaded, _promoted_today, _counters, REGISTRY_PATH
    global _near_miss_seen
    with _lock:
        if path is not None:
            REGISTRY_PATH = path
        _rules = {}
        _generation = 0
        _loaded = False
        _promoted_today = {}
        _counters = {}
        # Cleared in place, not rebound: `reset_refusals_for_test` and every
        # reader hold a reference to this dict, and rebinding would leave them
        # looking at the old one.
        _refusals.clear()
        _near_misses.clear()
        _near_miss_seen = 0


# --------------------------------------------------------------------------- #
# The decision
# --------------------------------------------------------------------------- #


def promoted_today(setup_class: Any, now: Optional[float] = None) -> int:
    return _promoted_today.get((_norm(setup_class), _utc_day(now)), 0)


def decide(sig: Any, gate: str, now: Optional[float] = None) -> PromotionDecision:
    """Should this diverted candidate be enqueued for real?

    Called at the divert site with a candidate that is already marked dark, so
    the default answer is the safe one and every path out of here that is not
    an explicit match returns it. The exception handler answers "stay dark"
    for the same reason: a measurement failing must never be the thing that
    puts a signal in front of a subscriber.
    """
    setup_class = _norm(getattr(sig, "setup_class", ""))
    try:
        if not master_enabled():
            return PromotionDecision(False, setup_class, gate, [DIM_MASTER])
        rule = get_rule(setup_class)
        if rule is None:
            return PromotionDecision(False, setup_class, gate, [DIM_NO_RULE])
        if not rule.enabled:
            return PromotionDecision(False, setup_class, gate, [DIM_RULE], rule=rule)

        unmet: List[str] = []
        matched: List[str] = []

        (matched if _matches(rule.gates, gate) else unmet).append(DIM_GATE)

        regime = str(getattr(sig, "entry_regime", "") or "")
        (matched if _matches(rule.regimes, regime) else unmet).append(DIM_REGIME)

        session = str(getattr(sig, "mc_session", "") or "")
        (matched if _matches(rule.sessions, session) else unmet).append(DIM_SESSION)

        side = str(
            getattr(getattr(sig, "direction", None), "value", None)
            or getattr(sig, "direction", "")
            or ""
        )
        ok_dir, dir_detail = _direction_ok(rule.direction, side, sig)
        (matched if ok_dir else unmet).append(DIM_DIRECTION)

        if rule.min_confidence is not None:
            try:
                conf = float(getattr(sig, "confidence", 0.0) or 0.0)
            except (TypeError, ValueError):
                conf = 0.0
            (matched if conf >= rule.min_confidence else unmet).append(DIM_CONFIDENCE)

        if unmet:
            _count(f"unmet:{setup_class}")
            _record_refusal(
                sig, setup_class, gate, unmet, matched, dir_detail, now
            )
            return PromotionDecision(
                False, setup_class, gate, unmet, matched, rule, dir_detail
            )

        # Every condition met — the cap is the last thing between here and a
        # subscriber, and it is checked last on purpose: a candidate refused
        # for the cap matched the rule, which is a different finding from one
        # that did not, and pooling them would hide a rule running at its
        # bound behind a rule that never fires.
        day = _utc_day(now)
        used = _promoted_today.get((setup_class, day), 0)
        if rule.max_per_day and used >= rule.max_per_day:
            _count(f"capped:{setup_class}")
            _cap_detail = f"{used}/{rule.max_per_day} promoted today"
            # Counted in the census too, and as its own dimension. A rule
            # running at its bound and a rule that never matches are opposite
            # findings — the first is working and throttled, the second is
            # misconfigured — and pooling them is what the cap check being last
            # exists to prevent.
            _record_refusal(
                sig, setup_class, gate, [DIM_CAP], matched, _cap_detail, now
            )
            return PromotionDecision(
                False, setup_class, gate, [DIM_CAP], matched, rule, _cap_detail,
            )
        return PromotionDecision(
            True, setup_class, gate, [], matched, rule, dir_detail
        )
    except Exception as exc:
        fail_open.record("dark_promotion.decide", exc)
        return PromotionDecision(False, setup_class, gate, ["error"])


def _direction_ok(condition: str, side: str, sig: Any) -> Tuple[bool, str]:
    """Resolve a direction condition against the candidate.

    The trend is read from the signal's own ``entry_regime`` — the label
    stamped where it became true — and its 15m sibling is consulted only when
    the 5m label names no trend. Two classifiers can disagree and the trigger
    timeframe's answer is the one a 5m entry acts on; the 15m read is a
    fallback for a range label, not an override of a trend one.
    """
    side_u = _norm(side)
    if condition == DIR_ANY:
        return True, ""
    if condition == DIR_LONG:
        return side_u == "LONG", ""
    if condition == DIR_SHORT:
        return side_u == "SHORT", ""
    trend = trend_of(getattr(sig, "entry_regime", ""))
    source = "entry_regime"
    if trend is None:
        trend = trend_of(getattr(sig, "entry_regime_15m", ""))
        source = "entry_regime_15m"
    if trend is None:
        # Abstain. An unknown trend is not an aligned one, and this is the
        # exact case `REGIME_SETUP_COMPATIBILITY` is protecting against.
        return False, "trend_unknown"
    aligned = (trend == "UP" and side_u == "LONG") or (
        trend == "DOWN" and side_u == "SHORT"
    )
    want = condition == DIR_WITH_TREND
    return (aligned is want), f"trend={trend} via {source}"


def note_promoted(setup_class: Any, now: Optional[float] = None) -> None:
    """Record that one candidate was promoted. Charges the daily cap.

    Separate from ``decide`` so the cap is charged where the promotion
    actually happens rather than where it is contemplated. A decision that the
    caller then fails to act on — a ledger write that refuses the row, an
    exception between the two — must not consume budget, or the bound stops
    describing what reached anyone.
    """
    key = (_norm(setup_class), _utc_day(now))
    _promoted_today[key] = _promoted_today.get(key, 0) + 1
    _count(f"promoted:{_norm(setup_class)}")


def runtime_report(now: Optional[float] = None) -> Dict[str, Any]:
    """The half of the snapshot that only the process running ``decide`` knows.

    Split out from :func:`snapshot` because **which process holds the state is
    not a deployment detail**. In isolated mode the ops control panel is served
    by the API container, which loads the registry file happily (shared volume)
    and has never evaluated a single candidate — so every counter here reads
    zero there, and ``promoted_today`` reads zero on every rule, forever. That
    is the ``/internal/diag/trail-governor`` ``INDEX COLD`` defect exactly, and
    it is worse on this page: zero is also what a correctly-armed rule reads
    before it fires, so the wrong number is indistinguishable from the right
    one and only becomes visibly wrong once the rule starts working.

    The engine publishes this block to Redis and the API prefers it, the same
    publish-then-read shape as the positions / data-intake / trail-governor
    X-rays. ``source`` names which process produced it, because a panel that
    cannot say whose counters it is showing is one deploy away from the same
    bug.
    """
    day = _utc_day(now)
    # Every read of process-local state happens under the lock: this runs on
    # the snapshot writer's thread while `decide` writes from the scanner's
    # event loop, and an unguarded iteration raises rather than returning a
    # slightly-stale answer.
    with _lock:
        counters = dict(_counters)
        promoted = {
            setup: count
            for (setup, d), count in _promoted_today.items()
            if d == day
        }
        refusals = {
            setup: {
                "total": int(cell.get("total") or 0),
                "by_dimension": dict(cell.get("by_dimension") or {}),
                "sole_blocker": dict(cell.get("sole_blocker") or {}),
            }
            for setup, cell in _refusals.items()
        }
        near_misses = list(_near_misses)
        seen = int(_near_miss_seen)
    return {
        "source": "engine",
        "generated_at": time.time() if now is None else float(now),
        "utc_day": day,
        "counters": counters,
        "promoted_today": promoted,
        "refusals": refusals,
        "refusal_dimensions": list(REFUSAL_DIMENSIONS),
        "near_misses": near_misses,
        # The ring's bound and the unbounded count it is a sample of. A capped
        # buffer feeding a statistic must publish its denominator.
        "near_miss_ring": int(NEAR_MISS_RING),
        "near_miss_seen": seen,
    }


def reset_refusals_for_test() -> None:
    """Clear only the refusal census. Tests only; never called by the engine."""
    global _near_miss_seen
    with _lock:
        _refusals.clear()
        _near_misses.clear()
        _near_miss_seen = 0


def top_blocker(setups: Iterable[Any]) -> str:
    """One sentence naming what is refusing these setups' candidates.

    For the liveness probe and any other single-line reader. Empty string when
    nothing has been refused — *no candidate reached the decision* and *every
    candidate was refused* are different states and must not share a caption.

    Reports the most common **sole** blocker where there is one, because that
    is the condition whose removal actually changes the outcome, and falls back
    to the marginal leader when every refusal had several conditions failing at
    once — a rule failing on four dimensions has no single edit that fixes it,
    and saying so is the honest answer.
    """
    total = 0
    sole: Dict[str, int] = {}
    marginal: Dict[str, int] = {}
    with _lock:
        for setup in setups:
            cell = _refusals.get(_norm(setup))
            if not cell:
                continue
            total += int(cell.get("total") or 0)
            for dim, n in (cell.get("sole_blocker") or {}).items():
                sole[dim] = sole.get(dim, 0) + int(n)
            for dim, n in (cell.get("by_dimension") or {}).items():
                marginal[dim] = marginal.get(dim, 0) + int(n)
    if not total:
        return ""
    if sole:
        dim, n = max(sole.items(), key=lambda kv: (kv[1], kv[0]))
        return (
            f"{total} candidate(s) refused, {n} on `{dim}` alone "
            f"(relaxing it would promote those)"
        )
    dim, n = max(marginal.items(), key=lambda kv: (kv[1], kv[0]))
    return (
        f"{total} candidate(s) refused, none on one condition alone; "
        f"`{dim}` failed most often ({n})"
    )


def snapshot(now: Optional[float] = None) -> Dict[str, Any]:
    """Everything the ops control panel renders. One writer, one reader.

    The ``runtime`` block is process-local — see :func:`runtime_report`. The
    rules themselves are file-backed and therefore correct in either container.
    """
    load()
    day = _utc_day(now)
    runtime = runtime_report(now)
    rules = []
    for rule in all_rules():
        entry = rule.to_dict()
        entry["promoted_today"] = _promoted_today.get((rule.setup_class, day), 0)
        rules.append(entry)
    return {
        "schema": REGISTRY_SCHEMA,
        "master_enabled": master_enabled(),
        "dark_lane_enabled": _dark_lane_enabled(),
        "utc_day": day,
        "rules": rules,
        "directions": list(DIRECTIONS),
        "any_token": ANY,
        "default_max_per_day": DEFAULT_MAX_PER_DAY,
        "counters": dict(_counters),
        "generation": _generation,
        "runtime": runtime,
    }


def apply_runtime(snap: Dict[str, Any], runtime: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Overlay an engine-published runtime block onto a locally-built snapshot.

    Called by the API handler in isolated mode. Overwrites exactly the fields
    that are process-local, and leaves the file-backed rule set alone —
    including each rule's ``promoted_today``, which is the cap's counter and
    lives with the process that charges it.

    A ``None`` runtime leaves the snapshot untouched rather than blanking it:
    *the engine has not published* and *nothing has been promoted* are
    different states, and ``source`` on the surviving block says which process
    the numbers came from.
    """
    if not isinstance(runtime, dict) or not runtime:
        return snap
    snap["runtime"] = runtime
    if isinstance(runtime.get("counters"), dict):
        snap["counters"] = dict(runtime["counters"])
    promoted = runtime.get("promoted_today")
    if isinstance(promoted, dict):
        for entry in snap.get("rules") or []:
            if isinstance(entry, dict):
                entry["promoted_today"] = int(
                    promoted.get(entry.get("setup_class"), 0) or 0
                )
    return snap


def _dark_lane_enabled() -> bool:
    """Is the lane that produces the rows these rules act on even running?

    Published beside ``master_enabled`` because a promotion rule with the dark
    lane switched off is not merely idle — the candidates it would promote are
    being killed by the gate outright, upstream of anything this module sees.
    An operator reading one switch without the other would see a rule that is
    on and does nothing, with no way to tell which half is missing.
    """
    try:
        from src import dark_emission

        return bool(dark_emission.enabled())
    except Exception as exc:  # pragma: no cover - defensive
        fail_open.record("dark_promotion.dark_lane_enabled", exc)
        return False
