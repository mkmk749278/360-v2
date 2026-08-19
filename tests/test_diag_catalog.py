"""The catalog's safety properties, asserted from the tree rather than trusted.

Owner, 2026-08-19, choosing "diag catalog + a few safe actions": the point is a
surface a guest session can drive without a shell. His security premise was that
the Binance key is IP-whitelisted, futures-only and cannot withdraw — correct
against a **stolen** key used elsewhere, and silent about code running ON the
whitelisted host, where futures permission is not symbol-scoped. So the loss
vector this file guards is not withdrawal, it is a position.

Every assertion below derives from the registry or the source, never from a
hand-kept list of forbidden things — a deny-list is silent by construction on
the next entry somebody adds, which is the defect this repo has paid for under
five different names.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from src import diag_catalog


def _entries():
    return list(diag_catalog._REGISTRY.values())


def test_every_entry_is_read_or_action_and_nothing_else():
    """A third kind would slip past every check below."""
    assert {e.kind for e in _entries()} <= {"read", "action"}


def test_every_action_states_what_it_changes():
    """"Reversible" is a claim somebody has to have written down.

    An action with a blank effect is one nobody has had to justify, which is how
    the list grows past what it was approved for.
    """
    for e in _entries():
        if e.kind == "action":
            assert e.effect.strip(), f"{e.key} is an action with no stated effect"
        else:
            assert not e.effect, f"{e.key} is a read and must change nothing"


def test_no_entry_key_names_a_forbidden_concept():
    for e in _entries():
        for bad in diag_catalog.FORBIDDEN_IN_KEY:
            assert bad not in e.key.lower(), f"{e.key} contains {bad!r}"


# ---------------------------------------------------------------------------
# The structural half: what the entry FUNCTIONS are allowed to reach.
# ---------------------------------------------------------------------------

#: Names that would put an entry on the money path. Matched against every
#: attribute and function name in each entry's own source.
MONEY_PATH_NAMES = {
    "place_order", "create_order", "cancel_order", "new_order", "submit_order",
    "close_position", "open_position", "set_leverage", "set_auto_execution_mode",
    "kill_switch", "engage", "signing", "sign", "api_secret", "secret",
    "api_key", "binance_client", "order_manager", "position_fsm",
    "full_signal_reset", "withdraw", "transfer",
}


def _names_in(fn):
    src = inspect.getsource(fn)
    tree = ast.parse(src.lstrip() if src.startswith(" ") else src)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
    return names


@pytest.mark.parametrize("entry", _entries(), ids=lambda e: e.key)
def test_no_entry_can_reach_the_money_path(entry):
    """Read the entry's own AST — not a docstring promising it behaves.

    This is the assertion the whole design rests on: a leaked read-only code
    must be able to cost disclosure and disruption, and never a position.
    """
    hit = _names_in(entry.fn) & MONEY_PATH_NAMES
    assert not hit, f"{entry.key} reaches the money path via {sorted(hit)}"


@pytest.mark.parametrize("entry", _entries(), ids=lambda e: e.key)
def test_no_entry_shells_out_or_evals(entry):
    """No shell, no eval, no import-by-string of an arbitrary name."""
    forbidden = {"system", "popen", "spawn", "Popen", "run", "call",
                 "check_output", "eval", "exec", "compile", "subprocess", "os"}
    hit = _names_in(entry.fn) & forbidden
    # `__import__` with a LITERAL module name is how the ledger flush reaches
    # its modules; that is fine and is asserted separately below.
    assert not hit, f"{entry.key} may shell out or eval via {sorted(hit)}"


def test_the_only_dynamic_import_uses_literal_module_names():
    """`__import__(f"src.{name}")` is safe only while `name` is not user input.

    It loops a hardcoded tuple. If a future edit made that list an argument, the
    catalog would gain arbitrary-import — the one place this design could turn
    into the thing it exists not to be.
    """
    src = inspect.getsource(diag_catalog._flush_ledgers)
    tree = ast.parse(src.lstrip())

    # The list must be a literal of string constants ASSIGNED INSIDE this
    # function. Bound to a name is fine and is what the code does; what must
    # never happen is it arriving as an argument or being built at runtime.
    literals = {
        t.id: node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for t in node.targets
        if isinstance(t, ast.Name) and isinstance(node.value, (ast.Tuple, ast.List))
    }
    loops = [n for n in ast.walk(tree) if isinstance(n, ast.For)]
    assert loops, "expected the module loop"
    for loop in loops:
        src_seq = loop.iter if isinstance(loop.iter, (ast.Tuple, ast.List)) else (
            literals.get(loop.iter.id) if isinstance(loop.iter, ast.Name) else None
        )
        assert src_seq is not None, (
            "the module list must be a literal in this function, never an "
            "argument — otherwise this becomes arbitrary import-by-name"
        )
        assert all(isinstance(el, ast.Constant) and isinstance(el.value, str)
                   for el in src_seq.elts), "every module name must be a literal string"

    # And the function must take nothing from the caller's args.
    assert "args" not in {
        n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)
    }, "_flush_ledgers must not read ctx.args — the module list is fixed"


def test_reseed_refuses_anything_that_is_not_one_plain_symbol():
    """A path, a wildcard or a shell fragment must be refused, not sanitised."""
    class _Store:
        def seed_symbol(self, s):  # pragma: no cover - must never be reached
            raise AssertionError(f"seed_symbol called with {s!r}")

    class _Engine:
        data_store = _Store()

    for bad in ("", "*", "../etc/passwd", "BTC;rm -rf /", "BTC USDT", None):
        out = diag_catalog.run("action.reseed_symbol", _Engine(), {"symbol": bad})
        assert out["result"].get("refused"), f"{bad!r} was not refused"


def test_an_unknown_key_is_refused_and_names_what_exists():
    out = diag_catalog.run("action.definitely_not_real", object())
    assert out["ok"] is False
    assert "unknown" in out["error"]
    assert out["known"], "a refusal should say what it does know"


def test_a_raising_entry_is_reported_never_propagated():
    """A diagnostic must not take down the loop it is describing."""
    diag_catalog.register(diag_catalog.Entry(
        "read.zz_test_boom", "boom", "read", "raises",
        lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")),
    ))
    try:
        out = diag_catalog.run("read.zz_test_boom", object())
        assert out["ok"] is False and "boom" in out["error"]
    finally:
        diag_catalog._REGISTRY.pop("read.zz_test_boom", None)


def test_a_missing_collaborator_is_unavailable_not_a_crash():
    out = diag_catalog.run("read.scan_executor", object())
    assert out["ok"] is False
    assert out["error"].startswith("unavailable:"), out["error"]


def test_the_catalog_is_data_so_ops_keeps_no_second_list():
    """Ops renders what this returns; a mirror there would drift."""
    rows = diag_catalog.catalog()
    assert {r["key"] for r in rows} == set(diag_catalog._REGISTRY)
    assert [r["kind"] for r in rows][0] == "read", "reads sort first"


def test_the_module_docstring_names_what_is_absent():
    """The prose and the guards must agree, or one of them is decoration."""
    # Whitespace-normalised: a line wrap inside "kill switch" is not the prose
    # failing to say it, and a matcher that cannot tell those apart fails on
    # reformatting rather than on meaning.
    doc = " ".join((diag_catalog.__doc__ or "").split())
    for word in ("order", "kill switch", "per-user settings", "shell"):
        assert word in doc, f"the module docstring does not mention {word!r}"
    # And the file itself must still carry the source-of-truth path for the
    # controls it defers to, so a reader knows where they DID go.
    assert "/control" in Path("src/diag_catalog.py").read_text()


def test_the_action_switch_is_enforced_where_entries_RUN(monkeypatch):
    """Hiding a button is not a control if the request still executes.

    This path is reachable by anything holding the endpoint, so the switch has
    to sit at `run`, not only in what `catalog()` renders.
    """
    monkeypatch.setattr(diag_catalog, "actions_enabled", lambda: False)
    out = diag_catalog.run("action.flush_ledgers", object())
    assert out["ok"] is False
    assert "switched off" in out["error"]

    # Reads are unaffected — they mutate nothing, so the switch does not apply.
    out = diag_catalog.run("read.scan_executor", object())
    assert "switched off" not in out["error"]


def test_a_switched_off_action_still_renders_as_off_not_missing(monkeypatch):
    """A vanished entry reads as a deploy problem; OFF reads as a decision."""
    monkeypatch.setattr(diag_catalog, "actions_enabled", lambda: False)
    rows = {r["key"]: r for r in diag_catalog.catalog()}
    assert "action.flush_ledgers" in rows, "must not disappear"
    assert rows["action.flush_ledgers"]["enabled"] is False
    assert rows["read.loop"]["enabled"] is True


# ---------------------------------------------------------------------------
# The cross-container bridge. The API container cannot see the scanner, so a
# diagnostic assembled there would describe the wrong process — the
# trail-governor INDEX COLD defect. These drive the REAL drain loop.
# ---------------------------------------------------------------------------

class _FakeRedis:
    """Enough of the client for the drain to be exercised, not mocked around."""

    def __init__(self):
        self.list: list[str] = []
        self.kv: dict[str, str] = {}

    async def rpop(self, _key):
        return self.list.pop() if self.list else None

    async def lpush(self, _key, val):
        self.list.append(val)

    async def set(self, key, val, ex=None):
        self.kv[key] = val

    async def get(self, key):
        return self.kv.get(key)


class _Bridge:
    def __init__(self):
        self.client = _FakeRedis()
        self.available = True


async def _drain(engine, redis):
    from src.api.snapshot_writer import SnapshotWriter

    w = SnapshotWriter.__new__(SnapshotWriter)
    w._redis = redis
    w._engine = engine
    await SnapshotWriter._apply_pending_diag_cmds(w)


async def test_a_request_crosses_the_bridge_and_the_answer_comes_back():
    import json

    from src.api import snapshot_store as _store

    redis = _Bridge()
    env = {"request_id": "abc123", "key": "read.scan_executor",
           "args": {}, "ts": __import__("time").time()}
    await redis.client.lpush(_store.KEY_CMD_DIAG, json.dumps(env))

    await _drain(object(), redis)

    raw = await redis.client.get(_store.KEY_DIAG_RESULT_PREFIX + "abc123")
    assert raw is not None, "the engine must publish a result for every request"
    out = json.loads(raw)
    # This engine stub has no scanner, so the honest answer is a NAMED
    # unavailability — not a crash, and not an empty success.
    assert out["ok"] is False and out["error"].startswith("unavailable:")


async def test_a_stale_request_is_refused_rather_than_applied():
    """The caller stopped waiting; running it spends engine time for nobody —
    and for an action it applies a change whose requester is long gone."""
    import json
    import time as _t

    from src.api import snapshot_store as _store

    redis = _Bridge()
    env = {"request_id": "old1", "key": "action.flush_ledgers", "args": {},
           "ts": _t.time() - (_store.DIAG_CMD_STALE_S + 30)}
    await redis.client.lpush(_store.KEY_CMD_DIAG, json.dumps(env))
    await _drain(object(), redis)

    out = json.loads(await redis.client.get(_store.KEY_DIAG_RESULT_PREFIX + "old1"))
    assert out["ok"] is False and "stale" in out["error"]


async def test_the_drain_is_bounded_so_a_flood_cannot_starve_the_writes():
    """This loop's day job is publishing snapshots; diagnostics ride along."""
    import json
    import time as _t

    from src.api import snapshot_store as _store
    from src.api.snapshot_writer import SnapshotWriter

    redis = _Bridge()
    for i in range(SnapshotWriter._DIAG_MAX_PER_CYCLE + 3):
        await redis.client.lpush(_store.KEY_CMD_DIAG, json.dumps(
            {"request_id": f"r{i}", "key": "read.tasks", "args": {}, "ts": _t.time()}))

    await _drain(object(), redis)
    assert len(redis.client.list) == 3, "the tail must wait for the next cycle"


async def test_an_unparseable_envelope_is_dropped_not_fatal():
    from src.api import snapshot_store as _store

    redis = _Bridge()
    await redis.client.lpush(_store.KEY_CMD_DIAG, "{not json")
    await _drain(object(), redis)   # must not raise
