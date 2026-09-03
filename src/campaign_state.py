"""What the last trade on this ``(symbol, setup_class, direction)`` did.

Owner-directed, 2026-09-02, off a guest-session read of the 90-day delivered
book.  Split ``MOVER_TREND_PULLBACK`` by the outcome of the *previous* signal
on the same symbol and side — a fact fully knowable at entry time — and the
path separates in a way none of its stamped entry features do::

    previous leg won   n=145  camps=66  +0.969%/trade  CI95 [+0.440, +1.506]
    first entry        n=261  camps=261 -0.136%/trade  CI95 [-0.502, +0.248]
    break-even/expiry  n=116  camps=59  -0.112%/trade  CI95 [-0.858, +0.564]
    previous stopped   n=153  camps=84  -0.304%/trade  CI95 [-0.769, +0.182]

MVRTP's entire positive contribution to the book is the first row; every other
bucket loses.  Two things about that measurement decide the shape of this
module, and both were checked before it was written.

**It does not generalise off MVRTP, and the module must not imply it does.**
Over every other path the same split reads +0.017% after a winner against
+0.123% after a stop — no effect at all.  This is momentum continuation on
promoted movers, not a property of the book, so what ships here is a *stamp on
every path* and a rule on none.  The lane's own history is the argument: the
first cut of the entry-feature generalisation copied MVRTP's feature list onto
paths whose entries turn on different variables, and the columns measured
nothing (``entry_features``' module docstring).  Recording a fact on every path
is how the non-effect stays re-checkable; acting on it everywhere is not.

**The effect is a window, not a state, and a stamp without the clock could not
express it.**  Splitting the winner bucket by hours since that winner *closed*::

    0-2h   n=64  +1.409%  CI95 [+0.788, +2.187]
    2-6h   n=35  +1.423%  CI95 [+0.150, +2.783]
    6-24h  n=17  -0.027%  CI95 [-1.636, +1.585]
    >24h   n=27  +0.056%  CI95 [-1.216, +1.305]

Both intervals inside six hours exclude zero and both beyond it collapse onto
it.  A row carrying only "the previous leg won" would have pooled a live
continuation with a symbol that worked last Tuesday, and any rule built on it
would have been measured on the pooled column.  So ``prev_age_h`` is recorded
beside the outcome and is not optional: the promoted-mover TTL is six hours,
which is the same window arriving from the other side.

Why this is a module and not four lines in the scanner
-----------------------------------------------------
The key is already in the scanner three times over — ``_cooldown_key_for``
builds ``(symbol, setup_class, direction)`` for the dispatch cooldown, the
loss-streak escalation and the active-duplicate guard.  This is a fourth
consumer of that same key, and it is deliberately *not* a fourth private dict:
the writer is the terminal-outcome path in the scanner and the reader is
``entry_features.stamp``, which runs inside an evaluator that cannot see the
scanner at all.  One module both sides import is the only shape where there is
one writer, one reader, and no import cycle.

Cost, because a scan-path read is where this file's Cost Discipline section
gets written: :func:`read` is a dict lookup against process memory.  No
Firestore, no disk, no network.  :func:`record_outcome` writes — and it runs at
terminal transitions, dozens a day, which is the same budget
``_persist_loss_streaks`` already spends beside it.

This is STATE, not a measurement ledger — and that changes the ANSWER, not the API
---------------------------------------------------------------------------------
A measurement ledger's old rows are evidence, so a loader that drops them on an
additive bump silently destroys the window an adoption decision reads (371 SAR
arms, 2026-08-09).  This file holds *current* state with a seven-day horizon:
losing it costs a few hours of leg history that rebuilds itself on the next
closes, and no analysis reads it.

That is an argument for ``ADDITIVE_FROM_SCHEMAS = frozenset()`` — the empty
answer, chosen out loud — and **not** an argument for hand-rolling the check.
The first cut of this module compared the stored schema against ``SCHEMA`` with
a bare inequality, under exactly the reasoning above, and
``tests/test_ledger_schema.py`` refused it: that guard is derived from the tree
precisely so a new module cannot inherit drop-everything by having a good story
for it.  (It scans source text, so it also refuses a docstring that spells the
old form out — which is why this paragraph names the shape in prose.)  ``accepts()`` takes the additive
set as a *required* argument for the same reason, and at schema 1 there is no
older schema to read — but when somebody bumps to 2 they will have to say which
kind of bump it is instead of getting the old behaviour by forgetting.

What is *not* different from a ledger is the load: a flush with no load is worse
than neither, because the first write after a deploy overwrites a file that
looked healthy on disk (2026-08-06).  :func:`load` exists, and the scanner calls
it.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from src import fail_open, ledger_schema
from src.utils import get_logger

log = get_logger(__name__)

#: On-disk shape. Bumped only when a field changes meaning; see the module
#: docstring for why an unknown schema starts empty here rather than migrating.
SCHEMA = 1

#: Older schemas this build reads unchanged.
#:
#: Empty, and deliberately so: this is current state with a seven-day horizon,
#: not evidence, so starting clean costs a few hours of leg history and no
#: analysis at all. Required by ``ledger_schema.accepts`` rather than defaulted,
#: so the next bump has to state which kind it is.
ADDITIVE_FROM_SCHEMAS: frozenset = frozenset()

_DEFAULT_PATH: str = os.getenv("CAMPAIGN_STATE_PATH", "data/campaign_state_v1.json")

#: How long a closed leg keeps describing a campaign.
#:
#: Seven days, and the number is a horizon rather than a threshold: the measured
#: effect is gone by six hours and the >24h bucket sits on zero, so anything
#: past a week is certainly a different move on the same ticker. It bounds the
#: file — 331 symbols x 15 setups x 2 sides is finite but a long-running process
#: accumulates every campaign it has ever seen — and it means ``leg_index``
#: counts *this* campaign rather than the symbol's lifetime history.
_MAX_AGE_SEC: float = float(os.getenv("CAMPAIGN_STATE_MAX_AGE_SEC", str(7 * 24 * 3600)))

#: Terminal labels that mean the thesis paid. Same set the loss-streak
#: escalation resets on, deliberately: two consumers of one key disagreeing
#: about what a win is would be the drift this module exists on the far side of.
WINNING_LABELS: frozenset = frozenset(
    {"TP1_HIT", "TP2_HIT", "TP3_HIT", "FULL_TP_HIT", "PROFIT_LOCKED"}
)

#: Terminal labels that mean it failed. Everything else — ``BREAKEVEN_EXIT``,
#: ``EXPIRED`` at a flat price — is neither, and is recorded under its own label
#: rather than folded into a loss. A break-even park is not evidence the thesis
#: failed, and the measurement above kept the two apart precisely because their
#: forward returns differ (-0.112% against -0.304%).
LOSING_LABELS: frozenset = frozenset({"SL_HIT", "INVALIDATED"})


@dataclass(frozen=True)
class CampaignRead:
    """What the registry knows about a campaign at one moment.

    ``prev_won`` is tri-state on purpose. ``None`` is "there is no previous
    leg", which is a real and common state (51% of the delivered book is a
    first entry) and is not the same fact as a previous leg that lost. Handing
    a first entry a ``0.0`` would be an em-dash rendered as a zero, one layer
    before the page that would render it.
    """

    #: Closed legs on this campaign inside the horizon, before this one. Always
    #: known — 0 on a first entry — which is what makes it the column a reader
    #: can grade the others' coverage against.
    leg_index: int
    #: Terminal label of the most recent closed leg, or "" if there is none.
    prev_outcome: str
    #: 1.0 won / 0.0 did not / None no previous leg.
    prev_won: Optional[float]
    #: Hours since that leg closed, or None if there is none.
    prev_age_h: Optional[float]
    #: Realised % of that leg, or None. Recorded because "won" is a label and
    #: the size of the win is not, and nothing else on the row carries it.
    prev_pnl_pct: Optional[float]

    @property
    def absence_reason(self) -> Optional[str]:
        """Why ``prev_won`` is absent, or None when it is present.

        A blank needs a cause before it gets a caption, and this one has
        exactly one cause worth naming: there was no previous leg. That is a
        fact about the campaign, not a dark upstream, and a probe that cannot
        tell them apart will page on the ordinary case.
        """
        return None if self.prev_won is not None else "first_leg"


_EMPTY = CampaignRead(
    leg_index=0, prev_outcome="", prev_won=None, prev_age_h=None, prev_pnl_pct=None
)


class CampaignRegistry:
    """In-memory campaign state, persisted at terminal transitions only."""

    def __init__(self, path: str = _DEFAULT_PATH) -> None:
        self._path = str(path or "")
        #: key -> {"n": int, "outcome": str, "closed_at": float, "pnl": float}
        self._state: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        #: Counted rather than logged: a registry that silently refused to read
        #: its own file looks exactly like a fresh deploy.
        self.load_errors: int = 0
        self.pruned: int = 0
        #: Why the last load refused, or None. `ledger_schema`'s own reasons —
        #: a newer file, a redefining schema and an unreadable one have three
        #: different next moves.
        self.refuse_reason: Optional[str] = None

    # -- reading -----------------------------------------------------------
    def read(
        self, key: Optional[Tuple[str, str, str]], now: Optional[float] = None
    ) -> CampaignRead:
        """The campaign's state, or the empty read. Never raises, never writes.

        A stale entry is treated as absent rather than deleted: this is the scan
        path, and a read that mutates shared state is a write with a different
        name. The prune happens where the registry is already being written.
        """
        if key is None:
            return _EMPTY
        entry = self._state.get(key)
        if not entry:
            return _EMPTY
        ts = float(entry.get("closed_at") or 0.0)
        age = (time.time() if now is None else float(now)) - ts
        if ts <= 0 or age > _MAX_AGE_SEC:
            return _EMPTY
        outcome = str(entry.get("outcome") or "")
        won: Optional[float]
        if outcome in WINNING_LABELS:
            won = 1.0
        elif outcome:
            won = 0.0
        else:
            won = None
        return CampaignRead(
            leg_index=int(entry.get("n") or 0),
            prev_outcome=outcome,
            prev_won=won,
            prev_age_h=(age / 3600.0) if age >= 0 else None,
            prev_pnl_pct=(
                float(entry["pnl"]) if entry.get("pnl") is not None else None
            ),
        )

    # -- writing -----------------------------------------------------------
    def record_outcome(
        self,
        key: Optional[Tuple[str, str, str]],
        outcome_label: str,
        pnl_pct: Optional[float] = None,
        closed_at: Optional[float] = None,
    ) -> bool:
        """Record a terminal outcome. Returns whether anything was stored.

        ``leg_index`` counts closed legs, so it increments here and nowhere
        else — a dispatched-but-still-open signal has no outcome yet and must
        not advance a counter a rule would read as evidence.
        """
        if key is None or not outcome_label:
            return False
        # Prune BEFORE inserting, never after: pruning after would delete the
        # row just written whenever its own `closed_at` is already past the
        # horizon, which makes a write silently self-destructive for exactly
        # the backdated case a caller would use to replay history.
        self._prune()
        prior = self._state.get(key) or {}
        self._state[key] = {
            "n": int(prior.get("n") or 0) + 1,
            "outcome": str(outcome_label),
            "closed_at": time.time() if closed_at is None else float(closed_at),
            "pnl": None if pnl_pct is None else float(pnl_pct),
        }
        self.persist()
        return True

    def _prune(self, now: Optional[float] = None) -> int:
        cutoff = (time.time() if now is None else float(now)) - _MAX_AGE_SEC
        stale = [
            k for k, v in self._state.items()
            if float(v.get("closed_at") or 0.0) < cutoff
        ]
        for k in stale:
            self._state.pop(k, None)
        self.pruned += len(stale)
        return len(stale)

    # -- persistence -------------------------------------------------------
    def persist(self) -> bool:
        """Atomically write the registry. In-memory registries touch no disk.

        The ``path == ""`` guard is checked BEFORE the temp file is created,
        not after: a ledger whose "don't persist" hook still ran its atomic
        write left a ``.tmp`` in whatever the process cwd happened to be, which
        under pytest is the repo root, and then raised into ``fail_open`` on
        every test run for two months (2026-08-08). A no-op returns before the
        side effect.
        """
        if not self._path:
            return False
        from pathlib import Path

        path = Path(self._path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "schema": SCHEMA,
                "rows": {
                    "|".join(k): v for k, v in self._state.items()
                },
            }
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            tmp.replace(path)
            return True
        except OSError as exc:
            log.debug("campaign state persist failed: {}", exc)
            return False

    def load(self) -> int:
        """Read the registry back. Returns rows loaded. Best-effort.

        Called by the scanner at construction, beside ``_load_loss_streaks``.
        *Defining this is not calling it* — the guard against the 2026-08-06
        flush-without-load defect is the call site, not the method.
        """
        if not self._path:
            return 0
        from pathlib import Path

        path = Path(self._path)
        if not path.exists():
            return 0
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self.load_errors += 1
            return 0
        if not isinstance(data, dict):
            self.load_errors += 1
            return 0
        ok, refusal = ledger_schema.accepts(
            data.get("schema"), SCHEMA, ADDITIVE_FROM_SCHEMAS
        )
        if not ok:
            # Counted and named, never silent: an unreadable file and a fresh
            # deploy look identical otherwise.
            self.load_errors += 1
            self.refuse_reason = refusal
            return 0
        rows = data.get("rows")
        if not isinstance(rows, dict):
            self.load_errors += 1
            return 0
        loaded = 0
        for raw_key, entry in rows.items():
            if not isinstance(raw_key, str) or not isinstance(entry, dict):
                continue
            parts = raw_key.split("|")
            if len(parts) != 3:
                continue
            try:
                self._state[(parts[0], parts[1], parts[2])] = {
                    "n": int(entry.get("n") or 0),
                    "outcome": str(entry.get("outcome") or ""),
                    "closed_at": float(entry.get("closed_at") or 0.0),
                    "pnl": (
                        None if entry.get("pnl") is None else float(entry["pnl"])
                    ),
                }
                loaded += 1
            except (TypeError, ValueError):
                continue
        self._prune()
        return loaded

    # -- introspection -----------------------------------------------------
    def summary(self) -> Dict[str, Any]:
        """Counters for the liveness probe and the ops panel."""
        return {
            "campaigns": len(self._state),
            "with_win": sum(
                1 for v in self._state.values()
                if str(v.get("outcome") or "") in WINNING_LABELS
            ),
            "load_errors": self.load_errors,
            "refuse_reason": self.refuse_reason,
            "pruned": self.pruned,
            "max_age_sec": _MAX_AGE_SEC,
            "schema": SCHEMA,
        }


_REGISTRY: Optional[CampaignRegistry] = None


def get_registry() -> CampaignRegistry:
    """Process-wide registry, loaded from disk on first use."""
    global _REGISTRY
    if _REGISTRY is None:
        reg = CampaignRegistry()
        try:
            reg.load()
        except Exception as exc:  # noqa: BLE001 — state must never kill a boot
            fail_open.record("campaign_state.load", exc)
        _REGISTRY = reg
    return _REGISTRY


def reset_for_tests(path: str = "") -> CampaignRegistry:
    """Replace the process registry. ``path=""`` is in-memory and never writes."""
    global _REGISTRY
    _REGISTRY = CampaignRegistry(path=path)
    return _REGISTRY


def key_for(sig: Any) -> Optional[Tuple[str, str, str]]:
    """``(symbol, setup_class, direction)`` off a signal, or None.

    Mirrors ``Scanner._cooldown_key_for`` exactly, including the upper-casing
    and the all-three-or-nothing refusal, because a campaign keyed one way and
    a cooldown keyed another would be two different campaigns under one word.
    ``tests/test_campaign_state.py`` asserts the two agree on the same object
    rather than trusting this comment.
    """
    symbol = str(getattr(sig, "symbol", "") or "")
    setup_class = str(getattr(sig, "setup_class", "") or "")
    direction_obj = getattr(sig, "direction", None)
    direction = (
        direction_obj.value
        if direction_obj is not None and hasattr(direction_obj, "value")
        else str(direction_obj or "")
    ).upper()
    if not symbol or not setup_class or not direction:
        return None
    return (symbol, setup_class, direction)


def read_for(sig: Any, now: Optional[float] = None) -> CampaignRead:
    """The campaign read for a signal. Never raises into an evaluator."""
    try:
        return get_registry().read(key_for(sig), now=now)
    except Exception as exc:  # noqa: BLE001
        fail_open.record("campaign_state.read_for", exc)
        return _EMPTY
