"""Tests for ``TradeMonitor._check_pre_tp_grab`` — Phase A pre-TP grab.

Verifies:
* Fires when threshold met in non-trending regime, allowed setup, age window
* Skipped when feature flag is OFF
* Skipped on breakout setups (VSB / BDS / ORB)
* Skipped in TRENDING regimes
* Skipped if signal too young or too old
* Skipped if signal already hit pre-TP (idempotent)
* Skipped if signal already in TP1_HIT / TP2_HIT / TP3_HIT state
* Moves SL to breakeven (entry) — only ratchets, never widens
* Posts to free channel for paid-tier signals; suppresses for WATCHLIST
* Original TP ladder unchanged
* Threshold math is fee-aware: +0.35% raw → +2.8% net @ 10x with 0.07% fees
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor
from src.utils import utcnow


@pytest.fixture(autouse=True)
def _enable_pretp_grab():
    """Session 34: the engine default ``PRE_TP_GRAB_FRACTION`` is now 0.0
    (pre-TP disabled — default exit is TP1-full + fixed SL).  This module tests
    the pre-TP *mechanics*, which presuppose a user has opted back into banking,
    so patch the grab to the legacy 50% for every test here.  Tests that need a
    different grab (e.g. 100% full-close) patch it themselves, overriding this;
    the dedicated ``test_default_grab_zero_disables_pre_tp`` patches it to 0.0
    to assert the new default.
    """
    with patch("src.trade_monitor.PRE_TP_GRAB_FRACTION", 0.50):
        yield


def _make_signal(
    *,
    channel: str = "360_SCALP",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    stop_loss: float = 29850.0,  # -0.5%
    tp1: float = 30450.0,  # +1.5%
    setup_class: str = "SR_FLIP_RETEST",
    signal_tier: str = "B",
    age_seconds: float = 60.0,
    pre_tp_hit: bool = False,
) -> Signal:
    sig = Signal(
        channel=channel,
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=entry * 1.025,
        confidence=85.0,
        signal_id=f"PRETP-{symbol}-001",
    )
    sig.tp3 = entry * 1.04
    sig.original_entry = entry
    sig.current_price = entry
    sig.setup_class = setup_class
    sig.signal_tier = signal_tier
    sig.pre_tp_hit = pre_tp_hit
    sig.timestamp = utcnow() - timedelta(seconds=age_seconds)
    sig.status = "ACTIVE"
    return sig


def _build_monitor(send_telegram, regime_label: str = "QUIET"):
    """Build monitor with a stub regime detector returning ``regime_label``."""
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value=regime_label)
    )
    monitor = TradeMonitor(
        data_store=MagicMock(),
                get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0, "ema_slope": 0.0},
    )
    return monitor


@pytest.fixture
def mock_send():
    sent: list[tuple[str, str]] = []

    async def _send(chat_id, text):
        sent.append((chat_id, text))
        return True

    return AsyncMock(side_effect=_send), sent


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------














# ---------------------------------------------------------------------------
# Real partial close (OWNER_BRIEF §3.2a + B17, 2026-05-17)
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# Feature flag + status gates
# ---------------------------------------------------------------------------


async def test_does_not_fire_when_feature_disabled(mock_send):
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal()

    with patch("src.trade_monitor.PRE_TP_ENABLED", False):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is False
    assert sig.pre_tp_hit is False


async def test_does_not_fire_twice(mock_send):
    """Idempotent — once pre-TP has fired, subsequent cycles are silent."""
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(pre_tp_hit=True)

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.01, c_low=29990.0)

    assert fired is False


async def test_does_not_fire_after_tp1_hit(mock_send):
    """Once the original TP ladder starts firing, pre-TP is moot."""
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal()
    sig.status = "TP1_HIT"

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.01, c_low=29990.0)

    assert fired is False


# ---------------------------------------------------------------------------
# Setup + regime gates
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "blacklisted_setup",
    ["VOLUME_SURGE_BREAKOUT", "BREAKDOWN_SHORT", "OPENING_RANGE_BREAKOUT"],
)
async def test_skipped_for_breakout_family(mock_send, blacklisted_setup):
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(setup_class=blacklisted_setup)

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is False


@pytest.mark.parametrize(
    "trending_regime",
    ["TRENDING_UP", "TRENDING_DOWN", "STRONG_TREND", "BREAKOUT_EXPANSION"],
)
async def test_skipped_in_trending_regime(mock_send, trending_regime):
    """Default config excludes TRENDING regimes from the allowlist — gate skips."""
    send, _ = mock_send
    monitor = _build_monitor(send, regime_label=trending_regime)
    sig = _make_signal()

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is False


async def test_user_override_unblocks_trending_regime(mock_send, tmp_path, monkeypatch):
    """Owner-flagged 2026-05-09: a user who turns ON the Trending toggle in
    the Pre-TP settings page must see Pre-TP fire on TRENDING_UP signals.

    Reproduces the production wiring: ``user_settings`` JSON has Trending in
    the allowlist; the gate must read through ``_resolved_regime_allowlist``
    and honour it.  Pre-fix the gate read ``PRE_TP_REGIME_ALLOWLIST``
    directly — a bare config constant — so user choice was ignored.
    """
    from src import user_settings

    # Isolated store rooted at tmp.
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    user_settings.update_pretp(
        {"regime_allowlist": ["TRENDING_UP", "TRENDING_DOWN", "RANGING"]}
    )

    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="TRENDING_UP")
    sig = _make_signal()
    entry = sig.entry
    original_sl = sig.stop_loss

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=entry * 1.005, c_low=entry * 0.999)

    assert fired is True
    assert sig.pre_tp_hit is True
    # SL must have ratcheted to breakeven.
    assert sig.stop_loss == pytest.approx(entry)
    assert sig.stop_loss != pytest.approx(original_sl)


async def test_user_override_blocks_default_allowed_regime(mock_send, tmp_path, monkeypatch):
    """Symmetric: a user who turns OFF Choppy must see Pre-TP skip in VOLATILE."""
    from src import user_settings

    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    user_settings.update_pretp(
        {"regime_allowlist": ["TRENDING_UP", "TRENDING_DOWN", "RANGING"]}
    )

    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="VOLATILE")
    sig = _make_signal()

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is False


async def test_fires_in_volatile_regime(mock_send):
    """VOLATILE is in the allowlist — pre-TP should fire."""
    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="VOLATILE")
    sig = _make_signal()

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is True


async def test_fires_when_regime_classification_unavailable(mock_send):
    """Fail-open: if we can't classify, allow pre-TP per soft-penalty doctrine."""
    send, _ = mock_send
    regime_detector = MagicMock()
    regime_detector.classify.side_effect = RuntimeError("classifier broken")
    monitor = TradeMonitor(
        data_store=MagicMock(),
                get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0},
    )
    sig = _make_signal()

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is True


