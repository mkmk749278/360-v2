"""The emergency stop must be throwable even when the api container is blind.

``POST /api/kill-switch`` returned 503 whenever the serving process had no
Firestore client, and in isolated mode that process initialises under a
stricter precondition than the engine's.  So on 2026-09-02 the owner could not
halt auto-trade from the control plane at all — against B18's five-second
requirement — while the engine traded normally with a working client, and the
ops page said so in the grey it uses for footnotes.
"""
from __future__ import annotations

import ast
import inspect
import json
import time


from src.api import snapshot_store as store
from src.execution import safety_switch_bridge as bridge


class _Redis:
    def __init__(self):
        self.available = True
        self.client = self
        self.sets: dict = {}

    async def set(self, key, value, ex=None):
        self.sets[key] = value


class _Client:
    def __init__(self):
        self.calls: list = []

    def engage_global(self, reason=""):
        self.calls.append(("engage", reason))

    def disengage_global(self):
        self.calls.append(("disengage", None))

    def enable_global_auto_trade(self):
        self.calls.append(("enable", None))

    def disable_global_auto_trade(self):
        self.calls.append(("disable", None))

    def set_signal_expiry_enabled(self, v):
        self.calls.append(("expiry", v))

    def set_billing_enabled(self, v):
        self.calls.append(("billing", v))


def _consumer(client=None, redis=None):
    c = client or _Client()
    r = redis or _Redis()
    return bridge.SafetySwitchConsumer(r, get_client=lambda: c), c, r


def _env(**kw):
    base = {"request_id": "r1", "switch": "kill_switch",
            "value": True, "reason": "ops", "ts": time.time()}
    base.update(kw)
    return json.dumps(base)


async def test_the_engine_throws_the_switch_the_api_container_could_not():
    con, client, redis = _consumer()
    await con._process(_env())
    assert client.calls == [("engage", "ops")]
    out = json.loads(redis.sets[store.KEY_SWITCH_RESULT_PREFIX + "r1"])
    assert out["ok"] is True
    assert out["applied_by"] == "engine"


async def test_every_switch_name_reaches_its_method():
    """A name accepted by the queue and unhandled by the dispatch would be a
    silent no-op on a safety control — reported as applied, doing nothing."""
    for switch, value, expected in (
        ("kill_switch", True, ("engage", "ops")),
        ("kill_switch", False, ("disengage", None)),
        ("auto_trade_global", True, ("enable", None)),
        ("auto_trade_global", False, ("disable", None)),
        ("signal_expiry", True, ("expiry", True)),
        ("play_billing", False, ("billing", False)),
    ):
        con, client, redis = _consumer()
        await con._process(_env(switch=switch, value=value))
        assert client.calls == [expected], switch
        assert json.loads(
            redis.sets[store.KEY_SWITCH_RESULT_PREFIX + "r1"]
        )["ok"] is True


def test_the_accepted_names_and_the_dispatch_table_cannot_drift():
    """Derived from the tree, not written in a list — a name in one and not the
    other is exactly the silent no-op above."""
    src = inspect.getsource(bridge._apply)
    handled = {
        n.comparators[0].value
        for n in ast.walk(ast.parse(src))
        if isinstance(n, ast.Compare)
        and isinstance(n.comparators[0], ast.Constant)
        and isinstance(n.comparators[0].value, str)
    }
    assert set(bridge._SWITCHES) == handled


async def test_an_unknown_switch_is_refused_and_reaches_no_method():
    con, client, redis = _consumer()
    await con._process(_env(switch="place_order"))
    assert client.calls == []
    out = json.loads(redis.sets[store.KEY_SWITCH_RESULT_PREFIX + "r1"])
    assert out["ok"] is False
    assert "unknown switch" in out["error"]


async def test_a_non_boolean_value_is_refused():
    """``value: "false"`` is truthy in Python and would ENGAGE a kill switch
    somebody was trying to release."""
    con, client, redis = _consumer()
    await con._process(_env(value="false"))
    assert client.calls == []
    assert json.loads(
        redis.sets[store.KEY_SWITCH_RESULT_PREFIX + "r1"]
    )["ok"] is False


async def test_a_stale_request_is_refused_rather_than_applied_late():
    """An operator who gave up waiting on an emergency stop has taken another
    action; applying their flip minutes later is worse than refusing it."""
    con, client, redis = _consumer()
    await con._process(
        _env(ts=time.time() - store.SWITCH_CMD_STALE_S - 1)
    )
    assert client.calls == []
    out = json.loads(redis.sets[store.KEY_SWITCH_RESULT_PREFIX + "r1"])
    assert out["ok"] is False
    assert "old" in out["error"]


def test_the_stale_window_is_tighter_than_the_diagnostic_channel_s():
    assert store.SWITCH_CMD_STALE_S < store.DIAG_CMD_STALE_S


async def test_a_failing_client_reports_rather_than_claiming_success():
    class _Bad(_Client):
        def engage_global(self, reason=""):
            raise RuntimeError("429 RESOURCE_EXHAUSTED")

    con, _c, redis = _consumer(client=_Bad())
    await con._process(_env())
    out = json.loads(redis.sets[store.KEY_SWITCH_RESULT_PREFIX + "r1"])
    assert out["ok"] is False
    assert "RESOURCE_EXHAUSTED" in out["error"]


async def test_every_consumed_envelope_with_an_id_gets_an_answer():
    """The api polls for a result; without one an emergency stop hangs and the
    operator is told nothing."""
    for env in (_env(switch="nope"), _env(value=None), _env()):
        con, _c, redis = _consumer()
        await con._process(env)
        assert store.KEY_SWITCH_RESULT_PREFIX + "r1" in redis.sets


async def test_malformed_input_is_dropped_without_raising():
    con, client, redis = _consumer()
    await con._process("not json")
    await con._process(json.dumps({"switch": "kill_switch", "value": True}))
    assert client.calls == []
    assert redis.sets == {}


def test_the_consumer_is_not_behind_a_feature_flag():
    """A flag on the emergency stop is a switch that can turn the switch off.

    Asserted by walking bootstrap's tree for the enclosing conditions of the
    construction, not by reading nearby text: the take consumer beside it IS
    flag-gated, so a substring check would be satisfied by that one's flag and
    go green over a kill switch somebody had quietly made optional.
    """
    import src.bootstrap as bootstrap

    tree = ast.parse(inspect.getsource(bootstrap))
    parents: dict = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    target = None
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "SafetySwitchConsumer"
        ):
            target = node
            break
    assert target is not None, "bootstrap must construct the consumer"

    # Every condition it sits under, all the way to module level.
    guards: list = []
    cur = target
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, ast.If):
            guards.extend(
                n.id for n in ast.walk(cur.test) if isinstance(n, ast.Name)
            )
    # ``API_ENABLED`` is allowed and is not a feature flag on this control:
    # with no HTTP surface there is no control plane to serve the flip, so the
    # consumer would have nothing to consume.  Anything else gating it IS a
    # switch that can turn the emergency stop off.
    guards = [g for g in guards if g != "API_ENABLED"]
    flagged = [g for g in guards if "ENABLED" in g or "DISABLED" in g]
    assert not flagged, (
        f"the safety-switch consumer must not be feature-gated; found {flagged}"
    )
    assert 'name="safety_switch_consumer"' in inspect.getsource(bootstrap), (
        "and the task must actually be started, not merely constructed"
    )
