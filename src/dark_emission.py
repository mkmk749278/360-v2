"""Dark emission lane — the silent paths, actually emitting, owner-only.

The question this exists for, owner 2026-07-31: *"we have 75 pairs and almost 15
paths but only MOVER_TREND_PULLBACK is our volume — what happened to the
others?"*  The measurement answer (``suppression_audit``) is a counterfactual:
it stamps a killed candidate and scores it later, which is optimistic (~0.38R
measured) and cannot say what the **feed** would look like.  The owner asked for
the other thing: loosen the gates per path, let those paths **emit for real**,
and show the result to the owner only.

Why this is a separate lane and not a flag on the live one
----------------------------------------------------------
A signal that reaches ``SignalRouter`` reaches, in order: the paid Telegram
channel, ``signal_dispatch.dispatch_signal_to_active_users`` (**real capital on
real users' keys**), the FCM ``signals`` topic, the free channel, the app feed,
and ``_position_lock`` — that last one being the subtle one, because a dark
signal taking the correlation lock would **block a real signal** on that symbol
and change what subscribers receive without ever appearing to.

Six places, six correct skips, and one missed skip places an order.  So the
divergence is structural instead: the scanner **marks** a candidate at the
loosened gate and keeps going — every other gate still applies, which is the
whole point, we want to know what else would have killed it — and diverts at the
**single** ``signal_queue.put`` site.  A dark signal is never put on the queue,
so the router, the dispatcher, Telegram, FCM, the app feed and the position lock
are unreachable by construction rather than skipped by convention.

What this lane does NOT yet do, stated because the count would mislead
----------------------------------------------------------------------
``SignalRouter._process`` applies a second layer — correlation lock, per-symbol
and per-channel cooldown, per-channel concurrency cap, correlation-group limit,
global same-direction throttle — and **drops most of what it dequeues**.  This
lane does not apply it.

So a dark row means *"the scanner was willing to send this"*, **not** *"a user
would have seen this"*, and the count over-reports a feed size accordingly.
Every surface that renders these rows has to say so; a number labelled as a feed
when it is a pre-router population is the #816 error (``emitted`` stamped at the
enqueue site inflated the only population allowed to justify a live change by
~30x, non-randomly, and the ops page read "Emitted to live (98)" for a window
with 3 real signals).

The fix is to **extract** the router's throttle predicates so both lanes call one
implementation with different state — not to reimplement them here, which would
be the mirror this repo keeps paying for.  That is a change to
``SignalRouter._process``, i.e. **paid-channel routing**, which is an
owner-sign-off item, so it ships as its own reviewed change rather than riding
in on a measurement PR.

Enrolment (owner, 2026-07-31)
-----------------------------
* Loosened: ``setup_compat`` (the regime confinement that idles 14 paths —
  MEAN_REVERT dies here on 98% of its rejects, RANGE_FADE 89%,
  TREND_PULLBACK_EMA 97%) and ``execution`` (overextended /
  trigger_not_confirmed).
* **Not** loosened: ``min_confidence`` and the context floors.  Those already
  carry KEEP/TUNE/DROP verdicts in the audit, so they add least, and they are
  the last thing between a scored candidate and a feed.
* **MOVER_TREND_PULLBACK is excluded.**  It contributes 24,327 pre-scoring
  rejects in one window against ~18,000 from every other path combined, it
  already owns 64% of the delivered book, and admitting it here would make the
  dark feed a second MTP feed.  The owner set no per-path budget precisely
  because excluding MTP removes the need for one.
* Detector-level thresholds (``WHALE_MOMENTUM`` 0 of 118,642 on
  ``momentum_reject``) are a **separate** change: they live inside the
  evaluators, not the gate chain, and they need this lane to exist first.
* **SR_FLIP longs are the first of those, admitted 2026-07-31 on owner
  direction.**  The long side has been disabled since 2026-06-29 on a measured
  −21.8% / 19% win, leaving a ``[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE`` log line
  as its only evidence — a candidate *count*, which cannot settle a re-enable
  because it says nothing about outcomes.  Here it earns a forward-resolved
  TP1/SL and an R.

  An evaluator-internal disable differs from the two gate-chain ones in a way
  that dictates the implementation: it fires long *before* scoring, MTF,
  min_confidence, the context floors and staleness.  Publishing there would
  put rows on a page whose first sentence promises every row cleared all of
  it.  So the candidate is **carried** — the evaluator finishes, every gate
  above still applies, and the divert happens at the same single
  ``signal_queue.put`` site as every other dark row.  ``will_admit`` answers
  the carry question before a signal object exists; it is *not* permission,
  and the mark is re-checked with ``is_dark`` before the evaluator returns,
  because an unmarked carry would put the −21.8% path back in front of paid
  subscribers.

Nothing here places an order, posts to any channel, or is visible to a user.
"""
from __future__ import annotations

import os
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from src import fail_open
from src.utils import get_logger

log = get_logger("dark_emission")

#: Attribute the scanner sets on a marked candidate. Read by the enqueue site.
DARK_ATTR = "dark_gate"

#: Gates whose rejection this lane overrides. Kept as prefixes because the token
#: carries the reason (``setup_compat:regime_STRONG_TREND``), and the reason is
#: what the owner reads.
LOOSENED_GATE_PREFIXES = ("setup_compat:", "execution:", "evaluator:")

#: The one evaluator-internal disable this lane carries (owner, 2026-07-31).
#: Named as a constant because two files must agree on it exactly: the
#: evaluator that carries the candidate and the fail-closed re-check that
#: refuses to emit one it could not mark.
GATE_SR_FLIP_LONG = "evaluator:sr_flip_long_disabled"

