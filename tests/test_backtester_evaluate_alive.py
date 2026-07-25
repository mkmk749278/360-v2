"""The Backtester's evaluate path must be ALIVE, not silently dead.

WHY (2026-07-25). `_backtest_channel` passed `ai_insight=` to `channel.evaluate`.
No channel has ever accepted that argument — `BaseChannel.evaluate` and
`ScalpChannel.evaluate` both take `(symbol, candles, indicators, smc_data,
spread_pct, volume_24h_usd, regime=...)`. So every candle raised TypeError, and
the handler logged at DEBUG and `continue`d. The Backtester therefore emitted
**zero signals for every input** from 2026-07-11 (#713) until this was found.

Nothing caught it for two weeks because every existing assertion is guarded:
`if results[0].total_signals > 0: ...`. A backtester that never emits satisfies
all of them. That is the hole these tests close.

The check is structural rather than "assert N signals" — signal counts depend on
market data and evaluator thresholds, so pinning a number would be brittle. What
must never regress is: the call signature matches, and no candle fails.
"""
from __future__ import annotations

import inspect

import numpy as np
import pytest

from src import fail_open
from src.backtester import Backtester
from src.channels.base import BaseChannel
from src.channels.scalp import ScalpChannel

_SITE = "backtester.channel_evaluate"


def _series(n: int, seed: int = 3) -> dict:
    rng = np.random.default_rng(seed)
    close = np.abs(100.0 + np.cumsum(rng.normal(0, 0.25, n))) + 1.0
    return {
        "open": np.concatenate([[close[0]], close[:-1]]),
        "high": close * 1.004,
        "low": close * 0.996,
        "close": close,
        "volume": rng.lognormal(10, 1.2, n),
    }


class TestEvaluateSignatureCompatibility:
    """The backtester's call must actually bind to the channel's signature."""

    @pytest.mark.parametrize("channel_cls", [ScalpChannel, BaseChannel])
    def test_backtester_kwargs_bind_to_evaluate(self, channel_cls):
        sig = inspect.signature(channel_cls.evaluate)
        # Exactly the kwargs _backtest_channel passes.
        sig.bind(
            self=None,
            symbol="BTCUSDT",
            candles={},
            indicators={},
            smc_data={},
            spread_pct=0.01,
            volume_24h_usd=1e7,
        )

    @pytest.mark.parametrize("channel_cls", [ScalpChannel, BaseChannel])
    def test_ai_insight_is_not_a_channel_argument(self, channel_cls):
        """Guards the specific regression: re-adding `ai_insight=` to the call
        would break every candle again, so it must not silently reappear on
        either side without the other."""
        params = inspect.signature(channel_cls.evaluate).parameters
        assert "ai_insight" not in params, (
            "a channel now accepts ai_insight — if that is intended, the "
            "backtester must pass it again; right now it deliberately does not"
        )


class TestBoundedEvaluationWindow:
    """Evaluators get a bounded tail, exactly like the live scanner.

    Handing them the whole growing prefix was unfaithful *and* quadratic:
    `_evaluate_sr_flip_retest` does `list(highs)` on every candle (scalp.py:3845)
    while only reading `[-50:]`, so the copy grew without bound and dominated
    runtime once the evaluators actually started running.
    """

    def _signals(self, eval_window: int) -> list:
        data = _series(4000)
        results = Backtester(
            lookahead_candles=20, fee_pct=0.07, eval_window=eval_window
        ).run(data, symbol="BTCUSDT", tag_regimes=True)
        return [
            (d.get("candle_index"), d.get("direction"),
             round(float(d.get("entry") or 0.0), 8), d.get("setup_class"))
            for d in results[0].signal_details
        ]

    def test_window_is_deeper_than_the_deepest_lookback(self):
        """50 bars in scalp.py, 100 in the SMC detector — keep real margin."""
        from src.backtester import _EVAL_WINDOW
        assert _EVAL_WINDOW >= 200

    @pytest.mark.parametrize("window", [150, 300, 600])
    def test_bounding_does_not_change_which_signals_fire(self, window):
        """The property that makes the bound safe rather than merely fast."""
        unbounded = self._signals(10**9)
        assert self._signals(window) == unbounded, (
            f"eval_window={window} changed signal output — an evaluator reads "
            "deeper history than the bound allows"
        )


class TestEvaluateRunsWithoutFailing:
    def test_no_candle_fails_evaluation(self):
        """The whole bug in one assertion: if evaluate raises on every candle the
        Backtester reports 0 signals and looks merely 'quiet'. fail_open now
        counts those, so a dead path is loud."""
        fail_open.reset()
        Backtester(lookahead_candles=20, fee_pct=0.07).run(
            _series(1200), symbol="BTCUSDT", tag_regimes=True
        )
        recorded = fail_open.snapshot().get(_SITE)
        assert not recorded, (
            f"channel evaluation failed during the run ({recorded}) — the "
            "measurement path is dead, every candle is being skipped"
        )

    def test_evaluators_actually_execute(self):
        """Beyond 'no exception': the evaluators must have been entered and
        reached a real decision, so a stubbed-out channel can't pass this."""
        channel = ScalpChannel()
        Backtester(channels=[channel], lookahead_candles=20, fee_pct=0.07).run(
            _series(1200), symbol="BTCUSDT", tag_regimes=True
        )
        telemetry = channel._generation_telemetry
        attempts = sum(telemetry["attempts"].values())
        assert attempts > 0, "no evaluator was ever attempted"

        # Real rejection reasons (adx_reject, regime_blocked, ...) prove the
        # evaluators ran their logic. ':exception' means they blew up instead.
        reasons = telemetry["no_signal_reason"]
        exception_reasons = {k: v for k, v in reasons.items()
                             if k.endswith(":exception") and v}
        assert not exception_reasons, (
            f"evaluators raised instead of deciding: {exception_reasons}"
        )
        assert any(v for v in reasons.values()) or any(
            v for v in telemetry["generated"].values()
        ), "evaluators neither generated nor rejected — they never really ran"
