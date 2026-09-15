"""Telegram must not gate the money path (2026-09-15).

Until this change `SignalRouter._process` resolved a Telegram channel id and
sent the message BEFORE anything else happened to a delivered signal. Both
failure modes returned:

* no ``CHANNEL_TELEGRAM_MAP`` entry -> ``_drop("no_channel_configured")``
* three failed sends            -> ``_drop("delivery_failed")``

Everything downstream sat after that ``return``: ``_write_dispatch_log``,
``dispatch_signal_to_active_users`` (which places the ORDERS), the
``_active_signals`` book that ``trade_monitor`` reads, and the FCM push that
is the app's own notification. So a third-party chat service was a single
point of failure in front of order execution and the primary user surface,
while ``CLAUDE.md`` and ``ARCHITECTURE.md`` both describe Telegram as a
"mirror". Nobody audits the delivery path of a mirror — which is exactly why
it survived.

These pin the inversion. The retry-and-lose machinery is unchanged and still
runs while ``TELEGRAM_SIGNALS_ENABLED`` is on, so every test here states
which world it is in; a test that did not would be measuring the default
rather than the behaviour.
"""
from __future__ import annotations

import ast
import asyncio
from pathlib import Path

import pytest

import src.signal_router as sr
from src.channels.base import Signal
from src.signal_router import SignalRouter
from src.smc import Direction
from src.utils import utcnow

SRC = Path(__file__).resolve().parents[1] / "src"


def _make_signal(symbol="BTCUSDT", channel="360_SCALP"):
    return Signal(
        channel=channel,
        symbol=symbol,
        direction=Direction.LONG,
        entry=32000,
        stop_loss=31900,
        tp1=32130,
        tp2=32200,
        tp3=32400,
        confidence=90,
        signal_id=f"TG-{symbol}",
        timestamp=utcnow(),
    )


async def _run(router, queue, sig):
    await queue.put(sig)
    task = asyncio.create_task(router.start())
    await asyncio.sleep(0.2)
    await router.stop()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


@pytest.fixture
def dispatched(monkeypatch):
    """Records every fan-out to the per-user order path.

    Patched on the module the router imports INSIDE the try block, so this
    observes the real call site rather than a stand-in for it.
    """
    seen: list[str] = []
    from src.execution import signal_dispatch as sd

    async def _fake(**kwargs):
        seen.append(kwargs["signal_id"])

    monkeypatch.setattr(sd, "dispatch_signal_to_active_users", _fake)
    return seen


def _channels(monkeypatch, *, enabled: bool):
    monkeypatch.setattr(sr, "TELEGRAM_SIGNALS_ENABLED", enabled)


def _router(queue, send):
    return SignalRouter(
        queue=queue,
        send_telegram=send,
        format_signal=lambda s: f"Signal: {s.signal_id}",
    )


