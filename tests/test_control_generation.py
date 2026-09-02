"""The invalidation channel that replaced the 5-second TTLs (2026-09-02).

Every test here is about a property whose failure is SILENT in production: a
bump that never lands, a poll that never fires, a listener nobody registered.
The defensive TTL converges anyway, so nothing breaks visibly — it just means
the kill switch is minutes late and the reads are back on the meter.
"""
from __future__ import annotations

import pytest

from src import control_generation as gen


class _FakeRedis:
    """Enough of redis-py for INCR/MGET, and it can be told to fail."""

    def __init__(self, fail: bool = False) -> None:
        self.store: dict = {}
        self.fail = fail
        self.incr_calls = 0
        self.mget_calls = 0

    def incr(self, key):
        self.incr_calls += 1
        if self.fail:
            raise RuntimeError("redis down")
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]

    def mget(self, keys):
        self.mget_calls += 1
        if self.fail:
            raise RuntimeError("redis down")
        return [self.store.get(k) for k in keys]


@pytest.fixture(autouse=True)
def _clean():
    gen.reset_for_test()
    yield
    gen.reset_for_test()


def test_a_bump_in_one_process_invalidates_the_listener_in_another():
    """The whole point: an ops write in the api container drops the engine's
    cache without either of them re-reading Firestore to find out."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    fired = []
    gen.register(gen.DOC_KILL_SWITCH, lambda: fired.append(1))

    gen.poll()                      # first sight — establishes the baseline
    assert fired == [], "boot must not invalidate: every cache is already cold"

    gen.bump(gen.DOC_KILL_SWITCH)   # the flip
    moved = gen.poll()
    assert moved == [gen.DOC_KILL_SWITCH]
    assert fired == [1]

    gen.poll()                      # nothing changed since
    assert fired == [1], "a quiet poll must not spend a Firestore read"


def test_one_poll_reads_every_document_in_one_round_trip():
    """It runs on the monitor's 5s loop, so it must not scale with documents."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    gen.poll()
    assert r.mget_calls == 1


def test_a_generation_that_went_backwards_invalidates():
    """A flushed Redis or a rebuilt container resets the counter.  "I cannot
    tell whether the document moved" is answered with one Firestore read, never
    with a stale cache on a safety flag."""
    r = _FakeRedis()
    gen.set_client_for_test(r)
    fired = []
    gen.register(gen.DOC_KILL_SWITCH, lambda: fired.append(1))
    gen.bump(gen.DOC_KILL_SWITCH)
    gen.bump(gen.DOC_KILL_SWITCH)
    gen.poll()
    r.store.clear()
    r.store[gen.KEY_PREFIX + gen.DOC_KILL_SWITCH] = 1   # backwards
    assert gen.poll() == [gen.DOC_KILL_SWITCH]
    assert fired == [1]


def test_redis_failure_never_raises_and_is_counted():
    """A control write must land in Firestore whatever Redis is doing — but a
    channel that is quietly dead means every reader is on the TTL floor, which
    is exactly the state that must not be silent."""
    r = _FakeRedis(fail=True)
    gen.set_client_for_test(r)
    gen.bump(gen.DOC_KILL_SWITCH)      # must not raise
    gen.poll()                         # must not raise
    st = gen.stats()
    assert st["bump_failures"] == 1
    assert st["poll_failures"] == 1
    assert st["bumps"] == 0


def test_no_redis_is_a_no_op_not_a_crash():
    """Redis is optional in this engine; the defensive TTL covers it."""
    gen.set_client_for_test(None)
    gen.register(gen.DOC_KILL_SWITCH, lambda: pytest.fail("must not fire"))
    gen.bump(gen.DOC_KILL_SWITCH)
    assert gen.poll() == []


def test_an_unknown_document_is_refused_at_both_ends():
    """A typo'd key would bump something nothing polls — a listener that can
    never fire, indistinguishable from a working one."""
    gen.set_client_for_test(_FakeRedis())
    with pytest.raises(ValueError):
        gen.bump("kill_swtich")
    with pytest.raises(ValueError):
        gen.register("kill_swtich", lambda: None)


def test_a_listener_that_raises_does_not_stop_the_others():
    r = _FakeRedis()
    gen.set_client_for_test(r)
    fired = []

    def _boom():
        raise RuntimeError("bad listener")

    gen.register(gen.DOC_KILL_SWITCH, _boom)
    gen.register(gen.DOC_KILL_SWITCH, lambda: fired.append(1))
    gen.poll()
    gen.bump(gen.DOC_KILL_SWITCH)
    gen.poll()
    assert fired == [1]
