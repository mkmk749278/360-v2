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


# ---------------------------------------------------------------------------
# grab_fraction (OWNER_BRIEF B17, 2026-05-17 doctrine amendment)
# ---------------------------------------------------------------------------


def test_grab_fraction_round_trip(store: UserOverridesStore) -> None:
    """Default-range value (between floor and ceiling) persists exactly."""
    out = store.update_pretp(1, {"grab_fraction": 0.50})
    assert out["grab_fraction"] == 0.50
    assert store.get_pretp(1)["grab_fraction"] == 0.50


def test_grab_fraction_clamped_at_floor(store: UserOverridesStore) -> None:
    """B17 hard 30% floor — no user can collapse to SL-to-BE-only behaviour."""
    out = store.update_pretp(1, {"grab_fraction": 0.10})
    assert out["grab_fraction"] == 0.30


def test_grab_fraction_clamped_at_ceiling(store: UserOverridesStore) -> None:
    """B17 ceiling — 100% fully banks the partial, leaves nothing riding."""
    out = store.update_pretp(1, {"grab_fraction": 1.50})
    assert out["grab_fraction"] == 1.00


def test_grab_fraction_zero_clamped_to_floor(store: UserOverridesStore) -> None:
    """Zero is the most-dangerous input — it would re-create the broken
    pre-2026-05-17 behaviour where nothing is closed and only the SL moves
    to BE.  B17 floor catches this."""
    out = store.update_pretp(1, {"grab_fraction": 0.0})
    assert out["grab_fraction"] == 0.30


def test_grab_fraction_non_numeric_dropped(store: UserOverridesStore) -> None:
    """Mirrors existing _coerce_pretp behaviour for ill-typed values."""
    out = store.update_pretp(1, {"enabled": True, "grab_fraction": "fifty"})
    assert out["enabled"] is True
    assert "grab_fraction" not in out


def test_grab_fraction_explicit_none_clears(store: UserOverridesStore) -> None:
    store.update_pretp(1, {"grab_fraction": 0.75})
    out = store.update_pretp(1, {"grab_fraction": None})
    assert "grab_fraction" not in out


def test_pretp_migration_adds_grab_fraction_to_existing_db(db_path) -> None:
    """Existing pre-B17 DB rows must survive the schema migration.

    Simulates a deploy where the existing user_pretp_settings table predates
    the grab_fraction column.  ALTER TABLE adds the column without dropping
    rows; pre-existing field values stay intact, the new column reads NULL
    (= use engine default).
    """
    import sqlite3
    # Open a connection and manually create the OLD-shape table (no grab_fraction).
    # Then write a row, close, and reopen via UserOverridesStore — the migration
    # should add the column without losing the pre-existing data.
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_pretp_settings (
            user_id           INTEGER PRIMARY KEY,
            enabled           INTEGER,
            regime_allowlist  TEXT,
            setup_allowlist   TEXT,
            threshold_pct     REAL,
            atr_multiplier    REAL,
            fee_floor_pct     REAL,
            min_age_sec       INTEGER,
            max_age_sec       INTEGER,
            updated_at        TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        INSERT INTO user_pretp_settings (user_id, enabled, threshold_pct, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (1, 1, 0.42, "2026-05-16T00:00:00+00:00"),
    )
    conn.commit()
    conn.close()

    # Open via the store — migration runs in __init__.
    store = UserOverridesStore(db_path)
    try:
        # Pre-existing data survives.
        out = store.get_pretp(1)
        assert out.get("enabled") is True
        assert out.get("threshold_pct") == 0.42
        # New column reads as absent (NULL) — user is on engine default.
        assert "grab_fraction" not in out
        # And writing the new column now works.
        updated = store.update_pretp(1, {"grab_fraction": 0.60})
        assert updated["grab_fraction"] == 0.60
        assert updated["threshold_pct"] == 0.42  # Old data still there
    finally:
        store.close()


# ---------------------------------------------------------------------------
# Invalidation table (OWNER_BRIEF B17)
# ---------------------------------------------------------------------------


def test_invalidation_empty_for_new_user(store: UserOverridesStore) -> None:
    assert store.get_invalidation(1) == {}


def test_invalidation_update_persists_mode(store: UserOverridesStore) -> None:
    out = store.update_invalidation(1, {"mode": "tight"})
    assert out["mode"] == "tight"
    assert store.get_invalidation(1) == out


def test_invalidation_mode_validation(store: UserOverridesStore) -> None:
    """Only the three B17 modes are accepted; other tokens silently dropped."""
    out = store.update_invalidation(1, {"mode": "aggressive"})
    assert out == {}  # Unknown mode dropped → no row update
    for mode in ("loose", "standard", "tight"):
        out = store.update_invalidation(1, {"mode": mode})
        assert out["mode"] == mode


def test_invalidation_mode_normalises_case(store: UserOverridesStore) -> None:
    out = store.update_invalidation(1, {"mode": "TIGHT"})
    assert out["mode"] == "tight"


def test_invalidation_advanced_knobs_round_trip(store: UserOverridesStore) -> None:
    """Advanced-section overrides persist independently of mode."""
    out = store.update_invalidation(1, {
        "mode": "tight",
        "trailing_mfe_r_threshold": 0.4,
        "trailing_retrace_pct": 0.6,
        "ema_crossover_enabled": False,
        "min_age_sec": 60,
    })
    assert out["mode"] == "tight"
    assert out["trailing_mfe_r_threshold"] == 0.4
    assert out["trailing_retrace_pct"] == 0.6
    assert out["ema_crossover_enabled"] is False
    assert out["min_age_sec"] == 60


def test_invalidation_partial_merge(store: UserOverridesStore) -> None:
    store.update_invalidation(1, {"mode": "tight", "trailing_mfe_r_threshold": 0.4})
    out = store.update_invalidation(1, {"mode": "standard"})
    assert out["mode"] == "standard"
    # Advanced knob is preserved (not cleared by a partial-update that omits it).
    assert out["trailing_mfe_r_threshold"] == 0.4


def test_invalidation_explicit_none_clears_field(store: UserOverridesStore) -> None:
    store.update_invalidation(1, {"mode": "tight", "trailing_mfe_r_threshold": 0.4})
    out = store.update_invalidation(1, {"trailing_mfe_r_threshold": None})
    assert out["mode"] == "tight"
    assert "trailing_mfe_r_threshold" not in out


def test_invalidation_isolated_per_user(store: UserOverridesStore) -> None:
    store.update_invalidation(1, {"mode": "tight"})
    store.update_invalidation(2, {"mode": "loose"})
    assert store.get_invalidation(1)["mode"] == "tight"
    assert store.get_invalidation(2)["mode"] == "loose"


def test_invalidation_unknown_keys_dropped(store: UserOverridesStore) -> None:
    out = store.update_invalidation(1, {"mode": "tight", "made_up_key": "x"})
    assert "made_up_key" not in out
    assert out["mode"] == "tight"


def test_invalidation_round_trip_across_reopen(db_path) -> None:
    s1 = UserOverridesStore(db_path)
    s1.update_invalidation(
        1,
        {"mode": "tight", "trailing_mfe_r_threshold": 0.35, "trailing_retrace_pct": 0.55},
    )
    s1.close()
    s2 = UserOverridesStore(db_path)
    try:
        assert s2.get_invalidation(1) == {
            "mode": "tight",
            "trailing_mfe_r_threshold": 0.35,
            "trailing_retrace_pct": 0.55,
        }
    finally:
        s2.close()
