"""Tests for the BTC-correlation invalidation overlay (session 19).

The overlay tightens the adverse-excursion fraction when BTC's 1H+4H macro
trend opposes an open position's direction.  It ships DARK
(``INVALIDATION_BTC_CORRELATION_ENABLED`` defaults False) so these tests
exercise both the off (no behaviour change) and on (earlier exit) paths.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Dict
from unittest.mock import MagicMock

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor
from src.utils import utcnow


def _make_sr_flip(
    *,
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    stop_loss: float = 29250.0,  # 2.5% SL → sl_dist = 750
    current_price: float = 29775.0,  # adverse 225 = 0.30 × sl_dist
    age_seconds: float = 100.0,
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="ETHUSDT",
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=entry + 300,
        tp2=entry + 600,
        confidence=85.0,
        signal_id="BTCCORR-SIG-001",
    )
    sig.setup_class = "SR_FLIP_RETEST"
    sig.current_price = current_price
    sig.timestamp = utcnow() - timedelta(seconds=age_seconds)
    return sig


def _build_monitor(active: Dict[str, Signal]) -> TradeMonitor:
    data_store = MagicMock()
    data_store.ticks = {}
    # BTC candle reads in _btc_opposes_direction return an empty dict; the
    # gate itself is patched per-test so the indicator math is irrelevant.
    data_store.get_candles.return_value = {}

    async def _mock_send(chat_id, text):
        return None

    return TradeMonitor(
        data_store=data_store,
        send_telegram=_mock_send,
        get_active_signals=lambda: dict(active),
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
    )


# ---------------------------------------------------------------------------
# _apply_btc_adverse_tightening — the pure fraction-tightening unit
# ---------------------------------------------------------------------------

def test_tightening_noop_when_flag_off(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    assert frac == 0.40
    assert reason == ""


def test_tightening_applies_when_btc_opposes(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", True)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate",
        lambda *a, **k: (False, "btc_1h_4h_both_bearish_long"),
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    assert frac == pytest.approx(0.28)  # 0.40 × 0.70
    assert "bearish" in reason


def test_tightening_noop_when_btc_aligned(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", True)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate", lambda *a, **k: (True, "")
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    assert frac == 0.40
    assert reason == ""


def test_tightening_noop_when_mult_out_of_range(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", True)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 1.0)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate",
        lambda *a, **k: (False, "btc_1h_4h_both_bearish_long"),
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    assert frac == 0.40
    assert reason == ""


# ---------------------------------------------------------------------------
# Shadow telemetry — flag off but DARK_FLAG_SHADOW_TELEMETRY on logs what the
# overlay *would* do without changing the exit (session 20 follow-up #3).
# ---------------------------------------------------------------------------

def _capture_logs():
    """Attach a loguru sink that collects INFO+ messages into a list."""
    from src.utils import get_logger  # noqa: F401  (ensures loguru configured)
    from loguru import logger

    captured: list[str] = []
    sink_id = logger.add(lambda m: captured.append(m.record["message"]), level="INFO")
    return captured, sink_id


def test_shadow_logs_when_flag_off_and_btc_opposes(monkeypatch):
    """Flag off + shadow on + BTC opposes → fraction unchanged (no behaviour
    change) but a [SHADOW] line records what the overlay would have done."""
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", True)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate",
        lambda *a, **k: (False, "btc_1h_4h_both_bearish_long"),
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})

    from loguru import logger
    captured, sink_id = _capture_logs()
    try:
        frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    finally:
        logger.remove(sink_id)

    # Behaviour-neutral: no tightening applied.
    assert frac == 0.40
    assert reason == ""
    # But the shadow line was emitted.
    assert any("[SHADOW]" in m and "INVALIDATION_BTC_CORRELATION_ENABLED" in m for m in captured)


def test_no_shadow_log_when_master_off(monkeypatch):
    """Flag off + shadow off → no log at all (and no opposition lookup cost)."""
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", False)

    def _must_not_be_called(*a, **k):
        raise AssertionError("BTC opposition check ran with shadow telemetry off")

    monkeypatch.setattr("src.trade_monitor.check_btc_direction_gate", _must_not_be_called)
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})

    from loguru import logger
    captured, sink_id = _capture_logs()
    try:
        frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    finally:
        logger.remove(sink_id)

    assert frac == 0.40
    assert reason == ""
    assert not any("[SHADOW]" in m for m in captured)


def test_no_shadow_log_when_btc_aligned(monkeypatch):
    """Flag off + shadow on but BTC aligned → nothing would fire → no line."""
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr("config.DARK_FLAG_SHADOW_TELEMETRY", True)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate", lambda *a, **k: (True, "")
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})

    from loguru import logger
    captured, sink_id = _capture_logs()
    try:
        frac, reason = monitor._apply_btc_adverse_tightening(sig, 0.40)
    finally:
        logger.remove(sink_id)

    assert frac == 0.40
    assert reason == ""
    assert not any("[SHADOW]" in m for m in captured)


# ---------------------------------------------------------------------------
# _btc_opposes_direction — fail-open contract
# ---------------------------------------------------------------------------

def test_btc_opposes_fail_open_on_gate_error(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("indicator blowup")

    monkeypatch.setattr("src.trade_monitor.check_btc_direction_gate", _boom)
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    opposes, reason = monitor._btc_opposes_direction(sig)
    assert opposes is False
    assert reason == ""


# ---------------------------------------------------------------------------
# End-to-end through _check_invalidation: same price, flag flips outcome
# ---------------------------------------------------------------------------

def test_invalidation_does_not_fire_at_base_fraction(monkeypatch):
    """Adverse 0.30×SL_dist is below the SR_FLIP base 0.40 fraction → no exit
    when the overlay is off."""
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", False)
    sig = _make_sr_flip()  # adverse 225 = 0.30 × 750
    monitor = _build_monitor({sig.signal_id: sig})
    assert monitor._check_invalidation(sig) is None


def test_invalidation_fires_with_btc_overlay(monkeypatch):
    """Same adverse 0.30×SL_dist now crosses the tightened 0.28 threshold when
    BTC opposes and the overlay is on → early invalidation with BTC tag."""
    # Session 34: engine default invalidation mode is now 'loose' (no kills).
    # This test exercises the adverse-excursion mechanics that run under an
    # opt-in non-loose mode, so pin 'standard'.
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_MODE_DEFAULT", "standard")
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", True)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate",
        lambda *a, **k: (False, "btc_1h_4h_both_bearish_long"),
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    reason = monitor._check_invalidation(sig)
    assert reason is not None
    assert "adverse excursion" in reason
    assert "BTC-correlated" in reason


def test_invalidation_still_holds_when_btc_aligned(monkeypatch):
    """Overlay on but BTC aligned/neutral → no tightening → still no exit at
    0.30×SL_dist (fail-open preserves baseline behaviour)."""
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_CORRELATION_ENABLED", True)
    monkeypatch.setattr("src.trade_monitor.INVALIDATION_BTC_ADVERSE_FRACTION_MULT", 0.70)
    monkeypatch.setattr(
        "src.trade_monitor.check_btc_direction_gate", lambda *a, **k: (True, "")
    )
    sig = _make_sr_flip()
    monitor = _build_monitor({sig.signal_id: sig})
    assert monitor._check_invalidation(sig) is None
