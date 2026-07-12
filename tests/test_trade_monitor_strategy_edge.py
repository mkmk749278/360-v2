"""Emitted-outcome feed into the Strategy×Context edge matrix (trade_monitor)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from src.channels.base import Signal
from src.smc import Direction
from src.strategy_edge import StrategyEdgeStore
from src.trade_monitor import TradeMonitor

CTX = "OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL"


def _make_signal(*, entry: float = 100.0) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="SOLUSDT",
        direction=Direction.LONG,
        entry=entry,
        stop_loss=entry * 0.99,
        tp1=entry * 1.02,
        tp2=entry * 1.04,
        confidence=75.0,
        signal_id="EDGE-1",
    )
    sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
    sig.setup_class = "BREAKOUT_RETEST"
    sig.status = "ACTIVE"
    sig.mc_context_key = CTX
    sig.original_sl_distance = entry * 0.01  # 1% initial risk
    return sig


def _build_monitor(edge_store) -> TradeMonitor:
    data_store = MagicMock()
    data_store.get_candles.return_value = {}
    data_store.ticks = {}

    async def _send(chat_id, text):
        return None

    return TradeMonitor(
        data_store=data_store,
        send_telegram=_send,
        get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        strategy_edge_store=edge_store,
    )


def test_tp_outcome_recorded_as_emitted_with_r_from_original_stop():
    edge_store = StrategyEdgeStore(min_samples=1, persist_path="")
    monitor = _build_monitor(edge_store)
    sig = _make_signal()
    sig.pnl_pct = 2.0  # +2% on a 1% initial risk = +2R
    sig.status = "FULL_TP_HIT"

    monitor._record_outcome(sig, hit_tp=1, hit_sl=False)

    cell = edge_store.matrix()[f"BREAKOUT_RETEST|{CTX}"]
    assert cell["n"] == 1
    assert cell["n_emitted"] == 1
    assert cell["n_suppressed"] == 0 and cell["n_shadow"] == 0
    assert cell["win_rate"] == 1.0
    assert abs(cell["avg_r"] - 2.0) < 1e-9


def test_sl_outcome_recorded_as_loss():
    edge_store = StrategyEdgeStore(min_samples=1, persist_path="")
    monitor = _build_monitor(edge_store)
    sig = _make_signal()
    sig.pnl_pct = -1.0
    sig.status = "SL_HIT"

    monitor._record_outcome(sig, hit_tp=0, hit_sl=True)

    cell = edge_store.matrix()[f"BREAKOUT_RETEST|{CTX}"]
    assert cell["win_rate"] == 0.0
    assert abs(cell["avg_r"] + 1.0) < 1e-9


def test_no_fill_expiry_is_never_recorded():
    edge_store = StrategyEdgeStore(min_samples=1, persist_path="")
    monitor = _build_monitor(edge_store)
    sig = _make_signal()
    sig.status = "EXPIRED"
    sig.entry_zone_low = sig.entry * 0.999
    sig.entry_zone_high = sig.entry * 1.001
    sig.entry_zone_filled = False  # never filled → not a trade

    monitor._record_outcome(sig, hit_tp=0, hit_sl=False, expired=True)

    assert edge_store.matrix() == {}


def test_missing_context_key_falls_back_to_unknown_cell():
    edge_store = StrategyEdgeStore(min_samples=1, persist_path="")
    monitor = _build_monitor(edge_store)
    sig = _make_signal()
    sig.mc_context_key = ""  # pre-context or restart-restored signal
    sig.pnl_pct = 1.0
    sig.status = "FULL_TP_HIT"

    monitor._record_outcome(sig, hit_tp=1, hit_sl=False)

    assert "BREAKOUT_RETEST|UNKNOWN" in edge_store.matrix()


def test_no_store_wired_is_a_noop():
    monitor = _build_monitor(None)
    sig = _make_signal()
    sig.pnl_pct = 1.0
    # Must not raise.
    monitor._record_outcome(sig, hit_tp=1, hit_sl=False)
