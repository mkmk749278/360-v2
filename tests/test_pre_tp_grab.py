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
        send_telegram=send_telegram,
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


async def test_fires_when_long_candle_high_reaches_threshold(mock_send):
    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    target_high = 30000.0 * 1.0035  # +0.35%

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    assert sig.pre_tp_hit is True
    assert sig.pre_tp_pct == pytest.approx(0.35)
    assert sig.pre_tp_timestamp is not None
    # SL moved to breakeven (entry)
    assert sig.stop_loss == pytest.approx(30000.0)
    # Original TP ladder untouched
    assert sig.tp1 == pytest.approx(30450.0)
    assert sig.tp2 == pytest.approx(30750.0)
    # Backfill — monitor stamps the trigger when it wasn't pre-stamped
    assert sig.pre_tp_threshold_pct == pytest.approx(0.35)
    assert sig.pre_tp_trigger_price > sig.entry  # LONG trigger above entry


async def test_uses_stamped_trigger_price_when_present(mock_send):
    """When the signal is dispatched with a stamped trigger price, the
    monitor must fire against the stamped target — NOT recompute from
    current ATR.  Locks the dispatch-time promise (B11)."""
    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    # Stamp values that disagree with what the static fallback would produce —
    # if the monitor honoured the stamp, it'll fire only at this price.
    sig.pre_tp_threshold_pct = 0.50  # locked higher than the 0.35 default
    sig.pre_tp_trigger_price = 30150.0  # entry × 1.005

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"):
        # +0.40% high — would fire at 0.35 floor, must NOT fire at 0.50 stamp.
        fired_below = await monitor._check_pre_tp_grab(
            sig, c_high=30000.0 * 1.0040, c_low=29990.0
        )
        assert fired_below is False
        assert sig.pre_tp_hit is False

        # +0.55% high — clears the stamped 0.50 target.
        fired_above = await monitor._check_pre_tp_grab(
            sig, c_high=30000.0 * 1.0055, c_low=29990.0
        )
        assert fired_above is True
        assert sig.pre_tp_hit is True
        # The post must report the stamped threshold, not the recomputed value.
        assert sig.pre_tp_pct == pytest.approx(0.50)


async def test_backfills_stamp_for_legacy_unstamped_signals(mock_send):
    """Pre-rollout signals already in flight have zero in the stamp fields.
    First monitor tick that resolves the threshold should backfill so that
    if persistence flushes between this tick and the next the trigger
    survives a restart."""
    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(direction=Direction.LONG, entry=30000.0)
    assert sig.pre_tp_threshold_pct == 0.0  # legacy state
    assert sig.pre_tp_trigger_price == 0.0

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"):
        # Probe at +0.10% — below threshold so we don't fire; just exercising
        # the resolution path which should NOT stamp (because we never
        # entered the fire branch).  Actually current implementation stamps
        # before threshold check — verify that.
        await monitor._check_pre_tp_grab(
            sig, c_high=30000.0 * 1.0010, c_low=29990.0
        )

    # Backfill happened during resolution, even though we didn't fire.
    assert sig.pre_tp_threshold_pct > 0
    assert sig.pre_tp_trigger_price > sig.entry


async def test_fires_when_short_candle_low_reaches_threshold(mock_send):
    send, _ = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(
        direction=Direction.SHORT,
        entry=30000.0,
        stop_loss=30150.0,  # SHORT SL above entry
        tp1=29550.0,  # -1.5%
    )
    target_low = 30000.0 * (1 - 0.0035)  # -0.35%

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30005.0, c_low=target_low)

    assert fired is True
    assert sig.pre_tp_hit is True
    # SL ratchets DOWN to entry for SHORT
    assert sig.stop_loss == pytest.approx(30000.0)


async def test_posts_to_both_active_and_free_channel(mock_send):
    send, sent = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(signal_tier="B")
    target_high = 30000.0 * 1.0035

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    chat_ids = [c for c, _ in sent]
    assert "FREE-CHAN" in chat_ids
    assert "ACTIVE-CHAN" in chat_ids
    free_msg = next(t for c, t in sent if c == "FREE-CHAN")
    # 2026-05-17 (PR #3): no broker attached in this test → no partial close
    # executed → "Quick Move" (signal-only mode) wording instead of "Quick Win"
    # (which is reserved for the partial-close-executed path).  See
    # test_partial_close_fires_when_broker_enabled for the broker-active case.
    assert "Quick Move" in free_msg
    assert "BTCUSDT" in free_msg
    # Math sanity: +0.35% raw at 10x = +3.5% gross; minus 0.7% fees = +2.8% net
    assert "+2.80%" in free_msg or "2.80%" in free_msg