#: Paths never admitted to this lane. MOVER_TREND_PULLBACK owns 64% of the
#: delivered book and 24,327 of the 37,782 pre-scoring rejects in one window —
#: it does not need a dark feed to be understood, and it would drown the paths
#: that do.
EXCLUDED_SETUPS = frozenset(
    s.strip().upper()
    for s in os.getenv("DARK_EMISSION_EXCLUDED_SETUPS", "MOVER_TREND_PULLBACK").split(",")
    if s.strip()
)

#: Per-path ring size. The owner set no emission budget; this is a **storage**
#: bound, not a cap on what emits, and it is per path for the reason the
#: suppression store just learned the hard way — one shared ring makes the
#: loudest path the only readable one.
_PER_PATH_MAX: int = int(os.getenv("DARK_EMISSION_PER_PATH_MAX", "500"))
_MAX_PATHS: int = int(os.getenv("DARK_EMISSION_MAX_PATHS", "32"))

#: Ledger schema. Readers gate on this, never on a date (#802).
LEDGER_SCHEMA = 1

STATUS_OPEN = "OPEN"
STATUS_TP1 = "CLOSED_TP1"
STATUS_SL = "CLOSED_SL"
STATUS_EXPIRED = "EXPIRED"
#: Past the horizon and never walkable — the candles for this symbol stopped
#: arriving (a rotated-out mover is the common case) so no verdict was ever
#: earned. Terminal, and deliberately **not** EXPIRED: an expiry is a walked
#: window in which nothing was touched, which is a real 0R outcome, while this
#: is the absence of a measurement and scores nothing at all. Without it a row
#: whose candles die simply never reaches the horizon test — the horizon lives
#: behind a successful walk — and sits OPEN forever on the page.
STATUS_INSUFFICIENT = "INSUFFICIENT"
#: Emitted by the scanner, then refused by the dark lane's own throttle. Not a
#: failure — it is the router layer doing what it does to live signals, and
#: counting it is how the feed's real size becomes knowable.
STATUS_THROTTLED = "THROTTLED"

#: Bar width of the series the resolver walks. Used only to express staleness in
#: bars rather than seconds — the unit the owner reads elsewhere.
BAR_SECONDS = 60.0

#: An open row whose newest consumed bar is this far behind the clock is no
#: longer being measured: its ``mfe_pct`` and its status describe bars that
#: stopped arriving. Named ``stalled`` on the row, apart from a row that simply
#: has no series at all, because the two have different fixes (#835).
STALE_BARS = 3

#: Why a cycle could not advance a row. Recorded **on the row**, not only in the
#: per-cycle tally: a fail-open ``continue`` with a global counter and no per-row
#: stamp is how one permanently-unresolvable row hides inside a healthy total
#: (#815). Each of these leaves the row OPEN and unscored, which is correct — a
#: loss-selected sample is worse than no sample — but it must be *visible*.
MISS_NO_CANDLES = "no_candles"
MISS_UNUSABLE_WINDOW = "unusable_window"
MISS_FETCH_ERROR = "fetch_error"

#: Fraction of a row's elapsed window that must actually have been walked before
#: an untouched row may be called EXPIRED.
#:
#: An expiry is scored 0R on the claim that the window was walked and nothing
#: happened. That claim is only as good as the walk: owner data 2026-08-01 had
#: ROBOUSDT expiring on 309 bars of a 362-minute window and ARBUSDT on 329 of
#: 365, so between them 89 minutes of unexamined bars were being reported as
#: "the setup did nothing". A touch inside those minutes would have been booked
#: as a zero — the fabrication class, arriving as a rate rather than a number.
#:
#: The separation in that window was clean: the other six expiries walked
#: 99.9–102% of theirs. Binance emits a kline per minute for a listed perp, so a
#: healthy walk lands at or just above 1.0 and only a series with holes falls
#: materially below it. Below this floor the row retires INSUFFICIENT — terminal
#: and deliberately unscored — rather than being handed a 0R it did not earn.
MIN_WINDOW_COVERAGE: float = float(
    os.getenv("DARK_MIN_WINDOW_COVERAGE", "0.98")
)

#: Retired because the walk did not cover the window, as opposed to there being
#: no series at all. Different causes, different fixes, so they are never pooled
#: — "blank needs a cause before it gets a caption".
INSUFFICIENT_PARTIAL_WINDOW = "partial_window"
INSUFFICIENT_NO_WALK = "no_walk"


def is_excluded(setup_class: Any) -> bool:
    """Is this path barred from the dark lane?"""
    return str(setup_class or "").upper() in EXCLUDED_SETUPS


def is_loosened_gate(gate_name: str) -> bool:
    return str(gate_name or "").startswith(LOOSENED_GATE_PREFIXES)


def enabled() -> bool:
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("dark_emission_enabled"))
    except Exception as exc:
        fail_open.record("dark_emission.enabled", exc)
        return False


def will_admit(setup_class: Any, gate_name: str) -> bool:
    """Would this lane take a candidate of *setup_class* carried past *gate_name*?

    The signal-free half of ``should_mark``, for a caller that has to decide
    *before* a signal object exists. The SR_FLIP long disable lives inside the
    evaluator, well before the gate chain, so the choice there is whether to
    keep building at all — and that choice has to be answerable without a
    ``sig`` to inspect.

    **This is not the safety boundary.** Answering True only starts the
    candidate down a path; what keeps it away from users is the mark at the end
    of the evaluator plus the ``is_dark`` re-check beside it. Treating this
    answer as permission — deciding here and assuming it holds sixty lines
    later — is how a disabled long side would emit live to paid subscribers if
    the lane were toggled off mid-evaluation.
    """
    try:
        if not enabled():
            return False
        if not is_loosened_gate(gate_name):
            return False
        return not is_excluded(setup_class)
    except Exception as exc:
        fail_open.record("dark_emission.will_admit", exc)
        return False


