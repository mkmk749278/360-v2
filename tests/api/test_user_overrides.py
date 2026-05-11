"""UserOverridesStore tests — Phase 2 per-user settings.

Covers the SQLite-backed per-user pretp + auto-trade override store:

- Fresh user has no overrides → get returns {}.
- update merges partials, persists, returns the new partial dict.
- Explicit None clears an existing override field.
- Unknown / ill-typed values are silently dropped (mirrors
  src.user_settings coercion behaviour).
- regime_allowlist normalises UI tokens (TRENDING) → backend tokens
  (TRENDING_UP, TRENDING_DOWN).
- Round-trip across reopens.
"""
from __future__ import annotations

import pytest

from src.api.user_overrides import UserOverridesStore
from src.api.users import UserStore


@pytest.fixture
def db_path(tmp_path):
    # UserStore opens first so the ``users`` table exists; foreign-key
    # constraints on user_overrides reference it.
    path = tmp_path / "lumin.sqlite"
    us = UserStore(path)
    us.get_or_create_by_phone("+15550000001")  # user_id=1
    us.get_or_create_by_phone("+15550000002")  # user_id=2
    yield path
    us.close()


@pytest.fixture
def store(db_path):
    s = UserOverridesStore(db_path)
    yield s
    s.close()


# ---------------------------------------------------------------------------
# pretp
# ---------------------------------------------------------------------------


def test_pretp_empty_for_new_user(store: UserOverridesStore) -> None:
    assert store.get_pretp(1) == {}


def test_pretp_update_persists_partial(store: UserOverridesStore) -> None:
    out = store.update_pretp(1, {"enabled": True, "threshold_pct": 0.25})
    assert out["enabled"] is True
    assert out["threshold_pct"] == 0.25
    # Fields not set stay absent.
    assert "atr_multiplier" not in out
    # Re-read to confirm persistence.
    fresh = store.get_pretp(1)
    assert fresh == out


def test_pretp_update_merges_subsequent_partials(store: UserOverridesStore) -> None:
    store.update_pretp(1, {"enabled": True})
    out = store.update_pretp(1, {"threshold_pct": 0.30})
    assert out["enabled"] is True
    assert out["threshold_pct"] == 0.30


def test_pretp_explicit_none_clears_field(store: UserOverridesStore) -> None:
    store.update_pretp(1, {"enabled": True, "threshold_pct": 0.25})
    out = store.update_pretp(1, {"threshold_pct": None})
    assert out["enabled"] is True
    assert "threshold_pct" not in out


def test_pretp_unknown_keys_dropped(store: UserOverridesStore) -> None:
    out = store.update_pretp(1, {"enabled": True, "nonsense": "x"})
    assert "nonsense" not in out
    assert out["enabled"] is True


def test_pretp_ill_typed_dropped(store: UserOverridesStore) -> None:
    # threshold_pct should be numeric ≥ 0.
    out = store.update_pretp(1, {"enabled": True, "threshold_pct": "abc"})
    assert "threshold_pct" not in out
    assert out["enabled"] is True


def test_pretp_regime_allowlist_normalises_ui_tokens(
    store: UserOverridesStore,
) -> None:
    out = store.update_pretp(1, {"regime_allowlist": ["TRENDING", "RANGING"]})
    # UI tokens expand to backend tokens.
    assert sorted(out["regime_allowlist"]) == [
        "RANGING", "TRENDING_DOWN", "TRENDING_UP",
    ]


def test_pretp_setup_allowlist_normalises_case(
    store: UserOverridesStore,
) -> None:
    out = store.update_pretp(
        1, {"setup_allowlist": ["whale_momentum", "  tpe  ", "TPE"]}
    )
    # Upper-cased + de-duplicated + sorted.
    assert out["setup_allowlist"] == ["TPE", "WHALE_MOMENTUM"]


def test_pretp_isolated_per_user(store: UserOverridesStore) -> None:
    store.update_pretp(1, {"threshold_pct": 0.25})
    store.update_pretp(2, {"threshold_pct": 0.50})
    assert store.get_pretp(1)["threshold_pct"] == 0.25
    assert store.get_pretp(2)["threshold_pct"] == 0.50


# ---------------------------------------------------------------------------
# auto-trade
# ---------------------------------------------------------------------------


def test_auto_trade_empty_for_new_user(store: UserOverridesStore) -> None:
    assert store.get_auto_trade(1) == {}


def test_auto_trade_update_persists(store: UserOverridesStore) -> None:
    out = store.update_auto_trade(
        1,
        {
            "mode": "paper",
            "position_size_pct": 2.0,
            "leverage_cap": 10.0,
            "max_concurrent_positions": 3,
        },
    )
    assert out == {
        "mode": "paper",
        "position_size_pct": 2.0,
        "leverage_cap": 10.0,
        "max_concurrent_positions": 3,
    }


def test_auto_trade_clamps_leverage_to_b12(store: UserOverridesStore) -> None:
    out = store.update_auto_trade(1, {"leverage_cap": 100.0})
    # B12 hard cap = 30.
    assert out["leverage_cap"] == 30.0


def test_auto_trade_rejects_unknown_mode(store: UserOverridesStore) -> None:
    out = store.update_auto_trade(1, {"mode": "yolo"})
    assert "mode" not in out


def test_auto_trade_explicit_none_clears(store: UserOverridesStore) -> None:
    store.update_auto_trade(1, {"mode": "paper", "leverage_cap": 5.0})
    out = store.update_auto_trade(1, {"mode": None})
    assert "mode" not in out
    assert out["leverage_cap"] == 5.0


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def test_round_trip_across_reopen(db_path) -> None:
    s1 = UserOverridesStore(db_path)
    s1.update_pretp(1, {"enabled": True, "threshold_pct": 0.25})
    s1.update_auto_trade(1, {"mode": "paper"})
    s1.close()

    s2 = UserOverridesStore(db_path)
    try:
        assert s2.get_pretp(1) == {"enabled": True, "threshold_pct": 0.25}
        assert s2.get_auto_trade(1) == {"mode": "paper"}
    finally:
        s2.close()
