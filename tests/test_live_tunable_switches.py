"""The two switches are flippable from ops, and flipping them does something.

Owner, 2026-08-22: *"how to make them live"*.

`DUAL_UNIVERSE_ENABLED` and `DIRECTION_CAP_MODE` shipped as env-only config,
read into module constants at import — so every flip cost an SSH session and an
engine restart. That is the wrong shape for a switch whose whole purpose is to
be toggled while watching a panel, and it makes the deploy the unit of
iteration rather than the decision.

They are ops tunables now. `runtime_tunables.get` is the hot-path-safe
accessor (one Firestore doc read per 5s TTL covers every key, never raises),
which is what makes it admissible inside the per-channel scan loop and the
router's per-candidate gate.

**The property that matters here is not "the key exists".** A tunable the
engine registers and never reads is the banned scaffold — a setting the engine
stores but does not consume — so every test below flips the value and asserts
the BEHAVIOUR changed.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict

import pytest

import config
import src.scanner as scanner_mod
import src.signal_router as sr
from src.channels.base import Signal
from src.runtime_tunables import registry
from src.signal_router import SignalRouter
from src.smc import Direction


_KEYS = (
    "dual_universe_enabled",
    "direction_cap_mode",
    "max_same_direction_per_path",
    "max_same_direction_cumulative",
)


# ---------------------------------------------------------------------------
# Registration — shape, not just presence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("key", _KEYS)
def test_the_switch_is_registered(key):
    assert key in registry(), f"{key} is not reachable from /control"


def test_the_mode_is_unselectable_wrong():
    """A setting with two legal values must not be free text.

    `trail_governor_timeframe` shipped as free text, the owner typed `5`, the
    store keys `"5m"`, and the governor went permanently inert with its switch
    reading ON. `choices` renders a select and makes `set_values` refuse
    anything else.
    """
    tun = registry()["direction_cap_mode"]
    assert tun.type == "str"
    assert tun.choices == ("global", "per_path")


def test_the_blast_radius_switches_are_bounded():
    """A cap with no bound is a text box pointed at the money path."""
    per_path = registry()["max_same_direction_per_path"]
    assert per_path.min_value == 1 and per_path.max_value == 10

    cumulative = registry()["max_same_direction_cumulative"]
    assert cumulative.min_value == 0, "0 must remain reachable — it is OFF"


@pytest.mark.parametrize("key", _KEYS)
def test_the_registered_default_is_the_shipped_default(key):
    """The registry must not quietly ship a different default than config."""
    expected = {
        "dual_universe_enabled": config.DUAL_UNIVERSE_ENABLED,
        "direction_cap_mode": config.DIRECTION_CAP_MODE,
        "max_same_direction_per_path": config.MAX_SAME_DIRECTION_PER_PATH,
        "max_same_direction_cumulative": config.MAX_SAME_DIRECTION_CUMULATIVE,
    }[key]
    assert registry()[key].default == expected


@pytest.mark.parametrize("key", _KEYS)
def test_every_switch_says_it_is_an_owner_sign_off_item(key):
    """These four change what emits or how much of it. The description is what
    the owner reads at the moment of flipping, so it carries the warning."""
    desc = registry()[key].description
    assert "owner sign-off item" in desc.lower(), (
        f"{key} can be flipped from ops with no statement of what it costs"
    )


# ---------------------------------------------------------------------------
# Flipping it changes BEHAVIOUR — the anti-scaffold assertion
# ---------------------------------------------------------------------------

@pytest.fixture
def tunables(monkeypatch):
    """Stand in for the Firestore-backed store with a plain dict."""
    values: Dict[str, Any] = {}

    def _get(key: str):
        from src.runtime_tunables import registry as _reg

        if key in values:
            return values[key]
        tun = _reg().get(key)
        return tun.default if tun is not None else None

    import src.runtime_tunables as rt_mod

    monkeypatch.setattr(rt_mod, "get", _get)
    return values


def _router() -> SignalRouter:
    async def _send(chat_id: str, text: str) -> bool:
        return True

    return SignalRouter(
        queue=asyncio.Queue(), send_telegram=_send,
        format_signal=lambda sig: "x",
    )


def _sig(sym: str, origin: str, direction: Direction = Direction.LONG) -> Signal:
    return Signal(
        channel="360_SCALP", symbol=sym, direction=direction,
        entry=100.0, stop_loss=98.0, tp1=103.0, tp2=106.0,
        setup_class=origin, origin_setup_class=origin,
        signal_id=f"{sym}-{origin}-{direction.value}",
    )


def _saturate(router: SignalRouter, origin="MOVER_TREND_PULLBACK", n=3) -> None:
    for i in range(n):
        s = _sig(f"S{i}USDT", origin)
        router._active_signals[s.signal_id] = s


def test_flipping_the_mode_changes_what_the_gate_does(tunables):
    """The whole point: a starved path gets through in per_path mode."""
    r = _router()
    _saturate(r)
    starved = _sig("NEWUSDT", "MEAN_REVERT")

    tunables["direction_cap_mode"] = "global"
    assert r._direction_cap_decision(starved).blocked is True

    tunables["direction_cap_mode"] = "per_path"
    assert r._direction_cap_decision(starved).blocked is False, (
        "flipping the tunable did not reach the gate — a setting the engine "
        "stores and does not consume is the banned scaffold"
    )


def test_the_per_path_budget_is_read_live(tunables):
    r = _router()
    _saturate(r)
    tunables["direction_cap_mode"] = "per_path"
    same_path = _sig("NEWUSDT", "MOVER_TREND_PULLBACK")

    tunables["max_same_direction_per_path"] = 3
    assert r._direction_cap_decision(same_path).blocked is True

    tunables["max_same_direction_per_path"] = 5
    assert r._direction_cap_decision(same_path).blocked is False


def test_the_cumulative_ceiling_is_read_live(tunables):
    r = _router()
    for path in ("P1", "P2", "P3", "P4"):
        _saturate(r, origin=path)
    tunables["direction_cap_mode"] = "per_path"
    fresh = _sig("NEWUSDT", "P5")

    tunables["max_same_direction_cumulative"] = 0        # off
    assert r._direction_cap_decision(fresh).blocked is False

    tunables["max_same_direction_cumulative"] = 10       # armed
    cap = r._direction_cap_decision(fresh)
    assert cap.blocked is True and cap.reason == "cumulative ceiling"


def test_the_report_shows_the_live_mode_not_the_boot_default(tunables):
    """A panel reporting the boot default while the engine runs an owner-set
    value is the cohort-edge census defect — it read `enabled=True` from a side
    process while the engine's own counter said the gate was off."""
    r = _router()
    tunables["direction_cap_mode"] = "per_path"
    tunables["max_same_direction_per_path"] = 4

    report = r.direction_cap_report()
    assert report["mode"] == "per_path"
    assert report["per_path_limit"] == 4