async def test_active_channel_alert_is_dedicated_format_not_generic_update(mock_send):
    """Regression guard for the 2026-05-07 fix.

    The original Pre-TP active-channel post piggybacked on ``_post_update``,
    so subscribers saw a generic status template (Entry/Current/PnL/SL/Conf
    rows) with the Pre-TP message buried as the first line.  Worse, the
    template injected literal ``\\|`` separators (MarkdownV2 escape under
    legacy parse_mode) so the line rendered with visible backslashes.

    The dedicated alert (``_post_pre_tp_alert``) sends a clean, eye-catching
    "PRE-TP BANKED" header with no MarkdownV2 leakage.
    """
    send, sent = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(signal_tier="B")
    target_high = 30000.0 * 1.0035

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    active_msgs = [t for c, t in sent if c == "ACTIVE-CHAN"]
    assert len(active_msgs) == 1, "Pre-TP must produce exactly one active-channel alert"
    msg = active_msgs[0]
    # 2026-05-17 (PR #3): no broker attached → "PRE-TP TRIGGER" (signal-only
    # mode) instead of "PRE-TP BANKED" (which only fires when a real partial
    # close was executed).  The dedicated-alert format is preserved either way.
    assert "PRE-TP TRIGGER" in msg or "PRE-TP PARTIAL CLOSE" in msg
    # No misleading "BANKED" wording when nothing was banked (B3 honesty fix).
    assert "BANKED" not in msg, (
        "Pre-2026-05-17 'Banked +X%' wording must not appear when no broker "
        "partial executed — B3 honesty fix (PR #3)."
    )
    assert "BTCUSDT" in msg
    assert "LONG" in msg
    assert "breakeven" in msg
    # No legacy generic-update artefacts
    assert "PnL:" not in msg, "Pre-TP alert must not piggyback on the generic status template"
    assert "Confidence:" not in msg, "Pre-TP alert must not include the generic confidence row"
    # No MarkdownV2 escape leakage under legacy Markdown parse mode
    assert "\\|" not in msg, "MarkdownV2 \\| escape must not appear under legacy Markdown"


# ---------------------------------------------------------------------------
# Real partial close (OWNER_BRIEF §3.2a + B17, 2026-05-17)
# ---------------------------------------------------------------------------


async def test_partial_close_fires_when_broker_enabled(mock_send):
    """When the auto-trade broker is enabled, pre-TP must call ``close_partial``
    on the order manager with the configured grab fraction and ``tp_level=0``.

    Pre-2026-05-17 behaviour was SL-to-breakeven only — the Telegram message
    claimed "Banked +X%" but no fill actually executed.  Post-PR-#3 the broker
    receives a real partial-close instruction, the residual SL moves to entry,
    and the "PRE-TP PARTIAL CLOSE" + "Quick Win" wording fires.
    """
    send, sent = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(signal_tier="B")
    target_high = 30000.0 * 1.0035

    # Wire a broker mock with is_enabled=True so the partial-close branch runs.
    order_manager = AsyncMock()
    order_manager.is_enabled = True
    order_manager.close_partial.return_value = "fill-id-pre-tp"
    monitor._order_manager = order_manager

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("src.trade_monitor.PRE_TP_GRAB_FRACTION", 0.50), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    # Broker received the partial-close instruction with the configured fraction
    # and tp_level=0 (distinguishes pre-TP partials from TP1/2/3 in telemetry).
    order_manager.close_partial.assert_awaited_once()
    args, kwargs = order_manager.close_partial.call_args
    assert args[0] is sig
    # close_partial(sig, fraction, tp_level=N) — accept positional or keyword
    fraction = kwargs.get("fraction") if "fraction" in kwargs else args[1]
    tp_level = kwargs.get("tp_level") if "tp_level" in kwargs else (args[2] if len(args) > 2 else None)
    assert fraction == pytest.approx(0.50)
    assert tp_level == 0, (
        "tp_level=0 marks this as a pre-TP partial in trade_records — "
        "distinguishes from TP1/2/3 partials (tp_level=1/2/3)."
    )

    # Signal state — partial_close_pct reflects the realised fraction; SL at
    # entry (breakeven) on the residual.
    assert sig.partial_close_pct == pytest.approx(0.50)
    assert sig.stop_loss == pytest.approx(sig.entry)
    assert sig.pre_tp_hit is True

    # Honest active-channel wording: "PARTIAL CLOSE", not "BANKED".  Free
    # channel uses "Quick Win" only when a real fill happened.
    active_msg = next(t for c, t in sent if c == "ACTIVE-CHAN")
    assert "PARTIAL CLOSE" in active_msg
    assert "BANKED" not in active_msg
    assert "50%" in active_msg
    free_msg = next(t for c, t in sent if c == "FREE-CHAN")
    assert "Quick Win" in free_msg
    assert "Closed 50%" in free_msg


