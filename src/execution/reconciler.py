"""Periodic reconciliation — every 60s, diff the FSM's view of each
user's positions against Binance's actual state and self-heal.

Why this exists per OWNER_BRIEF §3.9:

* WebSocket events can drop during reconnects.  A signal that fills
  mid-disconnect may NEVER reach the FSM via ORDER_TRADE_UPDATE —
  the FSM sees the position as still OPEN when it's actually
  CLOSED on Binance.
* Users may manually close positions from the Binance UI or
  another tool.  Without reconciliation the FSM thinks the
  position is still open + keeps consuming pre-TP ticks for it.
* Binance's eventual consistency: occasionally a SL fires but the
  event is delayed by seconds.  Reconciliation catches the
  divergence within one cycle.

Strategy: per-user every 60s,
  1. Fetch open positions from Binance (``GET /fapi/v2/positionRisk``).
  2. Pull all Firestore positions for this user in non-terminal state.
  3. Diff positions:
     - Position in FSM but missing/zero qty in Binance → manually
       closed.  Transition FSM to CLOSED, reason=MANUAL.
     - Position still open past the stale-age ceiling → force-close.
  4. Diff orders (2026-07-16 audit — this half was documented for a
     year but never implemented): for each still-open position, fetch
     the symbol's open ALGO orders (``GET /fapi/v1/algoOpenOrders`` —
     SL/TP/trail live there since the Dec 2025 ``-4120`` conditional-
     order migration, NOT on ``/fapi/v1/openOrders``).  A recorded
     order id absent from the open list was cancelled externally →
     clear it; if that leaves the position with NO protective stop,
     re-place one at the recorded SL price (page if even that fails).
     Skipped for positions with an event in the last 3 minutes so an
     in-flight FSM transition (pre-TP cancel→replace) is never raced.
  5. Persist FSM state changes.

Conservative: qty mismatches and modified SL/TP prices remain
deferred — they'd require deciding "is this a divergence to fix or
a divergence to alert about?" which is a policy call.

Signed calls route through PR-4's signing service so the engine
main process never touches the user's API secret.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Set

from src.security.signing_service import client as signing_client
from src.utils import get_logger

from . import position_state as _position_state

log = get_logger("execution.reconciler")

_FUTURES_POSITION_RISK_PATH = "/fapi/v2/positionRisk"

# Module-level singleton — set by bootstrap, read by worker_manager.
_instance: Optional["Reconciler"] = None


def set_instance(r: "Reconciler") -> None:
    global _instance
    _instance = r


def get_instance() -> Optional["Reconciler"]:
    return _instance


# Conditional (algo) open orders — SL / TP / trailing stops.  These moved
# off /fapi/v1/openOrders in Binance's Dec 2025 -4120 migration.
_FUTURES_ALGO_OPEN_ORDERS_PATH = "/fapi/v1/algoOpenOrders"
_DEFAULT_INTERVAL_S = 60.0

# ---------------------------------------------------------------------------
# Orphan backlog — the protective orders that were already resting when the
# terminal-close sweep shipped
# ---------------------------------------------------------------------------
#
# ``position_fsm.cancel_protective_orders`` retires a bracket at the moment a
# position goes terminal, so no NEW orphan can be created.  It says nothing
# about the ones already on the account: ``reconcile_user`` filters to
# non-terminal positions, so a document that closed before that fix shipped is
# never looked at again and its orders rest forever.  The owner's account
# carried 24 of them (Positions 0 / Conditional 24, oldest 15h) on 2026-09-01,
# and shipping the prevention without the cleanup leaves exactly that screen.
#
# The sweep is EVIDENCE-BASED, and that is the whole safety argument: it asks
# Binance which algo orders are actually open on the symbol and cancels only
# ids that appear in BOTH that answer and our own closed document.  So it can
# never fire at an order it did not place, never act on a stale id, and never
# touch anything protecting a live position.  An algoId is unique per account,
# so even a symbol that has since re-entered is safe.
#
# It converges to zero cost.  One bounded closed-history query per user per
# process (single-field index, no composite), and thereafter nothing at all
# once the user's suspect set is empty — a clean account does the read once,
# finds every order id already zero, makes no exchange call and never looks
# again.
_ORPHAN_SWEEP_HISTORY_LIMIT = 50

# Cancels attempted per user per cycle.  A bound you cannot compute in advance
# is a blast-radius cap and it is counted: the backlog is drained over several
# cycles rather than in one burst against an account that has been IP-banned
# for hammering before.  Residue carries to the next cycle.
_ORPHAN_SWEEP_MAX_CANCELS = 12

# Order healing skips positions with FSM activity in this window so a
# reconcile cycle can never race an in-flight cancel→replace transition
# (the pre-TP paths zero an order id and place its replacement within
# seconds; a fetch landing between the two would look like an external
# cancel and trigger a spurious re-protect).
_ORDER_HEAL_MIN_QUIET_S = 180.0


class Reconciler:
    """Per-engine reconciler.  Holds a list of (firebase_uid,
    signing_client) pairs for the active users and runs the diff
    loop every ``interval_s``.

    In production the PR-11 worker manager will register users with
    this instance as they enable auto-trade and unregister on
    disable.  For PR-9 the public API is the registration verbs +
    the diff logic itself.
    """

    def __init__(
        self,
        *,
        interval_s: float = _DEFAULT_INTERVAL_S,
        signing_client_factory: Optional[
            Callable[[], signing_client.SigningClient]
        ] = None,
        positions_for_user: Optional[
            Callable[[str], List[_position_state.Position]]
        ] = None,
        order_placer_factory: Optional[Callable[[str], Any]] = None,
        max_position_age_sec: Optional[int] = None,
        stale_close_enabled: Optional[bool] = None,
    ) -> None:
        self._interval_s = interval_s
        self._signing_client_factory = (
            signing_client_factory or signing_client.SigningClient
        )
        self._positions_for_user = (
            positions_for_user or _default_positions_for_user
        )
        # Order placer for the stale-position force-close backstop.  Lazily
        # constructs a per-user OrderPlacer; injectable for tests.
        self._order_placer_factory = (
            order_placer_factory or _default_order_placer_factory
        )
        # Stale-position ceiling + enable flag.  Defaults come from config
        # but are overridable for tests.
        if max_position_age_sec is None or stale_close_enabled is None:
            from config import (
                RECONCILER_MAX_POSITION_AGE_SEC as _CFG_MAX_AGE,
                RECONCILER_STALE_CLOSE_ENABLED as _CFG_STALE_ON,
            )
            self._max_position_age_sec = (
                _CFG_MAX_AGE if max_position_age_sec is None
                else max_position_age_sec
            )
            self._stale_close_enabled = (
                _CFG_STALE_ON if stale_close_enabled is None
                else stale_close_enabled
            )
        else:
            self._max_position_age_sec = max_position_age_sec
            self._stale_close_enabled = stale_close_enabled
        self._active_uids: Set[str] = set()
        self._lock = asyncio.Lock()
        self._stop_event = asyncio.Event()
        # Users whose historical closed positions have already been walked
        # once this process.  The backlog is finite and historical, so the
        # read happens once and never again unless a cancel fails.
        self._orphan_history_read: Set[str] = set()
        # uid -> [(symbol, attr, order_id), ...] still owed a cancel.  Carries
        # across cycles so the per-cycle cap drains rather than drops.
        self._orphan_pending: Dict[str, List[tuple]] = {}
        # Counted, because a sweep that silently finds nothing and a sweep
        # that never ran read identically from outside.
        self.orphan_counts: Dict[str, int] = {
            "history_reads": 0,
            "suspects_found": 0,
            "confirmed_open": 0,
            "cancelled": 0,
            "already_gone": 0,
            "failed": 0,
        }

    async def register_user(self, firebase_uid: str) -> None:
        async with self._lock:
            self._active_uids.add(firebase_uid)
        log.info("reconciler: registered uid={}", firebase_uid)

    async def unregister_user(self, firebase_uid: str) -> None:
        async with self._lock:
            self._active_uids.discard(firebase_uid)
        log.info("reconciler: unregistered uid={}", firebase_uid)

    async def stop(self) -> None:
        self._stop_event.set()

    async def run(self) -> None:
        """Main loop — sleep interval, then reconcile every active
        user.  Errors during reconciliation are logged but don't
        crash the loop."""
        while not self._stop_event.is_set():
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=self._interval_s
                )
                break  # stop fired
            except asyncio.TimeoutError:
                pass
            async with self._lock:
                uids = list(self._active_uids)
            for uid in uids:
                try:
                    await self.reconcile_user(uid)
                except Exception:
                    log.exception(
                        "reconciler: user-level error uid={}", uid
                    )
        log.info("reconciler: stopped")

    async def reconcile_user(self, firebase_uid: str) -> None:
        """One reconciliation pass for a single user.

        Pulls FSM state + Binance state; calls :meth:`_diff` to
        compute the divergence set; applies the fixes.  Public so
        tests can exercise without spinning up the loop.

        Also drains the orphan backlog (see ``_ORPHAN_SWEEP_HISTORY_LIMIT``).
        That runs on its own and is deliberately NOT inside the early return
        below: a user whose positions have all closed has no live position to
        reconcile and is exactly the user whose bracket may still be resting.
        """
        await self._sweep_orphan_backlog(firebase_uid)
        positions = self._positions_for_user(firebase_uid)
        # Filter to non-terminal positions — terminal ones are
        # already done; no point reconciling them.
        positions = [
            p for p in positions
            if not _position_state.is_terminal(p.state)
        ]
        if not positions:
            return  # nothing to reconcile
        client = self._signing_client_factory()
        # Fetch Binance state.  None means the request failed — skip
        # this cycle entirely rather than treating all symbols as flat
        # and wrongly marking every open position as MANUAL CLOSE.
        binance_positions = await self._fetch_binance_positions(
            firebase_uid, client
        )
        if binance_positions is None:
            return
        # Diff + apply.  Per-cycle cache of open algo-order ids so two
        # positions on the same symbol cost one fetch.
        algo_open_cache: Dict[str, Optional[Set[int]]] = {}
        for fsm_position in positions:
            symbol = fsm_position.symbol
            actual_amt = binance_positions.get(symbol, 0.0)
            if fsm_position.state == _position_state.PositionState.PENDING_ENTRY:
                # A resting LIMIT entry is flat on Binance by definition — the
                # normal flat-diff would misread that as a manual close. Handle
                # it separately: TTL-cancel an expired unfilled rest, else leave
                # it resting.  (Never falls through to _diff_and_heal.)
                await self._reconcile_pending_entry(fsm_position, actual_amt)
                continue
            if abs(actual_amt) < 1e-9:
                # Flat on Binance → manual/external close.  Heal FSM state.
                await self._diff_and_heal(fsm_position, binance_positions)
            else:
                # Still open on Binance → check the stale-position ceiling.
                # This is the last-resort backstop behind the JTOUSDT
                # 2026-06-01 incident (uncovered position rode 5h09m).
                await self._maybe_force_close_stale(fsm_position)
                if _position_state.is_terminal(fsm_position.state):
                    continue  # stale close just went terminal
                # Order-side diff: detect externally-cancelled SL/TP
                # algo orders and heal (audit F4).
                if symbol not in algo_open_cache:
                    algo_open_cache[symbol] = await self._fetch_open_algo_ids(
                        firebase_uid, client, symbol
                    )
                open_ids = algo_open_cache[symbol]
                if open_ids is not None:
                    await self._heal_external_order_cancels(
                        fsm_position, open_ids
                    )

    async def _diff_and_heal(
        self,
        fsm_position: _position_state.Position,
        binance_positions: Dict[str, float],
    ) -> None:
        """Apply one position's diff.

        binance_positions: {symbol -> position_amount}.  positionAmt
        sign matters: 0 = flat, positive = LONG, negative = SHORT.

        Async since 2026-09-01: a position Binance shows flat has a bracket
        that Binance does NOT show flat.  This is the catch-all close path —
        every exit the FSM did not book itself lands here (a missed
        user-data-stream event, a native fill we never saw, the user closing
        on Binance) — so it was the widest of the three orphan producers and
        the only one with no cancel of any kind.
        """
        symbol = fsm_position.symbol
        actual_amt = binance_positions.get(symbol, 0.0)
        # If Binance says flat (amt ~ 0) but FSM says non-terminal,
        # the position was closed externally.  Transition to CLOSED.
        if abs(actual_amt) < 1e-9:
            log.warning(
                "reconciler: detected manual close uid={} signal_id={} "
                "fsm_state={} (Binance shows flat for {})",
                fsm_position.firebase_uid,
                fsm_position.signal_id,
                fsm_position.state.value,
                symbol,
            )
            fsm_position.state = _position_state.PositionState.CLOSED
            fsm_position.closed_at = datetime.now(timezone.utc)
            if not fsm_position.close_reason:
                fsm_position.close_reason = "MANUAL"
            # Retire the bracket before persisting, so the document we write
            # does not claim orders that no longer exist.  Binance being flat
            # says nothing about the conditional orders still parked on the
            # symbol — that is the whole finding (see
            # ``position_fsm.cancel_protective_orders``).
            from src.execution import position_fsm as _fsm
            await _fsm.cancel_protective_orders(
                fsm_position,
                self._order_placer_factory(fsm_position.firebase_uid),
                site="reconciler:external_close",
            )
            fsm_position.last_event_at = datetime.now(timezone.utc)
            _position_state.put_position(fsm_position)
            from src.execution import pretp_dispatcher as _pd
            _pd.spawn_untrack(symbol)

    async def _reconcile_pending_entry(
        self,
        fsm_position: _position_state.Position,
        actual_amt: float,
    ) -> None:
        """Reconcile a resting LIMIT entry (PENDING_ENTRY).

        Two real states diverge from "still resting":

        * **Filled but FSM not advanced** (Binance shows a position while the
          FSM is still PENDING_ENTRY — a missed ORDER_TRADE_UPDATE on a WS
          gap): the position is OPEN on Binance with NO SL/TP yet. Heal by
          advancing to OPEN and laying protection via the same path the fill
          event would have used (``place_protection_on_limit_fill``), so a
          managed position is never left naked.
        * **Unfilled and past TTL** (flat on Binance, ``entry_expires_at``
          elapsed): cancel the resting LIMIT and mark ``CANCELLED_NO_FILL``
          (mirrors the signal book's EXPIRED_NO_FILL). No TTL → GTC, rest on.

        Never raises; a cancel/heal failure is logged and retried next cycle.
        """
        # Filled-but-unadvanced → heal to OPEN + place protection.
        if abs(actual_amt) >= 1e-9:
            log.warning(
                "reconciler: PENDING_ENTRY filled on Binance but FSM not "
                "advanced (missed fill event) uid={} signal_id={} amt={} — "
                "healing to OPEN + placing protection",
                fsm_position.firebase_uid, fsm_position.signal_id, actual_amt,
            )
            fsm_position.filled_qty = abs(actual_amt)
            if fsm_position.entry_price_filled <= 0:
                fsm_position.entry_price_filled = fsm_position.entry_price_target
            fsm_position.state = _position_state.PositionState.OPEN
            fsm_position.last_event_at = datetime.now(timezone.utc)
            _position_state.put_position(fsm_position)
            from src.execution import position_fsm as _pfsm
            from src.execution import pretp_dispatcher as _pd
            _pd.spawn_track(fsm_position.symbol)
            try:
                healer = _pfsm.PositionFSM(
                    fsm_position.firebase_uid,
                    order_placer_factory=self._order_placer_factory,
                )
                await healer.place_protection_on_limit_fill(fsm_position)
            except Exception as exc:
                log.error(
                    "reconciler: PENDING_ENTRY heal protection failed uid={} "
                    "signal_id={} exc={} — retry next cycle",
                    fsm_position.firebase_uid, fsm_position.signal_id, exc,
                )
            fsm_position.last_event_at = datetime.now(timezone.utc)
            _position_state.put_position(fsm_position)
            return

        # Unfilled — TTL check.
        expires = getattr(fsm_position, "entry_expires_at", None)
        if expires is None:
            return  # GTC rest, no expiry
        now = datetime.now(timezone.utc)
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if now < expires:
            return  # still inside the fill window — leave it resting

        # TTL elapsed → cancel the resting LIMIT, mark CANCELLED_NO_FILL.
        try:
            placer = self._order_placer_factory(fsm_position.firebase_uid)
            await placer.cancel_order(
                symbol=fsm_position.symbol,
                order_id=int(fsm_position.entry_order_id or 0),
            )
        except Exception as exc:
            log.warning(
                "reconciler: PENDING_ENTRY TTL cancel failed uid={} signal_id={} "
                "exc={} — retry next cycle",
                fsm_position.firebase_uid, fsm_position.signal_id, exc,
            )
            return  # don't mark terminal until the cancel is confirmed
        fsm_position.state = _position_state.PositionState.CANCELLED_NO_FILL
        fsm_position.closed_at = now
        if not fsm_position.close_reason:
            fsm_position.close_reason = "EXPIRED_NO_FILL"
        fsm_position.last_event_at = now
        _position_state.put_position(fsm_position)
        log.info(
            "reconciler: PENDING_ENTRY expired unfilled — cancelled + "
            "CANCELLED_NO_FILL uid={} signal_id={} symbol={}",
            fsm_position.firebase_uid, fsm_position.signal_id, fsm_position.symbol,
        )

    async def _maybe_force_close_stale(
        self, fsm_position: _position_state.Position
    ) -> None:
        """Force-close a position Binance confirms is STILL open but whose
        FSM record has aged past ``_max_position_age_sec``.

        The engine-wide TradeMonitor expiry (MAX_SCALP_HOLD) only closes
        signals still in its own book.  An orphaned per-user FSM position —
        e.g. one whose SL failed to place and whose signal already left the
        TradeMonitor book — has no other path to closure.  This is that
        path: a hard age ceiling, well beyond any legitimate scalp hold, so
        a naked or forgotten position can never ride indefinitely (the
        JTOUSDT 2026-06-01 5h09m / -2.15% failure mode).

        No-op when the backstop is disabled or the position is within the
        age ceiling.  Failures are logged but never crash the loop.
        """
        if not self._stale_close_enabled:
            return
        # user_owned manual takes: the user owns the exit (owner decision
        # 2026-07-18). The stale-age ceiling is an engine backstop for
        # forgotten *engine-managed* positions; it must not force-close a
        # user's discretionary trade out from under them. Blast-radius caps
        # still bound the size.
        if getattr(fsm_position, "protection_mode", "managed") == "user_owned":
            return
        created = getattr(fsm_position, "created_at", None)
        if created is None:
            return
        # Tolerate naive datetimes defensively (Firestore round-trips are
        # tz-aware, but a parse edge could yield naive).
        now = datetime.now(timezone.utc)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_sec = (now - created).total_seconds()
        if age_sec < self._max_position_age_sec:
            return

        log.error(
            "reconciler: STALE position past age ceiling — force-closing "
            "uid={} signal_id={} symbol={} state={} age={:.0f}s ceiling={}s",
            fsm_position.firebase_uid,
            fsm_position.signal_id,
            fsm_position.symbol,
            fsm_position.state.value,
            age_sec,
            self._max_position_age_sec,
        )
        remaining = fsm_position.total_qty - fsm_position.closed_qty
        if remaining <= 0:
            remaining = fsm_position.total_qty
        try:
            placer = self._order_placer_factory(fsm_position.firebase_uid)
            # Cancel the bracket BEFORE the market close, exactly as
            # ``close_fsm_positions_for_signal`` does: a resting SL that fires
            # in the same instant as our close would over-reduce, and a TP left
            # parked outlives the position (owner screenshot 2026-09-01 —
            # Positions 0, Conditional orders 24).  This path is the single
            # largest producer of those orphans: it fired on 39 of 140 matched
            # positions in the 24 Aug – 1 Sep window and cancelled nothing.
            from src.execution import position_fsm as _fsm
            await _fsm.cancel_protective_orders(
                fsm_position, placer, site="reconciler:stale_close",
            )
            await placer.place_market_close(
                signal_id=fsm_position.signal_id,
                symbol=fsm_position.symbol,
                direction=fsm_position.side,
                quantity=remaining,
            )
        except Exception as exc:
            log.error(
                "reconciler: stale force-close FAILED uid={} signal_id={} "
                "symbol={} exc={} — will retry next cycle",
                fsm_position.firebase_uid,
                fsm_position.signal_id,
                fsm_position.symbol,
                exc,
            )
            return
        # Close succeeded → mark terminal so we don't re-close next cycle.
        fsm_position.state = _position_state.PositionState.CLOSED
        fsm_position.closed_at = datetime.now(timezone.utc)
        if not fsm_position.close_reason:
            fsm_position.close_reason = "STALE_EXPIRY"
        fsm_position.last_event_at = datetime.now(timezone.utc)
        _position_state.put_position(fsm_position)
        from src.execution import pretp_dispatcher as _pd
        _pd.spawn_untrack(fsm_position.symbol)

    async def _sweep_orphan_backlog(self, firebase_uid: str) -> None:
        """Cancel protective orders left resting by a position that closed
        before the terminal-close sweep existed.

        See the module-level ``_ORPHAN_SWEEP_*`` note for why this exists and
        why it is safe.  In one sentence: it cancels only ids that appear both
        on one of OUR closed position documents and in Binance's own list of
        open algo orders for that symbol, so it can never reach an order we
        did not place or one that is protecting something live.

        Never raises — this is cleanup running beside real reconciliation, and
        a failure to tidy must not stop a naked position being healed.
        """
        try:
            await self._sweep_orphan_backlog_inner(firebase_uid)
        except Exception:
            log.exception(
                "reconciler: orphan backlog sweep failed uid={}", firebase_uid,
            )

    async def _sweep_orphan_backlog_inner(self, firebase_uid: str) -> None:
        pending = self._orphan_pending.get(firebase_uid) or []

        if not pending and firebase_uid not in self._orphan_history_read:
            # The one bounded history read, once per user per process.
            self._orphan_history_read.add(firebase_uid)
            self.orphan_counts["history_reads"] += 1
            try:
                closed = await asyncio.to_thread(
                    _position_state.list_recent_closed_positions_for_user,
                    firebase_uid,
                    limit=_ORPHAN_SWEEP_HISTORY_LIMIT,
                )
            except Exception as exc:
                # Allow a retry next cycle rather than marking the user done
                # on a transient Firestore error — "swept" and "could not
                # read" must not become the same state.
                self._orphan_history_read.discard(firebase_uid)
                log.warning(
                    "reconciler: orphan history read failed uid={} exc={}",
                    firebase_uid, exc,
                )
                return
            for pos in closed:
                for attr in _position_state.PROTECTIVE_ORDER_ATTRS:
                    order_id = int(getattr(pos, attr, 0) or 0)
                    if order_id:
                        pending.append((pos.symbol, pos.signal_id, attr, order_id))
            self.orphan_counts["suspects_found"] += len(pending)
            if pending:
                log.info(
                    "reconciler: orphan backlog uid={} — {} suspect order(s) "
                    "across {} closed position(s)",
                    firebase_uid, len(pending),
                    len({p[1] for p in pending}),
                )

        if not pending:
            self._orphan_pending.pop(firebase_uid, None)
            return

        client = self._signing_client_factory()
        placer = self._order_placer_factory(firebase_uid)
        # One algoOpenOrders fetch per distinct symbol, cached for this cycle.
        open_ids_cache: Dict[str, Optional[Set[int]]] = {}
        budget = _ORPHAN_SWEEP_MAX_CANCELS
        carried: List[tuple] = []

        for item in pending:
            symbol, signal_id, attr, order_id = item
            if budget <= 0:
                carried.append(item)
                continue
            if symbol not in open_ids_cache:
                open_ids_cache[symbol] = await self._fetch_open_algo_ids(
                    firebase_uid, client, symbol
                )
            open_ids = open_ids_cache[symbol]
            if open_ids is None:
                # The fetch failed. An empty set must only ever mean "Binance
                # confirmed nothing is open" — so a failure carries the item
                # rather than concluding the order is gone.
                carried.append(item)
                continue
            if order_id not in open_ids:
                # Already filled, cancelled, or expired. Nothing to do; clear
                # the id off the document so it is never reconsidered.
                self.orphan_counts["already_gone"] += 1
                await self._clear_orphan_id(firebase_uid, signal_id, attr)
                continue
            self.orphan_counts["confirmed_open"] += 1
            budget -= 1
            try:
                await placer.cancel_algo_order(symbol=symbol, algo_id=order_id)
            except Exception as exc:
                self.orphan_counts["failed"] += 1
                log.warning(
                    "reconciler: orphan cancel FAILED uid={} symbol={} "
                    "{}={} exc={} — retrying next cycle",
                    firebase_uid, symbol, attr, order_id, exc,
                )
                carried.append(item)
                continue
            self.orphan_counts["cancelled"] += 1
            log.info(
                "reconciler: cancelled ORPHANED {} uid={} symbol={} "
                "algo_id={} (position {} is closed)",
                attr, firebase_uid, symbol, order_id, signal_id,
            )
            await self._clear_orphan_id(firebase_uid, signal_id, attr)

        if carried:
            self._orphan_pending[firebase_uid] = carried
        else:
            self._orphan_pending.pop(firebase_uid, None)

    async def _clear_orphan_id(
        self, firebase_uid: str, signal_id: str, attr: str
    ) -> None:
        """Zero one protective order id on a closed position document.

        Persisted so the sweep converges: a document whose ids are all zero
        contributes no suspects on the next process's history read, which is
        what turns this from a recurring cost into a one-off cleanup.
        """
        try:
            pos = await asyncio.to_thread(
                _position_state.get_position, firebase_uid, signal_id
            )
            if int(getattr(pos, attr, 0) or 0) == 0:
                return  # already clear — nothing to write
            setattr(pos, attr, 0)
            await asyncio.to_thread(_position_state.put_position, pos)
        except Exception as exc:
            # Losing the write only costs a repeat of this exact check on the
            # next process boot, and the intersect makes that repeat a no-op.
            log.debug(
                "reconciler: could not clear {} on uid={} signal_id={} exc={}",
                attr, firebase_uid, signal_id, exc,
            )

    async def _fetch_open_algo_ids(
        self,
        firebase_uid: str,
        client: signing_client.SigningClient,
        symbol: str,
    ) -> Optional[Set[int]]:
        """Return the set of open algo-order ids for ``symbol``, or
        ``None`` on any fetch error (callers skip healing this cycle —
        an empty set must only ever mean "Binance confirmed nothing is
        open", never "the request failed")."""
        try:
            resp = await client.binance_signed_get(
                firebase_uid=firebase_uid,
                base="futures",
                path=_FUTURES_ALGO_OPEN_ORDERS_PATH,
                params={"symbol": symbol},
            )
        except Exception as exc:
            log.warning(
                "reconciler: algoOpenOrders request raised uid={} symbol={} "
                "exc={}",
                firebase_uid, symbol, exc,
            )
            return None
        if not resp.ok:
            log.warning(
                "reconciler: algoOpenOrders fetch failed uid={} symbol={} "
                "code={}",
                firebase_uid, symbol, resp.error_code,
            )
            return None
        body = resp.binance_body
        # Tolerate both a bare list and an {"orders": [...]}-style wrapper.
        entries = body if isinstance(body, list) else (
            body.get("orders") if isinstance(body, dict) else None
        )
        if not isinstance(entries, list):
            log.warning(
                "reconciler: algoOpenOrders returned unexpected body shape "
                "uid={} symbol={}",
                firebase_uid, symbol,
            )
            return None
        out: Set[int] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            try:
                algo_id = int(entry.get("algoId", 0))
            except (TypeError, ValueError):
                continue
            if algo_id:
                out.add(algo_id)
        return out

    async def _heal_external_order_cancels(
        self,
        fsm_position: _position_state.Position,
        open_algo_ids: Set[int],
    ) -> None:
        """Clear FSM order ids whose algo orders are no longer open on
        Binance, and re-protect if the position lost its stop.

        This is the order-side diff the module docstring promised from
        day one (audit F4).  Without it, an SL cancelled from the
        Binance UI left the FSM trusting a dead order id as live
        protection indefinitely — the reconciler's stale-age ceiling
        (hours) was the only backstop.

        Freshness guard: positions with FSM activity in the last
        ``_ORDER_HEAL_MIN_QUIET_S`` are skipped so we never race an
        in-flight cancel→replace transition.
        """
        last_event = getattr(fsm_position, "last_event_at", None)
        if last_event is not None:
            if last_event.tzinfo is None:
                last_event = last_event.replace(tzinfo=timezone.utc)
            quiet_s = (
                datetime.now(timezone.utc) - last_event
            ).total_seconds()
            if quiet_s < _ORDER_HEAL_MIN_QUIET_S:
                return

        # ``trail_stop_order_id`` is the TRAIL GOVERNOR's stop (#908) and is a
        # different field from ``trail_order_id``, which is the older native
        # TRAILING_STOP_MARKET.  One word apart, and its absence here meant a
        # governed position was invisible to this healer: after handover the
        # governor cancels ``sl_order_id`` and the ladder, so all three of the
        # original names read 0 and the position evaluated as permanently
        # unprotected while its real stop went unwatched.  An externally
        # cancelled governor stop would have produced no re-place and no
        # naked-residual page — the naked-position invariant with a hole in it,
        # on the one feature that moves a stop every bar.
        protection_fields = (
            "trail_order_id",
            "trail_stop_order_id",
            "sl_be_order_id",
            "sl_order_id",
        )
        tp_fields = ("tp1_order_id", "tp2_order_id", "tp3_order_id")
        changed = False
        lost_protection = False
        for field in protection_fields + tp_fields:
            oid = int(getattr(fsm_position, field, 0) or 0)
            if oid and oid not in open_algo_ids:
                log.warning(
                    "reconciler: {} {} cancelled externally uid={} "
                    "signal_id={} symbol={} — clearing stale id",
                    field, oid,
                    fsm_position.firebase_uid,
                    fsm_position.signal_id,
                    fsm_position.symbol,
                )
                setattr(fsm_position, field, 0)
                changed = True
                if field in protection_fields:
                    lost_protection = True
        if not changed:
            return

        still_protected = any(
            int(getattr(fsm_position, f, 0) or 0) for f in protection_fields
        )
        if lost_protection and not still_protected:
            await self._replace_lost_stop(fsm_position)
        _position_state.put_position(fsm_position)

    async def _replace_lost_stop(
        self, fsm_position: _position_state.Position
    ) -> None:
        """The position's protective stop was cancelled externally and no
        other stop remains — re-place one at the recorded SL price.
        Never raises; a total failure pages via the naked-residual alert
        (the stale-age force-close stays the last automatic resort)."""
        # user_owned manual takes: the user owns the exit (owner decision
        # 2026-07-18). An externally-cancelled SL on a user_owned position is
        # the user cancelling their own stop — do NOT re-place it, and do NOT
        # page it as naked. (managed positions keep the full re-protect +
        # naked-residual escalation below.)
        if getattr(fsm_position, "protection_mode", "managed") == "user_owned":
            log.info(
                "reconciler: user_owned position lost its stop (user cancel) "
                "uid={} signal_id={} — leaving as user manages it, no re-place",
                fsm_position.firebase_uid, fsm_position.signal_id,
            )
            return

        # Where to re-protect.  For a governed position the recorded
        # ``sl_price`` is the level the mechanism REPLACED at handover, so
        # re-placing there would widen risk back to the entry-time stop — the
        # one thing the governor guarantees never happens ("a trail only
        # tightens").  Re-protect at the level actually in force, and pick the
        # tighter of the two rather than trusting either blindly: a governed
        # position whose parked price is somehow unreadable still deserves its
        # designed stop, and a pre-handover one has no parked price at all.
        level = float(fsm_position.sl_price or 0.0)
        parked = float(getattr(fsm_position, "trail_stop_price", 0.0) or 0.0)
        if bool(getattr(fsm_position, "trail_governing", False)) and parked > 0:
            is_long = str(fsm_position.side).upper() == "LONG"
            level = (
                max(level, parked) if is_long else
                (min(level, parked) if level > 0 else parked)
            )
        log.error(
            "reconciler: position lost its protective stop (external "
            "cancel) — re-placing uid={} signal_id={} symbol={} at={} "
            "(sl_price={} parked={} governing={})",
            fsm_position.firebase_uid,
            fsm_position.signal_id,
            fsm_position.symbol,
            level,
            fsm_position.sl_price,
            parked,
            bool(getattr(fsm_position, "trail_governing", False)),
        )
        if level > 0:
            try:
                placer = self._order_placer_factory(fsm_position.firebase_uid)
                result = await placer.place_stop_loss(
                    signal_id=fsm_position.signal_id,
                    symbol=fsm_position.symbol,
                    direction=fsm_position.side,
                    stop_price=level,
                    coid_override=_position_state.coid_sl_be(
                        fsm_position.signal_id
                    ),
                )
                fsm_position.sl_be_order_id = result.order_id
                log.warning(
                    "reconciler: protective stop re-placed uid={} "
                    "signal_id={} order_id={}",
                    fsm_position.firebase_uid,
                    fsm_position.signal_id,
                    result.order_id,
                )
                return
            except Exception as exc:
                log.critical(
                    "reconciler: stop re-placement FAILED uid={} signal_id={} "
                    "symbol={} exc={} — position is UNPROTECTED until the "
                    "stale-age ceiling; operator paged",
                    fsm_position.firebase_uid,
                    fsm_position.signal_id,
                    fsm_position.symbol,
                    exc,
                )
        else:
            log.critical(
                "reconciler: cannot re-place stop (no usable level: "
                "sl_price and parked stop both unset) "
                "uid={} signal_id={} symbol={} — operator paged",
                fsm_position.firebase_uid,
                fsm_position.signal_id,
                fsm_position.symbol,
            )
        try:
            from . import telegram_alerts as _ta
            await _ta.alert_naked_residual(
                firebase_uid=fsm_position.firebase_uid,
                signal_id=fsm_position.signal_id,
                symbol=fsm_position.symbol,
                remaining_qty=max(
                    0.0, fsm_position.total_qty - fsm_position.closed_qty
                ),
            )
        except Exception:
            log.exception(
                "reconciler: naked-residual page failed uid={} signal_id={}",
                fsm_position.firebase_uid,
                fsm_position.signal_id,
            )

    async def _fetch_binance_positions(
        self,
        firebase_uid: str,
        client: signing_client.SigningClient,
    ) -> Optional[Dict[str, float]]:
        """Call ``GET /fapi/v2/positionRisk`` and return a
        {symbol -> position_amount} map.

        Returns ``None`` on any fetch error so the caller can skip
        the diff entirely — returning an empty dict would be
        indistinguishable from "user has no open positions" and
        would cause every FSM position to be marked MANUAL CLOSE.
        """
        try:
            resp = await client.binance_signed_get(
                firebase_uid=firebase_uid,
                base="futures",
                path=_FUTURES_POSITION_RISK_PATH,
            )
        except Exception as exc:
            log.warning(
                "reconciler: positionRisk request raised uid={} exc={}",
                firebase_uid, exc,
            )
            return None
        if not resp.ok:
            log.warning(
                "reconciler: positionRisk fetch failed uid={} code={}",
                firebase_uid, resp.error_code,
            )
            return None
        out: Dict[str, float] = {}
        body = resp.binance_body or []
        if not isinstance(body, list):
            log.warning(
                "reconciler: positionRisk returned non-list body uid={}",
                firebase_uid,
            )
            return None
        # Hand the WHOLE row to the exchange-position index before reducing it
        # to positionAmt.  Every cycle used to fetch liquidationPrice,
        # leverage, markPrice and Binance's own unRealizedProfit and throw all
        # of them away — and liquidation price and leverage exist NOWHERE else
        # (the ACCOUNT_UPDATE push does not carry them), so the position card
        # could not show what Binance's own position row shows.  Nothing extra
        # is requested here; this is the reader for a response we were already
        # paying for.
        from . import exchange_positions as _xp
        _xp.apply_position_risk(firebase_uid, body)
        for entry in body:
            if not isinstance(entry, dict):
                continue
            sym = str(entry.get("symbol", ""))
            try:
                amt = float(entry.get("positionAmt", "0"))
            except (TypeError, ValueError):
                continue
            if sym:
                out[sym] = amt
        return out


def _default_order_placer_factory(firebase_uid: str) -> Any:
    """Construct a per-user :class:`OrderPlacer` for the stale-position
    force-close backstop.  Imported lazily to avoid a module-load cycle
    (order_placer → signing client → … ) at reconciler import time."""
    from src.execution import order_placer as _op
    return _op.OrderPlacer(firebase_uid)


def _default_positions_for_user(
    firebase_uid: str,
) -> List[_position_state.Position]:
    """Query Firestore for one user's NON-TERMINAL positions.

    Routes through :func:`position_state.list_positions_for_user`
    (``include_closed=False``) so the read is server-side filtered to
    live positions only.  The reconciler runs every 60s per active user;
    an unfiltered collection stream here billed one Firestore read per
    CLOSED position in the user's entire (never-pruned) history on EVERY
    cycle — the dominant remaining Firestore cost after #609 fixed the
    per-tick pre-TP path.  Terminal positions are exactly what
    :meth:`Reconciler.reconcile_user` filters out anyway, so scoping the
    query to non-terminal is both cheaper and semantically identical.

    Production wiring; tests inject a fake via ``positions_for_user``.
    """
    if not _position_state.is_initialised():
        return []
    return _position_state.list_positions_for_user(firebase_uid)