class TestTheMoneyPathNoLongerNeedsTelegram:
    @pytest.mark.asyncio
    async def test_a_dead_telegram_no_longer_stops_the_orders(
        self, monkeypatch, dispatched
    ):
        """The whole point of the change, stated as one assertion.

        Telegram raises on every attempt. With channels off the signal must
        still reach the order fan-out and the active book.
        """
        _channels(monkeypatch, enabled=False)
        monkeypatch.setitem(sr.CHANNEL_TELEGRAM_MAP, "360_SCALP", "premium")

        async def dead(_chat_id, _text):
            raise RuntimeError("telegram down")

        queue = asyncio.Queue()
        r = _router(queue, dead)
        sig = _make_signal(symbol="ALIVEUSDT")
        await _run(r, queue, sig)

        assert sig.signal_id in r.active_signals
        assert dispatched == [sig.signal_id]

    @pytest.mark.asyncio
    async def test_channels_off_does_not_call_the_vendor_at_all(
        self, monkeypatch, dispatched
    ):
        """Not merely tolerating a failure — not making the call.

        A bypass that still sent and ignored the result would keep the
        latency and the rate limit while claiming to have removed them.
        """
        _channels(monkeypatch, enabled=False)
        monkeypatch.setitem(sr.CHANNEL_TELEGRAM_MAP, "360_SCALP", "premium")
        calls: list[str] = []

        async def counting(chat_id, _text):
            calls.append(chat_id)
            return True

        queue = asyncio.Queue()
        r = _router(queue, counting)
        await _run(r, queue, _make_signal(symbol="QUIETUSDT"))

        assert calls == []

    @pytest.mark.asyncio
    async def test_an_unmapped_channel_no_longer_kills_the_candidate(
        self, monkeypatch, dispatched
    ):
        """The ONE behaviour this change alters for a healthy Telegram.

        A path with no ``CHANNEL_TELEGRAM_MAP`` entry used to be dropped
        outright — silent by construction, for every candidate on that
        channel, forever. Counted separately so the watch window can say
        whether any path was being suppressed by a chat channel's config.
        """
        _channels(monkeypatch, enabled=False)
        monkeypatch.setitem(sr.CHANNEL_TELEGRAM_MAP, "360_SCALP", "")

        async def unused(_chat_id, _text):
            return True

        queue = asyncio.Queue()
        r = _router(queue, unused)
        sig = _make_signal(symbol="UNMAPUSDT")
        await _run(r, queue, sig)

        assert sig.signal_id in r.active_signals
        assert dispatched == [sig.signal_id]
        stats = r.delivery_stats()
        assert stats["drops_by_reason"].get("no_channel_configured") is None
        assert stats["telegram_bypassed"] == 1

class TestTheChannelsOnBehaviourIsUnchanged:
    """Only the dependency moved. With channels on, every old drop stands."""

    @pytest.mark.asyncio
    async def test_a_permanently_failed_send_still_drops_and_never_dispatches(
        self, monkeypatch, dispatched
    ):
        _channels(monkeypatch, enabled=True)
        monkeypatch.setitem(sr.CHANNEL_TELEGRAM_MAP, "360_SCALP", "premium")

        async def instant(_secs):
            pass

        monkeypatch.setattr(sr, "_delivery_sleep", instant)

        async def always_fails(_chat_id, _text):
            return False

        queue = asyncio.Queue()
        r = _router(queue, always_fails)
        sig = _make_signal(symbol="LOSTUSDT")
        await _run(r, queue, sig)

        assert sig.signal_id not in r.active_signals
        assert dispatched == []
        assert r.delivery_stats()["drops_by_reason"].get("delivery_failed") == 1

    @pytest.mark.asyncio
    async def test_an_unmapped_channel_still_drops(self, monkeypatch, dispatched):
        _channels(monkeypatch, enabled=True)
        monkeypatch.setitem(sr.CHANNEL_TELEGRAM_MAP, "360_SCALP", "")

        async def unused(_chat_id, _text):
            return True

        queue = asyncio.Queue()
        r = _router(queue, unused)
        sig = _make_signal(symbol="NOCHANUSDT")
        await _run(r, queue, sig)

        assert sig.signal_id not in r.active_signals
        assert dispatched == []
        assert (
            r.delivery_stats()["drops_by_reason"].get("no_channel_configured") == 1
        )

    @pytest.mark.asyncio
    async def test_a_successful_send_still_dispatches(self, monkeypatch, dispatched):
        _channels(monkeypatch, enabled=True)
        monkeypatch.setitem(sr.CHANNEL_TELEGRAM_MAP, "360_SCALP", "premium")
        sent: list[tuple] = []

        async def ok(chat_id, text):
            sent.append((chat_id, text))
            return True

        queue = asyncio.Queue()
        r = _router(queue, ok)
        sig = _make_signal(symbol="SENTUSDT")
        await _run(r, queue, sig)

        assert sent and sent[0][0] == "premium"
        assert dispatched == [sig.signal_id]
        assert r.delivery_stats()["telegram_bypassed"] == 0


