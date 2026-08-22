"""``signals_today`` across the engine/api process boundary.

Isolated mode (``API_PROCESS_ISOLATED=true``, which is production) splits the
engine in two: the **engine** container holds ``_signal_history`` and the
**api** container serves HTTP off a Redis snapshot.  ``SnapshotWriter``
published ``signals_today_count`` across that boundary from the day the
facade was written, and nothing ever read it —
``RedisEngineFacade._signal_history`` returned ``[]`` under a comment saying
the count was "pre-computed in engine_state", so ``build_pulse`` walked an
empty list and the Pulse header served ``signals_today: 0`` on every request
production answered.  The owner read that zero on 2026-08-22 beside a feed,
built from the same engine, showing eleven signals stamped that day.

A field one process writes and no process reads — #817 with the arrow
reversed, one deployment mode down, and invisible because **zero is also what
a correct count reads on a quiet morning**.  Nothing crashed and no screen was
empty; the number was simply always the same number.

So these tests do not assert a function's return shape against itself.  They
drive the **real** ``SnapshotWriter._build_engine_state`` to produce the
payload, hand that payload to the **real** ``RedisEngineFacade``, and assert
what ``build_pulse`` publishes off it — because a fixture chooses a shape and
then agrees with you about it, and this defect lived precisely in the gap
between two halves that were each individually right.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import pytest

from src.api.redis_engine import RedisEngineFacade
from src.api.snapshot import build_pulse
from src.api.snapshot_writer import SnapshotWriter
from src.channels.base import Signal
from src.smc import Direction


# ---------------------------------------------------------------------------
# Fixtures — the engine side is real ``Signal`` objects, never dicts.
# ---------------------------------------------------------------------------

def _sig(when: datetime, symbol: str = "BTCUSDT") -> Signal:
    return Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=Direction.LONG,
        entry=100.0,
        stop_loss=98.0,
        tp1=103.0,
        tp2=106.0,
        setup_class="MOVER_TREND_PULLBACK",
        signal_id=f"{symbol}-{when.isoformat()}",
        timestamp=when,
    )


class _Engine:
    """The smallest object ``_build_engine_state`` and ``build_pulse`` accept.

    Deliberately not a mock of the facade: this stands in for the **engine**
    container, the process that actually holds the history.
    """

    def __init__(self, history: List[Signal]) -> None:
        self._signal_history = history
        self._current_auto_mode = "paper"
        self._boot_time = 0.0
        self._risk_manager = None
        self._order_manager = None
        self.router = None
        self.pair_mgr = None


def _today(hour: int = 6) -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def _yesterday(hour: int = 6) -> datetime:
    return _today(hour) - timedelta(days=1)


def _engine_state(engine: Any) -> dict:
    """Run the REAL writer's engine-state build, off the event loop."""
    writer = SnapshotWriter(engine, redis_client=None)
    return writer._build_engine_state(task_names=[])


def _facade(state: dict) -> RedisEngineFacade:
    """The REAL facade, loaded with a payload the real writer produced."""
    facade = RedisEngineFacade(redis_client=None)
    facade._state = state
    return facade


# ---------------------------------------------------------------------------
# The contract
# ---------------------------------------------------------------------------

async def test_isolated_mode_pulse_reports_the_engines_own_count():
    """The defect, end to end: three signals today must not publish as zero."""
    engine = _Engine([_sig(_today(1)), _sig(_today(3)), _sig(_today(5))])

    state = _engine_state(engine)
    assert state["signals_today_count"] == 3, "writer half"

    pulse = await build_pulse(_facade(state))
    assert pulse.signals_today == 3, (
        "the api container published a count the engine did not compute — "
        "this is the 2026-08-22 defect"
    )


async def test_writer_and_reader_agree_on_which_day_a_signal_belongs_to():
    """Yesterday's rows are excluded at BOTH ends, not just one.

    Two implementations of "which day is this signal" is how the two halves
    drift apart while each looks right on its own, so both ends route through
    ``snapshot._signal_date``.
    """
    engine = _Engine([_sig(_yesterday()), _sig(_today(2)), _sig(_yesterday(23))])

    state = _engine_state(engine)
    pulse = await build_pulse(_facade(state))

    assert state["signals_today_count"] == 1
    assert pulse.signals_today == 1


