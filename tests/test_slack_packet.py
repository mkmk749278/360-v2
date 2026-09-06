"""D1 — the Slack report lane.

Two properties carry the whole lane's safety, and both are pinned here: the
webhook URL never reaches a reader, and nothing about the report can touch the
money path. The rest is the ordinary shape this repo asks of a new outbound
loop — default OFF, a budget spent on the branch that does nothing, named
refusals with no silent path, and the vendor's own words beside the counts.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pytest

from src import slack_packet as sp


@pytest.fixture(autouse=True)
def _clean():
    sp.reset_state_for_test()
    yield
    sp.reset_state_for_test()


class _Resp:
    def __init__(self, status: int, text: str = "ok"):
        self.status = status
        self._text = text

    async def text(self) -> str:
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class _Session:
    """A fake that behaves like the real collaborator's CONTEXT MANAGER shape.

    Hand-writing a return shape is how `classify_pending` shipped a guard on a
    key its collaborator never produced; here the seam is aiohttp's
    ``async with session.post(...)``, so the fake reproduces that and not a
    plain coroutine.
    """

    def __init__(self, status: int = 200, text: str = "ok", raises: Any = None):
        self.status, self.text_body, self.raises = status, text, raises
        self.calls: List[Dict[str, Any]] = []

    def post(self, url, json=None, timeout=None):  # noqa: A002
        self.calls.append({"url": url, "json": json})
        if self.raises is not None:
            raise self.raises
        return _Resp(self.status, self.text_body)

    async def close(self):
        return None


class _Sig:
    signal_id = "sig-1"
    symbol = "BTCUSDT"
    side = "LONG"
    setup_class = "MOVER_TREND_PULLBACK"
    entry = 100.0
    stop_loss = 98.0
    tp1 = 103.0
    confidence = 0.72


class _Verdict:
    signal_id = "sig-1"
    action = "ADJUST_SL"
    choice = "sl_be"
    confidence = 0.8
    rationale = "structure broke"
    served_model = "gemini-3.7-flash-002"


def _arm(monkeypatch, url="https://hooks.slack.com/services/T1/B2/ZZsecrettoken99"):
    monkeypatch.setattr(sp, "enabled", lambda: True)
    monkeypatch.setattr(sp, "_webhook_url", lambda: url)


# ── The lane ships OFF, and its states are four rather than two ─────────────


def test_the_lane_is_off_by_default():
    """A new outbound loop on the trading box is armed by the owner.

    2026-09-01: a default-ON sweep got this IP rate-limited off Binance and
    took auto-trade down for every paid user for about four hours. The default
    is that incident report.
    """
    from config import SLACK_PACKET_ENABLED

    assert SLACK_PACKET_ENABLED is False
    assert sp.lane_state() == sp.DISABLED


def test_armed_without_a_url_is_its_own_state(monkeypatch):
    """'Armed but not configured' is neither working nor broken.

    Collapsing it into either sends the owner to fix the wrong thing — four
    lane states on the AI-governor page, one lane over.
    """
    monkeypatch.setattr(sp, "enabled", lambda: True)
    monkeypatch.setattr(sp, "_webhook_url", lambda: "")
    assert sp.lane_state() == sp.NOT_CONFIGURED


def test_the_switch_is_a_registered_tunable_not_a_dead_key():
    """`runtime_tunables.get` RAISES on an unregistered key.

    So an unregistered switch reads as its boot default forever while the ops
    panel shows a control — `trail_governor_timeframe`, which went permanently
    inert with its switch reading ON. Pinning registration is what makes the
    key real rather than decorative.
    """
    from src import runtime_tunables as rt

    assert "slack_packet_enabled" in rt.registry()
    assert rt.registry()["slack_packet_enabled"].type == "bool"
    assert rt.get("slack_packet_enabled") is False


# ── The secret must not reach a reader ──────────────────────────────────────


async def test_no_error_path_renders_the_webhook_url(monkeypatch):
    """The URL is a write capability on the channel and this diag is
    guest-readable.

    aiohttp puts the URL it was dialling into the string form of a connection
    error, so trusting `str(exc)` to be clean would publish it to every reader
    of the ops page. Forced through the transport path, which is the one that
    carries it.
    """
    url = "https://hooks.slack.com/services/T1/B2/ZZsecrettoken99"
    _arm(monkeypatch, url)
    sess = _Session(raises=RuntimeError(f"Cannot connect to {url}"))
    sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})
    await sp.drain(session=sess)

    blob = repr(sp.build_diag())
    assert url not in blob
    assert "ZZsecrettoken99" not in blob
    assert "<webhook redacted>" in blob or "<redacted>" in blob


async def test_what_reaches_fail_open_is_redacted_too(monkeypatch):
    """`fail_open.record` WARNs the exception into the container log.

    Asserting only on the diag payload passes over code that writes the webhook
    token to disk on every transport failure — one surface fixed, the field
    still leaking, which is this repo's commonest defect shape. Found by
    reading the captured stderr of the test above rather than by a new idea.

    Pinned on what `record` RECEIVES rather than on captured output: it
    de-duplicates per site, so by the time a second test in this file reaches
    it the log line is suppressed and an output assertion goes green against
    unredacted code. Verified by reverting the fix — the output form passed,
    this one fails.
    """
    url = "https://hooks.slack.com/services/T1/B2/ZZsecrettoken99"
    _arm(monkeypatch, url)
    seen: List[str] = []
    monkeypatch.setattr(
        sp.fail_open, "record", lambda site, exc: seen.append(f"{site}: {exc}")
    )
    sess = _Session(raises=RuntimeError(f"Cannot connect to {url}"))
    sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})
    await sp.drain(session=sess)

    assert seen, "the failure must still be recorded — redaction is not silence"
    joined = " ".join(seen)
    assert "ZZsecrettoken99" not in joined
    assert url not in joined
    assert "RuntimeError" in joined, "the exception TYPE survives; only the secret goes"


def test_the_diag_publishes_whether_a_url_exists_never_the_url(monkeypatch):
    """The only question the page needs, and the only answer safe to give it."""
    _arm(monkeypatch)
    diag = sp.build_diag()
    assert diag["webhook_configured"] is True
    assert "webhook_url" not in diag
    assert "hooks.slack.com" not in repr(diag)


# ── The budget bounds the branch that does NOTHING ──────────────────────────


async def test_the_budget_is_spent_before_the_post_not_after_it(monkeypatch):
    """Spent per packet EXAMINED, at the top.

    The orphan sweep's cap was a CANCEL budget and the common production path
    cancels nothing, so it ran unbounded on the branch that did no work. Here
    that means the cap must bite on a queue full of packets whatever the HTTP
    call does — including when it fails.
    """
    _arm(monkeypatch)
    monkeypatch.setattr("config.SLACK_PACKET_MAX_PER_HOUR", 2)
    monkeypatch.setattr("config.SLACK_PACKET_MAX_PER_DRAIN", 10)
    sess = _Session(status=500, text="channel_not_found")
    for i in range(5):
        sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": f"S{i}"})

    sent = await sp.drain(session=sess)
    assert sent == 2, "the cap bit even though every post failed"
    assert len(sess.calls) == 2
    assert sp.health()["refusals"][sp.BUDGET_EXHAUSTED] == 1


async def test_one_drain_cannot_starve_the_monitor_loop(monkeypatch):
    """Depth is taken once, so a backlog drains over ticks rather than in one."""
    _arm(monkeypatch)
    monkeypatch.setattr("config.SLACK_PACKET_MAX_PER_DRAIN", 3)
    sess = _Session()
    for i in range(10):
        sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": f"S{i}"})
    assert await sp.drain(session=sess) == 3
    assert sp.build_diag()["queue_depth"] == 7


# ── Nothing is silent ───────────────────────────────────────────────────────


async def test_slack_s_own_words_are_kept_beside_the_count(monkeypatch):
    """A counter is not a cause on a path that talks to a vendor.

    `invalid_payload` and `channel_not_found` are one status code and two
    different fixes — `place_failed` on the trail governor, verbatim.
    """
    _arm(monkeypatch)
    sess = _Session(status=404, text="channel_not_found")
    sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})
    await sp.drain(session=sess)

    h = sp.health()
    assert h["outcomes"][sp.HTTP_ERROR] == 1
    last = h["responses"][-1]
    assert last["http_status"] == 404
    assert "channel_not_found" in last["detail"]


async def test_a_transport_failure_records_no_http_status_rather_than_zero(monkeypatch):
    """Slack never answering is a different fault from Slack answering badly.

    Rendering the first as `0` would put a code where none was received — the
    trail governor's "no code means the rejection did not come from the vendor"
    rule, arriving at a report lane.
    """
    _arm(monkeypatch)
    sess = _Session(raises=RuntimeError("boom"))
    sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})
    await sp.drain(session=sess)

    last = sp.health()["responses"][-1]
    assert last["status"] == sp.TRANSPORT_ERROR
    assert last["http_status"] is None


def test_an_enqueue_while_disabled_is_a_named_refusal_not_a_silence():
    assert sp.enqueue({"kind": sp.KIND_SIGNAL}) == sp.DISABLED
    assert sp.health()["refusals"][sp.DISABLED] == 1


async def test_a_disabled_lane_makes_no_network_call(monkeypatch):
    """The switch is enforced where packets are SENT, not only where they are
    built — hiding a control while the request still executes is a control in
    appearance only."""
    sess = _Session()
    sp._queue.append({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})
    assert await sp.drain(session=sess) == 0
    assert sess.calls == []


# ── Content ────────────────────────────────────────────────────────────────


def test_a_verdict_packet_carries_its_blindness():
    """A verdict issued with no order book and no CVD is legitimate;
    presenting it as a fully-informed one is not. Measured 2026-09-06: 200 of
    200 governor rows fully blind."""
    pkt = sp.build_verdict_packet(_Verdict(), unknown_frac=1.0)
    assert pkt["unknown_frac"] == 1.0
    assert "unknown_frac `1.00`" in sp.render(pkt)


def test_an_unmeasured_blindness_renders_a_dash_not_a_zero():
    """`None` is 'the engine did not say', and `0.00` there would read as a
    fully-informed verdict — a blank becoming a finding."""
    pkt = sp.build_verdict_packet(_Verdict(), unknown_frac=None)
    assert "unknown_frac `—`" in sp.render(pkt)


def test_a_signal_packet_carries_no_per_user_field():
    """Quantity, uid and the B17 exit profile are facts about a subscriber and
    have no business in a third-party workspace (§6.4)."""
    pkt = sp.build_signal_packet(_Sig(), trigger_tf="15m")
    for banned in ("uid", "user_id", "qty", "quantity", "notional", "exit_mechanism"):
        assert banned not in pkt


def test_the_verdict_line_says_it_applied_to_nothing():
    """Apply is OFF. A report that read like a live intervention would be the
    reassuring direction of a wrong caption, which is the dangerous one."""
    assert "applied to nothing" in sp.render(sp.build_verdict_packet(_Verdict()))


def test_a_failed_spawn_releases_the_latch(monkeypatch):
    """`spawn_drain` guards against two concurrent drains with a flag.

    If the task is never created — `asyncio.create_task` raises without a
    running loop — a flag left set disables the lane for the life of the
    process while every counter still reads healthy. Ask of any guard: what
    advances the clock, and does a FAILURE advance it?
    """
    _arm(monkeypatch)
    sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})

    def _boom(coro):
        # Closed explicitly: an un-awaited coroutine is a ResourceWarning, and
        # a test that leaves warnings behind trains the reader to skim them.
        coro.close()
        raise RuntimeError("no running event loop")

    assert sp.spawn_drain(task_factory=_boom) is False
    assert sp._drain_running is False, "the latch must not survive a failed spawn"

    started = []
    assert sp.spawn_drain(task_factory=lambda c: started.append(c) or c.close()) is True
    assert started, "a later drain must still be able to start"
