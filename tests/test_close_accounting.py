"""Every close must reach the closed-signal record, or stay retryable.

Four ways a delivered trade could vanish from the record before 2026-08-24,
none of which crashed, all of which left the app feed looking correct:

* the wedge -- a terminal status stamped, the close raised, the signal sat in
  the active book forever (fixed in #980);
* ``close_signal_manual`` -- ``_post_update`` sat ahead of ``_record_outcome``
  inside one try, and ``_remove`` ran unconditionally after it, so a Telegram
  timeout archived and dropped the signal with no record.  Measured: BTCUSDT
  SHORT +1.08% on 2026-08-22, in the feed, in none of the record's 1,297 rows;
* the reconciler's zombie close -- called ``_record_outcome`` zero times, so
  every reconciler-closed signal was missing by construction;
* the router's restore -- tested ``status != "ACTIVE"``, which both discarded
  still-live ``TP1_HIT``/``TP2_HIT`` signals and silently dropped genuinely
  terminal ones instead of recording them.

Each test here fails against the pre-fix tree.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.channels.base import LIVE_STATUSES, TERMINAL_STATUSES, Signal
from src.signal_router import SignalRouter, _signal_to_dict
from src.smc import Direction
from src.trade_monitor import TradeMonitor


def _make_signal(*, signal_id="CA-1", status="ACTIVE", symbol="BTCUSDT") -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=Direction.SHORT,
        entry=100.0,
        stop_loss=102.0,
        tp1=98.0,
        tp2=96.0,
        confidence=71.0,
        signal_id=signal_id,
    )
    sig.timestamp = datetime.now(timezone.utc) - timedelta(seconds=900)
    sig.setup_class = "QUIET_COMPRESSION_BREAK"
    sig.status = status
    sig.current_price = 99.0
    sig.entry_zone_filled = True
    return sig


def _monitor(active, tracker=None, send=None):
    removed: list = []

    async def _ok_send(chat_id, text):
        return None

    ds = MagicMock()
    ds.get_candles.return_value = {}
    ds.ticks = {}
    mon = TradeMonitor(
        data_store=ds,
        send_telegram=send or _ok_send,
        get_active_signals=lambda: dict(active),
        remove_signal=lambda sid: removed.append(sid),
        update_signal=MagicMock(),
        performance_tracker=tracker,
    )
    mon._broker_close_full = AsyncMock()
    return mon, removed


class TestManualClose:
    async def test_telegram_failure_does_not_cost_the_record(self, monkeypatch):
        monkeypatch.setattr(
            "src.trade_monitor.CHANNEL_TELEGRAM_MAP", {"360_SCALP": "-100999"}
        )
        tracker = MagicMock()

        async def _boom(chat_id, text):
            raise TimeoutError("telegram down")

        sig = _make_signal()
        mon, removed = _monitor({sig.signal_id: sig}, tracker, send=_boom)
        monkeypatch.setattr(mon, "_latest_price", lambda symbol: 99.0)

        res = await mon.close_signal_manual(sig.signal_id, reason="owner")

        assert tracker.record_outcome.call_count == 1, (
            "the record must be written even though the Telegram post failed"
        )
        assert res["recorded"] is True
        assert removed == [sig.signal_id]

    async def test_a_close_that_cannot_record_is_not_removed(self, monkeypatch):
        """Removing an unrecorded close is what makes the loss permanent."""
        tracker = MagicMock()
        tracker.record_outcome.side_effect = RuntimeError("disk full")

        sig = _make_signal()
        mon, removed = _monitor({sig.signal_id: sig}, tracker)
        monkeypatch.setattr(mon, "_latest_price", lambda symbol: 99.0)

        res = await mon.close_signal_manual(sig.signal_id, reason="owner")

        assert res["recorded"] is False
        assert removed == [], (
            "an unrecorded close must stay in the active book so it can retry"
        )
        assert mon._unrecorded_closes == 1

    async def test_manual_close_is_labelled_closed_not_expired(self, monkeypatch):
        tracker = MagicMock()
        sig = _make_signal()
        mon, _ = _monitor({sig.signal_id: sig}, tracker)
        monkeypatch.setattr(mon, "_latest_price", lambda symbol: 99.0)

        await mon.close_signal_manual(sig.signal_id, reason="owner")

        assert tracker.record_outcome.call_args.kwargs["outcome_label"] == "CLOSED", (
            "an operator close is not an expiry — the record should keep the "
            "label the close committed to"
        )


class TestRestoreVocabulary:
    def _router(self):
        return SignalRouter(
            queue=MagicMock(), send_telegram=AsyncMock(), format_signal=MagicMock()
        )

    @pytest.mark.parametrize("status", sorted(LIVE_STATUSES))
    def test_live_signals_are_restored(self, status):
        """TP1_HIT / TP2_HIT are live — a restart must not discard them."""
        sig = _make_signal(signal_id=f"L-{status}", status=status)
        r = self._router()
        counts = r._absorb_restored({sig.signal_id: _signal_to_dict(sig)})
        assert counts["live"] == 1
        assert sig.signal_id in r._active_signals

    @pytest.mark.parametrize("status", sorted(TERMINAL_STATUSES))
    def test_terminal_signals_are_handed_back_not_dropped(self, status):
        sig = _make_signal(signal_id=f"T-{status}", status=status)
        r = self._router()
        counts = r._absorb_restored({sig.signal_id: _signal_to_dict(sig)})
        assert counts["terminal"] == 1
        assert sig.signal_id not in r._active_signals, "a closed signal is not live"
        assert [s.signal_id for s in r.restored_terminal_signals] == [sig.signal_id], (
            "it is owed a closed-signal record, so it must not be discarded"
        )

    def test_unrecognised_status_is_its_own_bucket(self):
        sig = _make_signal(signal_id="U-1", status="WAT")
        r = self._router()
        counts = r._absorb_restored({sig.signal_id: _signal_to_dict(sig)})
        assert counts == {"live": 0, "terminal": 0, "unknown": 1, "unparseable": 0}
        assert not r.restored_terminal_signals


class TestStatusVocabularyHasOneDefinition:
    """A second copy of these nine strings is how the two drift apart."""

    def test_no_module_redefines_the_terminal_set(self):
        root = Path(__file__).resolve().parents[1] / "src"
        offenders = []
        for path in root.rglob("*.py"):
            if path.name == "base.py" and path.parent.name == "channels":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                if not (isinstance(fn, ast.Name) and fn.id in {"frozenset", "set"}):
                    continue
                literals = {
                    e.value
                    for arg in node.args
                    if isinstance(arg, (ast.Set, ast.List, ast.Tuple))
                    for e in arg.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                }
                if {"SL_HIT", "PROFIT_LOCKED"} <= literals:
                    offenders.append(f"{path.relative_to(root)}:{node.lineno}")
        assert not offenders, (
            "these re-declare the terminal-status vocabulary instead of "
            f"importing channels.base.TERMINAL_STATUSES: {offenders}"
        )

    def test_live_and_terminal_do_not_overlap(self):
        assert not (LIVE_STATUSES & TERMINAL_STATUSES)
        assert "TP1_HIT" in LIVE_STATUSES and "TP1_HIT" not in TERMINAL_STATUSES


# ---------------------------------------------------------------------------
# Engine-side: the reconciler close, and the restore drain
# ---------------------------------------------------------------------------


def _engine(monitor, router=None, history=None):
    """A CryptoSignalEngine with only the attributes these paths touch.

    ``__new__`` deliberately skips the real constructor -- it builds the whole
    scanner, stores and executor -- while still running the real method bodies
    under test rather than a reimplementation of them.
    """
    from src.main import CryptoSignalEngine

    eng = CryptoSignalEngine.__new__(CryptoSignalEngine)
    eng.monitor = monitor
    eng.router = router if router is not None else MagicMock()
    eng._signal_history = history if history is not None else []
    eng._content_scheduler = MagicMock()
    eng.telegram = MagicMock()
    eng.telegram.send_admin_alert = AsyncMock()
    return eng


class TestReconcilerZombieClose:
    async def test_zombie_close_reaches_the_record(self, monkeypatch):
        monkeypatch.setattr("src.main.save_history", lambda *_a, **_k: None)
        tracker = MagicMock()
        sig = _make_signal(signal_id="Z-1")
        mon, _ = _monitor({sig.signal_id: sig}, tracker)

        router = MagicMock()
        router.active_signals = {sig.signal_id: sig}
        eng = _engine(mon, router=router)

        await eng._reconciler_close_signal(sig, reason="drift")

        assert tracker.record_outcome.call_count == 1, (
            "a reconciler-closed signal must not be archived with no record"
        )
        assert tracker.record_outcome.call_args.kwargs["outcome_label"] == "CANCELLED", (
            "the broker held no position — it must stay separable from real fills"
        )

    async def test_a_zombie_that_cannot_record_is_not_archived(self, monkeypatch):
        monkeypatch.setattr("src.main.save_history", lambda *_a, **_k: None)
        tracker = MagicMock()
        tracker.record_outcome.side_effect = RuntimeError("nope")
        sig = _make_signal(signal_id="Z-2")
        mon, _ = _monitor({sig.signal_id: sig}, tracker)

        router = MagicMock()
        router.active_signals = {sig.signal_id: sig}
        eng = _engine(mon, router=router)
        eng._remove_and_archive = MagicMock()

        await eng._reconciler_close_signal(sig, reason="drift")

        assert eng._remove_and_archive.call_count == 0


class TestRestoreDrain:
    async def test_terminal_signals_from_the_last_run_are_recorded(self, monkeypatch):
        monkeypatch.setattr("src.main.save_history", lambda *_a, **_k: None)
        tracker = MagicMock()
        wedged = _make_signal(signal_id="LIT-1", status="BREAKEVEN_EXIT",
                              symbol="LITUSDT")
        live = _make_signal(signal_id="BNB-1", status="TP1_HIT", symbol="BNBUSDT")

        router = SignalRouter(
            queue=MagicMock(), send_telegram=AsyncMock(), format_signal=MagicMock()
        )
        router._absorb_restored({
            wedged.signal_id: _signal_to_dict(wedged),
            live.signal_id: _signal_to_dict(live),
        })

        mon, _ = _monitor({}, tracker)
        eng = _engine(mon, router=router)

        n = eng.finalise_restored_terminals()

        assert n == 1
        assert tracker.record_outcome.call_count == 1
        assert tracker.record_outcome.call_args.kwargs["outcome_label"] == "BREAKEVEN_EXIT"
        assert [s.signal_id for s in eng._signal_history] == ["LIT-1"], (
            "the app feed and the record must agree about what closed"
        )
        assert live.signal_id in router._active_signals, (
            "a TP1_HIT signal is still running and must be back in the book"
        )

    def test_drain_is_idempotent(self, monkeypatch):
        monkeypatch.setattr("src.main.save_history", lambda *_a, **_k: None)
        tracker = MagicMock()
        router = SignalRouter(
            queue=MagicMock(), send_telegram=AsyncMock(), format_signal=MagicMock()
        )
        sig = _make_signal(signal_id="D-1", status="SL_HIT")
        router._absorb_restored({sig.signal_id: _signal_to_dict(sig)})
        eng = _engine(_monitor({}, tracker)[0], router=router)

        assert eng.finalise_restored_terminals() == 1
        assert eng.finalise_restored_terminals() == 0
        assert tracker.record_outcome.call_count == 1
