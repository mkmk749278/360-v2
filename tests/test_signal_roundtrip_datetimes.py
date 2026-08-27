"""The persisted Signal round trip is a contract, and it was lossy.

``_signal_to_dict`` stringifies **every** datetime by walking the values;
``_signal_from_dict`` restored three of them **by name**. That list is a floor:
it covers exactly the fields somebody already typed and is silent by
construction on the next one. Five had accumulated — ``dispatch_timestamp``,
``first_sl_touch_timestamp``, ``first_tp_touch_timestamp``,
``terminal_outcome_timestamp``, ``pre_tp_timestamp`` — and every one came back
as a ``str``.

Nothing could observe it while the process lived, so it sat there until #981
handed a restored terminal signal to ``_record_outcome``, which calls
``.timestamp()`` on three of them:

    AttributeError: 'str' object has no attribute 'timestamp'

…so the restore drain recorded nothing and the trade it exists to save stayed
missing from the track record. The ``close_accounting`` probe shipped in that
same PR caught it in production 28 minutes after deploy.

Every test here fails against the pre-fix tree.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.channels.base import Signal
from src.signal_router import (
    SignalRouter,
    _signal_from_dict,
    _signal_to_dict,
    _SIGNAL_DATETIME_FIELDS,
)
from src.smc import Direction
from src.trade_monitor import TradeMonitor


def _datetime_fields_on_signal() -> list[str]:
    """Derived here too, so this test cannot drift from the dataclass."""
    return [f.name for f in dataclasses.fields(Signal) if "datetime" in str(f.type)]


def _fully_stamped_signal() -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="LITUSDT",
        direction=Direction.LONG,
        entry=3.0,
        stop_loss=2.9,
        tp1=3.2,
        tp2=3.3,
        confidence=70.0,
        signal_id="RT-1",
    )
    now = datetime.now(timezone.utc)
    # Populate EVERY datetime field, whatever they are — a field added
    # tomorrow is covered without editing this test.
    for i, name in enumerate(_datetime_fields_on_signal()):
        setattr(sig, name, now - timedelta(minutes=i))
    sig.status = "BREAKEVEN_EXIT"
    sig.setup_class = "MOVER_TREND_PULLBACK"
    return sig


class TestRoundTrip:
    def test_the_derived_set_matches_the_dataclass(self):
        assert set(_SIGNAL_DATETIME_FIELDS) == set(_datetime_fields_on_signal())
        assert len(_SIGNAL_DATETIME_FIELDS) >= 8, (
            "a shrinking set means the derivation stopped seeing annotations"
        )

    @pytest.mark.parametrize("field", _datetime_fields_on_signal())
    def test_every_datetime_field_survives_the_round_trip(self, field):
        sig = _fully_stamped_signal()
        back = _signal_from_dict(_signal_to_dict(sig))
        assert back is not None
        value = getattr(back, field)
        assert isinstance(value, datetime), (
            f"{field} came back as {type(value).__name__} — the serializer "
            f"stringifies every datetime, so the restore must parse every one"
        )
        assert value == getattr(sig, field)

    def test_the_serializer_stringifies_exactly_what_the_restore_parses(self):
        """Pin both halves against each other, not against a written list."""
        sig = _fully_stamped_signal()
        raw = _signal_to_dict(sig)
        stringified = {
            k for k, v in raw.items()
            if isinstance(v, str) and k in _datetime_fields_on_signal()
        }
        assert stringified == set(_SIGNAL_DATETIME_FIELDS)


class TestRestoredSignalCanBeRecorded:
    """The failure that surfaced it, driven through the real collaborators."""

    def _monitor(self, tracker):
        ds = MagicMock()
        ds.get_candles.return_value = {}
        ds.ticks = {}
        return TradeMonitor(
            data_store=ds,
            send_telegram=AsyncMock(),
            get_active_signals=lambda: {},
            remove_signal=lambda sid: None,
            update_signal=MagicMock(),
            performance_tracker=tracker,
        )

    def test_record_outcome_accepts_a_restored_signal(self):
        tracker = MagicMock()
        mon = self._monitor(tracker)
        back = _signal_from_dict(_signal_to_dict(_fully_stamped_signal()))

        ok = mon._record_outcome_guarded(
            back, hit_tp=0, hit_sl=True, site="test.restored"
        )

        assert ok is True, "a restored terminal signal must be recordable"
        assert mon._unrecorded_closes == 0
        assert tracker.record_outcome.call_count == 1

    def test_the_restore_drain_actually_records(self, monkeypatch):
        """End to end: persisted terminal signal -> restore -> record.

        This is the path #981 added and this bug made inert.
        """
        monkeypatch.setattr("src.main.save_history", lambda *_a, **_k: None)
        from src.main import CryptoSignalEngine

        tracker = MagicMock()
        mon = self._monitor(tracker)

        router = SignalRouter(
            queue=MagicMock(), send_telegram=AsyncMock(), format_signal=MagicMock()
        )
        sig = _fully_stamped_signal()
        router._absorb_restored({sig.signal_id: _signal_to_dict(sig)})
        assert len(router.restored_terminal_signals) == 1

        eng = CryptoSignalEngine.__new__(CryptoSignalEngine)
        eng.monitor = mon
        eng.router = router
        eng._signal_history = []

        assert eng.finalise_restored_terminals() == 1
        assert tracker.record_outcome.call_count == 1
        assert mon._unrecorded_closes == 0
        assert [s.signal_id for s in eng._signal_history] == ["RT-1"]
