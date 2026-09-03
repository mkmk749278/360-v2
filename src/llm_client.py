"""Provider-neutral LLM transport — one client, one secret, one usage record.

Written 2026-09-02 for `docs/PLAN_AI_TRADE_GOVERNOR.md`. It is deliberately
**not** owned by the governor: `docs/LLM_SIGNAL_CRITIC_BRIDGE.md` describes a
second lane (the pre-dispatch critic) that wants the same transport, the same
secret handling and the same rate table, and two bespoke vendor clients for two
lanes is the drifting-mirror defect this repo has paid for under several names.

The two lanes disagree about the vendor on purpose — the critic bridge names
Anthropic, the governor runs Gemini (owner, 2026-09-02) — which is precisely
why the provider is a parameter and not an import.

What this module refuses to do
------------------------------
* **It does not retry.** A governor verdict is bar-clocked: if the call did not
  land inside the timeout, the bar has moved and the answer would be about a
  state that is gone. A retry would spend the budget to produce a stale verdict,
  which is worse than none. The caller's next bar is the retry.
* **It does not parse free text.** Structured output is requested at the API
  level and the response is `json.loads`-ed or refused. A "flexible" reader that
  accepts several shapes is a guess wearing a feature's clothes
  (`zone_distance_atr`, 0 of 57 rows, two passing tests over a shape nothing
  ever produced).
* **It does not decide anything.** It returns what the vendor said plus what it
  cost, and every failure is a *named* `LLMResult` rather than an exception, so
  a caller cannot accidentally treat "the provider was down" as "the model said
  maintain".

Secret handling
---------------
The key is treated exactly as the Binance secret is (`OWNER_BRIEF` §1.4): env
only, never logged at any level, never written to disk, and scrubbed from every
error string this module produces — including the URL, because Gemini's REST
surface accepts the key as a query parameter and an unscrubbed URL in a
traceback is a leaked credential. `tests/test_llm_client.py` drives every
failure path and asserts the key appears in none of them.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

import aiohttp

from src import fail_open
from src.utils import get_logger

log = get_logger("llm_client")

#: Providers this module knows how to speak to. An unknown provider is a named
#: refusal, never a fallback to whichever one happens to be first — a silent
#: fallback is a mirror nobody knows is a mirror.
PROVIDER_GOOGLE = "google"
PROVIDER_ANTHROPIC = "anthropic"
KNOWN_PROVIDERS = (PROVIDER_GOOGLE, PROVIDER_ANTHROPIC)

#: Env var per provider. Read at CALL time, never snapshotted at import: a
#: module-level read freezes whatever the process booted with, and the whole
#: point of a deploy-injected secret is that it can arrive without a code change.
_KEY_ENV = {
    PROVIDER_GOOGLE: "GEMINI_API_KEY",
    PROVIDER_ANTHROPIC: "ANTHROPIC_API_KEY",
}

# ── Named outcomes ──────────────────────────────────────────────────────────
# Every one of these is a state a panel renders under its own name. "The
# provider was not configured" and "the provider refused" have different next
# moves, and pooling them is how a spent budget reads as a quiet market.

OK = "ok"
NOT_CONFIGURED = "not_configured"      # no API key — the lane is off, not broken
UNKNOWN_PROVIDER = "unknown_provider"  # config names a vendor we cannot speak to
TIMEOUT = "timeout"
HTTP_ERROR = "http_error"              # provider answered with a non-2xx
TRANSPORT_ERROR = "transport_error"    # never reached the provider
BAD_JSON = "bad_json"                  # answered, but not the shape promised
EMPTY = "empty"                        # answered 2xx with no candidate text


@dataclass(frozen=True)
class LLMResult:
    """What the provider said, what it cost, and which world we are in.

    ``ok`` is the ONLY field a caller may branch on to mean "there is a
    verdict". Everything else is telemetry, and `status` is what the ops page
    renders — never a bare boolean, because "we could not ask" and "the answer
    is no" are different facts (`CLAUDE.md`, the money-path readability rule).
    """

    status: str
    data: Optional[Dict[str, Any]] = None
    #: The version the provider says it actually SERVED, not the alias we asked
    #: for. Gemini rotates aliases; stamping the request's model string would
    #: let a rotation redefine every row in the ledger with no diff in our repo.
    served_model: str = ""
    requested_model: str = ""
    latency_ms: int = 0
    usage: Dict[str, int] = field(default_factory=dict)
    detail: str = ""
    #: Why the provider stopped generating, in its own words (Gemini
    #: `finishReason`, Anthropic `stop_reason`). A truncated answer and a
    #: malformed one both arrive as `bad_json`, and only this field separates
    #: them: MAX_TOKENS means the budget was the fault and the fix is a number,
    #: anything else means the model answered badly and the fix is the prompt.
    #: Empty means the provider did not say, never that it stopped cleanly.
    finish_reason: str = ""

    @property
    def ok(self) -> bool:
        return self.status == OK and self.data is not None


def _scrub(text: str, *keys: str) -> str:
    """Remove every secret from a string bound for a log, an error or a panel.

    Belt and braces on purpose: the key can reach a message through the URL
    (Gemini takes it as a query parameter), through a header dump, or through
    a vendor error that echoes the request. One scrub at the boundary covers
    all three, and it is cheaper than auditing every future call site.
    """
    out = str(text)
    for key in keys:
        if key and len(key) >= 8:
            out = out.replace(key, "***")
    return out


def api_key_for(provider: str) -> str:
    return os.getenv(_KEY_ENV.get(provider, ""), "") or ""


def configured(provider: str) -> bool:
    """Is this provider usable right now?

    Exposed so a caller can report `not_configured` as its own counted state
    without making a call to find out — an unconfigured lane must render as a
    decision somebody has not yet taken, not as a failure.
    """
    return provider in KNOWN_PROVIDERS and bool(api_key_for(provider))


class LLMClient:
    """One session, one provider, no retries, every failure named."""

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        timeout_sec: float = 20.0,
    ) -> None:
        self._provider = str(provider or "").lower()
        self._model = str(model or "")
        self._timeout = float(timeout_sec)
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: Dict[str, Any],
        max_output_tokens: int = 1024,
    ) -> LLMResult:
        """One structured-JSON completion. Never raises.

        ``system`` is the stable prefix (rules, action semantics, refusal
        rules) and is passed separately so a provider that supports prefix
        caching can cache it; ``user`` is the volatile snapshot. Ordering is
        the caller's cost lever, not this module's business.
        """
        key = api_key_for(self._provider)
        if self._provider not in KNOWN_PROVIDERS:
            return LLMResult(
                status=UNKNOWN_PROVIDER,
                requested_model=self._model,
                detail=f"provider {self._provider!r} is not one of {KNOWN_PROVIDERS}",
            )
        if not key:
            return LLMResult(
                status=NOT_CONFIGURED,
                requested_model=self._model,
                detail=f"{_KEY_ENV[self._provider]} is unset",
            )

        started = time.monotonic()
        try:
            url, headers, body = self._build_request(key, system, user, schema, max_output_tokens)
            session = await self._get_session()
            async with session.post(
                url, headers=headers, json=body,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            ) as resp:
                text = await resp.text()
                elapsed = int((time.monotonic() - started) * 1000)
                if resp.status < 200 or resp.status >= 300:
                    # The vendor's own words, kept — a counter is not a cause on
                    # a path that talks to a vendor (`trail_governor`'s
                    # `place_failed`, which said "refused" and could not say
                    # what was refused).
                    return LLMResult(
                        status=HTTP_ERROR,
                        requested_model=self._model,
                        latency_ms=elapsed,
                        detail=_scrub(f"HTTP {resp.status}: {text[:400]}", key),
                    )
                return self._parse(text, elapsed, key)
        except Exception as exc:  # noqa: BLE001 — every failure is a named result
            elapsed = int((time.monotonic() - started) * 1000)
            status = TIMEOUT if _is_timeout(exc) else TRANSPORT_ERROR
            # Counted, because a measurement path that swallows an exception
            # silently is the thing `fail_open` exists to stop. The behaviour
            # stays fail-open; the failure does not stay invisible.
            fail_open.record(f"llm_client.{self._provider}", exc)
            return LLMResult(
                status=status,
                requested_model=self._model,
                latency_ms=elapsed,
                detail=_scrub(f"{type(exc).__name__}: {exc}", key),
            )

    # ── Provider shapes ─────────────────────────────────────────────────────

    def _build_request(
        self,
        key: str,
        system: str,
        user: str,
        schema: Dict[str, Any],
        max_output_tokens: int,
    ) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
        if self._provider == PROVIDER_GOOGLE:
            # The key goes in a HEADER, not the query string. Both are accepted;
            # only one of them stays out of proxy logs and out of any URL that
            # reaches a traceback.
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{self._model}:generateContent"
            )
            headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
            body: Dict[str, Any] = {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {
                    # Zero temperature does not make an LLM deterministic; it
                    # makes it as close as the vendor offers. The ledger stamps
                    # the served version because that is the part we can
                    # actually pin.
                    "temperature": 0.0,
                    "maxOutputTokens": int(max_output_tokens),
                    "responseMimeType": "application/json",
                    "responseSchema": schema,
                },
            }
            return url, headers, body

        # Anthropic — present so the critic bridge has a transport when it is
        # built, and so this module cannot be described as provider-neutral
        # while speaking exactly one protocol.
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        body = {
            "model": self._model,
            "max_tokens": int(max_output_tokens),
            "temperature": 0.0,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            # Schema is enforced through a forced single tool rather than a
            # response-format flag: that is the shape this API supports, and a
            # prompt-level "please return JSON" is not a schema.
            "tools": [{
                "name": "emit",
                "description": "Return the structured result.",
                "input_schema": schema,
            }],
            "tool_choice": {"type": "tool", "name": "emit"},
        }
        return url, headers, body

    def _parse(self, text: str, elapsed_ms: int, key: str) -> LLMResult:
        try:
            payload = json.loads(text)
        except Exception as exc:  # noqa: BLE001
            return LLMResult(
                status=BAD_JSON, requested_model=self._model, latency_ms=elapsed_ms,
                detail=_scrub(f"envelope not JSON: {exc}", key),
            )

        # `inner` is a str on one provider and a dict on the other — the two
        # APIs return the structured result in genuinely different shapes,
        # and the branch below handles both rather than pretending otherwise.
        inner: Any
        if self._provider == PROVIDER_GOOGLE:
            served = str(payload.get("modelVersion") or "")
            usage = _google_usage(payload)
            inner = _google_text(payload)
            finish = _google_finish_reason(payload)
        else:
            served = str(payload.get("model") or "")
            usage = _anthropic_usage(payload)
            inner = _anthropic_tool_input(payload)
            finish = str(payload.get("stop_reason") or "")

        if inner is None:
            return LLMResult(
                status=EMPTY, requested_model=self._model, served_model=served,
                latency_ms=elapsed_ms, usage=usage, finish_reason=finish,
                detail="provider returned no content",
            )
        if isinstance(inner, dict):
            data = inner
        else:
            try:
                data = json.loads(inner)
            except Exception as exc:  # noqa: BLE001
                return LLMResult(
                    status=BAD_JSON, requested_model=self._model, served_model=served,
                    latency_ms=elapsed_ms, usage=usage, finish_reason=finish,
                    detail=_scrub(f"content not JSON: {exc}", key),
                )
        if not isinstance(data, dict):
            return LLMResult(
                status=BAD_JSON, requested_model=self._model, served_model=served,
                latency_ms=elapsed_ms, usage=usage, finish_reason=finish,
                detail=f"content was {type(data).__name__}, expected object",
            )
        return LLMResult(
            status=OK, data=data, requested_model=self._model, served_model=served,
            latency_ms=elapsed_ms, usage=usage, finish_reason=finish,
        )


def _is_timeout(exc: BaseException) -> bool:
    import asyncio

    return isinstance(exc, (asyncio.TimeoutError, TimeoutError))


def _google_text(payload: Dict[str, Any]) -> Optional[str]:
    for cand in payload.get("candidates") or []:
        for part in (cand.get("content") or {}).get("parts") or []:
            txt = part.get("text")
            if txt:
                return str(txt)
    return None


def _google_finish_reason(payload: Dict[str, Any]) -> str:
    """Why generation stopped, from the first candidate that says.

    Read even on the paths that already failed: `MAX_TOKENS` beside a
    `bad_json` is the whole diagnosis (the budget truncated the JSON mid-object
    and the fix is a number), and without it a truncation is indistinguishable
    from a model that answered badly.
    """
    for cand in payload.get("candidates") or []:
        reason = cand.get("finishReason")
        if reason:
            return str(reason)
    return ""


def _google_usage(payload: Dict[str, Any]) -> Dict[str, int]:
    meta = payload.get("usageMetadata") or {}
    out = {
        "input_tokens": int(meta.get("promptTokenCount") or 0),
        "output_tokens": int(meta.get("candidatesTokenCount") or 0),
        "cached_input_tokens": int(meta.get("cachedContentTokenCount") or 0),
    }
    # Reasoning tokens are drawn from the SAME output budget as the answer on a
    # thinking-class model, so a generous-looking `maxOutputTokens` can be spent
    # entirely before the first character of JSON is written. Recorded under its
    # own name rather than folded into `output_tokens`: the two have different
    # fixes, and pooling them hides the one that truncates the answer.
    #
    # `cost_usd` deliberately does NOT add this to the billed output count.
    # Whether the vendor already includes thoughts in `candidatesTokenCount`
    # is a fact about their meter that this ledger has not yet observed, and
    # both guesses are wrong in a way somebody would act on: adding it
    # double-counts if they are included, omitting it under-counts if they are
    # not. The first week of rows against the provider's own billing page
    # settles it; until then the call-count bounds are what hold, and this
    # column is what makes the question answerable at all.
    thoughts = meta.get("thoughtsTokenCount")
    if thoughts is not None:
        out["thinking_tokens"] = int(thoughts or 0)
    return out


def _anthropic_tool_input(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for block in payload.get("content") or []:
        if block.get("type") == "tool_use" and isinstance(block.get("input"), dict):
            return block["input"]
    return None


def _anthropic_usage(payload: Dict[str, Any]) -> Dict[str, int]:
    usage = payload.get("usage") or {}
    return {
        "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "cached_input_tokens": int(usage.get("cache_read_input_tokens") or 0),
    }


# ── Cost, from the vendor's own usage numbers ───────────────────────────────
#
# Never estimated. `AI_GOV_MAX_USD_PER_DAY` degrades the governor to MAINTAIN
# when it is hit, so the number it is compared against has to be what was
# actually billed-for, not what we guessed the prompt weighed.
#
# The table is VERSION-STAMPED and the version rides into the ledger. A vendor
# price change must not silently rewrite what historical rows cost — the
# ledger says which table priced each row, so a reader can tell a spend
# increase from a repricing.
RATE_TABLE_VERSION = 1
RATE_TABLE_READ_ON = "2026-09-02"

#: USD per 1M tokens, as (input, output). Read from the vendors' own pricing
#: pages on RATE_TABLE_READ_ON. Prices change: re-read before quoting, and bump
#: RATE_TABLE_VERSION when you do.
#:
#: `gemini-3.7-flash` carries PROMOTIONAL pricing through 2026-12-31 and
#: doubles on 2027-01-01 with no change on our side. That is a dated liability,
#: not a price, which is why the note is here rather than in a PR body nobody
#: re-reads.
RATES: Dict[str, Tuple[float, float]] = {
    "gemini-3.7-flash": (0.75, 3.75),      # → (1.50, 7.50) on 2027-01-01
    "gemini-3.6-flash": (0.75, 3.75),
    "gemini-3.5-flash": (1.50, 9.00),
    "gemini-2.5-flash": (0.30, 2.50),
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.5-pro": (1.25, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-opus-5": (5.00, 25.00),
}

#: Cache reads are billed at a fraction of the input rate on both vendors.
#: One multiplier rather than a second table: the exact figure differs per
#: model, this is the common case, and a cost that is slightly conservative is
#: the safe direction for a cap that converts spend into a degradation.
_CACHE_READ_MULTIPLIER = 0.1


def cost_usd(model: str, usage: Dict[str, int]) -> Optional[float]:
    """What this call cost, or ``None`` if we cannot say.

    ``None`` is a real answer and is kept apart from ``0.0``: an unpriced model
    is a table that needs updating, while zero is a call that genuinely cost
    nothing. Pooling them would let an unknown model spend without moving the
    counter that is supposed to bound it — so the caller treats ``None`` as
    "cannot bound this" and says so, rather than as free.
    """
    rate = RATES.get(str(model or ""))
    if rate is None:
        return None
    in_rate, out_rate = rate
    cached = float(usage.get("cached_input_tokens") or 0)
    billed_in = max(0.0, float(usage.get("input_tokens") or 0) - cached)
    out = float(usage.get("output_tokens") or 0)
    return (
        billed_in * in_rate / 1_000_000.0
        + cached * in_rate * _CACHE_READ_MULTIPLIER / 1_000_000.0
        + out * out_rate / 1_000_000.0
    )