async def test_partial_close_skipped_when_broker_disabled(mock_send):
    """When ``order_manager.is_enabled`` is False, the path falls back to
    SL-to-breakeven only — no broker call, no "BANKED" wording, honest
    "PRE-TP TRIGGER" framing instead.
    """
    send, sent = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(signal_tier="B")
    target_high = 30000.0 * 1.0035

    order_manager = AsyncMock()
    order_manager.is_enabled = False
    monitor._order_manager = order_manager

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    order_manager.close_partial.assert_not_called()
    # 2026-05-19 update: partial_close_pct IS stamped on the broker-disabled
    # fallback so the signal-level pnl_pct blend in _set_realized_pnl
    # reflects the doctrine-true gross return (50% × +0.35% banked + 50%
    # × 0% BE exit on residual = +0.175%).  Pre-fix, this assertion
    # required `sig.partial_close_pct == 0.0` and the Signals tab then
    # showed 0.00% on signals that the doctrine intended to lock +0.15%.
    assert sig.partial_close_pct == pytest.approx(0.5)
    # But SL still ratchets to breakeven so signal-only subscribers get the
    # downside protection
    assert sig.stop_loss == pytest.approx(sig.entry)
    active_msg = next(t for c, t in sent if c == "ACTIVE-CHAN")
    assert "PRE-TP TRIGGER" in active_msg
    assert "BANKED" not in active_msg


async def test_partial_close_failure_falls_through_to_sl_only(mock_send):
    """If ``broker.close_partial`` raises, the path must still ratchet SL to
    breakeven and post the signal-only fallback alert.  Capital preservation
    is the doctrine — never silently fail to protect.
    """
    send, sent = mock_send
    monitor = _build_monitor(send, regime_label="QUIET")
    sig = _make_signal(signal_tier="B")
    target_high = 30000.0 * 1.0035

    order_manager = AsyncMock()
    order_manager.is_enabled = True
    order_manager.close_partial.side_effect = RuntimeError("broker down")
    monitor._order_manager = order_manager

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True  # Pre-TP still fires even when broker fails
    # 2026-05-19: partial_close_pct IS stamped on this fallback path so
    # the signal-level pnl_pct blend reports the doctrine-true gross
    # return (matches the broker-disabled path above).  The "no broker
    # fill happened" semantic is now carried by the execution_note
    # string + the alert wording ("BANKED" must NOT appear) — not by
    # leaving partial_close_pct at 0.
    assert sig.partial_close_pct == pytest.approx(0.5)
    assert sig.stop_loss == pytest.approx(sig.entry)  # SL still ratcheted
    active_msg = next(t for c, t in sent if c == "ACTIVE-CHAN")
    assert "PRE-TP TRIGGER" in active_msg or "PRE-TP PARTIAL CLOSE" in active_msg
    # Critical: no false "BANKED" wording on broker failure
    assert "BANKED" not in active_msg


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
        send_telegram=send,
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


