"""Tests for Phase 5 — signal-close storytelling.

`TradeMonitor._post_signal_closed` mirrors paid-tier signal closes (TP3 / SL)
to the free channel as social proof. Verifies:

* Paid-tier TP close posts to BOTH active and free channel
* Paid-tier SL close posts to BOTH (B3 — equal weight for losses)
* WATCHLIST tier never reaches the free mirror (defensive guard)
* Free-channel free-send failure does not break active-channel send
* CONTENT_ENGINE_ENABLED=False → no posts at all
* Free channel id missing → active-only
* Free == active (misconfig) → no duplicate
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor


def _make_signal(
    channel: str = "360_SCALP",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    stop_loss: float = 29850.0,
    tp1: float = 30150.0,
    tp2: float = 30300.0,
    tp3: float = 30450.0,
    signal_id: str = "STORY-001",
    signal_tier: str = "B",
) -> Signal:
    sig = Signal(
        channel=channel,
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        confidence=85.0,
        signal_id=signal_id,
    )
    sig.tp3 = tp3
    sig.original_entry = entry
    sig.current_price = entry
    sig.signal_tier = signal_tier
    sig.pnl_pct = 1.5
    return sig


def _build_monitor(send_telegram):
    monitor = TradeMonitor(
        data_store=MagicMock(),
        send_telegram=send_telegram,
        get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
    )
    monitor.engine_context_fn = lambda: {"regime": "RANGING"}
    return monitor


@pytest.fixture
def mock_send():
    """Tracks (chat_id, text) tuples for every Telegram send."""
    sent: list[tuple[str, str]] = []

    async def _send(chat_id, text):
        sent.append((chat_id, text))
        return True

    return AsyncMock(side_effect=_send), sent


@pytest.fixture
def patched_close_post():
    """Patch content_engine + config so close-post generation always returns text."""
    body = "✅ BTCUSDT LONG closed at TP3 — clean +2.0R execution."
    with patch("src.content_engine.generate_signal_closed_post", new=AsyncMock(return_value=body)), \
         patch("config.TELEGRAM_ACTIVE_CHANNEL_ID", "PAID-CHAN"), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"), \
         patch("config.CONTENT_ENGINE_ENABLED", True):
        yield body


# ---------------------------------------------------------------------------
# Routing matrix
# ---------------------------------------------------------------------------


async def test_paid_tier_tp_close_posts_to_both_channels(mock_send, patched_close_post):
    """Paid-tier TP3 hit → active channel + free channel (with header)."""
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(signal_tier="B")

    await monitor._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=30450.0)

    chat_ids = [chat for chat, _ in sent]
    assert "PAID-CHAN" in chat_ids
    assert "FREE-CHAN" in chat_ids
    assert len(sent) == 2

    free_text = next(t for c, t in sent if c == "FREE-CHAN")
    assert "Paid Signal Result" in free_text
    assert patched_close_post in free_text


async def test_paid_tier_sl_close_posts_to_both_channels(mock_send, patched_close_post):
    """Paid-tier SL hit → both channels (B3: SL gets equal weight)."""
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(signal_tier="A+")
    sig.pnl_pct = -1.0

    await monitor._post_signal_closed(sig, is_tp=False, close_price=29850.0)

    chat_ids = [chat for chat, _ in sent]
    assert chat_ids.count("PAID-CHAN") == 1
    assert chat_ids.count("FREE-CHAN") == 1


async def test_watchlist_tier_skips_free_mirror(mock_send, patched_close_post):
    """WATCHLIST signals never mirror to free channel even if they reach here."""
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(signal_tier="WATCHLIST")

    await monitor._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=30450.0)

    chat_ids = [chat for chat, _ in sent]
    assert chat_ids == ["PAID-CHAN"]


# ---------------------------------------------------------------------------
# Resilience / config edge cases
# ---------------------------------------------------------------------------


async def test_free_channel_failure_does_not_break_active_send(patched_close_post):
    """If free-channel send raises, the active-channel post is still recorded."""
    sent: list[tuple[str, str]] = []

    async def _send(chat_id, text):
        if chat_id == "FREE-CHAN":
            raise RuntimeError("free channel telegram down")
        sent.append((chat_id, text))
        return True

    monitor = _build_monitor(AsyncMock(side_effect=_send))
    sig = _make_signal(signal_tier="B")

    await monitor._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=30450.0)

    assert [c for c, _ in sent] == ["PAID-CHAN"]


async def test_content_engine_disabled_silent(mock_send):
    """CONTENT_ENGINE_ENABLED=False → zero posts."""
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal()

    with patch("src.content_engine.generate_signal_closed_post", new=AsyncMock(return_value="x")), \
         patch("config.TELEGRAM_ACTIVE_CHANNEL_ID", "PAID-CHAN"), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "FREE-CHAN"), \
         patch("config.CONTENT_ENGINE_ENABLED", False):
        await monitor._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=30450.0)

    assert sent == []


async def test_free_channel_unconfigured_active_only(mock_send):
    """TELEGRAM_FREE_CHANNEL_ID empty → posts only to active."""
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(signal_tier="B")

    with patch("src.content_engine.generate_signal_closed_post", new=AsyncMock(return_value="body")), \
         patch("config.TELEGRAM_ACTIVE_CHANNEL_ID", "PAID-CHAN"), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", ""), \
         patch("config.CONTENT_ENGINE_ENABLED", True):
        await monitor._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=30450.0)

    assert [c for c, _ in sent] == ["PAID-CHAN"]


async def test_free_equals_active_no_duplicate(mock_send):
    """Misconfiguration where free==active must not cause duplicate post."""
    send, sent = mock_send
    monitor = _build_monitor(send)
    sig = _make_signal(signal_tier="B")

    with patch("src.content_engine.generate_signal_closed_post", new=AsyncMock(return_value="body")), \
         patch("config.TELEGRAM_ACTIVE_CHANNEL_ID", "SAME-CHAN"), \
         patch("config.TELEGRAM_FREE_CHANNEL_ID", "SAME-CHAN"), \
         patch("config.CONTENT_ENGINE_ENABLED", True):
        await monitor._post_signal_closed(sig, is_tp=True, tp_label="TP3", close_price=30450.0)

    assert [c for c, _ in sent] == ["SAME-CHAN"]
