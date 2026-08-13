"""Dynamic mover retention — keep a promoted pair while it is still working.

A promoted mover is held for a flat ``MOVER_PROMOTION_TTL_SEC`` (6 h) and then
dropped, whatever it did in that window. The owner's question (2026-08-13) is
the right one: *are we keeping unwanted pairs for six hours and dropping good
ones at six hours?* A fixed clock cannot answer, because it never looks at the
pair.

This module looks. It scores every held pair on what it is **doing right now**
and returns a verdict — hold, release, or extend — so the 30-slot budget goes
to pairs that are producing rather than to pairs that happened to be promoted
recently.

The one design rule, and everything else follows from it
--------------------------------------------------------

**Retention is scored on OPPORTUNITY and LIVENESS, never on OUTCOMES.**

That is not a stylistic preference. A dark row resolves up to six hours after
it is stamped, so profitability is simply not knowable inside a promotion
window — and if it were, gating on it would be fatal in a way this repo has
already paid for: drop a pair for bad outcomes → it produces no candidates →
it records no outcomes → it can never earn its way back. That is
``cohort_edge``'s absorbing state exactly (CLAUDE.md; a gate whose evidence
arrives only from what it lets through), which cost 23 days of a starved feed
and locked verdicts on a single day's data.

So this module answers *"is this pair still offering us setups"* and leaves
*"were those setups any good"* where it already lives — the dark ledger and
the closed-signal record, judged after the fact, on their own clock.

What it reads
-------------

Two independent signals, and they fail differently, so both are published and
neither is called *the* score:

* **Opportunity** — per-symbol counters through the scan chain: how many times
  we scanned it, how many candidates an evaluator produced, how many reached
  the enqueue choke point. A pair scanned fifty times that has produced no
  candidate is not offering setups, whatever its 24 h number says.
* **Liveness** — the move's own pulse, off the ``!ticker@arr`` stream the
  ignition detector already ingests: is the trade rate still elevated against
  the pair's own EWMA baseline, or has it settled back to normal? A spent move
  reads ~1.0× and is the "promote after the move, then fight it" failure the
  ignition detector's own docstring describes, caught on the way *out* instead
  of on the way in.

Neither is a proxy for the other. A pair can be structurally dead and still
throw candidates (an evaluator firing on stale structure), or be violently
alive and produce nothing (every gate rejecting it). The verdict says which of
the two is missing, because the fix differs: the first is ours to gate, the
second is the market being finished with the pair.

Why this ships measure-first
----------------------------

Releasing a pair early changes which symbols are scanned, which changes which
signals emit — a money-path change. So the scorer runs from the moment it
ships (measurement ON, per the two-flag rule) and stamps the verdict it
*would* have reached, while ``MOVER_RETENTION_ENFORCE`` decides whether the
promotion loop acts on it. The owner reads a window of would-be releases
before any pair is actually dropped.

Bounds, because an early-release mechanism can thrash
-----------------------------------------------------

* ``MOVER_RETENTION_MIN_HOLD_SEC`` — nothing is released before this. A pair
  promoted at minute zero of an ignition has produced nothing *yet*, and
  releasing it for that is measuring the clock rather than the pair.
* ``MOVER_RETENTION_MAX_HOLD_SEC`` — a ceiling on extension. "Still
  productive" must not mean "held forever": the ceiling is what keeps this a
  retention policy rather than a permanent universe expansion, and it bounds
  the blast radius of a scorer that is wrong in the generous direction.
* Every release is counted and named. A pair dropped for ``no_candidates`` and
  one dropped for ``move_spent`` are different findings with different fixes,
  and pooling them into "released" is how a page reports a fault that is not
  happening.

Cost: pure in-memory arithmetic over counters the scanner already increments
and state the ignition detector already holds. No new reads on any hot path.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src import fail_open
from src.utils import get_logger

log = get_logger("mover_retention")

#: Verdicts. `HOLD` is the quiet case and by far the most common — a pair
#: inside its normal window that is behaving. The other three are decisions.
HOLD = "hold"
RELEASE = "release"
EXTEND = "extend"
#: Too young to judge. Named apart from HOLD because "we are not releasing
#: this" and "we have not looked yet" are different states, and a panel that
#: pooled them would report a scorer as passing pairs it never scored.
WARMUP = "warmup"

#: Why a pair is being released. Separate reasons, never pooled.
REASON_NO_CANDIDATES = "no_candidates"      # scanned, produced nothing
REASON_MOVE_SPENT = "move_spent"            # trade rate back to baseline
REASON_TTL = "ttl"                          # reached the ceiling
#: Why it is being kept past the flat TTL.
REASON_PRODUCING = "producing"
#: Why no verdict was reached.
REASON_WARMUP = "warmup"
REASON_NO_ACTIVITY_DATA = "no_activity_data"

#: Minimum hold before a pair may be released for producing nothing. A pair
#: promoted at minute zero has produced nothing yet by construction.
#:
#: **This number is a guess, and saying so is the point.** The rule this repo
#: works to is *"does the threshold come from code that already exists, or
#: from this window?"* — and this one comes from neither. The mover paths
#: trigger on a 15m pullback-and-reclaim, so 30 minutes is two bars, and
#: whether a pair that has produced nothing in two bars is dead or merely
#: early is a question **nothing in the engine could answer**: no artifact
#: recorded how long a promoted pair takes to produce its first candidate.
#:
#: That is why `first_candidate_at` ships beside this constant and why
#: enforcement is OFF. The floor is deliberately generous — set too low it
#: releases pairs before their own setup can form, which is the destructive
#: direction — and it is meant to be replaced by the measured distribution
#: rather than defended.
MIN_HOLD_SEC: float = float(os.getenv("MOVER_RETENTION_MIN_HOLD_SEC", "1800"))

#: Ceiling on extension. Beyond this a pair is released whatever it is doing —
#: the bound that keeps this a retention policy rather than an unbounded
#: universe expansion.
MAX_HOLD_SEC: float = float(os.getenv("MOVER_RETENTION_MAX_HOLD_SEC", "43200"))

#: Scans a pair must have had before "it produced no candidates" is a fact
#: about the pair rather than about how little we looked at it.
MIN_SCANS_TO_JUDGE: int = int(os.getenv("MOVER_RETENTION_MIN_SCANS", "20"))

#: Burst ratio at or below which the move is called spent. 1.0 is the pair's
#: own EWMA baseline — i.e. "trading at its normal rate again". Deliberately
#: at the baseline rather than below it: a pair can be quiet and still be in a
#: trend, and this releases the budget slot rather than vetoing a trade, so
#: the cost of being wrong is one re-promotion.
SPENT_BURST_RATIO: float = float(os.getenv("MOVER_RETENTION_SPENT_BURST", "1.0"))

#: A spent reading must persist this long before it releases. One quiet
#: 30-second window inside a live move is noise, not exhaustion.
SPENT_FOR_SEC: float = float(os.getenv("MOVER_RETENTION_SPENT_FOR_SEC", "900"))


@dataclass
class PairWindow:
    """What one promoted pair has done since it was admitted.

    Counters only — no outcome ever enters this structure, which is the
    invariant the module's docstring rests on and the one a future change is
    most likely to break by adding "just a win rate".
    """

    symbol: str
    source: str
    promoted_at: float
    #: The pair's **signed** 24h % change at the moment it was promoted.
    #:
    #: NOT an outcome — it is a market fact about the pair at admission, known
    #: before any trade exists, and it is the thing `volatility_24h=abs(...)`
    #: throws away. A top gainer and a top loser are the same number to every
    #: consumer downstream, and on the delivered book they are not the same
    #: trade: buying a gainer ran +1.448%/trade over 110 trades, shorting a
    #: loser -0.497% over 39 (2026-08-13).
    #:
    #: `None` = the detector could not report it. Not 0.0 — "unknown which
    #: kind of mover" and "moved 0%" are different, and only one is filterable.
    change_pct: Optional[float] = None
    scans: int = 0
    candidates: int = 0
    reached_enqueue: int = 0
    enqueued: int = 0
    dark: int = 0
    #: When this pair FIRST produced a candidate. The field that makes
    #: `MIN_HOLD_SEC` choosable from evidence instead of from a guess — see
    #: that constant's own note. Nothing in the engine recorded it before,
    #: which is exactly why the floor had to be invented.
    first_candidate_at: Optional[float] = None
    last_candidate_at: Optional[float] = None
    #: When the burst ratio was last observed ABOVE the spent floor. A move is
    #: only called spent once this is far enough behind us — a single quiet
    #: sample inside a live move must not release the pair.
    last_alive_at: Optional[float] = None
    last_burst: Optional[float] = None
    #: The verdict this pair last received, and when. Stamped whether or not
    #: enforcement is on, so a window of would-be releases accumulates before
    #: anything is acted on.
    last_verdict: str = WARMUP
    last_reason: str = REASON_WARMUP
    verdict_at: Optional[float] = None

    def age_sec(self, now: float) -> float:
        return max(0.0, now - self.promoted_at)

    def to_row(self, now: float) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "source": self.source,
            "change_pct": self.change_pct,
            "gainer": (None if self.change_pct is None else self.change_pct > 0),
            "promoted_at": self.promoted_at,
            "age_sec": self.age_sec(now),
            "scans": self.scans,
            "candidates": self.candidates,
            "reached_enqueue": self.reached_enqueue,
            "enqueued": self.enqueued,
            "dark": self.dark,
            "first_candidate_at": self.first_candidate_at,
            # How long this pair took to produce anything. The column the
            # release floor should be chosen from — a pair whose first
            # candidate arrives at minute 50 is evidence that releasing at
            # minute 30 drops setups before they can form.
            "first_candidate_sec": (
                None if self.first_candidate_at is None
                else max(0.0, self.first_candidate_at - self.promoted_at)
            ),
            "last_candidate_at": self.last_candidate_at,
            "last_burst": self.last_burst,
            "last_alive_at": self.last_alive_at,
            "verdict": self.last_verdict,
            "reason": self.last_reason,
            "verdict_at": self.verdict_at,
        }


@dataclass
class RetentionVerdict:
    """One pair's decision, with the evidence that produced it.

    ``evidence`` is not decoration: a release with no numbers beside it is a
    counter, and a counter is not a cause (CLAUDE.md, on ``place_failed``).
    The ops panel renders these, so "released 14 pairs" can never be all the
    reader gets.
    """

    symbol: str
    verdict: str
    reason: str
    age_sec: float
    evidence: Dict[str, Any] = field(default_factory=dict)

    @property
    def releases(self) -> bool:
        return self.verdict == RELEASE


class MoverRetention:
    """Per-pair retention state for the promoted mover set.

    Bounded by ``MOVER_PROMOTION_MAX_PAIRS`` (30) by construction — entries are
    created on promotion and dropped on release, so this cannot grow.
    """

    def __init__(self) -> None:
        self._windows: Dict[str, PairWindow] = {}
        #: Cumulative, since process start. A low number after a deploy is a
        #: young process, not a quiet market — the panel says so.
        self.counters: Dict[str, int] = {}

    # -- lifecycle ---------------------------------------------------------

    def on_promoted(
        self,
        symbol: str,
        source: str,
        now: Optional[float] = None,
        change_pct: Optional[float] = None,
    ) -> None:
        sym = str(symbol or "").upper()
        if not sym:
            return
        ts = time.time() if now is None else float(now)
        # Re-promotion of a symbol we already hold keeps the ORIGINAL window.
        # Resetting it would make a pair that keeps re-igniting immortal — its
        # age would never reach any ceiling — which is the opposite of a
        # retention policy.
        if sym in self._windows:
            return
        self._windows[sym] = PairWindow(
            symbol=sym, source=str(source or ""), promoted_at=ts,
            change_pct=(None if change_pct is None else float(change_pct)),
        )
        self._count(f"promoted:{source}")

    def on_released(self, symbol: str, reason: str) -> None:
        sym = str(symbol or "").upper()
        self._windows.pop(sym, None)
        self._count(f"released:{reason}")

    def window(self, symbol: str) -> Optional[PairWindow]:
        return self._windows.get(str(symbol or "").upper())

    def held_symbols(self) -> List[str]:
        """Every symbol this module currently holds a window for.

        The caller reconciles against its own promoted set with this, so a
        drop site that forgets to call `on_released` leaks nothing — the
        requirement is derived from the two sets rather than remembered at
        each site.
        """
        return list(self._windows)

    def change_pct_at_promotion(self, symbol: str) -> Optional[float]:
        """The pair's signed 24h move when it was admitted, or None."""
        w = self.window(symbol)
        return None if w is None else w.change_pct

    def promoted_at(self, symbol: str) -> Optional[float]:
        w = self.window(symbol)
        return w.promoted_at if w else None

    def age_sec(self, symbol: str, now: Optional[float] = None) -> Optional[float]:
        w = self.window(symbol)
        if w is None:
            return None
        return w.age_sec(time.time() if now is None else float(now))

    # -- counters, called from the scan chain -------------------------------
    #
    # Every one is a no-op for a symbol this module does not hold, so the call
    # sites need no "is this a mover" branch of their own — one predicate,
    # here, rather than four in the scanner that can drift apart.

    def note_scan(self, symbol: str) -> None:
        w = self.window(symbol)
        if w is not None:
            w.scans += 1

    def note_candidate(self, symbol: str, now: Optional[float] = None) -> None:
        w = self.window(symbol)
        if w is not None:
            ts = time.time() if now is None else float(now)
            w.candidates += 1
            w.last_candidate_at = ts
            if w.first_candidate_at is None:
                w.first_candidate_at = ts

    def note_reached_enqueue(self, symbol: str) -> None:
        w = self.window(symbol)
        if w is not None:
            w.reached_enqueue += 1

    def note_enqueued(self, symbol: str) -> None:
        w = self.window(symbol)
        if w is not None:
            w.enqueued += 1

    def note_dark(self, symbol: str) -> None:
        w = self.window(symbol)
        if w is not None:
            w.dark += 1

    def note_activity(
        self, symbol: str, burst: Optional[float], now: Optional[float] = None
    ) -> None:
        """Record the pair's current trade-rate burst against its own baseline.

        ``None`` means the detector could not measure it — a reconnect, a
        thin symbol, a window that has not re-warmed. That is **not** a spent
        move, and it must never be read as one: absence of knowledge is not
        permission, and the direction of this particular fail decides whether
        we drop a pair mid-trend on a websocket hiccup.
        """
        w = self.window(symbol)
        if w is None or burst is None:
            return
        ts = time.time() if now is None else float(now)
        w.last_burst = float(burst)
        if float(burst) > SPENT_BURST_RATIO:
            w.last_alive_at = ts

    # -- the verdict -------------------------------------------------------

    def verdict(self, symbol: str, now: Optional[float] = None) -> Optional[RetentionVerdict]:
        """Should this pair keep its slot?

        Returns ``None`` for a symbol not held. Never raises: a scorer that
        throws must not be able to affect which pairs are scanned, so the
        caller's fallback is always the flat TTL it replaces.
        """
        w = self.window(symbol)
        if w is None:
            return None
        ts = time.time() if now is None else float(now)
        age = w.age_sec(ts)
        ev = {
            "scans": w.scans,
            "candidates": w.candidates,
            "reached_enqueue": w.reached_enqueue,
            "enqueued": w.enqueued,
            "dark": w.dark,
            "burst": w.last_burst,
            "source": w.source,
            "quiet_for_sec": (None if w.last_alive_at is None else max(0.0, ts - w.last_alive_at)),
        }

        def _stamp(v: str, reason: str) -> RetentionVerdict:
            w.last_verdict, w.last_reason, w.verdict_at = v, reason, ts
            return RetentionVerdict(w.symbol, v, reason, age, ev)

        # The ceiling wins over everything, including "still producing". A
        # bound that a good score can talk its way past is not a bound.
        if age >= MAX_HOLD_SEC:
            return _stamp(RELEASE, REASON_TTL)

        # Too young to judge. Counted apart from HOLD so a panel can never
        # report the scorer as passing pairs it has not scored.
        if age < MIN_HOLD_SEC:
            return _stamp(WARMUP, REASON_WARMUP)

        # Opportunity: scanned enough times to have shown us something, and
        # showed us nothing. `MIN_SCANS_TO_JUDGE` is what separates "this pair
        # offers no setups" from "we barely looked at it".
        if w.scans >= MIN_SCANS_TO_JUDGE and w.candidates == 0:
            return _stamp(RELEASE, REASON_NO_CANDIDATES)

        # Liveness: the move has been trading at its own baseline for long
        # enough that it is over. Requires a reading — an unmeasurable pair is
        # held, not dropped.
        if w.last_alive_at is not None:
            quiet_for = ts - w.last_alive_at
            if quiet_for >= SPENT_FOR_SEC:
                return _stamp(RELEASE, REASON_MOVE_SPENT)
        elif w.last_burst is None:
            # Never had a usable activity reading at all. Recorded so a lane
            # that has gone blind is visible rather than looking healthy.
            self._count("no_activity_data")
            ev["activity"] = REASON_NO_ACTIVITY_DATA

        # Still producing past the flat TTL — the half of "dynamic" that keeps
        # a good pair rather than dropping a bad one.
        if age >= _flat_ttl() and w.candidates > 0:
            return _stamp(EXTEND, REASON_PRODUCING)

        return _stamp(HOLD, REASON_PRODUCING if w.candidates else REASON_WARMUP)

    def sweep(self, now: Optional[float] = None) -> List[RetentionVerdict]:
        """Score every held pair. The promotion loop's one call."""
        ts = time.time() if now is None else float(now)
        out: List[RetentionVerdict] = []
        for sym in list(self._windows):
            try:
                v = self.verdict(sym, ts)
            except Exception as exc:  # pragma: no cover - defensive
                fail_open.record("mover_retention.verdict", exc)
                continue
            if v is not None:
                out.append(v)
                self._count(f"verdict:{v.verdict}")
        return out

    # -- reporting ---------------------------------------------------------

    def report(self, now: Optional[float] = None) -> Dict[str, Any]:
        """Everything the ops panel renders. One writer, one reader."""
        ts = time.time() if now is None else float(now)
        rows = [w.to_row(ts) for w in self._windows.values()]
        rows.sort(key=lambda r: -(r["age_sec"] or 0.0))
        # Time-to-first-candidate across the pairs that have produced one.
        # Published because `MIN_HOLD_SEC` is a guess and this is what
        # replaces it: a floor below the bulk of this distribution releases
        # pairs before their own setup can form, which is the direction that
        # costs signals rather than saving budget.
        #
        # It is measured only on pairs that HAVE produced — the pairs that
        # never do contribute nothing to it by construction, so it says
        # "when do producers produce", never "how many produce". Both counts
        # are published so the reader cannot mistake one for the other.
        _firsts = sorted(
            r["first_candidate_sec"] for r in rows
            if r.get("first_candidate_sec") is not None
        )
        ttfc: Dict[str, Any] = {
            "n_produced": len(_firsts),
            "n_held": len(rows),
            "median_sec": (_firsts[len(_firsts) // 2] if _firsts else None),
            "max_sec": (_firsts[-1] if _firsts else None),
            # How many produced their first candidate only AFTER the floor
            # would have released them. Non-zero means the floor is too low
            # and this lane would be dropping pairs that were about to work.
            "first_after_min_hold": sum(1 for f in _firsts if f > MIN_HOLD_SEC),
        }
        return {
            "enforcing": enforce_enabled(),
            "held": len(rows),
            "pairs": rows,
            "time_to_first_candidate": ttfc,
            "counters": dict(self.counters),
            "bounds": {
                "min_hold_sec": MIN_HOLD_SEC,
                "max_hold_sec": MAX_HOLD_SEC,
                "flat_ttl_sec": _flat_ttl(),
                "min_scans_to_judge": MIN_SCANS_TO_JUDGE,
                "spent_burst_ratio": SPENT_BURST_RATIO,
                "spent_for_sec": SPENT_FOR_SEC,
            },
        }

    def _count(self, key: str) -> None:
        self.counters[key] = self.counters.get(key, 0) + 1


def _flat_ttl() -> float:
    """The TTL this scorer is measured against. Read from config, not copied.

    A second constant here would drift from the promotion loop's own, and the
    whole verdict is expressed relative to it.
    """
    try:
        from config import MOVER_PROMOTION_TTL_SEC

        return float(MOVER_PROMOTION_TTL_SEC)
    except Exception:  # pragma: no cover - defensive
        return 21600.0


def enforce_enabled() -> bool:
    """Does the promotion loop ACT on these verdicts?

    Fail-closed: any error answers False, so the flat TTL — the behaviour
    that has been running — is what survives a broken tunable read. The
    measurement above runs regardless.
    """
    try:
        from src import runtime_tunables as _rt

        return bool(_rt.get("mover_retention_enforce"))
    except Exception as exc:
        fail_open.record("mover_retention.enforce_enabled", exc)
        return False


_retention: Optional[MoverRetention] = None


def get_retention() -> MoverRetention:
    global _retention
    if _retention is None:
        _retention = MoverRetention()
    return _retention


def reset_for_test(inst: Optional[MoverRetention] = None) -> None:
    global _retention
    _retention = inst
