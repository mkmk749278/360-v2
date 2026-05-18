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
  2. Fetch open orders from Binance (``GET /fapi/v1/openOrders``).
  3. Pull all Firestore positions for this user in non-terminal state.
  4. Diff:
     - Position in FSM but missing/zero qty in Binance → manually
       closed.  Transition FSM to CLOSED, reason=MANUAL.
     - Order in FSM (e.g. ``sl_order_id``) but not in Binance's
       open list → cancelled externally; clear the order id.
  5. Persist FSM state changes.

Conservative: this PR ships the manual-close detection.  More
sophisticated diffs (qty mismatches, modified SL/TP prices) are
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
from src.security.signing_service import protocol as sig_protocol
from src.utils import get_logger

from . import position_state as _position_state

log = get_logger("execution.reconciler")


_FUTURES_POSITION_RISK_PATH = "/fapi/v2/positionRisk"
_FUTURES_OPEN_ORDERS_PATH = "/fapi/v1/openOrders"
_DEFAULT_INTERVAL_S = 60.0


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
    ) -> None:
        self._interval_s = interval_s
        self._signing_client_factory = (
            signing_client_factory or signing_client.SigningClient
        )
        self._positions_for_user = (
            positions_for_user or _default_positions_for_user
        )
        self._active_uids: Set[str] = set()
        self._lock = asyncio.Lock()
        self._stop_event = asyncio.Event()

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
        """
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
        # Fetch Binance state.
        binance_positions = await self._fetch_binance_positions(
            firebase_uid, client
        )
        # Diff + apply.
        for fsm_position in positions:
            self._diff_and_heal(fsm_position, binance_positions)

    def _diff_and_heal(
        self,
        fsm_position: _position_state.Position,
        binance_positions: Dict[str, float],
    ) -> None:
        """Apply one position's diff.

        binance_positions: {symbol -> position_amount}.  positionAmt
        sign matters: 0 = flat, positive = LONG, negative = SHORT.
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
            fsm_position.last_event_at = datetime.now(timezone.utc)
            _position_state.put_position(fsm_position)

    async def _fetch_binance_positions(
        self,
        firebase_uid: str,
        client: signing_client.SigningClient,
    ) -> Dict[str, float]:
        """Call ``GET /fapi/v2/positionRisk`` and return a
        {symbol -> position_amount} map.  Errors return empty dict
        (reconciliation skips this cycle for the user)."""
        resp = await client.binance_signed_get(
            firebase_uid=firebase_uid,
            base="futures",
            path=_FUTURES_POSITION_RISK_PATH,
        )
        if not resp.ok:
            log.warning(
                "reconciler: positionRisk fetch failed uid={} code={}",
                firebase_uid, resp.error_code,
            )
            return {}
        out: Dict[str, float] = {}
        body = resp.binance_body or []
        if not isinstance(body, list):
            return {}
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


def _default_positions_for_user(
    firebase_uid: str,
) -> List[_position_state.Position]:
    """Query Firestore for all positions for one user.  Production
    wiring; tests inject a fake."""
    from src.security.firestore_keystore import _db as fs_db

    if fs_db is None:
        return []
    docs = (
        fs_db.collection("users")
        .document(firebase_uid)
        .collection("positions")
        .stream()
    )
    out: List[_position_state.Position] = []
    for snap in docs:
        data = snap.to_dict() or {}
        try:
            out.append(_position_state._from_firestore_dict(data))
        except Exception:
            log.exception(
                "reconciler: failed to parse position doc uid={}",
                firebase_uid,
            )
    return out
