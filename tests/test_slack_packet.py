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


def _real_signal(**over):
    """Build the ENGINE'S OWN `Signal`, never a stub.

    The first cut of this file hand-wrote a class with `side = "LONG"` on it.
    `Signal` has never had a `side` attribute — it is `direction` — so every
    packet in the first live window rendered a BLANK where the direction
    belongs, and the tests were green the whole time because they asserted my
    invented key back at me. That is `zone_distance_atr` and
    `classify_pending` verbatim, committed in the change whose PR body quoted
    the rule. Driving the real dataclass is the fix for the class, not just for
    the field.
    """
    from src.channels.base import Direction, Signal

    kwargs = dict(
        channel="360_SCALP", symbol="BTCUSDT", direction=Direction.LONG,
        entry=100.0, stop_loss=98.0, tp1=103.0, tp2=106.0,
        confidence=72.0, setup_class="MOVER_TREND_PULLBACK",
        original_sl_distance=2.0,
    )
    kwargs.update(over)
    return Signal(**kwargs)


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
    pkt = sp.build_signal_packet(_real_signal(), trigger_tf="15m")
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


def test_the_diag_publishes_the_upstream_switch_too(monkeypatch):
    """Two switches, and the lane is inert if either is off.

    Packets are enqueued from the governor's sweep, so turning
    `ai_gov_measure_enabled` off stops the reports while this lane still reads
    "ready" — armed, configured, and fed by nothing. A page showing one switch
    cannot say which half is missing; that is the promotions page's `lane_off`
    state arriving one repo earlier.
    """
    _arm(monkeypatch)
    from src.execution import ai_governor as aig

    monkeypatch.setattr(aig, "measure_enabled", lambda: False)
    diag = sp.build_diag()
    assert diag["lane"] == "ready", "this lane's own switches are both on"
    assert diag["source_lane_enabled"] is False, "and nothing is feeding it"
    assert diag["source"] == "ai_governor.sweep"


def test_an_unreadable_upstream_switch_is_none_not_false(monkeypatch):
    """"We could not ask" and "the governor is off" are different facts.

    Rendering the first as the second tells the owner his governor is disabled
    when it may be running perfectly — `INDEX COLD` and the kill switch's
    `initialised` boolean, at a report lane.
    """
    _arm(monkeypatch)
    from src.execution import ai_governor as aig

    def _boom():
        raise RuntimeError("cannot read")

    monkeypatch.setattr(aig, "measure_enabled", _boom)
    assert sp.build_diag()["source_lane_enabled"] is None


# ── The pre-arm test post, and the bypass it is confined to ─────────────────
#
# The lane arms after a watched cycle and its real trigger is a delivered
# signal (~16/day), so without this the first evidence that the webhook works
# arrives at the moment the lane is supposed to start being useful. That is the
# opposite of a watched cycle.


async def test_the_test_post_works_while_the_lane_is_disabled(monkeypatch):
    """The one path that does not consult the switch — deliberately.

    A cycle you cannot trigger is a cycle you cannot watch, so the arming rule
    would be unsatisfiable without it.
    """
    monkeypatch.setattr(sp, "enabled", lambda: False)
    monkeypatch.setattr(sp, "_webhook_url", lambda: "https://hooks.slack.com/services/T/B/tok12345")
    assert sp.lane_state() == sp.DISABLED

    sent = []
    out = sp.dispatch_test_post(note="hello", task_factory=lambda c: sent.append(c) or c.close())
    assert out["dispatched"] is True
    assert out["lane_at_dispatch"] == sp.DISABLED, "it reports the state it bypassed"
    assert sent, "a post was actually dispatched"


