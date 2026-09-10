"""The output budget, and what else draws on it.

PROMPT_SCHEMA 3 shipped a payload roughly four times richer and did not touch
the budget the model reasons inside. First live call after that deploy:
`bad_json`, `finish_reason=MAX_TOKENS`, output 339 / thinking 1570 against a
ceiling of 1924. Zero verdicts.

This file pins the two properties that failure had: the ceiling must clear the
thinking that has actually been observed with real headroom, and it must scale
with batch size rather than being a constant the next payload change outgrows
silently.
"""
from __future__ import annotations

import ast
import inspect

from src.execution import ai_governor as gov


#: The live measurement that sized this, kept as a NUMBER in the test rather
#: than a sentence in a docstring so a future reduction has to argue with it.
OBSERVED_THINKING_TOKENS = 1570
OBSERVED_FAILING_CEILING = 1924
OBSERVED_BATCH = 6


def _budget(n: int) -> int:
    from config import AI_GOV_OUTPUT_TOKEN_FLOOR, AI_GOV_OUTPUT_TOKEN_PER_SIGNAL

    return AI_GOV_OUTPUT_TOKEN_FLOOR + AI_GOV_OUTPUT_TOKEN_PER_SIGNAL * max(1, n)


def test_the_budget_clears_the_thinking_that_actually_truncated():
    """Fails against the pre-fix defaults, which is the point."""
    assert _budget(OBSERVED_BATCH) > OBSERVED_FAILING_CEILING
    # 1570 is a LOWER bound — the ceiling cut the thinking off — so a budget
    # that merely exceeds it is not enough. Require real headroom.
    assert _budget(OBSERVED_BATCH) >= OBSERVED_THINKING_TOKENS * 3


def test_a_single_signal_batch_is_not_starved():
    """The floor carries a lone position: thinking is largely fixed per request,
    so a batch of one is where a per-signal-only budget fails first."""
    assert _budget(1) >= OBSERVED_THINKING_TOKENS * 2


def test_the_budget_scales_with_the_batch():
    """A constant ceiling is one the next payload change outgrows in silence."""
    assert _budget(12) > _budget(6) > _budget(1)


def test_the_per_signal_term_is_configurable_not_a_literal():
    """It was a bare `150` in the call. A number that has already been wrong
    once belongs behind a name that can be moved without a deploy."""
    src = inspect.getsource(gov.evaluate)
    tree = ast.parse(src.lstrip())
    literals = [
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant)
        and isinstance(n.value, int)
        and not isinstance(n.value, bool)
        and n.value > 100
    ]
    assert not literals, f"a large numeric literal is back in evaluate: {literals}"


def test_both_budget_knobs_are_env_overridable():
    """B8: reversible without a code change, so a bad size costs a restart and
    not a release."""
    import config

    for name in ("AI_GOV_OUTPUT_TOKEN_FLOOR", "AI_GOV_OUTPUT_TOKEN_PER_SIGNAL"):
        assert isinstance(getattr(config, name), int)
        assert getattr(config, name) > 0