# ---------------------------------------------------------------------------
# Threshold gate
# ---------------------------------------------------------------------------


async def test_skipped_when_threshold_not_met(mock_send):
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    # Only +0.20% — below 0.35 threshold
    insufficient_high = 30000.0 * 1.002

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=insufficient_high, c_low=29990.0)

    assert fired is False
    assert sig.pre_tp_hit is False


# ---------------------------------------------------------------------------
# Age gate
# ---------------------------------------------------------------------------


async def test_skipped_when_too_young(mock_send):
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(age_seconds=5)  # below 30s min

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.01, c_low=29990.0)

    assert fired is False


async def test_skipped_when_too_old(mock_send):
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(age_seconds=2400)  # above 1800s max

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.01, c_low=29990.0)

    assert fired is False


# ---------------------------------------------------------------------------
# SL ratcheting + tier filter
# ---------------------------------------------------------------------------


async def test_sl_ratchets_only_never_widens_long(mock_send):
    """If SL is already above entry (e.g. trailing), pre-TP must not loosen it."""
    send, _ = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(direction=Direction.LONG, entry=30000.0, stop_loss=30100.0)

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=30050.0)

    # SL should remain at 30100, NOT drop to 30000
    assert sig.stop_loss == pytest.approx(30100.0)






# ---------------------------------------------------------------------------
# ATR-adaptive threshold (B11 fee-aware refinement)
# ---------------------------------------------------------------------------


def _build_monitor_with_atr(send, regime_label: str = "QUIET", atr_last: float = 0.0):
    """Build monitor whose indicators_fn returns the given atr_last.

    A non-zero ``atr_last`` makes the resolved pre-TP threshold ATR-adaptive
    (``max(fee_floor, atr_mult × atr_pct)``); zero/missing falls back to the
    static ``PRE_TP_THRESHOLD_PCT``.
    """
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value=regime_label)
    )
    indicators = {"adx_last": 18.0, "ema_slope": 0.0}
    if atr_last > 0:
        indicators["atr_last"] = atr_last
    monitor = TradeMonitor(
        data_store=MagicMock(),
                get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: indicators,
    )
    return monitor


