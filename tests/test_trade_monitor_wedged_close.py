"""A terminal status is not proof the close completed.

Every terminal path in ``trade_monitor`` stamps ``sig.status`` with its final
label *before* it awaits, and only afterwards records the outcome and drops the
signal from the active book.  A raise anywhere in between therefore leaves a
signal carrying a terminal label with **no** closed-signal record and **no**
removal — and the short-circuit at the top of ``_evaluate_signal`` then returned
on every subsequent tick, which turned a transient Telegram timeout into a
permanent leak.

Measured on production 2026-08-24: LITUSDT LONG sat ``BREAKEVEN_EXIT`` for two
days, absent from all 1,297 rows of the closed-signal record, still walked by
the monitor, and holding one of the three slots in the global same-direction
budget — which the router counts straight off ``_active_signals``, so a dead
signal starves live ones.  That is why the owner saw both "track record not
updating" and "only some signals auto-trade".

``_post_update`` was the raiser: first await on every close path, zero
exception handling, ending in a raw Telegram send.

Each test here fails against the pre-fix tree.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.trade_monitor import TradeMonitor


def _make_signal(
    *,
    signal_id: str = "WEDGE-1",
    status: str = "ACTIVE",
    entry: float = 100.0,
    direction: Direction = Direction.LONG,
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="LITUSDT",
        direction=direction,
        entry=entry,
        stop_loss=entry * 0.98,
        tp1=entry * 1.02,
        tp2=entry * 1.04,
        confidence=75.0,
        signal_id=signal_id,
    )
    sig.timestamp = datetime.now(timezone.utc) - timedelta(seconds=600)
    sig.setup_class = "MOVER_TREND_PULLBACK"
    sig.status = status
    sig.current_price = entry
    # Market-order semantics: no entry zone, so the fill gate never applies.
    sig.entry_zone_filled = True
    return sig


def _build_monitor(active, tracker=None, send=None):
    removed: list = []
    sent: list = []

    async def _default_send(chat_id, text):
        sent.append((chat_id, text))

    data_store = MagicMock()
    data_store.get_candles.return_value = {}
    data_store.ticks = {}
    monitor = TradeMonitor(
        data_store=data_store,
        send_telegram=send or _default_send,
        get_active_signals=lambda: dict(active),
        remove_signal=lambda sid: removed.append(sid),
        update_signal=MagicMock(),
        performance_tracker=tracker,
    )
    monitor._broker_close_full = AsyncMock()
    return monitor, removed, sent


class TestWedgedCloseRecovery:
    """The terminal short-circuit must finalise, not return forever."""

    async def test_terminal_status_without_a_record_is_finalised(self):
        tracker = MagicMock()
        sig = _make_signal(status="BREAKEVEN_EXIT")
        active = {sig.signal_id: sig}
        monitor, removed, _ = _build_monitor(active, tracker)

        await monitor._evaluate_signal(sig)

        assert tracker.record_outcome.call_count == 1, (
            "a terminal signal with no closed-signal record must be recorded"
        )
        assert removed == [sig.signal_id], "and dropped from the active book"
        assert monitor._unfinalised_recovered == 1

    async def test_the_recovered_record_keeps_the_label_the_close_committed_to(self):
        tracker = MagicMock()
        sig = _make_signal(status="BREAKEVEN_EXIT")
        sig.pnl_pct = 0.0
        monitor, _, _ = _build_monitor({sig.signal_id: sig}, tracker)

        await monitor._evaluate_signal(sig)

        kwargs = tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "BREAKEVEN_EXIT", (
            "recovery must not re-classify the trade into a different outcome"
        )
        assert kwargs["hit_sl"] is True

    async def test_invalidated_is_honoured_verbatim_on_recovery(self):
        tracker = MagicMock()
        sig = _make_signal(status="INVALIDATED")
        monitor, removed, _ = _build_monitor({sig.signal_id: sig}, tracker)

        await monitor._evaluate_signal(sig)

        assert tracker.record_outcome.call_args.kwargs["outcome_label"] == "INVALIDATED"
        assert removed == [sig.signal_id]

    async def test_a_recorded_but_unremoved_signal_is_removed_not_re_recorded(self):
        """Double-recording is the failure the original guard existed to stop."""
        tracker = MagicMock()
        sig = _make_signal(status="SL_HIT")
        monitor, removed, _ = _build_monitor({sig.signal_id: sig}, tracker)
        # The record landed; the removal did not.
        monitor._outcome_recorded_ids.add(sig.signal_id)

        await monitor._evaluate_signal(sig)

        assert tracker.record_outcome.call_count == 0, (
            "an already-recorded trade must never be counted twice"
        )
        assert removed == [sig.signal_id], "but it must still free its slot"

    async def test_repeated_evaluation_records_exactly_once(self):
        """The double-evaluation guard still holds after the fix."""
        tracker = MagicMock()
        sig = _make_signal(status="SL_HIT")
        monitor, removed, _ = _build_monitor({sig.signal_id: sig}, tracker)

        await monitor._evaluate_signal(sig)
        await monitor._evaluate_signal(sig)
        await monitor._evaluate_signal(sig)

        assert tracker.record_outcome.call_count == 1
        assert removed.count(sig.signal_id) >= 1


class TestPostUpdateNeverAbortsAClose:
    """The raiser itself: a subscriber post must not cost the record."""

    async def test_telegram_failure_does_not_abort_the_close(self, monkeypatch):
        monkeypatch.setattr(
            "src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "-100123"}
        )
        tracker = MagicMock()

        async def _boom(chat_id, text):
            raise TimeoutError("telegram timed out")

        sig = _make_signal(status="ACTIVE")
        monitor, removed, _ = _build_monitor(
            {sig.signal_id: sig}, tracker, send=_boom
        )
        # Drive the real SL path: price through the stop on both wick and mark.
        sig.current_price = sig.stop_loss * 0.99
        monkeypatch.setattr(
            monitor, "_candle_extremes",
            lambda symbol: (sig.stop_loss * 0.99, sig.stop_loss * 0.99),
        )

        await monitor._evaluate_signal(sig)

        assert tracker.record_outcome.call_count == 1, (
            "the outcome must be recorded even though the Telegram post raised"
        )
        assert removed == [sig.signal_id], (
            "and the signal must leave the active book, freeing direction budget"
        )

    async def test_post_update_swallows_and_counts_the_failure(self, monkeypatch):
        monkeypatch.setattr(
            "src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "-100123"}
        )
        from src import fail_open

        fail_open.reset()

        async def _boom(chat_id, text):
            raise TimeoutError("telegram timed out")

        sig = _make_signal()
        monitor, _, _ = _build_monitor({sig.signal_id: sig}, None, send=_boom)

        await monitor._post_update(sig, "🔴 EXIT")  # must not raise

        assert "trade_monitor._post_update" in fail_open.snapshot(), (
            "a fail-open except must count, never swallow silently"
        )


class TestOneBadSignalCostsOneSignal:
    async def test_a_raising_signal_does_not_abort_the_whole_cycle(self, monkeypatch):
        good = _make_signal(signal_id="GOOD-1")
        bad = _make_signal(signal_id="BAD-1")
        active = {good.signal_id: good, bad.signal_id: bad}
        monitor, _, _ = _build_monitor(active)
        monitor._publish_pricing_freshness = MagicMock()

        seen: list = []
        original = TradeMonitor._evaluate_signal

        async def _evaluate(self, sig):
            if sig.signal_id == "BAD-1":
                raise RuntimeError("boom")
            seen.append(sig.signal_id)
            return await original(self, sig)

        monkeypatch.setattr(TradeMonitor, "_evaluate_signal", _evaluate)
        monkeypatch.setattr(monitor, "_latest_price", lambda symbol: 100.0)

        await monitor._check_all()

        assert "GOOD-1" in seen, "a sibling's failure must not skip this signal"
        assert monitor._publish_pricing_freshness.called, (
            "everything below the gather must still run — the trailing sweeps, "
            "the ledger flushes and the live trail governor are down there"
        )
