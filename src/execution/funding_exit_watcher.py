"""Pre-funding exit watcher — exit positions that would pay funding.

Binance Futures charges funding only on positions held at the exact
settlement timestamp (every 4h / 8h / 1h depending on the pair). The
sign of the funding rate decides who pays: positive → longs pay shorts;
negative → shorts pay longs. In crowded trends the rate becomes elevated
and the fee drag is material.

This watcher reads each symbol's real funding rate and next-funding-time
directly from the mark-price stream (``MarkPriceFeed.get_funding_info``),
so it needs no hardcoded funding interval and no extra REST poll. When a
symbol is within ``PRE_FUNDING_EXIT_WINDOW_SEC`` of its next settlement
and an open position is on the *paying* side with a rate above
``PRE_FUNDING_MIN_RATE``, the position is market-closed to dodge the fee.

Why a materiality gate: closing early costs a taker fee. Dodging the
~0.01% baseline funding would cost more in fees than it saves, so we only
act when funding is clearly elevated (default ≥0.05%).

Lifecycle:
    watcher = FundingExitWatcher()
    task = asyncio.create_task(watcher.run())
    # ... later ...
    await watcher.stop()
    await task

The watcher polls every 30 s. TRAILING positions are skipped — they are
managed by a Binance-native trailing stop that is riding a confirmed
trend, and the expected continuation value exceeds one funding fee.
"""

from __future__ import annotations

import asyncio
import time

from src.utils import get_logger

log = get_logger("execution.funding_exit_watcher")


def _position_pays_funding(side: str, funding_rate: float) -> bool:
    """True when a position on ``side`` would PAY at the next settlement.

    Positive funding → longs pay shorts. Negative funding → shorts pay
    longs. A zero rate means nobody pays.
    """
    s = (side or "").upper()
    if s == "LONG":
        return funding_rate > 0.0
    if s == "SHORT":
        return funding_rate < 0.0
    return False


class FundingExitWatcher:
    """Periodic check that exits positions about to pay material funding.

    Runs as a background asyncio task.  Reads positions from Firestore
    via ``position_state.list_positions_for_user``, active UIDs from
    ``signal_dispatch._active_uids``, and real funding info from the
    shared ``MarkPriceFeed`` singleton.
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
        from config import PRE_FUNDING_EXIT_WINDOW_SEC, PRE_FUNDING_MIN_RATE
        from src.execution import mark_price_feed as _mpf
        from src.execution import order_placer as _op
        from src.execution import position_state as _ps
        from src.execution import signal_dispatch as _sd

        if not _ps.is_initialised():
            return

        feed = _mpf.get_instance()
        if feed is None:
            # No mark-price feed → no funding data → cannot decide safely.
            return

        now_ms = time.time() * 1000.0
        window_ms = float(PRE_FUNDING_EXIT_WINDOW_SEC) * 1000.0

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
                # TRAILING positions ride a Binance-native trailing stop on a
                # confirmed trend; skip to avoid cancelling it for a fee dodge.
                if pos.state == _ps.PositionState.TRAILING:
                    continue

                info = feed.get_funding_info(pos.symbol)
                if info is None:
                    continue
                funding_rate, next_funding_ms = info

                # Within the pre-funding window for THIS symbol?
                if (next_funding_ms - now_ms) > window_ms:
                    continue
                if (next_funding_ms - now_ms) < 0:
                    # Settlement already passed for this tick; the feed will
                    # roll T forward within a second.  Skip until then.
                    continue

                # Only act when this position would PAY and the rate is
                # material enough to be worth the taker fee to close early.
                if not _position_pays_funding(pos.side, funding_rate):
                    continue
                if abs(funding_rate) < PRE_FUNDING_MIN_RATE:
                    continue

                log.info(
                    "funding_exit_watcher: exiting uid={} signal_id={} symbol={} "
                    "side={} state={} funding_rate={:.5f} seconds_to_funding={:.0f}s",
                    uid,
                    pos.signal_id,
                    pos.symbol,
                    pos.side,
                    pos.state,
                    funding_rate,
                    (next_funding_ms - now_ms) / 1000.0,
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