async def test_the_bypass_does_not_leak_into_the_automatic_path(monkeypatch):
    """The property the switch actually guarantees: the ENGINE posts nothing on
    its own while it is off.

    This is the assertion that makes the bypass admissible. If `enqueue`,
    `drain` or `spawn_drain` ever stopped consulting the switch, a "default OFF"
    outbound loop would be posting anyway — 2026-09-01's incident, arriving
    through the door built for testing.
    """
    monkeypatch.setattr(sp, "enabled", lambda: False)
    monkeypatch.setattr(sp, "_webhook_url", lambda: "https://hooks.slack.com/services/T/B/tok12345")

    assert sp.enqueue({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"}) == sp.DISABLED
    sp._queue.append({"kind": sp.KIND_SIGNAL, "symbol": "BTCUSDT"})
    sess = _Session()
    assert await sp.drain(session=sess) == 0
    assert sess.calls == [], "drain made no network call while disabled"
    assert sp.spawn_drain(task_factory=lambda c: c.close()) is False


def test_the_test_post_refuses_by_name_with_no_url(monkeypatch):
    """"No URL" and "switch off" have different fixes, and telling them apart is
    the whole reason this entry exists."""
    monkeypatch.setattr(sp, "_webhook_url", lambda: "")
    out = sp.dispatch_test_post()
    assert out["dispatched"] is False
    assert out["reason"] == sp.NOT_CONFIGURED
    assert "SLACK_PACKET_WEBHOOK_URL" in out["detail"]


def test_the_test_message_cannot_be_mistaken_for_a_signal(monkeypatch):
    """A message that reads like a tradeable signal, in the channel signals
    arrive on, is a message somebody can act on.

    It shares the transport, the budget and the counters with the real lane and
    shares nothing with the signal FORMAT.
    """
    body = sp.render(sp.build_test_packet("smoke"))
    assert "NOT a signal" in body
    assert "nothing was traded" in body.lower()
    for field in ("entry", "SL", "TP1", "conf"):
        assert f"{field} `" not in body, f"the test message renders a {field} like a real signal"


async def test_the_test_post_spends_the_same_hourly_budget(monkeypatch):
    """Bounded to one message per invocation, and it cannot be hammered — the
    bypass does not come with its own unbounded allowance."""
    monkeypatch.setattr(sp, "enabled", lambda: False)
    monkeypatch.setattr(sp, "_webhook_url", lambda: "https://hooks.slack.com/services/T/B/tok12345")
    monkeypatch.setattr("config.SLACK_PACKET_MAX_PER_HOUR", 2)

    fired = []
    fac = lambda c: fired.append(c) or c.close()  # noqa: E731
    assert sp.dispatch_test_post(task_factory=fac)["dispatched"] is True
    assert sp.dispatch_test_post(task_factory=fac)["dispatched"] is True
    third = sp.dispatch_test_post(task_factory=fac)
    assert third["dispatched"] is False
    assert third["reason"] == sp.BUDGET_EXHAUSTED
    assert len(fired) == 2


def test_the_catalog_entry_is_an_action_with_a_written_effect():
    """An action nobody had to justify is how a list grows past what it was
    approved for — and this one bypasses a safety switch, so its effect line is
    where that is stated in the operator's own words."""
    from src import diag_catalog as dc

    entry = [e for e in dc.catalog() if e["key"] == "action.slack_test_post"]
    assert entry, "the entry is not registered"
    e = entry[0]
    assert e["kind"] == "action"
    assert e["effect"].strip(), "an action with no written effect"
    assert "slack_packet_enabled" in e["effect"], (
        "the effect line must say it bypasses the switch — a bypass a reader "
        "has to discover from the source is not a documented one"
    )
    assert e["needs"] == [], (
        "the ops console renders a text input for `symbol` and nothing else, so "
        "a declared need no surface can satisfy is declared-and-unread"
    )


# ── What the first live window actually rendered ────────────────────────────


def test_the_direction_comes_from_the_real_field_name():
    """`Signal.direction`, not `side`.

    Measured in production 2026-09-06: every packet in the first live window
    posted `*GRTUSDT*  · MOVER_TREND_PULLBACK` — two spaces and no direction —
    because `build_signal_packet` read `sig.side`, which does not exist. It
    shipped green because the test built its own stub carrying that key.
    """
    pkt = sp.build_signal_packet(_real_signal(), trigger_tf="15m")
    assert pkt["direction"] == "LONG"
    assert "side" not in pkt, "the field that never existed must not linger"
    body = sp.render(pkt)
    assert "*BTCUSDT* LONG ·" in body
    assert "*BTCUSDT*  ·" not in body, "the blank-direction render is back"


def test_a_missing_direction_renders_a_question_mark_not_a_blank():
    """A blank is invisible, which is precisely why nobody caught the real
    defect for a whole live window. `?` is a question somebody asks."""
    pkt = sp.build_signal_packet(_real_signal(), trigger_tf="15m")
    pkt["direction"] = ""
    assert "*BTCUSDT* ? ·" in sp.render(pkt)


def test_a_stop_sitting_at_entry_is_named_as_break_even():
    """`trade_monitor` sets `signal.stop_loss = signal.entry` on the BE shift.

    Rendered under a bare "SL" that reads as a zero-risk trade — which is what
    BNBUSDT posted live: `entry 765.36 · SL 765.36`. The resting stop is the
    useful number; that it is no longer the designed one is the missing half.
    """
    pkt = sp.build_signal_packet(_real_signal(stop_loss=100.0), trigger_tf="5m")
    body = sp.render(pkt)
    assert "at break-even" in body
    assert "not the designed stop" in body


def test_an_unmoved_stop_carries_no_note():
    """The note must mean something. A caption on every row is a caption on
    none."""
    body = sp.render(sp.build_signal_packet(_real_signal(), trigger_tf="15m"))
    assert "break-even" not in body
    assert "moved" not in body


def test_a_signal_with_no_designed_distance_claims_nothing():
    """Three states, not two. Unknown renders no note rather than implying the
    stop is original — a missing stamp is not a pass."""
    pkt = sp.build_signal_packet(
        _real_signal(stop_loss=97.0, original_sl_distance=0.0), trigger_tf="15m")
    assert pkt["designed_sl_distance"] is None
    assert "moved" not in sp.render(pkt)
