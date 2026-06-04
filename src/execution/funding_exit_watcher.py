"""Pre-funding exit watcher for TRENDING_UP LONG positions.

Binance Futures charges funding fees at 00:00, 08:00, and 16:00 UTC
(every 8 hours). In TRENDING_UP markets the funding rate is almost
always positive — longs pay shorts. This watcher exits OPEN LONG
positions that were entered in a TRENDING_UP regime within the
configured window before each funding event, avoiding the fee drag
while preserving the profitable entry leg.

Lifecycle:
    watcher = FundingExitWatcher()
    task = asyncio.create_task(watcher.run())
    # ... later ...
    await watcher.stop()
    await task

The watcher polls every 30 s. When ``seconds_until_next_funding()``
drops below ``PRE_FUNDING_EXIT_WINDOW_SEC``, it scans all active
users' open positions and exits qualifying ones. Once the funding
event passes, the condition is false again until the next 8-hour mark.
"""

from __future__ import annotations

import asyncio
import time
from typing import Optional

from src.utils import get_logger

log = get_logger("execution.funding_exit_watcher")

# Binance Futures perpetuals: funding collected at 00:00, 08:00, 16:00 UTC.
FUNDING_PERIOD_SEC: int = 8 * 3600


def seconds_until_next_funding(now: Optional[float] = None) -> float:
    """Seconds until the next 8-hour Binance funding event.

    Accepts an optional ``now`` Unix timestamp (float) for testing;
    defaults to ``time.time()``.
    """
    t = now if now is not None else time.time()
    elapsed_in_period = t % FUNDING_PERIOD_SEC
    return float(FUNDING_PERIOD_SEC - elapsed_in_period)


class FundingExitWatcher:
    """Periodic check that exits TRENDING_UP LONG positions before funding.

    Runs as a background asyncio task.  No external state — reads
    positions from Firestore via ``position_state.list_positions_for_user``
    and active UIDs from ``signal_dispatch._active_uids``.
    """

    # How often (seconds) to re-check in normal operation.
    _POLL_INTERVAL_S: float = 30.0

    def __init__(self) -> None:
        self._stop_event = asyncio.Event()

    async def stop(self) -> None:
        """Request graceful shutdown.  Safe to call concurrently with run."""
        self._stop_event.set()

    async def run(self) -> None:
        from config import PRE_FUNDING_EXIT_WINDOW_SEC

        if PRE_FUNDING_EXIT_WINDOW_SEC <= 0:
            log.info("funding_exit_watcher: disabled (PRE_FUNDING_EXIT_WINDOW_SEC=0)")
            return

        log.info(
            "funding_exit_watcher: started window={}s poll={}s",
            PRE_FUNDING_EXIT_WINDOW_SEC,
            self._POLL_INTERVAL_S,
        )
        while not self._stop_event.is_set():
            try:
                await self._check()
            except Exception:
                log.exception("funding_exit_watcher: unexpected error in check")
            try:
                await asyncio.wait_for(
                    self._stop_event.wait(), timeout=self._POLL_INTERVAL_S
                )
            except asyncio.TimeoutError:
                pass
        log.info("funding_exit_watcher: stopped")

    async def _check(self) -> None:
        from config import PRE_FUNDING_EXIT_WINDOW_SEC
        from src.execution import order_placer as _op
        from src.execution import position_state as _ps
        from src.execution import signal_dispatch as _sd

        secs = seconds_until_next_funding()
        if secs > PRE_FUNDING_EXIT_WINDOW_SEC:
            return

        if not _ps.is_initialised():
            return

        uids = _sd._active_uids()
        for uid in uids:
            try:
                positions = _ps.list_positions_for_user(uid, include_closed=False)
            except Exception:
                log.exception(
                    "funding_exit_watcher: list_positions_for_user failed uid={}", uid
                )
                continue

            for pos in positions:
                if _ps.is_terminal(pos.state):
                    continue
                if (pos.entry_regime or "").upper() != "TRENDING_UP":
                    continue
                if (pos.side or "").upper() != "LONG":
                    continue
                # TRAILING positions are already managed by a Binance native
                # trailing stop; skip to avoid double-exit.
                if pos.state == _ps.PositionState.TRAILING:
                    continue

                log.info(
                    "funding_exit_watcher: exiting uid={} signal_id={} symbol={} "
                    "state={} seconds_to_funding={:.0f}s",
                    uid,
                    pos.signal_id,
                    pos.symbol,
                    pos.state,
                    secs,
                )
                await _close_for_funding(uid, pos, _op.OrderPlacer(uid))


async def _close_for_funding(uid: str, pos: "object", placer: "object") -> None:
    """Cancel bracket orders then market-close for funding exit.

    Mirrors the pattern in ``signal_dispatch.close_fsm_positions_for_signal``:
    cancel first (to avoid fighting an active SL/TP), then place MARKET close.
    Uses ``place_funding_market_close`` so the FSM records close_reason=FUNDING_EXIT.
    """
    from src.execution import order_placer as _op
    from src.execution import position_state as _ps

    assert isinstance(placer, _op.OrderPlacer)
    assert isinstance(pos, _ps.Position)

    # Cancel active bracket orders (SL, optional tightened SL-BE, TP1/2/3).
    # Tolerant of -2011/-20121 (already gone / filled / expired).
    for order_id in (
        pos.sl_order_id,
        pos.sl_be_order_id,
        pos.tp1_order_id,
        pos.tp2_order_id,
        pos.tp3_order_id,
    ):
        if not order_id:
            continue
        try:
            await placer.cancel_algo_order(symbol=pos.symbol, algo_id=order_id)
        except _op.OrderPlacementError as exc:
            log.warning(
                "funding_exit_watcher: cancel_algo_order failed uid={} "
                "signal_id={} algo_id={} exc={}",
                uid, pos.signal_id, order_id, exc,
            )

    # Place REDUCE_ONLY MARKET close for remaining quantity.
    remaining = max(pos.total_qty - pos.closed_qty, 0.0) or pos.total_qty
    try:
        await placer.place_funding_market_close(
            signal_id=pos.signal_id,
            symbol=pos.symbol,
            direction=pos.side,
            quantity=remaining,
        )
    except _op.OrderPlacementError as exc:
        # Fail-soft: log and continue. The Trade Monitor's 5s backstop
        # and TradeMonitor._check_all will catch stale open positions.
        log.error(
            "funding_exit_watcher: place_funding_market_close failed uid={} "
            "signal_id={} exc={}",
            uid, pos.signal_id, exc,
        )
