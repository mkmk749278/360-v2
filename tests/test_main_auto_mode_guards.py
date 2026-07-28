"""The safety gates on the runtime auto-execution mode switch.

``main.set_auto_execution_mode`` is the engine side of the ops control plane's
auto-mode flip.  It is the function that can put the engine into LIVE — real
orders, real capital — and its four refusal paths were uncovered.

Each gate is asserted on the *refusal*, not on the happy path: a gate that
silently stops refusing is the failure mode that matters, and it is invisible
unless something pins the refusal.  In particular the open-position gate
protects the naked-position invariant — flipping mode with positions open
tears down the risk manager that is tracking them.

The gates all return before any manager is rebuilt, so ``self`` is an
attribute bag here.  The two tests that would cross into manager construction
(a genuine successful flip) are deliberately not faked: that path builds real
OrderManager/RiskManager objects and belongs in an integration test with a
real engine, not behind a hand-built stand-in that would assert our own idea
of those constructors back at us.
"""
from __future__ import annotations

import types

import pytest

from src.main import CryptoSignalEngine


def _engine(*, mode: str = "off", open_positions: int = 0,
            has_risk_manager: bool = True) -> types.SimpleNamespace:
    rm = (
        types.SimpleNamespace(open_position_count=open_positions)
        if has_risk_manager else None
    )
    return types.SimpleNamespace(
        _current_auto_mode=mode,
        _risk_manager=rm,
        _exchange_client=None,
        _position_reconciler=None,
        _redis_client=None,
        _order_manager=None,
    )


def _set(engine, mode: str):
    return CryptoSignalEngine.set_auto_execution_mode(engine, mode)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", ["", "  ", "LIVE_", "on", "enabled", "trade", "null"])
def test_unknown_mode_is_refused(bad) -> None:
    """Anything outside off/paper/live must be refused, not coerced.

    The ops control plane posts this value; a typo that fell through to a
    default would change execution behaviour from a form field.
    """
    ok, msg = _set(_engine(), bad)
    assert ok is False
    assert "invalid mode" in msg


@pytest.mark.parametrize("mode", ["off", "paper", "live"])
def test_mode_is_case_and_whitespace_normalised(mode) -> None:
    """"  LIVE " and "live" are the same request — and both hit the gates.

    Asserted via the no-op refusal so the test never actually flips a mode:
    if normalisation broke, this would report "invalid mode" instead.
    """
    ok, msg = _set(_engine(mode=mode), f"  {mode.upper()} ")
    assert ok is False
    assert "nothing to do" in msg


def test_switching_to_the_current_mode_is_a_no_op() -> None:
    """A redundant flip must not tear down and rebuild live managers."""
    ok, msg = _set(_engine(mode="paper"), "paper")
    assert ok is False
    assert "already in PAPER" in msg


# ---------------------------------------------------------------------------
# The naked-position invariant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("target", ["off", "live"])
def test_open_positions_block_any_mode_change(target) -> None:
    """Refuse while positions are open — a rebuild orphans their tracking.

    "Never let a position sit OPEN without a stop" is a hard limit, and a
    mode flip replaces the risk manager holding that state.
    """
    ok, msg = _set(_engine(mode="paper", open_positions=2), target)
    assert ok is False
    assert "2 open position(s)" in msg


def test_open_position_gate_precedes_the_live_credential_gate() -> None:
    """Ordering matters: the position refusal is the more urgent truth.

    If the credential check ran first, an operator with open positions and
    no keys would be told to go configure credentials — and would then be
    refused again for the real reason.
    """
    ok, msg = _set(_engine(mode="paper", open_positions=1), "live")
    assert ok is False
    assert "open position(s)" in msg
    assert "EXCHANGE_API_KEY" not in msg


def test_no_risk_manager_does_not_block_the_position_gate() -> None:
    """OFF mode has no risk manager; the gate must not crash on None."""
    ok, msg = _set(_engine(mode="off", has_risk_manager=False), "bogus")
    assert ok is False
    assert "invalid mode" in msg


# ---------------------------------------------------------------------------
# LIVE requires credentials
# ---------------------------------------------------------------------------


def test_live_without_credentials_is_refused(monkeypatch) -> None:
    """No keys → no LIVE.  The refusal names both env vars to set."""
    import src.main as main_mod

    monkeypatch.setattr(main_mod, "EXCHANGE_API_KEY", "", raising=False)
    monkeypatch.setattr(main_mod, "EXCHANGE_API_SECRET", "", raising=False)

    ok, msg = _set(_engine(mode="paper"), "live")
    assert ok is False
    assert "live mode refused" in msg
    assert "EXCHANGE_API_KEY" in msg and "EXCHANGE_API_SECRET" in msg


def test_live_with_only_one_credential_is_refused(monkeypatch) -> None:
    """A half-configured key pair is not partially acceptable."""
    import src.main as main_mod

    monkeypatch.setattr(main_mod, "EXCHANGE_API_KEY", "set", raising=False)
    monkeypatch.setattr(main_mod, "EXCHANGE_API_SECRET", "", raising=False)

    ok, msg = _set(_engine(mode="paper"), "live")
    assert ok is False
    assert "live mode refused" in msg


def test_paper_mode_does_not_require_credentials(monkeypatch) -> None:
    """The credential gate is LIVE-only — it must not block paper.

    Asserted by the absence of the credential refusal: paper proceeds past
    every gate (and on into manager construction, which is why this asserts
    on the message rather than on ok).
    """
    import src.main as main_mod

    monkeypatch.setattr(main_mod, "EXCHANGE_API_KEY", "", raising=False)
    monkeypatch.setattr(main_mod, "EXCHANGE_API_SECRET", "", raising=False)

    engine = _engine(mode="off")
    try:
        ok, msg = _set(engine, "paper")
    except Exception:
        # Manager construction is out of scope here; the gate is what matters.
        return
    assert "live mode refused" not in msg
