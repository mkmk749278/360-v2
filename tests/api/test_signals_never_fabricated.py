"""The Signals tab must never be served an invented trade.

The 2026-07-27 incident (same signature the 2026-07-24 IP ban produced, see
#778's "re-restored signals as entry-0 shells every cycle"): live subscribers
opened the Lumin Signals tab and saw three cards reading blank symbol, LONG,
ENTRY/SL/TP1/TP2 all ``0.00``, ``0.0 B``, ``Engine • UNCLASSIFIED``, ``ACTIVE``,
``open 1h`` / ``open 3h``, ``+0.00%``.

None of those signals existed.  In isolated mode ``/api/signals`` served from
``snapshot_cache``; when that cache went stale (>30 s with no fresh
``snapshot:signals_all`` — i.e. the engine container stopped publishing) the
route fell back to ``build_signals(engine, ...)`` where ``engine`` is a
``RedisEngineFacade``.  The facade's ``router.active_signals`` holds
``_MockSignal`` stubs carrying *only* ``signal_id`` and ``dispatch_timestamp``;
``_signal_to_detail`` reads every other field through ``getattr(..., default)``,
so each stub rendered as a complete, confident card of dataclass defaults.  The
facade also caches its engine-state dict last-good forever, so the stub map was
frozen — and ``hold_mins`` measures dispatch→*now*, so the phantoms aged
indefinitely with nothing able to close them.

Three properties are pinned here, each of which fails against the pre-fix code:

1. ``_signal_to_detail`` **refuses** an object that cannot support a card
   (no symbol / no entry) instead of clamping it to defaults.
2. ``build_signals`` pointed at a real ``RedisEngineFacade`` yields **nothing**,
   and the refusal is counted through ``fail_open`` so it can never be silent.
3. ``refresh_signals_all`` keeps the last-good published snapshot when the
   Redis key expires — that snapshot is the only real signal data the API
   container has, and discarding it is what left the route with only stubs.

No network, no real Redis — fakes only.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import MagicMock

import pytest

pytest.importorskip("pydantic")

from src import fail_open
from src.api.redis_engine import RedisEngineFacade
from src.api.snapshot import (
    UnrenderableSignal,
    _signal_to_detail,
    build_signals,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _facade_with_dispatch_map(**ages_hours: float) -> RedisEngineFacade:
    """A facade in exactly the state the incident left it in: a frozen
    ``active_signal_dispatch`` map and no published signal snapshot."""
    facade = RedisEngineFacade(redis_client=MagicMock())
    facade._state = {
        "active_signal_dispatch": {
            sid: (_now() - timedelta(hours=hours)).isoformat()
            for sid, hours in ages_hours.items()
        }
    }
    return facade


# ---------------------------------------------------------------------------
# 1. Refuse, don't clamp
# ---------------------------------------------------------------------------


class _Stub:
    """Stands in for ``_MockSignal`` — identity and timing, no geometry."""

    def __init__(self, signal_id: str) -> None:
        self.signal_id = signal_id
        self.dispatch_timestamp = _now() - timedelta(hours=1)
        self.timestamp = self.dispatch_timestamp


def test_signal_to_detail_refuses_a_stub_with_no_geometry():
    with pytest.raises(UnrenderableSignal):
        _signal_to_detail(_Stub("SCALP-AAA"))


def test_signal_to_detail_refuses_blank_symbol():
    sig = MagicMock()
    sig.signal_id = "SCALP-BBB"
    sig.symbol = "   "
    sig.entry = 50000.0
    with pytest.raises(UnrenderableSignal):
        _signal_to_detail(sig)


def test_signal_to_detail_refuses_zero_entry():
    sig = MagicMock()
    sig.signal_id = "SCALP-CCC"
    sig.symbol = "BTCUSDT"
    sig.entry = 0.0
    with pytest.raises(UnrenderableSignal):
        _signal_to_detail(sig)


def test_signal_to_detail_still_renders_a_real_signal():
    """Drive the real ``Signal`` dataclass, not a hand-shaped mock — a mock
    whose fields we chose can only assert our own assumptions back at us."""
    from src.channels.base import Direction, Signal

    sig = Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=Direction.LONG,
        entry=50000.0,
        stop_loss=49000.0,
        tp1=51000.0,
        tp2=52000.0,
        signal_id="SCALP-REAL",
        setup_class="SR_FLIP_RETEST",
        confidence=72.0,
        quality_tier="A",
        dispatch_timestamp=_now(),
    )

    detail = _signal_to_detail(sig, is_open=True)

    assert detail.symbol == "BTCUSDT"
    assert detail.entry == 50000.0
    assert detail.setup_class == "SR_FLIP_RETEST"
    assert detail.quality_tier == "A"
    assert detail.is_open is True


# ---------------------------------------------------------------------------
# 2. build_signals on the facade produces nothing — loudly
# ---------------------------------------------------------------------------


def test_build_signals_on_the_facade_fabricates_nothing():
    """The incident, reproduced end to end.

    Pre-fix this returned three SignalDetail objects with symbol='',
    entry=0.0, confidence=0.0, quality_tier='B', setup_class='UNCLASSIFIED',
    agent_name='Engine', status='ACTIVE', is_open=True — i.e. the screenshot.
    """
    facade = _facade_with_dispatch_map(
        **{"SCALP-AAA": 1.0, "SCALP-BBB": 3.0, "SCALP-CCC": 3.0}
    )

    assert build_signals(facade, status="all", limit=50) == []
    # The 'open' filter is what the app's Open tab requests — the stubs
    # carried no status at all, so they passed the open filter too.
    assert build_signals(facade, status="open", limit=50) == []


def test_refusals_are_counted_not_swallowed():
    """A dropped signal is never routine — the Hard Limit forbids a silent
    swallow in a data path, and the liveness watchdog pages off this counter."""
    site = "api.snapshot.unrenderable_signal"
    before = fail_open.snapshot().get(site, {}).get("count", 0)

    build_signals(_facade_with_dispatch_map(**{"SCALP-AAA": 1.0}), status="all")

    after = fail_open.snapshot().get(site, {}).get("count", 0)
    assert after == before + 1


# ---------------------------------------------------------------------------
# 3. The last-good published snapshot survives an engine outage
# ---------------------------------------------------------------------------


class _FakeRedis:
    """Minimal Redis stand-in whose GET result the test controls."""

    def __init__(self, value: Optional[str]) -> None:
        self.available = True
        self.client = self
        self._value = value

    async def get(self, _key: str) -> Optional[str]:
        return self._value


@pytest.mark.asyncio
async def test_refresh_signals_all_keeps_last_good_when_the_key_expires():
    import json

    payload = [{"signal_id": "SCALP-REAL", "symbol": "BTCUSDT"}]
    facade = RedisEngineFacade(redis_client=_FakeRedis(json.dumps(payload)))

    await facade.refresh_signals_all()
    assert facade.published_signals_all() == payload

    # Engine dies; snapshot:signals_all expires (TTL 60 s).
    facade._redis = _FakeRedis(None)
    await facade.refresh_signals_all()

    # Pre-fix this became None, leaving the route with nothing but stubs.
    assert facade.published_signals_all() == payload


def test_published_signals_all_is_none_before_any_publish():
    facade = RedisEngineFacade(redis_client=MagicMock())
    assert facade.published_signals_all() is None
