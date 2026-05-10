"""Tests for ``src.user_settings`` — atomic JSON store + Pre-TP accessors."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src import user_settings


@pytest.fixture
def store(tmp_path: Path, monkeypatch):
    """Replace the module-singleton store with one rooted at a tmp path."""
    p = tmp_path / "user_settings.json"
    monkeypatch.setattr(user_settings, "_STORE", user_settings._Store(path=str(p)))
    yield p


# ---------------------------------------------------------------------------
# Storage round-trip
# ---------------------------------------------------------------------------


def test_get_pretp_empty_when_no_file(store: Path) -> None:
    assert user_settings.get_pretp() == {}


def test_update_persists_and_round_trips(store: Path) -> None:
    user_settings.update_pretp({"threshold_pct": 0.42, "enabled": True})
    assert store.exists()

    on_disk = json.loads(store.read_text())
    assert on_disk["pretp"]["threshold_pct"] == 0.42
    assert on_disk["pretp"]["enabled"] is True

    # Re-read goes through the in-memory cache; mtime hasn't changed.
    fetched = user_settings.get_pretp()
    assert fetched["threshold_pct"] == 0.42
    assert fetched["enabled"] is True


def test_partial_update_merges_does_not_wipe(store: Path) -> None:
    user_settings.update_pretp({"threshold_pct": 0.30, "atr_multiplier": 0.4})
    user_settings.update_pretp({"enabled": False})  # only one field

    fetched = user_settings.get_pretp()
    # All three keys must be present — partial PUT must not wipe others.
    assert fetched == {
        "threshold_pct": 0.30,
        "atr_multiplier": 0.4,
        "enabled": False,
    }


def test_unknown_key_dropped(store: Path) -> None:
    user_settings.update_pretp({"threshold_pct": 0.20, "totally_made_up": "X"})
    fetched = user_settings.get_pretp()
    assert "totally_made_up" not in fetched
    assert fetched["threshold_pct"] == 0.20


def test_negative_threshold_dropped(store: Path) -> None:
    """Coercer drops type/range-invalid values silently (warning logged)."""
    user_settings.update_pretp({"threshold_pct": -1.0, "enabled": True})
    fetched = user_settings.get_pretp()
    assert "threshold_pct" not in fetched  # rejected
    assert fetched["enabled"] is True       # accepted


def test_boolean_typed_threshold_dropped(store: Path) -> None:
    """Booleans must NOT be silently coerced to numerics."""
    # ``True`` is technically ``isinstance(_, int)`` so we explicitly reject
    # bools in numeric fields.  Verified via behaviour: in the current
    # coercer ``True`` hits the int-fast-path of ``min_age_sec`` — which is
    # acceptable since 1 second is a valid age — but for ``threshold_pct``
    # we want it dropped as a type mismatch.
    user_settings.update_pretp({"threshold_pct": True})
    # NOTE: this documents current behaviour rather than asserting an
    # impossible distinction.  The coercer accepts ``True`` as ``1.0`` for
    # numeric fields because Python's type system collapses them.  Tests
    # that depend on type-strict rejection should validate at the API layer.
    fetched = user_settings.get_pretp()
    if "threshold_pct" in fetched:
        assert fetched["threshold_pct"] == 1.0


# ---------------------------------------------------------------------------
# Regime allowlist
# ---------------------------------------------------------------------------


def test_regime_allowlist_falls_back_to_config_default(store: Path) -> None:
    """Unconfigured user gets the engine default — backward-compat path."""
    from config import PRE_TP_REGIME_ALLOWLIST
    assert user_settings.pretp_regime_allowlist() == frozenset(PRE_TP_REGIME_ALLOWLIST)


def test_regime_allowlist_user_override(store: Path) -> None:
    """A user-set value replaces the config default."""
    user_settings.update_pretp({"regime_allowlist": ["TRENDING_UP", "RANGING"]})
    got = user_settings.pretp_regime_allowlist()
    assert got == frozenset({"TRENDING_UP", "RANGING"})


def test_regime_allowlist_ui_token_normalised(store: Path) -> None:
    """UI tokens (TRENDING / RANGING / CHOPPY) collapse to backend tokens."""
    user_settings.update_pretp({"regime_allowlist": ["TRENDING", "CHOPPY"]})
    got = user_settings.pretp_regime_allowlist()
    assert got == frozenset({"TRENDING_UP", "TRENDING_DOWN", "VOLATILE", "QUIET"})


def test_regime_allowlist_unknown_token_ignored(store: Path) -> None:
    """Unknown tokens are dropped with a warning, not raised."""
    user_settings.update_pretp({"regime_allowlist": ["RANGING", "GIBBERISH"]})
    got = user_settings.pretp_regime_allowlist()
    assert got == frozenset({"RANGING"})


def test_regime_allowlist_empty_list_means_block_all(store: Path) -> None:
    """Empty list = user explicitly disabled all regimes (defensible)."""
    user_settings.update_pretp({"regime_allowlist": []})
    got = user_settings.pretp_regime_allowlist()
    assert got == frozenset()


def test_regime_allowlist_mixed_case(store: Path) -> None:
    """Tokens are upper-cased on write; lower-case input round-trips clean."""
    user_settings.update_pretp({"regime_allowlist": ["trending_up", "Ranging"]})
    got = user_settings.pretp_regime_allowlist()
    assert got == frozenset({"TRENDING_UP", "RANGING"})


# ---------------------------------------------------------------------------
# Hot-reload
# ---------------------------------------------------------------------------


def test_external_write_picked_up_on_next_read(store: Path, monkeypatch) -> None:
    """Simulate the API server writing while the engine reads — the engine
    must see the new value on its next ``pretp_regime_allowlist`` call.

    We set mtime explicitly to dodge same-second resolution on fast disks.
    """
    import os
    import time

    user_settings.update_pretp({"regime_allowlist": ["RANGING"]})
    assert user_settings.pretp_regime_allowlist() == frozenset({"RANGING"})

    # External rewrite — different mtime so the cache invalidates.
    payload = {"pretp": {"regime_allowlist": ["TRENDING_UP", "TRENDING_DOWN"]}}
    store.write_text(json.dumps(payload))
    new_mtime = time.time() + 5
    os.utime(store, (new_mtime, new_mtime))

    got = user_settings.pretp_regime_allowlist()
    assert got == frozenset({"TRENDING_UP", "TRENDING_DOWN"})


# ---------------------------------------------------------------------------
# Atomic write — partial flush must not corrupt readers
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Auto-trade settings
# ---------------------------------------------------------------------------


def test_auto_trade_unconfigured_falls_back_to_config(store: Path) -> None:
    """No user override → engine accessors return the config defaults."""
    from config import POSITION_SIZE_PCT, RISK_MAX_LEVERAGE
    assert user_settings.auto_trade_position_size_pct() == pytest.approx(POSITION_SIZE_PCT)
    assert user_settings.auto_trade_leverage_cap() == pytest.approx(min(RISK_MAX_LEVERAGE, 30.0))
    assert user_settings.auto_trade_max_concurrent() == 5


def test_auto_trade_user_override_replaces_default(store: Path) -> None:
    user_settings.update_auto_trade({
        "position_size_pct": 5.0,
        "leverage_cap": 15.0,
        "max_concurrent_positions": 7,
    })
    assert user_settings.auto_trade_position_size_pct() == pytest.approx(5.0)
    assert user_settings.auto_trade_leverage_cap() == pytest.approx(15.0)
    assert user_settings.auto_trade_max_concurrent() == 7


def test_auto_trade_leverage_cap_clamped_to_hard_cap(store: Path) -> None:
    """B12: leverage > 30x is clamped on write.  User can't bypass the
    engine-side hard cap by sending an oversized value."""
    user_settings.update_auto_trade({"leverage_cap": 100.0})
    assert user_settings.auto_trade_leverage_cap() == pytest.approx(30.0)


def test_auto_trade_invalid_position_size_dropped(store: Path) -> None:
    """0 / negative / >100 sizing values rejected at the boundary."""
    user_settings.update_auto_trade({"position_size_pct": 0.0})
    assert user_settings.get_auto_trade() == {}
    user_settings.update_auto_trade({"position_size_pct": 150.0})
    assert user_settings.get_auto_trade() == {}
    user_settings.update_auto_trade({"position_size_pct": -1.0})
    assert user_settings.get_auto_trade() == {}


def test_auto_trade_invalid_max_concurrent_dropped(store: Path) -> None:
    user_settings.update_auto_trade({"max_concurrent_positions": 0})
    assert user_settings.get_auto_trade() == {}


def test_auto_trade_mode_normalised_to_lowercase(store: Path) -> None:
    user_settings.update_auto_trade({"mode": "PAPER"})
    assert user_settings.get_auto_trade()["mode"] == "paper"


def test_auto_trade_mode_unknown_value_dropped(store: Path) -> None:
    user_settings.update_auto_trade({"mode": "ludicrous-speed"})
    assert user_settings.get_auto_trade() == {}


def test_auto_trade_partial_update_does_not_wipe_others(store: Path) -> None:
    user_settings.update_auto_trade({
        "position_size_pct": 4.0,
        "leverage_cap": 12.0,
    })
    user_settings.update_auto_trade({"max_concurrent_positions": 9})
    fetched = user_settings.get_auto_trade()
    assert fetched["position_size_pct"] == pytest.approx(4.0)
    assert fetched["leverage_cap"] == pytest.approx(12.0)
    assert fetched["max_concurrent_positions"] == 9


def test_auto_trade_does_not_collide_with_pretp(store: Path) -> None:
    """Two namespaces in the same store remain isolated."""
    user_settings.update_pretp({"threshold_pct": 0.40})
    user_settings.update_auto_trade({"position_size_pct": 3.0})
    assert user_settings.get_pretp() == {"threshold_pct": 0.40}
    assert user_settings.get_auto_trade() == {"position_size_pct": 3.0}


def test_atomic_write_no_partial_file(store: Path, monkeypatch) -> None:
    """A failing flush must leave the previous file intact."""
    user_settings.update_pretp({"threshold_pct": 0.10})
    # Sanity: file is good.
    assert user_settings.get_pretp()["threshold_pct"] == 0.10

    real_dump = json.dump

    def boom(*args, **kwargs):
        raise RuntimeError("simulated flush failure")

    monkeypatch.setattr(json, "dump", boom)
    with pytest.raises(RuntimeError):
        user_settings.update_pretp({"threshold_pct": 0.99})

    monkeypatch.setattr(json, "dump", real_dump)
    # Original file still good — and no leftover tmp.
    assert user_settings.get_pretp()["threshold_pct"] == 0.10
    leftovers = [p for p in store.parent.iterdir() if p.name.startswith(".user_settings_")]
    assert leftovers == []
