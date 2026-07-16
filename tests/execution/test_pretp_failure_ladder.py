"""Tests for the pre-TP exit failure ladder (2026-07-16 audit fix).

Before this fix, all three pre-TP exit paths cancelled the original SL
and zeroed ``sl_order_id`` BEFORE placing the replacement protection.
When the replacement failed (and, where one existed, the BE-SL fallback
too), the ladder ended at an ERROR log — the residual sat on Binance
with NO stop until the reconciler's stale-age close, hours later.  That
violates the "never OPEN without a stop" hard limit.

``PositionFSM._protect_residual_final`` is the shared final rung this
suite pins:

1. BE-SL at fill price.
2. Force-close the residual (REDUCE_ONLY MARKET) — can't protect it,
   don't hold it.
3. Both failed → CRITICAL log + Telegram naked-residual page; never
   raises.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import order_placer, position_fsm, position_state


@pytest.fixture(autouse=True)
def _reset_state(monkeypatch: pytest.MonkeyPatch):
    position_state.reset_for_test()
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT")
    yield
    position_state.reset_for_test()


def _placer(**overrides) -> MagicMock:
    placer = MagicMock()
    placer.cancel_algo_order = AsyncMock(return_value=None)
    placer.place_market_close = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=9001, client_order_id="lumin_s_close",
            status="FILLED", avg_price=29100.0, binance_body={},
        )
    )
    placer.place_stop_loss = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=4001, client_order_id="lumin_s_sl_be",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    placer.place_trailing_stop_market = AsyncMock(
        return_value=order_placer.OrderPlacementResult(
            order_id=7001, client_order_id="lumin_s_sl_be",
            status="NEW", avg_price=0.0, binance_body={},
        )
    )
    for name, value in overrides.items():
        setattr(placer, name, value)
    return placer


def _position(closed_qty: float = 0.3) -> position_state.Position:
    return position_state.Position(
        signal_id="s",
        firebase_uid="uid",
        symbol="BTCUSDT",
        side="LONG",
        state=position_state.PositionState.OPEN,
        entry_price_target=29000.0,
        entry_price_filled=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=0.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.7,
        tp3_qty=0.0,
        sl_order_id=2001,
        tp1_order_id=3001,
        tp2_order_id=3002,
        tp3_order_id=0,
        closed_qty=closed_qty,
        entry_regime="TRENDING_UP",
        entry_regime_15m="TRENDING_UP",
        atr_percentile_at_entry=50.0,
        atr_value_at_entry=290.0,
    )


def _fsm() -> position_fsm.PositionFSM:
    return position_fsm.PositionFSM("uid", order_placer_factory=MagicMock())


_FAIL = order_placer.OrderPlacementError("rejected")


class TestTrailPathLadder:
    async def test_trail_failure_falls_back_to_be_sl(self):
        pos = _position()
        placer = _placer(
            place_trailing_stop_market=AsyncMock(side_effect=_FAIL)
        )
        await _fsm()._pretp_trail_path(pos, placer)
        placer.place_stop_loss.assert_awaited_once()
        assert pos.sl_be_order_id == 4001
        assert pos.sl_price == pytest.approx(29000.0)

    async def test_trail_and_be_sl_failure_force_closes_residual(self):
        pos = _position(closed_qty=0.3)
        placer = _placer(
            place_trailing_stop_market=AsyncMock(side_effect=_FAIL),
            place_stop_loss=AsyncMock(side_effect=_FAIL),
        )
        await _fsm()._pretp_trail_path(pos, placer)
        placer.place_market_close.assert_awaited_once()
        kwargs = placer.place_market_close.await_args.kwargs
        assert kwargs["quantity"] == pytest.approx(0.7)
        assert pos.close_reason == "PROTECTION_FAILSAFE"

    async def test_total_failure_pages_and_never_raises(self):
        pos = _position()
        placer = _placer(
            place_trailing_stop_market=AsyncMock(side_effect=_FAIL),
            place_stop_loss=AsyncMock(side_effect=_FAIL),
            place_market_close=AsyncMock(side_effect=_FAIL),
        )
        with patch(
            "src.execution.telegram_alerts.alert_naked_residual",
            new_callable=AsyncMock,
        ) as page:
            await _fsm()._pretp_trail_path(pos, placer)
        page.assert_awaited_once()
        assert page.await_args.kwargs["symbol"] == "BTCUSDT"
        assert page.await_args.kwargs["remaining_qty"] == pytest.approx(0.7)

    async def test_page_failure_is_swallowed(self):
        pos = _position()
        placer = _placer(
            place_trailing_stop_market=AsyncMock(side_effect=_FAIL),
            place_stop_loss=AsyncMock(side_effect=_FAIL),
            place_market_close=AsyncMock(side_effect=_FAIL),
        )
        with patch(
            "src.execution.telegram_alerts.alert_naked_residual",
            new_callable=AsyncMock,
            side_effect=RuntimeError("telegram down"),
        ):
            # Failure handlers must never raise.
            await _fsm()._pretp_trail_path(pos, placer)


class TestVolatilePathLadder:
    async def test_tightened_sl_failure_now_engages_be_sl_fallback(self):
        """Pre-fix, the volatile path had NO fallback at all — a failed
        tightened-SL placement left the residual uncovered silently."""
        pos = _position()
        placer = _placer(
            place_stop_loss=AsyncMock(
                side_effect=[
                    _FAIL,  # tightened SL
                    order_placer.OrderPlacementResult(
                        order_id=4001, client_order_id="lumin_s_sl_be",
                        status="NEW", avg_price=0.0, binance_body={},
                    ),  # BE-SL fallback
                ]
            )
        )
        await _fsm()._pretp_volatile_path(pos, placer)
        assert placer.place_stop_loss.await_count == 2
        assert pos.sl_be_order_id == 4001

    async def test_all_sl_failures_force_close(self):
        pos = _position()
        placer = _placer(place_stop_loss=AsyncMock(side_effect=_FAIL))
        await _fsm()._pretp_volatile_path(pos, placer)
        placer.place_market_close.assert_awaited_once()


class TestCancelPathLadder:
    async def test_market_close_failure_falls_back_to_be_sl(self):
        pos = _position()
        placer = _placer(place_market_close=AsyncMock(side_effect=_FAIL))
        await _fsm()._pretp_cancel_path(pos, placer)
        placer.place_stop_loss.assert_awaited_once()
        assert pos.sl_be_order_id == 4001

    async def test_close_and_be_sl_failure_retries_the_close(self):
        """Final rung retries the market close — a transient first
        failure no longer strands the residual."""
        pos = _position()
        placer = _placer(
            place_market_close=AsyncMock(
                side_effect=[
                    _FAIL,
                    order_placer.OrderPlacementResult(
                        order_id=9001, client_order_id="lumin_s_close",
                        status="FILLED", avg_price=29100.0, binance_body={},
                    ),
                ]
            ),
            place_stop_loss=AsyncMock(side_effect=_FAIL),
        )
        await _fsm()._pretp_cancel_path(pos, placer)
        assert placer.place_market_close.await_count == 2


class TestSpawnHelpers:
    async def test_spawn_track_holds_strong_reference_until_done(self):
        from src.execution import pretp_dispatcher as _pd

        inst = MagicMock()
        started = False

        async def _track(symbol: str) -> None:
            nonlocal started
            started = True

        inst.track = _track
        with patch.object(_pd, "get_instance", return_value=inst):
            _pd.spawn_track("BTCUSDT")
            assert len(_pd._background_tasks) == 1
            task = next(iter(_pd._background_tasks))
            await task
        assert started
        # Done callback dropped the strong reference.
        assert task not in _pd._background_tasks

    async def test_spawn_untrack_noop_without_instance(self):
        from src.execution import pretp_dispatcher as _pd

        with patch.object(_pd, "get_instance", return_value=None):
            _pd.spawn_untrack("BTCUSDT")  # must not raise