def should_mark(sig: Any, gate_name: str) -> bool:
    """May this candidate continue past ``gate_name`` as a dark signal?

    Deliberately *not* "would it have been good" — that is what the forward
    measure is for.  This is admission only: the lane is on, the gate is one we
    loosen, the path is enrolled, and the candidate is not already dark (a
    candidate can be caught by both loosened gates, and the first one is the one
    that would have killed it live).
    """
    try:
        if not enabled():
            return False
        if not is_loosened_gate(gate_name):
            return False
        if is_excluded(getattr(sig, "setup_class", "")):
            return False
        return getattr(sig, DARK_ATTR, None) is None
    except Exception as exc:
        fail_open.record("dark_emission.should_mark", exc)
        return False


def mark(sig: Any, gate_name: str) -> None:
    """Record which gate this candidate is being carried past.

    Set on the signal rather than held here because the value has to survive
    the rest of the gate chain, and because the enqueue site — the one place
    that must never confuse a dark candidate for a live one — reads it directly.
    """
    try:
        setattr(sig, DARK_ATTR, str(gate_name))
    except Exception as exc:
        fail_open.record("dark_emission.mark", exc)


def is_dark(sig: Any) -> bool:
    """The single predicate the enqueue site branches on.

    Anything True here must never be handed to ``signal_queue.put``.
    """
    return getattr(sig, DARK_ATTR, None) is not None


# --------------------------------------------------------------------------- #
# Ledger
# --------------------------------------------------------------------------- #


class DarkLedger:
    """Bounded, per-path ring of dark-emitted signals and their outcomes."""

    DEFAULT_PATH = "data/dark_signals_live_v1.json"

    def __init__(
        self, path: Optional[str] = None, per_path_max: Optional[int] = None
    ) -> None:
        self._lock = threading.Lock()
        self._path = self.DEFAULT_PATH if path is None else path
        self._per_path_max = int(
            per_path_max if per_path_max is not None else _PER_PATH_MAX
        )
        self._paths: Dict[str, Deque[dict]] = {}
        self.emitted_total: int = 0
        self.throttled_total: int = 0
        self.paths_refused: int = 0
        self._dirty = False

    def add(self, row: dict) -> bool:
        with self._lock:
            setup = str(row.get("setup_class") or "UNKNOWN")
            ring = self._paths.get(setup)
            if ring is None:
                if len(self._paths) >= _MAX_PATHS:
                    self.paths_refused += 1
                    return False
                ring = deque(maxlen=self._per_path_max)
                self._paths[setup] = ring
            ring.append(row)
            if row.get("status") == STATUS_THROTTLED:
                self.throttled_total += 1
            else:
                self.emitted_total += 1
            self._dirty = True
            return True

    def rows(self) -> List[dict]:
        with self._lock:
            out: List[dict] = []
            for ring in self._paths.values():
                out.extend(ring)
        out.sort(key=lambda r: float(r.get("emitted_at") or 0.0), reverse=True)
        return out

    def open_rows(self) -> List[dict]:
        return [r for r in self.rows() if r.get("status") == STATUS_OPEN]

    def mark_dirty(self) -> None:
        with self._lock:
            self._dirty = True

    def flush(self, force: bool = False) -> bool:
        """Persist. Writes on a heartbeat even with nothing to say.

        An idle engine that writes nothing produces no file, and a missing file
        reads to ops as "the lane is not running" — a fault that is not
        happening.  #832 shipped exactly that bug and the owner caught it
        minutes after deploy.
        """
        import json

        with self._lock:
            if not (self._dirty or force):
                return False
            payload = {
                "schema": LEDGER_SCHEMA,
                "written_at": time.time(),
                "emitted_total": self.emitted_total,
                "throttled_total": self.throttled_total,
                "rows": [r for ring in self._paths.values() for r in ring],
            }
            self._dirty = False
        if not self._path:
            # `path=""` is the in-memory convention the tests construct with.
            # Without this the atomic write still ran: it created `.tmp` in the
            # process's cwd — the repo root under pytest, where `git add -A`
            # then committed it on every branch, conflicting on every merge —
            # and `os.replace(".tmp", "")` raised into `fail_open`, filling the
            # counter with a non-failure. Returning True because nothing was
            # asked to be persisted and nothing failed.
            return True
        try:
            dirname = os.path.dirname(self._path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:
            fail_open.record("dark_emission.flush", exc)
            return False

    def load(self) -> None:
        import json

        try:
            if not os.path.exists(self._path):
                return
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            if not isinstance(raw, dict) or int(raw.get("schema") or 0) != LEDGER_SCHEMA:
                # A schema bump drops rows rather than reinterpreting them.
                return
            for row in raw.get("rows") or []:
                if isinstance(row, dict):
                    self.add(row)
            self.emitted_total = int(raw.get("emitted_total") or self.emitted_total)
            self.throttled_total = int(
                raw.get("throttled_total") or self.throttled_total
            )
        except Exception as exc:
            fail_open.record("dark_emission.load", exc)


_ledger: Optional[DarkLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> DarkLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = DarkLedger()
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[DarkLedger] = None) -> None:
    global _ledger
    with _ledger_lock:
        _ledger = ledger


# --------------------------------------------------------------------------- #
# Publish
# --------------------------------------------------------------------------- #


def _row_from_signal(sig: Any, now: float) -> dict:
    _direction = getattr(sig, "direction", None)
    row: Dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "signal_id": str(getattr(sig, "signal_id", "") or ""),
        "symbol": str(getattr(sig, "symbol", "") or ""),
        "channel": str(getattr(sig, "channel", "") or ""),
        "setup_class": str(getattr(sig, "setup_class", "") or "UNKNOWN"),
        "side": str(getattr(_direction, "value", None) or _direction or ""),
        "entry": float(getattr(sig, "entry", 0.0) or 0.0),
        "stop_loss": float(getattr(sig, "stop_loss", 0.0) or 0.0),
        "tp1": float(getattr(sig, "tp1", 0.0) or 0.0),
        # Which gate carried it here. The whole point of the lane: this row
        # exists because THIS gate said no, so the gate's name is the finding.
        "dark_gate": str(getattr(sig, DARK_ATTR, "") or ""),
        # Scored confidence, not the evaluator's — a dark signal has been
        # through the full scoring engine and every gate except the loosened
        # one, which is exactly what makes it different from a suppression stamp.
        "confidence": float(getattr(sig, "confidence", 0.0) or 0.0),
        "regime": str(getattr(sig, "entry_regime", "") or ""),
        "context_key": str(getattr(sig, "mc_context_key", "") or ""),
        "valid_for_minutes": float(getattr(sig, "valid_for_minutes", 0.0) or 0.0),
        "pair_admission": str(getattr(sig, "pair_admission", "") or ""),
        "emitted_at": now,
        "status": STATUS_OPEN,
        "closed_at": None,
        "exit_price": None,
        "pnl_pct": None,
        "r_multiple": None,
        "mfe_pct": 0.0,
        # The adverse half of the same geometry, present from creation for the
        # same reason every other stamp is: a reader must never have to tell
        # "this row predates the field" from "this row has not moved yet".
        "mae_pct": 0.0,
        "bars_seen": 0,
        # Currency of the measurement, one per row. ``last_bar_ms`` is the newest
        # bar the resolver actually consumed for THIS row and ``last_resolved_at``
        # is when it did — three different clocks (the file's, the row's, and the
        # reader's price feed) that #108 proved a surface cannot collapse into
        # one. Filled by ``resolve_open``; None here means "not yet", which the
        # reader must not render as a pass.
        "last_bar_ms": None,
        "last_resolved_at": None,
        "bars_behind": None,
        "stalled": None,
        "resolve_misses": 0,
        "resolve_miss_reason": None,
        # How much of the elapsed window the walk covered, and — when the row
        # ends without a touch — whether that was enough to call it an expiry.
        # Present from creation so a reader never has to tell "this row predates
        # the field" from "this row has not been advanced yet" (#817's class).
        "window_coverage": None,
        "insufficient_reason": None,
    }
    # Recorded where it becomes true (#802): the SL distance is knowable the
    # instant the geometry exists and never changes afterwards. Any reader
    # dividing an unrealized move into R needs this denominator to be the
    # engine's, not one it re-derived — ops ports the math, it does not invent it.
    entry = float(row["entry"] or 0.0)
    stop = float(row["stop_loss"] or 0.0)
    row["sl_distance_pct"] = (
        abs(entry - stop) / entry * 100.0 if entry > 0 and stop > 0 else None
    )
    return row


