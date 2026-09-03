"""The provider's own words, kept — and the budget that starved the answer.

The lane's first live window, read off `/signals/ai-governor` on 2026-09-03:
**1,955 sweeps, 22 triggers, 20 model calls, 20 failures, 0 verdicts, 0 ledger
rows** — `bad_json` 9, `timeout` 5, `empty` 3, `http_error` 3. The page could
show those four counts and nothing else, and each of them covers several faults
with different fixes: a truncated answer, a schema-shaped answer with the wrong
types and an error envelope all arrive as `bad_json`.

The vendor had already said which. `LLMResult.detail` names every failure
precisely and never left the engine process, so the panel counted twenty
failures and could not say what any of them was. That is
`trail_governor.place_failed` verbatim — *a counter is not a cause on a path
that talks to a vendor* — arriving one lane over, in code that shipped the day
before.

These tests pin the instrument, not the hypothesis about what it will report.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pytest

from src import ai_governor_ledger, llm_client
from src.execution import ai_governor as gov
from src.execution import ai_governor_menu as menu
from src.execution import ai_governor_snapshot as snap


@dataclass
class FakeSignal:
    signal_id: str = "sig-1"
    symbol: str = "ARBUSDT"
    direction: str = "LONG"
    entry: float = 100.0
    stop_loss: float = 98.0
    tp1: float = 104.0
    setup_class: str = "MOVER_TREND_PULLBACK"
    entry_regime: str = "TRENDING_UP"
    status: str = "ACTIVE"
    max_favorable_excursion_pct: float = 1.2
    max_adverse_excursion_pct: float = -0.4
    original_sl_distance: float = 2.0


def _series(n: int = 60) -> Dict[str, Any]:
    base = 100.0
    opens, highs, lows, closes, times = [], [], [], [], []
    for i in range(n):
        drift = (i % 7) * 0.3
        opens.append(base + drift - 0.1)
        closes.append(base + drift)
        highs.append(base + drift + 0.6)
        lows.append(base + drift - 0.6)
        times.append(1_700_000_000_000 + i * 900_000)
    return {"open": opens, "high": highs, "low": lows,
            "close": closes, "open_time": times}


def _menu_for() -> menu.Menu:
    s = _series()
    return menu.build_menu(
        side="LONG", entry=100.0, current_sl=98.0, current_tp1=104.0,
        highs=s["high"], lows=s["low"], closes=s["close"], last_price=101.0,
    )


def _batch(n: int = 1) -> Dict[str, Any]:
    """Built through the REAL snapshot and menu builders, never hand-shaped."""
    out = {}
    for i in range(n):
        m = _menu_for()
        s = snap.with_menu(
            snap.build_snapshot(
                signal=FakeSignal(signal_id=f"sig-{i}"), trigger_tf="15m",
                as_of_bar_ms=1, bars_since_entry=2, last_price=101.0, menu=m,
            ),
            m,
        )
        out[f"sig-{i}"] = (s, m)
    return out


class _Client:
    """Returns a canned RESULT, but records the REQUEST it was asked to make.

    The result is a real `llm_client.LLMResult`; what is faked is the network,
    which is the only thing a test may fake here.
    """

    provider = llm_client.PROVIDER_GOOGLE

    def __init__(self, results):
        self._results = list(results)
        self.asked_max_output_tokens: list[int] = []

    async def complete_json(self, **kw) -> llm_client.LLMResult:
        self.asked_max_output_tokens.append(int(kw["max_output_tokens"]))
        return self._results.pop(0) if self._results else self._results

    async def close(self) -> None:
        return None


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-a-real-secret")
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(ai_governor_ledger.GovernorLedger(path=""))
    yield
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(None)


def _failure(**kw) -> llm_client.LLMResult:
    base = dict(
        status=llm_client.BAD_JSON, requested_model="gemini-3.7-flash",
        served_model="gemini-3.7-flash-002", latency_ms=1343,
        usage={"input_tokens": 1200, "output_tokens": 150},
        detail="content not JSON: Unterminated string starting at: line 1 col 2",
    )
    base.update(kw)
    return llm_client.LLMResult(**base)


# ── The ring ────────────────────────────────────────────────────────────────

async def test_a_failed_call_keeps_the_providers_own_words():
    cli = _Client([_failure(finish_reason="MAX_TOKENS")])
    assert await gov.evaluate(_batch(), now=1000.0, client=cli) == 0

    h = gov.health()
    assert h["provider_status"][llm_client.BAD_JSON] == 1
    rows = h["provider_failures"]
    assert len(rows) == 1
    row = rows[0]
    assert row["status"] == llm_client.BAD_JSON
    assert "Unterminated string" in row["detail"]
    # The whole diagnosis: the answer was truncated, so the fix is a number and
    # not the prompt. Without this field the two are indistinguishable.
    assert row["finish_reason"] == "MAX_TOKENS"
    assert row["output_tokens"] == 150
    assert row["max_output_tokens"] == cli.asked_max_output_tokens[0]
    assert row["served_model"] == "gemini-3.7-flash-002"


async def test_the_unbounded_count_stays_beside_the_bounded_ring():
    """The newest few must never be readable as the whole population — the
    sampled-ring rule this repo already applies to the suppression audit."""
    for _ in range(25):
        await gov.evaluate(_batch(), now=1000.0, client=_Client([_failure()]))

    h = gov.health()
    assert h["provider_status"][llm_client.BAD_JSON] == 25
    assert len(h["provider_failures"]) == gov._PROVIDER_FAILURE_RING


async def test_the_ring_keeps_the_NEWEST_failures():
    for i in range(25):
        await gov.evaluate(
            _batch(), now=1000.0 + i,
            client=_Client([_failure(detail=f"failure-{i}")]),
        )
    rows = gov.health()["provider_failures"]
    assert rows[-1]["detail"] == "failure-24"
    assert rows[0]["detail"] == "failure-5"


async def test_a_successful_call_records_no_failure_row():
    ok = llm_client.LLMResult(
        status=llm_client.OK, data={"verdicts": []},
        requested_model="gemini-3.7-flash", served_model="gemini-3.7-flash-002",
        latency_ms=900, usage={"input_tokens": 1200, "output_tokens": 40},
    )
    await gov.evaluate(_batch(), now=1000.0, client=_Client([ok]))
    assert gov.health()["provider_failures"] == []


class _Resp:
    """The one shape a vendor error genuinely takes: a non-2xx whose BODY
    echoes the request, key included. That is the path `_scrub` exists for."""

    def __init__(self, status: int, body: str):
        self.status = status
        self._body = body

    async def text(self) -> str:
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self, resp):
        self._resp = resp

    def post(self, *a, **kw):
        return self._resp


async def test_the_api_key_never_reaches_the_ring(monkeypatch):
    """Driven through the REAL transport error path, where the scrub lives.

    A test that hand-builds an already-scrubbed detail asserts its own
    assumption back at itself one layer short of the code under test.
    """
    secret = "AIzaSyD-not-a-real-key-0123456789"
    monkeypatch.setenv("GEMINI_API_KEY", secret)
    cli = llm_client.LLMClient(provider=llm_client.PROVIDER_GOOGLE,
                               model="gemini-3.7-flash")

    async def _session():
        return _Session(_Resp(400, f'{{"error":{{"message":"API key {secret} '
                                   f'not valid","status":"INVALID_ARGUMENT"}}}}'))

    monkeypatch.setattr(cli, "_get_session", _session)
    result = await cli.complete_json(
        system="s", user="u", schema={"type": "object"}, max_output_tokens=64,
    )
    assert result.status == llm_client.HTTP_ERROR
    assert secret not in result.detail
    assert "***" in result.detail
    # …and the vendor's own words survive the scrub, or the ring is a counter
    # again.
    assert "INVALID_ARGUMENT" in result.detail

    await gov.evaluate(_batch(), now=1000.0, client=_Client([result]))
    row = gov.health()["provider_failures"][0]
    assert secret not in row["detail"]
    assert "INVALID_ARGUMENT" in row["detail"]


# ── The budget ──────────────────────────────────────────────────────────────

async def test_the_output_budget_carries_a_floor_above_the_per_signal_share():
    """150 tokens per signal was ample for the ANSWER and is the whole budget a
    thinking-class model has to reason in before writing it."""
    from config import AI_GOV_OUTPUT_TOKEN_FLOOR

    cli = _Client([_failure()])
    await gov.evaluate(_batch(1), now=1000.0, client=cli)
    assert cli.asked_max_output_tokens == [AI_GOV_OUTPUT_TOKEN_FLOOR + 150]

    cli = _Client([_failure()])
    await gov.evaluate(_batch(3), now=1000.0, client=cli)
    assert cli.asked_max_output_tokens == [AI_GOV_OUTPUT_TOKEN_FLOOR + 450]


def test_the_floor_is_big_enough_to_be_worth_calling_a_floor():
    """A floor below the per-signal share would be decoration. This fails if a
    later edit quietly reduces it to one."""
    from config import AI_GOV_OUTPUT_TOKEN_FLOOR

    assert AI_GOV_OUTPUT_TOKEN_FLOOR >= 512


# ── What the vendor actually returns ────────────────────────────────────────

def test_a_truncated_gemini_answer_reports_MAX_TOKENS_not_just_bad_json():
    """The documented Gemini envelope: `finishReason` and `thoughtsTokenCount`
    sit beside the content, and both survive into the result."""
    cli = llm_client.LLMClient(provider=llm_client.PROVIDER_GOOGLE,
                              model="gemini-3.7-flash")
    envelope = (
        '{"candidates":[{"finishReason":"MAX_TOKENS","content":{"parts":'
        '[{"text":"{\\"verdicts\\":[{\\"signal_id\\":\\"sig-1\\""}]}}],'
        '"modelVersion":"gemini-3.7-flash-002",'
        '"usageMetadata":{"promptTokenCount":1200,"candidatesTokenCount":150,'
        '"thoughtsTokenCount":148}}'
    )
    result = cli._parse(envelope, 1343, "test-key-not-a-real-secret")
    assert result.status == llm_client.BAD_JSON
    assert result.finish_reason == "MAX_TOKENS"
    # Kept under its own name: reasoning and answer tokens have different
    # fixes, and pooling them hides the one that truncated the answer.
    assert result.usage["thinking_tokens"] == 148
    assert result.served_model == "gemini-3.7-flash-002"


def test_a_gemini_answer_with_no_content_still_says_why_it_stopped():
    """`empty` with MAX_TOKENS is the budget; `empty` with STOP is the model."""
    cli = llm_client.LLMClient(provider=llm_client.PROVIDER_GOOGLE,
                              model="gemini-3.7-flash")
    envelope = (
        '{"candidates":[{"finishReason":"MAX_TOKENS","content":{"parts":[]}}],'
        '"modelVersion":"gemini-3.7-flash-002",'
        '"usageMetadata":{"promptTokenCount":1200,"candidatesTokenCount":150,'
        '"thoughtsTokenCount":150}}'
    )
    result = cli._parse(envelope, 1200, "test-key-not-a-real-secret")
    assert result.status == llm_client.EMPTY
    assert result.finish_reason == "MAX_TOKENS"


def test_an_absent_finish_reason_is_empty_never_a_guess():
    """The provider not saying and the provider saying STOP are different
    facts, and only one of them means it finished cleanly."""
    cli = llm_client.LLMClient(provider=llm_client.PROVIDER_GOOGLE,
                              model="gemini-3.7-flash")
    result = cli._parse('{"candidates":[]}', 10, "test-key-not-a-real-secret")
    assert result.status == llm_client.EMPTY
    assert result.finish_reason == ""


def test_the_ring_is_published_where_the_page_reads_it():
    """A field one repo writes and no repo reads is the defect this whole lane
    keeps paying for — so the contract is pinned on the producing side."""
    diag = gov.build_diag()
    assert "provider_failures" in diag["health"]