async def test_paid_tier_pre_tp_fires_free_post(mock_send):
    """Replaces the legacy "WATCHLIST suppresses free-channel post" test.
    The WATCHLIST tier was removed in the app-era doctrine reset; every
    signal that reaches trade_monitor is paid (B+) and DOES post pre-TP
    storytelling to the free channel.
    """
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(signal_tier="B")

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is True
    chat_ids = [c for c, _ in sent]
    assert "FREE-CHAN" in chat_ids


async def test_free_post_failure_does_not_break_state_change(mock_send):
    """A free-channel send error must not roll back pre_tp_hit / SL move."""
    sent: list[tuple[str, str]] = []

    async def _send(chat_id, text):
        if chat_id == "FREE-CHAN":
            raise RuntimeError("free channel down")
        sent.append((chat_id, text))
        return True

    monitor = _build_monitor(AsyncMock(side_effect=_send))
    sig = _make_signal()

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"):
        fired = await monitor._check_pre_tp_grab(sig, c_high=30000.0 * 1.005, c_low=29990.0)

    assert fired is True
    assert sig.pre_tp_hit is True
    assert sig.stop_loss == pytest.approx(30000.0)


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
        send_telegram=send,
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


async def test_full_close_finalizes_and_removes_signal(mock_send):
    """grab_fraction == 1.00 closes 100% of the position — there is NO residual
    riding to TP1.  The engine-wide Signal must be finalized (terminal outcome
    label) and removed from the Open book, not left ACTIVE forever.  This is the
    orphan that showed signals ACTIVE in the app while the account was flat.
    """
    send, sent = mock_send
    book: dict = {}
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value="QUIET")
    )
    monitor = TradeMonitor(
        data_store=MagicMock(),
        send_telegram=send,
        get_active_signals=lambda: book,
        remove_signal=lambda sid: book.pop(sid, None),
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0, "ema_slope": 0.0},
    )
    sig = _make_signal(signal_tier="B")
    book[sig.signal_id] = sig
    target_high = 30000.0 * 1.0035

    order_manager = AsyncMock()
    order_manager.is_enabled = True
    order_manager.close_partial.return_value = "fill-id-pre-tp"
    monitor._order_manager = order_manager

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("src.trade_monitor.PRE_TP_GRAB_FRACTION", 1.00), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    # Finalized + removed from the Open book — no orphan.
    assert sig.signal_id not in book
    assert sig.status.upper() != "ACTIVE"
    # PnL frozen at the banked threshold (100% × pre-TP move).
    assert sig.pre_tp_pct > 0
    assert sig.pnl_pct == pytest.approx(sig.pre_tp_pct)
    # Free-channel wording reflects a full bank, not a riding residual.
    free_msg = next(t for c, t in sent if c == "FREE-CHAN")
    assert "Closed 100%" in free_msg
    assert "fully banked" in free_msg
    assert "rides to TP1" not in free_msg


async def test_partial_close_keeps_signal_active_with_residual(mock_send):
    """grab_fraction < 1.00 banks a partial and the residual rides to TP1 —
    the Signal must STAY ACTIVE and remain in the Open book (regression guard
    for the full-close finalize: it must not finalize a partial)."""
    send, sent = mock_send
    book: dict = {}
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value="QUIET")
    )
    monitor = TradeMonitor(
        data_store=MagicMock(),
        send_telegram=send,
        get_active_signals=lambda: book,
        remove_signal=lambda sid: book.pop(sid, None),
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0, "ema_slope": 0.0},
    )
    sig = _make_signal(signal_tier="B")
    book[sig.signal_id] = sig
    target_high = 30000.0 * 1.0035

    order_manager = AsyncMock()
    order_manager.is_enabled = True
    order_manager.close_partial.return_value = "fill-id-pre-tp"
    monitor._order_manager = order_manager

    with patch("src.trade_monitor.PRE_TP_ENABLED", True), \
         patch("src.trade_monitor.PRE_TP_GRAB_FRACTION", 0.50), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"), \
         patch("src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "ACTIVE-CHAN"}):
        fired = await monitor._check_pre_tp_grab(sig, c_high=target_high, c_low=29990.0)

    assert fired is True
    # Partial — still open, still in the book, residual rides to TP1.
    assert sig.signal_id in book
    assert sig.status == "ACTIVE"
    free_msg = next(t for c, t in sent if c == "FREE-CHAN")
    assert "rides to TP1" in free_msg