def test_flipping_dual_universe_changes_the_evaluator_set(tunables):
    """Same anti-scaffold assertion on the scanner side."""
    tunables["dual_universe_enabled"] = False
    assert scanner_mod._dual_universe_live() is False

    tunables["dual_universe_enabled"] = True
    assert scanner_mod._dual_universe_live() is True


def test_the_census_reports_the_live_effect_state(tunables):
    """The panel must say what the ENGINE is doing, not what it booted with."""
    sc = scanner_mod.Scanner.__new__(scanner_mod.Scanner)
    sc._mover_promoted_pairs = {}
    sc._synthetic_mover_pairs = set()
    sc.pair_mgr = type("_PM", (), {"pairs": {}})()

    tunables["dual_universe_enabled"] = True
    assert sc._dual_universe_census()["enabled"] is True

    tunables["dual_universe_enabled"] = False
    assert sc._dual_universe_census()["enabled"] is False


# ---------------------------------------------------------------------------
# A read failure must never decide a money-path gate
# ---------------------------------------------------------------------------

def test_an_unreadable_tunable_falls_back_to_the_boot_value(monkeypatch):
    """Not to a guess, and not to an exception.

    The behaviour on a failed config read is the behaviour that was already
    shipping — a gate must not change because Firestore hiccupped.
    """
    import src.runtime_tunables as rt_mod

    def _boom(key: str):
        raise RuntimeError("firestore down")

    monkeypatch.setattr(rt_mod, "get", _boom)

    assert scanner_mod._dual_universe_live() is config.DUAL_UNIVERSE_ENABLED
    assert sr._tunable_str("direction_cap_mode", "global") == "global"
    assert sr._tunable_int("max_same_direction_per_path", 3) == 3

    # …and the gate still decides rather than raising.
    r = _router()
    _saturate(r)
    assert r._direction_cap_decision(_sig("XUSDT", "MEAN_REVERT")).blocked is True