async def test_a_restart_restored_iso_string_timestamp_is_counted_not_crashed():
    """``Signal.timestamp`` can come back as a string, and did.

    ``main.py``'s expiry path already documents "the ISO-string form a
    restart-restored Signal may carry".  The pre-fix count guarded with
    ``getattr(s, "timestamp", None) is not None``, which **passes** on a
    string and then raises on ``.date()`` — a guard about presence where the
    hazard was type.
    """
    sig = _sig(_today(4))
    sig.timestamp = _today(4).isoformat()  # type: ignore[assignment]
    engine = _Engine([sig])

    state = _engine_state(engine)
    assert state["signals_today_count"] == 1

    pulse = await build_pulse(_facade(state))
    assert pulse.signals_today == 1


async def test_an_unreadable_timestamp_is_skipped_rather_than_raising():
    """A row we cannot date is not counted, and does not take the page down."""
    good, bad = _sig(_today(4)), _sig(_today(5))
    bad.timestamp = "not-a-timestamp"  # type: ignore[assignment]
    worse = _sig(_today(6))
    worse.timestamp = None  # type: ignore[assignment]

    state = _engine_state(_Engine([good, bad, worse]))
    assert state["signals_today_count"] == 1


async def test_an_engine_that_never_published_the_key_is_not_read_as_zero():
    """``None`` means *the engine did not say*, and must fall through.

    An older engine publishes no ``signals_today_count``.  Reading that as
    ``0`` is the same conflation the whole fix is about — "no signals today"
    and "nobody told me" are different states with different next moves.
    """
    facade = _facade({})  # an engine predating the key
    assert facade.signals_today_count is None

    # Single-process mode has no precomputed count either, and there the walk
    # over a REAL history is authoritative — so both deployments answer the
    # same question rather than one of them answering zero.
    engine = _Engine([_sig(_today(1)), _sig(_today(2))])
    pulse = await build_pulse(engine)
    assert pulse.signals_today == 2


async def test_the_facade_history_stays_empty_and_the_count_carries_it():
    """Pin the split itself.

    If a future change makes ``_signal_history`` non-empty on the facade this
    test should be revisited deliberately rather than passing by accident —
    the facade has no signals and must not pretend to.
    """
    state = _engine_state(_Engine([_sig(_today(1))]))
    facade = _facade(state)

    assert facade._signal_history == []
    assert facade.signals_today_count == 1


@pytest.mark.parametrize("raw", ["4", 4, 4.0])
async def test_a_json_roundtripped_count_still_reads_as_an_int(raw: Any):
    """The payload crosses Redis as JSON; tolerate what comes back."""
    assert _facade({"signals_today_count": raw}).signals_today_count == 4


@pytest.mark.parametrize("raw", ["", "many", [], {}])
async def test_an_uninterpretable_count_falls_back_rather_than_guessing(raw: Any):
    assert _facade({"signals_today_count": raw}).signals_today_count is None


# ---------------------------------------------------------------------------
# The derived guard — the half that stops the NEXT field reading zero
# ---------------------------------------------------------------------------

async def test_no_pulse_field_may_derive_from_the_facades_empty_history():
    """``build_pulse`` must not reach ``_signal_history`` without a fallback.

    The fix above repairs one field.  This is the guard against the next one:
    any quantity ``build_pulse`` computes by walking ``_signal_history`` is
    structurally zero in isolated mode, so it needs a precomputed sibling the
    way ``signals_today`` now has one.  Asserted by **behaviour** rather than
    by reading the source — a facade whose history is empty and whose
    precomputed counts are present must publish the same pulse as an engine
    holding the real rows.
    """
    history = [_sig(_today(1)), _sig(_today(2)), _sig(_today(3)), _sig(_yesterday())]
    engine = _Engine(history)

    single_process = await build_pulse(engine)
    isolated = await build_pulse(_facade(_engine_state(engine)))

    assert isolated.signals_today == single_process.signals_today, (
        "isolated mode disagreed with single-process mode about the same "
        "history — a pulse field is being derived from the facade's empty "
        "history with no precomputed sibling"
    )
