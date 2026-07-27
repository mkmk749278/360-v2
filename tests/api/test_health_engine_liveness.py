"""``/api/health`` must report engine liveness — and must never fail on it.

Both halves matter, and they pull in opposite directions.

**Report it.** On 2026-07-27 the isolated API container ran ``healthy`` for
three hours with a dead engine and a dead Redis behind it. Every signal the
ops agent inspected was read *through* this container's last-good snapshot,
and a frozen snapshot looks perfectly healthy: pulse returned a plausible
status, ``/api/health`` returned 200, and the redis-idletime probe couldn't
run at all so it reported nothing. The detection mechanism ended up being a
subscriber's screenshot of three phantom signal cards.

``RedisEngineFacade.state_age_seconds`` — which already existed and was
surfaced nowhere — is the one quantity a freeze cannot fake: it measures how
long since Redis *answered*, not what the answer contained.

**Never fail on it.** This endpoint backs the api container's docker
HEALTHCHECK, which carries ``autoheal=true``. Returning non-200 while the
engine is down would make autoheal restart-loop the API for the duration of
the outage, and restarting the API cannot cure a dead engine. That is exactly
the loop #778 had to break on the engine container. The status code stays 200;
the fields carry the news.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

pytest.importorskip("pydantic")

from src.api.redis_engine import RedisEngineFacade
from src.api.schemas import HealthResponse


def _facade(refreshed_at: float | None) -> RedisEngineFacade:
    f = RedisEngineFacade(redis_client=MagicMock())
    if refreshed_at is not None:
        f._refreshed_at = refreshed_at
    return f


# ---------------------------------------------------------------------------
# state_age_seconds — the signal the whole fix rests on
# ---------------------------------------------------------------------------


def test_never_refreshed_reports_infinite_age():
    """Distinct from "stale": the API has never once heard from the engine."""
    assert _facade(None).state_age_seconds == float("inf")


def test_age_tracks_last_successful_read():
    f = _facade(time.monotonic() - 3600.0)
    assert 3590.0 < f.state_age_seconds < 3610.0


def test_a_failed_refresh_does_not_reset_the_clock():
    """The property that makes this detectable at all.

    ``refresh_state`` keeps the last-good ``_state`` when Redis returns
    nothing — deliberately, so the API can serve last-known-good. If it also
    advanced ``_refreshed_at`` the age would reset to zero on every failed
    poll and a permanently-dead engine would look permanently fresh.
    """
    f = _facade(time.monotonic() - 500.0)
    before = f.state_age_seconds
    f._redis.available = False  # refresh_state early-returns
    assert f.state_age_seconds >= before


# ---------------------------------------------------------------------------
# The response model — what the ops agent reads
# ---------------------------------------------------------------------------


def test_defaults_are_the_single_process_answer():
    """No facade → the engine IS this process → connected, age not applicable.

    ``None``, not ``0.0``: "the question doesn't apply" is not "just refreshed".
    """
    h = HealthResponse(uptime_seconds=10.0)
    assert h.engine_connected is True
    assert h.engine_state_age_seconds is None


def test_disconnected_payload_serialises_without_infinity():
    """``inf`` is not valid JSON — it must never reach the wire.

    Python's json module emits a bare ``Infinity`` token that strict parsers
    reject, so the handler maps a never-connected facade to ``None`` + a
    False flag rather than passing the raw age through.
    """
    h = HealthResponse(
        uptime_seconds=10.0,
        engine_connected=False,
        engine_state_age_seconds=None,
    )
    payload = h.model_dump_json()
    assert "Infinity" not in payload
    assert '"engine_connected":false' in payload
    assert '"engine_state_age_seconds":null' in payload


def test_ok_stays_true_when_the_engine_is_gone():
    """``ok`` is this container's own liveness and must not track the engine.

    It is what the docker HEALTHCHECK and autoheal key off. See the module
    docstring: a non-200 here restart-loops the API through an outage it
    cannot fix.
    """
    h = HealthResponse(
        uptime_seconds=10800.0,
        engine_connected=False,
        engine_state_age_seconds=9000.0,
    )
    assert h.ok is True