def publish(sig: Any, now_ts: Optional[float] = None) -> bool:
    """Record a dark signal. Returns True when it entered the ledger.

    Called from the **one** site that would otherwise enqueue, so reaching here
    means the candidate cleared every gate except the loosened one — scoring,
    MTF, min_confidence, the context floors, level_still_in_play, dispatch
    cooldown and staleness all still said yes.  That is what makes these rows
    different in kind from a suppression stamp: a stamp is a candidate, this is
    a signal the engine was willing to send.

    It is still **not** what a subscriber would have received, and the ledger
    says so: ``SignalRouter`` applies a second layer this lane does not yet
    share (correlation lock, cooldowns, concurrency caps, same-direction
    throttle) and drops most of what it dequeues.  Until those predicates are
    extracted for both lanes to call, a dark row means *"the scanner would have
    sent this"*, not *"a user would have seen this"* — and the page must say the
    difference rather than let the count read as a feed size.
    """
    now = time.time() if now_ts is None else float(now_ts)
    try:
        row = _row_from_signal(sig, now)
        if row["entry"] <= 0 or row["stop_loss"] <= 0 or row["tp1"] <= 0:
            # No tradeable geometry, nothing to forward-measure. Refuse rather
            # than store a row that can never resolve.
            return False
        ledger = get_ledger()
        ok = ledger.add(row)
        if ok:
            log.info(
                "[DARK] {} {} {} past {} conf={:.1f} — owner-only, no user, no order",
                row["symbol"], row["side"], row["setup_class"],
                row["dark_gate"], row["confidence"],
            )
        return ok
    except Exception as exc:
        fail_open.record("dark_emission.publish", exc)
        return False


# --------------------------------------------------------------------------- #
# Forward resolution — on the money-path clock, not a replay
# --------------------------------------------------------------------------- #


