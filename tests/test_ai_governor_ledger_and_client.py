"""Round trip through the REAL serializer, and the secret that must never render.

`open_time` was added to the candle store, written by one path and dropped by
`_save_snapshot_sync`, so bar timestamps did not survive a restart and every
open dark row read `no candles` on pairs whose candles were plainly arriving.
Every link was individually right. **A round trip is a contract: pin it with a
test that drives the real serializer.**
"""
from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict

import pytest

from src import ai_governor_ledger as led
from src import llm_client
from src.execution import ai_governor as gov


def _row(i: int) -> Dict[str, Any]:
    return {"signal_id": f"sig-{i}", "action": gov.MAINTAIN, "rationale": "x"}


def test_flush_then_load_round_trips_through_the_real_file():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ai_governor_v1.json")
        a = led.GovernorLedger(path=path)
        for i in range(5):
            a.add(_row(i))
        assert a.flush(force=True) is True

        b = led.GovernorLedger(path=path)
        b.load()
        assert b.count() == 5
        assert [r["signal_id"] for r in b.rows()] == [f"sig-{i}" for i in range(5)]


def test_a_deploy_resumes_the_window_instead_of_overwriting_it():
    """Flush without load is worse than neither: it DELETES the window on every
    deploy while the page reports a healthy ledger. Four windows were destroyed
    across two lanes before anyone noticed the row count going down."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "l.json")
        first = led.GovernorLedger(path=path)
        for i in range(3):
            first.add(_row(i))
        first.flush(force=True)

        # A restart: fresh object, load, add one, flush.
        second = led.GovernorLedger(path=path)
        second.load()
        second.add(_row(99))
        second.flush(force=True)

        third = led.GovernorLedger(path=path)
        third.load()
        assert third.count() == 4, "the pre-restart window was overwritten"


def test_get_ledger_calls_load(monkeypatch):
    """Defining a method is not calling it — pin the call site."""
    called = {"n": 0}
    real_load = led.GovernorLedger.load

    def _spy(self):
        called["n"] += 1
        return real_load(self)

    monkeypatch.setattr(led.GovernorLedger, "load", _spy)
    led.reset_ledger(None)
    led.get_ledger()
    led.reset_ledger(None)
    assert called["n"] == 1


def test_a_newer_schema_is_refused_rather_than_guessed():
    """Reading forward means guessing what a field the writer added will mean."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "l.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"schema": led.SCHEMA + 1, "rows": [_row(1)]}, fh)
        lg = led.GovernorLedger(path=path)
        lg.load()
        assert lg.count() == 0


def test_the_additive_set_is_declared_out_loud():
    """`accepts()` takes it as a REQUIRED argument so a new ledger cannot
    inherit the old `!=` behaviour by forgetting."""
    assert isinstance(led.ADDITIVE_FROM_SCHEMAS, frozenset)


def test_an_in_memory_ledger_never_touches_the_disk(tmp_path, monkeypatch):
    """`path=""` means in memory — what every test constructs with. Both
    structural ledgers ran their atomic write anyway, creating stray .tmp files
    in the repo root under pytest and raising into `fail_open` on every test
    run for two months, filling the counter whose whole purpose is making a
    real failure stand out."""
    monkeypatch.chdir(tmp_path)
    lg = led.GovernorLedger(path="")
    lg.add(_row(1))
    assert lg.flush(force=True) is False
    assert list(tmp_path.iterdir()) == []


def test_the_eviction_count_is_persisted_with_the_data():
    """A rate computed on a bounded ring is a sample, and a reader in another
    process cannot see the cap."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "l.json")
        lg = led.GovernorLedger(path=path, max_rows=3)
        for i in range(6):
            lg.add(_row(i))
        lg.flush(force=True)
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
        assert payload["evicted"] == 3
        assert payload["max_rows"] == 3


def test_there_is_no_blended_cross_arm_figure():
    """Three of the four arms are decidable from the closed-signal record and
    one is not. A single number over all four would move with the SL arm's
    refusal rate rather than with the mechanism."""
    diag = gov.build_diag()
    flat = json.dumps(diag)
    for banned in ("overall_edge", "combined_delta", "blended", "avg_r"):
        assert banned not in flat


# ── The secret ──────────────────────────────────────────────────────────────

SECRET = "AIzaSyTOTALLY-SECRET-KEY-VALUE-0123456789"


@pytest.mark.parametrize("provider,env", [("google", "GEMINI_API_KEY"),
                                          ("anthropic", "ANTHROPIC_API_KEY")])
async def test_the_key_never_appears_in_a_transport_error(monkeypatch, provider, env):
    """Treated exactly as the Binance secret is: never logged, never written,
    never surfaced in an error trace."""
    monkeypatch.setenv(env, SECRET)
    cli = llm_client.LLMClient(provider=provider, model="m", timeout_sec=0.001)

    class _Boom:
        def post(self, *a, **kw):
            raise RuntimeError(f"connection to {a[0] if a else '?'} failed with key={SECRET}")

        async def close(self):
            return None

        @property
        def closed(self):
            return False

    monkeypatch.setattr(cli, "_get_session", lambda: _done(_Boom()))
    res = await (cli.complete_json(system="s", user="u", schema={}))
    assert res.status in (llm_client.TRANSPORT_ERROR, llm_client.TIMEOUT)
    assert SECRET not in res.detail
    assert SECRET not in json.dumps(res.__dict__, default=str)


async def _done(value):
    return value


async def test_an_unset_key_is_a_named_state_not_a_failure(monkeypatch):
    """An unconfigured lane is a decision nobody has taken yet. Rendering it as
    a failure sends the owner to debug something that is not broken."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    cli = llm_client.LLMClient(provider="google", model="gemini-3.7-flash")
    res = await (cli.complete_json(system="s", user="u", schema={}))
    assert res.status == llm_client.NOT_CONFIGURED
    assert not res.ok


async def test_an_unknown_provider_is_refused_never_defaulted(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", SECRET)
    cli = llm_client.LLMClient(provider="acme", model="m")
    res = await (cli.complete_json(system="s", user="u", schema={}))
    assert res.status == llm_client.UNKNOWN_PROVIDER


def test_cost_is_none_for_an_unpriced_model_never_zero():
    """An unpriced model is a table that needs updating; reading it as free
    would let a cap be silently escaped by configuring a model nobody priced."""
    assert llm_client.cost_usd("model-nobody-priced", {"input_tokens": 1_000_000}) is None
    priced = llm_client.cost_usd("gemini-3.7-flash",
                                 {"input_tokens": 1_000_000, "output_tokens": 0})
    assert priced == pytest.approx(0.75)


def test_the_rate_table_is_version_stamped():
    """A vendor price change must not silently rewrite what historical rows
    cost — the ledger says which table priced each row."""
    assert isinstance(llm_client.RATE_TABLE_VERSION, int)
    assert llm_client.RATE_TABLE_READ_ON
