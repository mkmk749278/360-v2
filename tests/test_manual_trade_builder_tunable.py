"""The manual trade builder's live switch is an ops-controllable runtime tunable.

Pins that `manual_trade_builder_enabled` is registered (so the ops panel surfaces
the toggle and set_values can flip it live), and that reads fall back to the
config env default when Firestore isn't wired — the fail-safe the three flag
read sites (dispatch_manual_trade, build_manual_trade_for_user, the endpoint)
rely on.
"""
from __future__ import annotations

import config
from src import runtime_tunables as rt


def test_manual_trade_builder_tunable_registered():
    reg = rt.registry()
    assert "manual_trade_builder_enabled" in reg
    tun = reg["manual_trade_builder_enabled"]
    assert tun.type == "bool"
    assert tun.category == "Execution"
    # default is the config env value captured at registry-build time
    assert tun.default == config.MANUAL_TRADE_BUILDER_ENABLED


def test_get_falls_back_to_config_default_when_uninitialised():
    rt.reset_for_test()  # no Firestore client wired
    assert bool(rt.get("manual_trade_builder_enabled")) == bool(
        config.MANUAL_TRADE_BUILDER_ENABLED
    )