def slice_window(candles: Any, since_ts: float) -> Optional[Dict[str, Any]]:
    """The 1m bars from the one containing ``since_ts`` onward.

    Two outcomes, and the difference between them is the whole point:

    * **Dated** — the entry bar was located by ``open_time``. The window carries
      its timestamps, so the caller can stamp which bar it last consumed and the
      reader can tell a current row from a frozen one.
    * **Undated** — the timestamps needed to place the stamp are not there, so
      the window is the last ``elapsed // 60`` bars and carries **no**
      ``open_time``. The walk still happens; the row simply never claims to be
      current, and ops renders it ``unverified``.

    Refusing outright was the first cut, and it was wrong in a way worth
    recording: on 2026-07-31 the snapshot loader restored candles with no
    ``open_time`` at all (it saved five keys and read back the same five), so
    every bucket in a freshly-restarted engine was undatable and **every** dark
    row reported ``no_candles`` — including core pairs whose candles were
    plainly arriving. Turning "I cannot date these bars" into "there is no
    measurement" is a worse failure than the imprecision it was avoiding, and it
    is invisible in exactly the same way, because a blank page and a quiet market
    look identical. Refuse the *claim*, not the measurement.

    None is still returned when there is genuinely nothing to walk — no series,
    ragged series, or history that rolled off before the stamp. That last one
    stays a refusal: the bars between entry and the array's start are gone, so a
    walk over what remains could book a TP1 that a missing SL preceded. Those
    rows retire at the horizon as INSUFFICIENT rather than being scored.
    """
    import numpy as np

    if not candles:
        return None
    highs, lows = candles.get("high"), candles.get("low")
    closes = candles.get("close")
    open_time = candles.get("open_time")
    if highs is None or lows is None or closes is None:
        return None
    n = len(highs)
    if n == 0 or len(lows) != n or len(closes) != n:
        return None
    since_ms = float(since_ts) * 1000.0

    def _undated(reason: str) -> Optional[Dict[str, Any]]:
        # The legacy window: elapsed time, counted back from the end. Imprecise
        # by construction — it assumes gap-free and current — which is why the
        # row it produces is labelled rather than trusted.
        elapsed = max(0.0, time.time() - float(since_ts))
        want = int(elapsed // BAR_SECONDS) + 1
        take = min(want, n)
        if take <= 0:
            return None
        return {
            "high": [float(v) for v in highs[-take:]],
            "low": [float(v) for v in lows[-take:]],
            "close": [float(v) for v in closes[-take:]],
            "undated_reason": reason,
        }

    if open_time is None or len(open_time) != n:
        return _undated("no_timestamps")
    times = np.asarray(open_time, dtype=np.float64)
    finite = np.isfinite(times)
    if not finite.any():
        return _undated("all_timestamps_padded")
    # The store pads a bucket's pre-existing history with NaN when timestamps
    # start arriving mid-life, so the real shape is a NaN prefix followed by a
    # finite tail. searchsorted over the whole array would be reading an
    # unsorted sequence — undefined, not merely imprecise — so it runs over the
    # finite tail only.
    first = int(np.argmax(finite))
    tail = times[first:]
    if not np.all(np.isfinite(tail)):
        # Interleaved NaNs: not a prefix, so no contiguous region can be trusted.
        return _undated("timestamps_interleaved")
    if tail.size > 1 and not np.all(np.diff(tail) >= 0):
        # ``searchsorted`` on an unsorted array is **undefined**, not imprecise:
        # it returns an index with no relationship to the bar we asked for, and
        # the walk that follows is structurally valid, stamps ``last_bar_ms``
        # and reads ``current``. Nothing downstream could tell.
        #
        # This is reachable whenever a bucket carries duplicate or out-of-order
        # bars — which `_merge_candles` produced on every gap fill until
        # 2026-08-01, because `_estimate_gap_candles` over-fetches on purpose
        # and the merge appended the overlap. That is fixed at the source; this
        # stays because the guard belongs where the assumption is made, and a
        # store is not the only thing that can hand us a bad series.
        return _undated("timestamps_unsorted")
    if since_ms < float(tail[0]):
        # The entry bar is inside the undated prefix (or older than the array).
        # Undatable here, but still walkable — unless the array itself begins
        # after the stamp, which is the rolled-off case handled below.
        if first == 0:
            return None      # history rolled off before the stamp — refuse
        return _undated("stamp_before_timestamps")
    idx = first + int(np.searchsorted(tail, since_ms, side="right")) - 1
    if idx < 0:
        return None
    return {
        "high": [float(v) for v in highs[idx:]],
        "low": [float(v) for v in lows[idx:]],
        "close": [float(v) for v in closes[idx:]],
        "open_time": [float(t) for t in times[idx:]],
    }


def _walk(row: dict, ohlc: Dict[str, List[float]]) -> Optional[dict]:
    """Resolve one dark signal by walking bars in order.

    Bars in order, never window extremes: a bar that touches both TP1 and SL
    cannot be ordered from OHLC, and taking the max/min of the whole window
    silently books whichever the reader prefers. Ambiguity is resolved
    pessimistically **and flagged**, so the row is visibly a judgement rather
    than quietly averaged in as a fact.

    ``open_time`` is optional in the mapping but is what makes the walk
    *datable*: the newest bar consumed is stamped as ``last_bar_ms``, and that
    single field is the difference between "this row is open" and "this row
    stopped being measured at 09:14 and has looked open ever since". A window
    without it is walked exactly as before and stamps nothing rather than
    guessing a time from the array's length — a missing stamp is not a pass, and
    the caller counts it.
    """
    highs, lows = ohlc.get("high"), ohlc.get("low")
    if highs is None or lows is None or len(highs) == 0:
        return None
    times = ohlc.get("open_time")
    if times is not None and len(times) != len(highs):
        # Ragged window: the bar at index i is not the bar timed at index i, so
        # every stamp derived from it would be wrong. Drop the times, keep the
        # walk, and let the row read as unstamped.
        times = None
    entry = float(row["entry"])
    sl = float(row["stop_loss"])
    tp1 = float(row["tp1"])
    if entry <= 0:
        return None
    is_long = str(row.get("side") or "").upper() == "LONG"
    sl_dist_pct = abs(entry - sl) / entry * 100.0
    mfe = float(row.get("mfe_pct") or 0.0)
    # Maximum ADVERSE excursion, added 2026-08-01 beside the favourable one.
    #
    # Without it no question about stop distance can be answered at all. We
    # could see how far a trade ran in our favour and never how far it went
    # against us first, so "would a tighter stop have helped" was unanswerable:
    # the optimistic reading (every winner survives) and the pessimistic one
    # (winners are cut first) differ by more than the entire edge being argued
    # about, and nothing in the record could separate them.
    #
    # Measured to the same bar as MFE and in the same units, so the pair reads
    # as one geometry rather than two measurements: with both, the fraction of
    # winners whose adverse excursion exceeded a candidate stop is a count, not
    # an assumption.
    mae = float(row.get("mae_pct") or 0.0)
    for i in range(len(highs)):
        hi, lo = float(highs[i]), float(lows[i])
        fav = (hi - entry) if is_long else (entry - lo)
        mfe = max(mfe, fav / entry * 100.0)
        adv = (entry - lo) if is_long else (hi - entry)
        mae = max(mae, adv / entry * 100.0)
        sl_hit = (lo <= sl) if is_long else (hi >= sl)
        tp_hit = (hi >= tp1) if is_long else (lo <= tp1)
        if sl_hit or tp_hit:
            ambiguous = bool(sl_hit and tp_hit)
            # Pessimistic on a same-bar tie.
            exit_price = sl if sl_hit else tp1
            status = STATUS_SL if sl_hit else STATUS_TP1
            pnl = ((exit_price - entry) if is_long else (entry - exit_price)) / entry * 100.0
            out = {
                "status": status,
                "exit_price": exit_price,
                "pnl_pct": pnl,
                "r_multiple": (pnl / sl_dist_pct) if sl_dist_pct > 0 else None,
                "mfe_pct": mfe,
                "mae_pct": mae,
                "ambiguous_bar": ambiguous,
                "bars_seen": i + 1,
            }
            if times is not None:
                out["last_bar_ms"] = float(times[i])
            return out
    out = {"mfe_pct": mfe, "mae_pct": mae, "bars_seen": len(highs)}
    if times is not None:
        out["last_bar_ms"] = float(times[-1])
    return out


def _note_advance(row: dict, now: float) -> None:
    """Stamp that this row was advanced on real bars, and how current they are.

    ``bars_behind`` is computed here because the engine owns both ends of it —
    the bar and the clock. A reader that fetched its own price and graded the
    row's liveness on *that* clock is #108, which this repo has now paid for
    twice; the reader's job is to render this stamp and to notice when it stops
    moving.
    """
    row["last_resolved_at"] = now
    row["resolve_misses"] = 0
    row["resolve_miss_reason"] = None
    last_ms = row.get("last_bar_ms")
    if last_ms is None:
        # Walked, but on a window that carried no usable timestamps. That is an
        # unknown, and it stays an unknown: `stalled` is None, not False. The
        # row was advanced — it is not a miss — but nothing here can say the
        # bars it was advanced on were current, so the reader must not print an
        # age beside it as though something had.
        row["bars_behind"] = None
        row["stalled"] = None
        return
    behind = (now - float(last_ms) / 1000.0) / BAR_SECONDS - 1.0
    row["bars_behind"] = max(0.0, behind)
    row["stalled"] = row["bars_behind"] > STALE_BARS


def _note_miss(row: dict, reason: str, now: float) -> None:
    """Stamp a cycle that could not advance this row.

    The row stays OPEN and unscored — correct, because scoring it on bars nobody
    saw is the fabrication class. What changes is that the row now *says* so:
    ``last_resolved_at`` stops moving while ``resolve_misses`` climbs, so a row
    that will never resolve stops looking exactly like one emitted a minute ago.
    """
    row["resolve_misses"] = int(row.get("resolve_misses") or 0) + 1
    row["resolve_miss_reason"] = reason
    row["last_miss_at"] = now
    row["stalled"] = True


def _retire_unwalkable(row: dict, ts: float, now: float, horizon_sec: float) -> bool:
    """Close a row that is past the horizon and cannot be walked. True if retired.

    The horizon test lives inside the walked branch, so a row whose candles stop
    arriving never reaches it: it stays OPEN, keeps a stale ``mfe_pct``, and
    renders forever as a live trade. Retiring it as INSUFFICIENT is the honest
    end — no fill, no loss, and explicitly **no score**, so it can be counted
    without being averaged into anything.
    """
    if (now - ts) < horizon_sec:
        return False
    row["status"] = STATUS_INSUFFICIENT
    row["insufficient_reason"] = INSUFFICIENT_NO_WALK
    row["closed_at"] = now
    row["stalled"] = None
    return True


def _window_coverage(row: dict, ts: float, now: float) -> Optional[float]:
    """Fraction of this row's elapsed window the walk actually covered.

    Only meaningful for a row that walked to the **end** of its window without
    touching a level: a row that hit stops at the hit bar, so its ``bars_seen``
    is where the outcome was, not how much was examined. The caller stamps this
    on untouched rows only.

    ``None`` when it cannot be computed, which is not the same as low coverage
    and must not be rendered as it — a row too young to have a meaningful
    denominator is simply young.
    """
    elapsed = now - ts
    if elapsed < BAR_SECONDS:
        return None
    seen = row.get("bars_seen")
    if seen is None:
        return None
    try:
        expected = elapsed / BAR_SECONDS
        return float(seen) / expected if expected > 0 else None
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def resolve_open(
    fetch_ohlc_since: Any,
    *,
    now_ts: Optional[float] = None,
    horizon_sec: float = 6 * 3600.0,
    ledger: Optional[DarkLedger] = None,
) -> Dict[str, int]:
    """Advance every open dark row. Returns a per-cycle tally.

    Keyed on **the rows owed a verdict** (#815/#835), not on the live universe
    or the current scan set — a dark signal on a symbol that has since rotated
    out is exactly the row most at risk of never resolving, and it stays in this
    population whether or not its symbol does.

    A row past ``horizon_sec`` with no touch is EXPIRED, which is a real outcome
    for a scalp and is counted apart from a loss: the mechanism did nothing, it
    did not lose. Rows whose candles cannot be fetched are left OPEN and counted
    as ``no_candles`` — an unresolved row must never be scored, because a
    loss-selected sample is worse than no sample.

    Every outcome of a cycle is stamped **on the row** as well as in the tally
    (``last_resolved_at`` / ``bars_behind`` / ``stalled`` / ``resolve_misses``).
    The tally says the population is fine; only the row can say that *this* one
    stopped advancing four hours ago, and a page that prints a live price beside
    an unstamped open row is telling the reader something it does not know.
    """
    now = time.time() if now_ts is None else float(now_ts)
    book = ledger if ledger is not None else get_ledger()
    tally = {
        "resolved": 0, "still_open": 0, "expired": 0, "no_candles": 0,
        "stalled": 0, "insufficient": 0, "undated": 0, "partial_window": 0,
    }
    try:
        for row in book.open_rows():
            ts = float(row.get("emitted_at") or 0.0)
            if ts <= 0:
                continue
            miss_reason = None
            try:
                ohlc = fetch_ohlc_since(str(row.get("symbol") or ""), ts)
            except Exception as exc:
                fail_open.record("dark_emission.fetch_ohlc", exc)
                ohlc = None
                miss_reason = MISS_FETCH_ERROR
            # None/len checks, never truthiness: the data store holds numpy
            # arrays and `not ohlc` raises on them, which is the class that
            # killed 8 features silently on 2026-07-14.
            if ohlc is None or len(ohlc) == 0:
                _note_miss(row, miss_reason or MISS_NO_CANDLES, now)
                tally["no_candles"] += 1
                if _retire_unwalkable(row, ts, now, horizon_sec):
                    tally["insufficient"] += 1
                book.mark_dirty()
                continue
            out = _walk(row, ohlc)
            if out is None:
                _note_miss(row, MISS_UNUSABLE_WINDOW, now)
                tally["no_candles"] += 1
                if _retire_unwalkable(row, ts, now, horizon_sec):
                    tally["insufficient"] += 1
                book.mark_dirty()
                continue
            row.update(out)
            # Why this row is undatable, recorded where it is known. Without it
            # "no timestamps" and "the stamp predates them" are one blank, and
            # they have different fixes — a snapshot that drops `open_time`
            # versus a bucket still carrying its pre-restart prefix.
            row["window_undated_reason"] = ohlc.get("undated_reason") or None
            _note_advance(row, now)
            if row["window_undated_reason"]:
                tally["undated"] += 1
            if out.get("status"):
                row["closed_at"] = now
                tally["resolved"] += 1
            elif (now - ts) >= horizon_sec:
                # How much of the window this verdict is actually standing on.
                # Stamped before the branch, so a row that expires and a row
                # that retires both carry the number the decision was made on.
                coverage = _window_coverage(row, ts, now)
                row["window_coverage"] = coverage
                if coverage is not None and coverage < MIN_WINDOW_COVERAGE:
                    # The walk did not cover the window, so "nothing happened"
                    # is a claim about bars nobody looked at. Terminal and
                    # unscored, counted apart from a real expiry.
                    row["status"] = STATUS_INSUFFICIENT
                    row["insufficient_reason"] = INSUFFICIENT_PARTIAL_WINDOW
                    row["closed_at"] = now
                    tally["insufficient"] += 1
                    tally["partial_window"] += 1
                else:
                    row["status"] = STATUS_EXPIRED
                    row["closed_at"] = now
                    # No fill, no loss. Scored 0R deliberately: the honest cost
                    # of a setup that never resolved is nothing happening, not a
                    # stop.
                    row["pnl_pct"] = 0.0
                    row["r_multiple"] = 0.0
                    tally["expired"] += 1
            else:
                row["window_coverage"] = _window_coverage(row, ts, now)
                tally["still_open"] += 1
                if row.get("stalled"):
                    tally["stalled"] += 1
            if row.get("status") != STATUS_OPEN:
                # Staleness is a property of a row still owed a verdict. A closed
                # row is owed nothing, so it carries no verdict on its own
                # currency rather than a False that would read as "checked".
                row["stalled"] = None
            book.mark_dirty()
        # Force: an idle lane still has to write. `flush()` only persists when
        # something changed, so a window with no open rows and no new emissions
        # left the file untouched — and a file that stops being written is
        # exactly how a reader reports a fault that is not happening (#832, the
        # bug this ledger's own flush docstring claims to have fixed and did
        # not). One small write per resolve cycle, ~5 min.
        book.flush(force=True)
    except Exception as exc:
        fail_open.record("dark_emission.resolve_open", exc)
    return tally


def summary(ledger: Optional[DarkLedger] = None) -> Dict[str, Any]:
    """Per-path rollup. Resolved rows only — an open row has no outcome, and
    pooling it as a zero would drag every path toward flat."""
    book = ledger if ledger is not None else get_ledger()
    out: Dict[str, Any] = {}
    for row in book.rows():
        setup = str(row.get("setup_class") or "UNKNOWN")
        agg = out.setdefault(setup, {
            "setup_class": setup, "n": 0, "open": 0, "resolved": 0,
            "tp1": 0, "sl": 0, "expired": 0, "insufficient": 0,
            "insufficient_partial_window": 0, "insufficient_no_walk": 0,
            "sum_r": 0.0, "n_r": 0, "gates": {},
        })
        agg["n"] += 1
        gate = str(row.get("dark_gate") or "")
        agg["gates"][gate] = agg["gates"].get(gate, 0) + 1
        status = row.get("status")
        if status == STATUS_OPEN:
            agg["open"] += 1
            continue
        if status == STATUS_INSUFFICIENT:
            # Terminal but unmeasured. Counted so the shortfall is visible, and
            # kept out of `resolved` so no rate is ever divided by a population
            # that includes rows nobody scored.
            agg["insufficient"] += 1
            # Split by cause: a series that never arrived and a series with
            # holes are different faults with different fixes, and pooling them
            # reports whichever one happens to be smaller as the whole story.
            if row.get("insufficient_reason") == INSUFFICIENT_PARTIAL_WINDOW:
                agg["insufficient_partial_window"] += 1
            else:
                agg["insufficient_no_walk"] += 1
            continue
        agg["resolved"] += 1
        if status == STATUS_TP1:
            agg["tp1"] += 1
        elif status == STATUS_SL:
            agg["sl"] += 1
        elif status == STATUS_EXPIRED:
            agg["expired"] += 1
        r = row.get("r_multiple")
        if r is not None:
            agg["sum_r"] += float(r)
            agg["n_r"] += 1
    for agg in out.values():
        agg["avg_r"] = (agg["sum_r"] / agg["n_r"]) if agg["n_r"] else None
        decided = agg["tp1"] + agg["sl"]
        # Win rate over DECIDED rows: an expiry is neither a win nor a loss, and
        # counting it as a loss is the #685 fabrication class.
        agg["win_rate"] = (agg["tp1"] / decided) if decided else None
    return out


#: Cycles a row may fail to advance before it counts as unmeasured. The resolve
#: loop runs ~every 5 min, so this is ~15 minutes of a row not moving while the
#: page keeps drawing it as a live trade.
STALL_MISS_LIMIT = 3

#: How long after emission a row may go untouched by the resolver before its
#: silence is a fault rather than a first cycle that has not run yet.
FIRST_RESOLVE_GRACE_SEC = 900.0


def resolution_health(
    ledger: Optional[DarkLedger] = None, *, now_ts: Optional[float] = None
) -> tuple:
    """Are the rows that are owed a verdict actually being advanced?

    Keyed on **the population that would be harmed** (#815): the open rows. A
    tally of a healthy cycle says nothing about the one row whose symbol rotated
    out four hours ago, and that row is the one rendering as a live trade with a
    live price beside it.

    Returns ``(ok, detail)`` for a ``PredicateProbe``. A disabled lane and an
    empty book both return **True with a reason** — never a raise, which would
    convert into a ``fail_open.record`` and bury a real failure in a counter full
    of non-failures.
    """
    try:
        if not enabled():
            return True, "dark emission lane disabled"
        now = time.time() if now_ts is None else float(now_ts)
        book = ledger if ledger is not None else get_ledger()
        open_rows = book.open_rows()
        if not open_rows:
            return True, "no dark rows owed a verdict"
        stalled = [
            r for r in open_rows
            if int(r.get("resolve_misses") or 0) >= STALL_MISS_LIMIT
            or r.get("stalled") is True
        ]
        untouched = [
            r for r in open_rows
            if r.get("last_resolved_at") is None
            and (now - float(r.get("emitted_at") or now)) > FIRST_RESOLVE_GRACE_SEC
        ]
        bad = {id(r): r for r in stalled + untouched}
        if not bad:
            # Advancing, but on windows nobody can date. Not a miss and not a
            # stall — the rows resolve — yet it means the timestamp chain is
            # broken upstream, which on 2026-07-31 was a snapshot loader that
            # dropped `open_time` and blanked the whole lane for a full cycle
            # before a human noticed. A probe that only watches for stalls
            # cannot see it, so it is named here.
            undated = [r for r in open_rows if r.get("window_undated_reason")]
            if undated and len(undated) == len(open_rows):
                reasons = sorted({str(r.get("window_undated_reason")) for r in undated})
                return False, (
                    f"all {len(open_rows)} open dark rows are being advanced on "
                    f"windows that cannot be dated ({', '.join(reasons)}) — the "
                    "outcomes are still real, but nothing can say whether the "
                    "bars behind them are current"
                )
            return True, f"{len(open_rows)} open rows, all advancing"
        worst = max(bad.values(), key=lambda r: int(r.get("resolve_misses") or 0))
        return False, (
            f"{len(bad)} of {len(open_rows)} open dark rows are not being "
            f"advanced (worst: {worst.get('symbol')} "
            f"{worst.get('resolve_misses') or 0} missed cycles, "
            f"{worst.get('resolve_miss_reason') or 'no fresh bars'}) — their "
            "outcomes on the ops page describe bars that stopped arriving"
        )
    except Exception as exc:
        fail_open.record("dark_emission.resolution_health", exc)
        return True, "health check failed open"