class TestTheCountersAreReadable:
    def test_the_new_keys_carry_no_colon(self):
        """`delivery_stats` partitions `_drop_counters` on ":" and a key
        carrying the delimiter lands in the wrong table — the defect
        `/system/redis` and the ops throttle table have both already paid
        for. These are not drop counters, but the file's own convention is
        what makes the next one safe."""
        queue = asyncio.Queue()

        async def unused(_c, _t):
            return True

        stats = _router(queue, unused).delivery_stats()
        for key in (
            "telegram_channels_enabled",
            "telegram_bypassed",
        ):
            assert key in stats, f"{key} must be published or the watch is blind"
            assert ":" not in key

    def test_the_flag_state_is_published_beside_the_counts(self, monkeypatch):
        """Zero bypasses means one of two opposite things — channels are on,
        or nothing has been routed yet. The flag is what separates them."""
        _channels(monkeypatch, enabled=False)
        queue = asyncio.Queue()

        async def unused(_c, _t):
            return True

        assert _router(queue, unused).delivery_stats()[
            "telegram_channels_enabled"
        ] is False


class TestTheStructureIsPinnedOnTheTree:
    """Pinned on the AST, not on a substring.

    Reverting the change must fail this. Both Telegram drops existed before
    and still exist, so any text search for their names passes against BOTH
    trees — the rot this repo has already recorded. The property that is
    actually new is that neither is reachable without the flag.
    """

    @staticmethod
    def _process_body():
        tree = ast.parse((SRC / "signal_router.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "_process":
                return node
        raise AssertionError("SignalRouter._process not found")

    @staticmethod
    def _drop_reasons_under_the_flag(node):
        """Reasons of every `self._drop(sig, "<reason>")` lexically inside a
        bare `if TELEGRAM_SIGNALS_ENABLED:` body."""
        found: set[str] = set()

        def visit(n, guarded: bool):
            if (
                isinstance(n, ast.Call)
                and isinstance(n.func, ast.Attribute)
                and n.func.attr == "_drop"
                and len(n.args) >= 2
                and isinstance(n.args[1], ast.Constant)
                and guarded
            ):
                found.add(n.args[1].value)
            if (
                isinstance(n, ast.If)
                and isinstance(n.test, ast.Name)
                and n.test.id == "TELEGRAM_SIGNALS_ENABLED"
            ):
                for child in n.body:
                    visit(child, True)
                for child in n.orelse:
                    visit(child, guarded)
                return
            for child in ast.iter_child_nodes(n):
                visit(child, guarded)

        for stmt in node.body:
            visit(stmt, False)
        return found

    def test_both_telegram_drops_are_behind_the_flag(self):
        guarded = self._drop_reasons_under_the_flag(self._process_body())
        assert "no_channel_configured" in guarded, (
            "an evaluator path with no Telegram mapping must not be able to "
            "kill a candidate while broadcast channels are off"
        )
        assert "delivery_failed" in guarded, (
            "a failed chat-service send must not be able to kill a candidate "
            "while broadcast channels are off"
        )

    def test_the_dispatch_fanout_is_not_inside_the_flag(self):
        """The order path must sit OUTSIDE the branch, or the fix is only a
        rename of the dependency."""
        node = self._process_body()
        for child in ast.walk(node):
            if (
                isinstance(child, ast.If)
                and isinstance(child.test, ast.Name)
                and child.test.id == "TELEGRAM_SIGNALS_ENABLED"
            ):
                inside = ast.dump(ast.Module(body=child.body, type_ignores=[]))
                assert "dispatch_signal_to_active_users" not in inside
                assert "_write_dispatch_log" not in inside
                return
        raise AssertionError(
            "no `if TELEGRAM_SIGNALS_ENABLED:` branch in _process — the fix "
            "has been reverted"
        )