async def test_atr_adaptive_low_vol_pair_uses_fee_floor(mock_send):
    """Low-vol pair (5m ATR ≈ 0.30%) → 0.5×0.30% = 0.15% < 0.20% floor.
    Resolved threshold = 0.20%.  Fires at +0.20% raw (would NOT fire under
    static 0.35%).  Validates the floor protects subscribers from sub-fee
    moves while still capturing the small-but-real wins on quiet pairs."""
    send, _ = mock_send
    entry = 30000.0
    atr_last = entry * 0.003  # 0.30% of price
    monitor = _build_monitor_with_atr(send, atr_last=atr_last)
    sig = _make_signal(direction=Direction.LONG, entry=entry)
    # Candle high reaches +0.22% — above 0.20% floor, below 0.35% static
    target_high = entry * 1.0022

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    # Banked pct should reflect the resolved threshold (0.20 floor), not 0.35
    assert sig.pre_tp_pct == pytest.approx(0.20, abs=0.01)
    assert sig.stop_loss == pytest.approx(entry)


async def test_atr_adaptive_high_vol_pair_lifts_threshold(mock_send):
    """High-vol pair (5m ATR ≈ 1.0%) → 0.5×1.0% = 0.50% > 0.20% floor.
    Resolved threshold = 0.50%.  +0.30% raw should NOT fire — pre-TP at 0.30%
    on a 1.0% ATR pair would cap winners that have plenty of room to run."""
    send, _ = mock_send
    entry = 30000.0
    atr_last = entry * 0.010  # 1.0% of price
    monitor = _build_monitor_with_atr(send, atr_last=atr_last)
    sig = _make_signal(direction=Direction.LONG, entry=entry)
    # Candle high reaches +0.30% — above static 0.35 floor would have fired,
    # but ATR-adaptive resolved threshold is 0.50% so this should skip.
    insufficient_high = entry * 1.003

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=insufficient_high, c_low=29990.0)

    assert fired is False
    assert sig.pre_tp_hit is False


async def test_atr_adaptive_high_vol_fires_at_resolved_threshold(mock_send):
    """High-vol pair fires at +0.50% (the resolved threshold), banking the
    bigger win the volatility supports."""
    send, _ = mock_send
    entry = 30000.0
    atr_last = entry * 0.010  # 1.0% ATR
    monitor = _build_monitor_with_atr(send, atr_last=atr_last)
    sig = _make_signal(direction=Direction.LONG, entry=entry)
    # +0.51% high — clears the 0.50% resolved threshold
    target_high = entry * 1.0051

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    assert sig.pre_tp_pct == pytest.approx(0.50, abs=0.01)


async def test_atr_adaptive_mid_vol_pair_uses_atr_term(mock_send):
    """Mid-vol pair (5m ATR ≈ 0.5%) → 0.5×0.5% = 0.25% > 0.20% floor.
    Resolved threshold = 0.25%.  Fires at +0.26% — between the floor and
    the static 0.35%, validating the atr-driven middle ground."""
    send, _ = mock_send
    entry = 30000.0
    atr_last = entry * 0.005  # 0.5% ATR
    monitor = _build_monitor_with_atr(send, atr_last=atr_last)
    sig = _make_signal(direction=Direction.LONG, entry=entry)
    target_high = entry * 1.0026

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    assert sig.pre_tp_pct == pytest.approx(0.25, abs=0.01)


async def test_falls_back_to_static_when_atr_missing(mock_send):
    """When ``atr_last`` is missing from indicators we use the static
    ``PRE_TP_THRESHOLD_PCT`` (0.35%).  Soft-penalty doctrine — never block
    on missing data."""
    send, _ = mock_send
    monitor = _build_monitor_with_atr(send, atr_last=0.0)  # no atr_last
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    # +0.22% — would fire if ATR-adaptive (0.20 floor), should NOT fire on static 0.35
    insufficient = 30000.0 * 1.0022

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=insufficient, c_low=29990.0)

    assert fired is False


async def test_short_atr_adaptive_low_vol_uses_floor(mock_send):
    """SHORT side: low-vol → 0.20% floor; +0.22% favourable move fires."""
    send, _ = mock_send
    entry = 30000.0
    atr_last = entry * 0.003  # 0.30% ATR
    monitor = _build_monitor_with_atr(send, atr_last=atr_last)
    sig = _make_signal(
        direction=Direction.SHORT,
        entry=entry,
        stop_loss=entry * 1.005,
        tp1=entry * 0.985,
    )
    target_low = entry * (1 - 0.0022)  # -0.22%

    with patch("src.trade_monitor.PRE_TP_ENABLED", True):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30005.0, c_low=target_low)

    assert fired is True
    assert sig.pre_tp_pct == pytest.approx(0.20, abs=0.01)
    assert sig.stop_loss == pytest.approx(entry)






