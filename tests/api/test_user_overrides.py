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


def test_pretp_clear_reverts_to_defaults(store: UserOverridesStore) -> None:
    """clear_pretp deletes the override row → get_pretp returns {} (the
    'using engine defaults' signal the API view keys off)."""
    store.update_pretp(1, {"enabled": False, "threshold_pct": 0.25, "grab_fraction": 0.9})
    assert store.get_pretp(1) != {}
    assert store.clear_pretp(1) == {}
    assert store.get_pretp(1) == {}


def test_pretp_clear_idempotent_for_new_user(store: UserOverridesStore) -> None:
    # Clearing with no prior row is a safe no-op.
    assert store.clear_pretp(1) == {}
    assert store.get_pretp(1) == {}


def test_pretp_clear_isolated_per_user(store: UserOverridesStore) -> None:
    store.update_pretp(1, {"threshold_pct": 0.25})
    store.update_pretp(2, {"threshold_pct": 0.50})
    store.clear_pretp(1)
    # User 2's overrides are untouched.
    assert store.get_pretp(1) == {}
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
# symbol_preference (per-user picker — PR E)
# ---------------------------------------------------------------------------


def test_symbol_preference_persists_as_canonical_uppercase(
    store: UserOverridesStore,
) -> None:
    """Mixed-case input → stored as sorted unique uppercase list."""
    out = store.update_auto_trade(
        1, {"symbol_preference": ["btcusdt", "ETHUSDT", "btcusdt"]}
    )
    assert out["symbol_preference"] == ["BTCUSDT", "ETHUSDT"]


def test_symbol_preference_rejects_non_usdt_symbols(
    store: UserOverridesStore,
) -> None:
    """Doctrine: only USDT-M futures are tradable; reject foreign tokens."""
    out = store.update_auto_trade(
        1, {"symbol_preference": ["BTCUSDT", "ETHBTC", "INVALID", "SOLUSDT"]}
    )
    assert out["symbol_preference"] == ["BTCUSDT", "SOLUSDT"]


def test_symbol_preference_empty_list_persists_as_explicit_block_all(
    store: UserOverridesStore,
) -> None:
    """Empty list ≠ None.  Empty means "user explicitly chose nothing —
    block ALL orders".  None means "no preference — fall through to
    engine-wide allowlist".  Both code paths must be storable."""
    out = store.update_auto_trade(1, {"symbol_preference": []})
    assert out["symbol_preference"] == []


def test_symbol_preference_none_clears(store: UserOverridesStore) -> None:
    """Passing None drops the column → defaults back to engine-wide
    allowlist for this user."""
    store.update_auto_trade(1, {"symbol_preference": ["BTCUSDT"]})
    out = store.update_auto_trade(1, {"symbol_preference": None})
    assert "symbol_preference" not in out


def test_symbol_preference_survives_other_field_updates(
    store: UserOverridesStore,
) -> None:
    """Setting leverage_cap doesn't clobber a previously-set symbol_preference."""
    store.update_auto_trade(1, {"symbol_preference": ["BTCUSDT", "ETHUSDT"]})
    out = store.update_auto_trade(1, {"leverage_cap": 10.0})
    assert out["symbol_preference"] == ["BTCUSDT", "ETHUSDT"]
    assert out["leverage_cap"] == 10.0


def test_symbol_preference_round_trips_via_get(
    store: UserOverridesStore,
) -> None:
    """JSON column round-trips through get_auto_trade as a list[str]."""
    store.update_auto_trade(1, {"symbol_preference": ["BTCUSDT", "SOLUSDT"]})
    out = store.get_auto_trade(1)
    assert out["symbol_preference"] == ["BTCUSDT", "SOLUSDT"]


# ---------------------------------------------------------------------------
# path_preference / regime_preference (per-user path + regime picker —
# 2026-06-20).  LIVE trade-eligibility filters consumed at dispatch.
# ---------------------------------------------------------------------------


def test_path_preference_persists_as_canonical_uppercase(
    store: UserOverridesStore,
) -> None:
    out = store.update_auto_trade(
        1, {"path_preference": ["sr_flip_retest", "DIVERGENCE_CONTINUATION",
                                "sr_flip_retest"]}
    )
    assert out["path_preference"] == ["DIVERGENCE_CONTINUATION", "SR_FLIP_RETEST"]


def test_path_preference_empty_list_persists_as_block_all(
    store: UserOverridesStore,
) -> None:
    """Empty list ≠ None — mirrors symbol_preference block-all semantics."""
    out = store.update_auto_trade(1, {"path_preference": []})
    assert out["path_preference"] == []


def test_path_preference_none_clears(store: UserOverridesStore) -> None:
    store.update_auto_trade(1, {"path_preference": ["SR_FLIP_RETEST"]})
    out = store.update_auto_trade(1, {"path_preference": None})
    assert "path_preference" not in out


def test_regime_preference_normalises_ui_tokens_to_backend(
    store: UserOverridesStore,
) -> None:
    """App sends UI tokens (TRENDING/RANGING/CHOPPY); stored as backend
    regime labels so the dispatcher can compare ``regime_label`` directly."""
    out = store.update_auto_trade(1, {"regime_preference": ["trending", "RANGING"]})
    assert out["regime_preference"] == ["RANGING", "TRENDING_DOWN", "TRENDING_UP"]


def test_regime_preference_none_clears(store: UserOverridesStore) -> None:
    store.update_auto_trade(1, {"regime_preference": ["RANGING"]})
    out = store.update_auto_trade(1, {"regime_preference": None})
    assert "regime_preference" not in out


def test_path_and_regime_survive_other_field_updates(
    store: UserOverridesStore,
) -> None:
    store.update_auto_trade(
        1,
        {"path_preference": ["BREAKDOWN_SHORT"], "regime_preference": ["RANGING"]},
    )
    out = store.update_auto_trade(1, {"notional_usd": 250.0})
    assert out["path_preference"] == ["BREAKDOWN_SHORT"]
    assert out["regime_preference"] == ["RANGING"]
    assert out["notional_usd"] == 250.0


def test_path_regime_round_trip_via_get(store: UserOverridesStore) -> None:
    store.update_auto_trade(
        1,
        {"path_preference": ["FAILED_AUCTION_RECLAIM"],
         "regime_preference": ["CHOPPY"]},
    )
    out = store.get_auto_trade(1)
    assert out["path_preference"] == ["FAILED_AUCTION_RECLAIM"]
    # CHOPPY → VOLATILE + QUIET
    assert out["regime_preference"] == ["QUIET", "VOLATILE"]


def test_resolve_auto_trade_preferences_uid_semantics(
    store: UserOverridesStore, monkeypatch,
) -> None:
    """None (unset) → None (allow-all); empty list → empty frozenset
    (block-all); populated list → frozenset of allowed tokens."""
    import src.api.user_overrides as uo

    class _User:
        user_id = 1

    class _UserStore:
        def get_by_firebase_uid(self, _uid):
            return _User()

    monkeypatch.setattr(uo, "_SINGLETON", store, raising=False)
    import src.api.users as _users
    monkeypatch.setattr(_users, "get_singleton", lambda: _UserStore())

    # Unset → allow-all.
    path_fs, regime_fs = uo.resolve_auto_trade_preferences_uid("uid")
    assert path_fs is None and regime_fs is None

    # Populated → frozensets.
    store.update_auto_trade(
        1, {"path_preference": ["SR_FLIP_RETEST"], "regime_preference": ["RANGING"]}
    )
    path_fs, regime_fs = uo.resolve_auto_trade_preferences_uid("uid")
    assert path_fs == frozenset({"SR_FLIP_RETEST"})
    assert regime_fs == frozenset({"RANGING"})

    # Explicit empty → block-all (empty frozenset, NOT None).
    store.update_auto_trade(1, {"path_preference": []})
    path_fs, _ = uo.resolve_auto_trade_preferences_uid("uid")
    assert path_fs == frozenset()
    assert path_fs is not None


# ---------------------------------------------------------------------------
# Per-symbol management mode (Signals-tab full vs entry — 2026-06-20)
# ---------------------------------------------------------------------------


def test_symbol_management_empty_for_new_user(store: UserOverridesStore) -> None:
    assert store.get_symbol_management_map(1) == {}


def test_symbol_management_set_entry_persists(store: UserOverridesStore) -> None:
    out = store.set_symbol_management(1, "btcusdt", "entry")
    assert out == {"BTCUSDT": "entry"}
    assert store.get_symbol_management_map(1) == {"BTCUSDT": "entry"}


def test_symbol_management_full_clears_row(store: UserOverridesStore) -> None:
    """`full` is the default — storing it just deletes the override so we
    never persist rows that restate the default."""
    store.set_symbol_management(1, "BTCUSDT", "entry")
    out = store.set_symbol_management(1, "BTCUSDT", "full")
    assert out == {}
    assert store.get_symbol_management_map(1) == {}


def test_symbol_management_rejects_invalid_mode(store: UserOverridesStore) -> None:
    out = store.set_symbol_management(1, "BTCUSDT", "yolo")
    assert out == {}


def test_symbol_management_isolated_per_user(store: UserOverridesStore) -> None:
    store.set_symbol_management(1, "BTCUSDT", "entry")
    store.set_symbol_management(2, "ETHUSDT", "entry")
    assert store.get_symbol_management_map(1) == {"BTCUSDT": "entry"}
    assert store.get_symbol_management_map(2) == {"ETHUSDT": "entry"}


def test_resolve_symbol_management_uid_default_full_then_entry(
    store: UserOverridesStore, monkeypatch,
) -> None:
    import src.api.user_overrides as uo

    class _User:
        user_id = 1

    class _UserStore:
        def get_by_firebase_uid(self, _uid):
            return _User()

    monkeypatch.setattr(uo, "_SINGLETON", store, raising=False)
    import src.api.users as _users
    monkeypatch.setattr(_users, "get_singleton", lambda: _UserStore())

    # Unset → full (the protective default).
    assert uo.resolve_symbol_management_uid("uid", "BTCUSDT") == "full"
    # Set entry → entry; case-insensitive symbol match.
    store.set_symbol_management(1, "BTCUSDT", "entry")
    assert uo.resolve_symbol_management_uid("uid", "btcusdt") == "entry"
    # A different symbol is still full.
    assert uo.resolve_symbol_management_uid("uid", "ETHUSDT") == "full"


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


def test_invalidation_clear_reverts_to_defaults(store: UserOverridesStore) -> None:
    store.update_invalidation(1, {"mode": "tight", "trailing_retrace_pct": 0.55})
    assert store.get_invalidation(1) != {}
    assert store.clear_invalidation(1) == {}
    assert store.get_invalidation(1) == {}


def test_invalidation_clear_idempotent_and_isolated(store: UserOverridesStore) -> None:
    store.update_invalidation(2, {"mode": "loose"})
    # No row for user 1 → no-op; user 2 untouched.
    assert store.clear_invalidation(1) == {}
    assert store.get_invalidation(2)["mode"] == "loose"


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


# ---------------------------------------------------------------------------
# protect_manual_entries (OWNER_BRIEF B17, 2026-05-17 — manual-entry pre-TP coverage)
# ---------------------------------------------------------------------------


def test_protect_manual_entries_round_trip_true(store: UserOverridesStore) -> None:
    """True persists as bool, not int — the JSON contract returns bool."""
    out = store.update_pretp(1, {"protect_manual_entries": True})
    assert out["protect_manual_entries"] is True
    assert store.get_pretp(1)["protect_manual_entries"] is True


def test_protect_manual_entries_round_trip_false(store: UserOverridesStore) -> None:
    """False persists distinctly from absent.  This is the 'pure manual'
    opt-out — the watcher must respect it and stay stopped when mode=off."""
    out = store.update_pretp(1, {"protect_manual_entries": False})
    assert out["protect_manual_entries"] is False
    assert store.get_pretp(1)["protect_manual_entries"] is False


def test_protect_manual_entries_non_bool_dropped(store: UserOverridesStore) -> None:
    """Mirrors existing _coerce_pretp behaviour for ill-typed values.
    Int 1 must not silently become True — the field is strictly bool."""
    out = store.update_pretp(1, {"enabled": True, "protect_manual_entries": 1})
    assert out["enabled"] is True
    assert "protect_manual_entries" not in out


def test_protect_manual_entries_explicit_none_clears(
    store: UserOverridesStore,
) -> None:
    store.update_pretp(1, {"protect_manual_entries": False})
    out = store.update_pretp(1, {"protect_manual_entries": None})
    assert "protect_manual_entries" not in out


def test_protect_manual_entries_isolated_per_user(
    store: UserOverridesStore,
) -> None:
    store.update_pretp(1, {"protect_manual_entries": False})
    store.update_pretp(2, {"protect_manual_entries": True})
    assert store.get_pretp(1)["protect_manual_entries"] is False
    assert store.get_pretp(2)["protect_manual_entries"] is True


def test_protect_manual_entries_round_trip_across_reopen(db_path) -> None:
    s1 = UserOverridesStore(db_path)
    s1.update_pretp(1, {"protect_manual_entries": False, "grab_fraction": 0.65})
    s1.close()
    s2 = UserOverridesStore(db_path)
    try:
        out = s2.get_pretp(1)
        assert out["protect_manual_entries"] is False
        assert out["grab_fraction"] == 0.65
    finally:
        s2.close()


def test_pretp_migration_adds_protect_manual_entries_to_existing_db(
    db_path,
) -> None:
    """Existing pre-2026-05-17 DB rows must survive the schema migration.

    Simulates a deploy where the existing user_pretp_settings table predates
    the protect_manual_entries column.  ALTER TABLE adds the column without
    dropping rows; pre-existing field values stay intact, the new column
    reads NULL (interpreted as 'use engine default') for the existing user.
    """
    import sqlite3

    # Create the legacy schema by hand — no protect_manual_entries column.
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
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
            grab_fraction     REAL,
            updated_at        TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
    )
    conn.execute(
        "INSERT INTO user_pretp_settings (user_id, enabled, threshold_pct, "
        "grab_fraction, updated_at) VALUES (?, 1, 0.25, 0.60, 'pre-migration')",
        (1,),
    )
    conn.commit()
    conn.close()

    # Open via the store — triggers the idempotent ALTER TABLE migration.
    s = UserOverridesStore(db_path)
    try:
        existing = s.get_pretp(1)
        # Pre-migration data preserved untouched.
        assert existing["enabled"] is True
        assert existing["threshold_pct"] == 0.25
        assert existing["grab_fraction"] == 0.60
        # New column reads NULL → omitted from the partial dict.
        assert "protect_manual_entries" not in existing

        # A subsequent write must populate the new column without disturbing
        # the pre-existing values.
        out = s.update_pretp(1, {"protect_manual_entries": True})
        assert out["protect_manual_entries"] is True
        assert out["enabled"] is True
        assert out["threshold_pct"] == 0.25
        assert out["grab_fraction"] == 0.60
    finally:
        s.close()


# ---------------------------------------------------------------------------
# notional_usd (per-user notional override — 2026-05-20)
# ---------------------------------------------------------------------------


def test_notional_usd_persists_within_bounds(store: UserOverridesStore) -> None:
    """Mid-band value persists as-is."""
    out = store.update_auto_trade(1, {"notional_usd": 100.0})
    assert out["notional_usd"] == 100.0


def test_notional_usd_clamps_to_ceiling(store: UserOverridesStore) -> None:
    """Above $2000 (B18 per-user position cap) → clamps to ceiling.
    Same UX as ``leverage_cap`` clamping into B12."""
    out = store.update_auto_trade(1, {"notional_usd": 5000.0})
    assert out["notional_usd"] == 2000.0


def test_notional_usd_clamps_to_floor(store: UserOverridesStore) -> None:
    """Below $5 (Binance MIN_NOTIONAL for most pairs) → clamps to floor.
    Anything below $5 is guaranteed to fail Binance's filter on every
    symbol; silently fixing avoids a foot-gun."""
    out = store.update_auto_trade(1, {"notional_usd": 1.0})
    assert out["notional_usd"] == 5.0


def test_notional_usd_rejects_non_positive(store: UserOverridesStore) -> None:
    """Zero / negative not stored — caller should clear via explicit None."""
    out = store.update_auto_trade(1, {"notional_usd": 0})
    assert "notional_usd" not in out
    out = store.update_auto_trade(1, {"notional_usd": -10.0})
    assert "notional_usd" not in out


def test_notional_usd_explicit_none_clears(store: UserOverridesStore) -> None:
    """``notional_usd=None`` clears a previously-set override → dispatch
    falls back to the engine default ($500)."""
    store.update_auto_trade(1, {"notional_usd": 50.0})
    out = store.update_auto_trade(1, {"notional_usd": None})
    assert "notional_usd" not in out


def test_notional_usd_survives_other_field_updates(store: UserOverridesStore) -> None:
    """Setting leverage_cap doesn't clobber a previously-set notional_usd."""
    store.update_auto_trade(1, {"notional_usd": 75.0})
    out = store.update_auto_trade(1, {"leverage_cap": 10.0})
    assert out["notional_usd"] == 75.0
    assert out["leverage_cap"] == 10.0


def test_notional_usd_migrated_on_pre_existing_db(tmp_path) -> None:
    """Existing deploys carry a pre-notional_usd schema.  Opening the
    store must ALTER TABLE in the new column and preserve pre-existing
    rows."""
    import sqlite3 as _sqlite3
    db_path = tmp_path / "lumin.sqlite"

    # Create the pre-migration schema by hand — NO ``notional_usd`` column.
    conn = _sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        );
        CREATE TABLE IF NOT EXISTS user_auto_trade_settings (
            user_id                  INTEGER PRIMARY KEY,
            mode                     TEXT,
            position_size_pct        REAL,
            leverage_cap             REAL,
            max_concurrent_positions INTEGER,
            symbol_preference        TEXT,
            updated_at               TEXT NOT NULL
        );
        """
    )
    conn.execute("INSERT INTO users (user_id) VALUES (1)")
    conn.execute(
        "INSERT INTO user_auto_trade_settings (user_id, mode, leverage_cap, "
        "updated_at) VALUES (?, 'live', 10.0, 'pre-migration')",
        (1,),
    )
    conn.commit()
    conn.close()

    # Open via the store — triggers the idempotent ALTER TABLE migration.
    s = UserOverridesStore(db_path)
    try:
        existing = s.get_auto_trade(1)
        assert existing["mode"] == "live"
        assert existing["leverage_cap"] == 10.0
        assert "notional_usd" not in existing  # NULL → omitted

        # A subsequent write must populate the new column without
        # disturbing the pre-existing fields.
        out = s.update_auto_trade(1, {"notional_usd": 50.0})
        assert out["notional_usd"] == 50.0
        assert out["mode"] == "live"
        assert out["leverage_cap"] == 10.0
    finally:
        s.close()


def test_resolve_notional_usd_falls_back_when_singleton_unset() -> None:
    """No store singleton registered → returns the default unchanged.
    Soft-fail semantics required because dispatch must never block on
    an override lookup."""
    from src.api import user_overrides as _uo
    _uo.clear_singleton()
    assert _uo.resolve_notional_usd("any-uid", 500.0) == 500.0


def test_resolve_notional_usd_returns_default_when_user_unknown(
    store: UserOverridesStore, tmp_path,
) -> None:
    """Singleton registered but firebase_uid doesn't resolve to a user
    → return the default.  Mirrors the production case of a stale
    firebase_uid cache after a user delete."""
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.set_singleton(store)
    user_store = _users.UserStore(tmp_path / "users.sqlite")
    _users.set_singleton(user_store)
    try:
        assert _uo.resolve_notional_usd("nonexistent-uid", 500.0) == 500.0
    finally:
        _uo.clear_singleton()
        _users.set_singleton(None)
        user_store.close()


def test_resolve_notional_usd_returns_user_override(
    store: UserOverridesStore, tmp_path,
) -> None:
    """End-to-end: user with a set ``notional_usd`` gets that value
    returned via ``resolve_notional_usd``."""
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.set_singleton(store)
    user_store = _users.UserStore(tmp_path / "users.sqlite")
    _users.set_singleton(user_store)
    try:
        # Create user + their override.
        user = user_store.get_or_create_by_firebase_uid(
            "test-firebase-uid", "+15551234567",
        )
        store.update_auto_trade(user.user_id, {"notional_usd": 75.0})

        # Resolve returns the override, not the default.
        assert _uo.resolve_notional_usd("test-firebase-uid", 500.0) == 75.0

        # User without an override gets the default.
        user_store.get_or_create_by_firebase_uid(
            "uid-no-override", "+15557654321",
        )
        assert _uo.resolve_notional_usd("uid-no-override", 500.0) == 500.0
    finally:
        _uo.clear_singleton()
        _users.set_singleton(None)
        user_store.close()


# ---------------------------------------------------------------------------
# resolve_pretp_enabled_uid (2026-05-29: master pre-TP enable toggle)
# ---------------------------------------------------------------------------


def test_resolve_pretp_enabled_falls_back_when_singleton_unset() -> None:
    from src.api import user_overrides as _uo
    _uo.clear_singleton()
    assert _uo.resolve_pretp_enabled_uid("any-uid", default=True) is True
    assert _uo.resolve_pretp_enabled_uid("any-uid", default=False) is False


def test_resolve_pretp_enabled_honours_stored_value(
    store: UserOverridesStore, tmp_path,
) -> None:
    """End-to-end: a user who explicitly disabled pre-TP gets False; a
    user who enabled it gets True; an unset user falls back to default
    (True for the per-user FSM path)."""
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.set_singleton(store)
    user_store = _users.UserStore(tmp_path / "users.sqlite")
    _users.set_singleton(user_store)
    try:
        off = user_store.get_or_create_by_firebase_uid("uid-off", "+15551110001")
        on = user_store.get_or_create_by_firebase_uid("uid-on", "+15551110002")
        store.update_pretp(off.user_id, {"enabled": False})
        store.update_pretp(on.user_id, {"enabled": True})

        # Explicit OFF is honoured even though default is True.
        assert _uo.resolve_pretp_enabled_uid("uid-off", default=True) is False
        # Explicit ON.
        assert _uo.resolve_pretp_enabled_uid("uid-on", default=True) is True
        # Unset user → default (preserves current pre-TP-on behaviour).
        user_store.get_or_create_by_firebase_uid("uid-unset", "+15551110003")
        assert _uo.resolve_pretp_enabled_uid("uid-unset", default=True) is True
    finally:
        _uo.clear_singleton()
        _users.set_singleton(None)
        user_store.close()


# ---------------------------------------------------------------------------
# Per-user paper subscription windows (2026-05-23 fix for fresh-account bug)
# ---------------------------------------------------------------------------


def test_paper_subscriptions_empty_for_new_user(
    store: UserOverridesStore,
) -> None:
    """Fresh users have no subscription rows — their trade view is empty."""
    assert store.get_paper_subscriptions(1) == []


def test_paper_enable_opens_active_subscription(
    store: UserOverridesStore,
) -> None:
    """Setting mode=paper inserts an active (ended_at=None) subscription."""
    store.update_auto_trade(1, {"mode": "paper"})
    subs = store.get_paper_subscriptions(1)
    assert len(subs) == 1
    started_at, ended_at = subs[0]
    assert started_at  # ISO stamp present
    assert ended_at is None  # active


def test_paper_disable_closes_active_subscription(
    store: UserOverridesStore,
) -> None:
    """Transitioning paper→off stamps ended_at on the active row."""
    store.update_auto_trade(1, {"mode": "paper"})
    store.update_auto_trade(1, {"mode": "off"})
    subs = store.get_paper_subscriptions(1)
    assert len(subs) == 1
    assert subs[0][1] is not None  # closed


def test_paper_reenable_creates_second_window(
    store: UserOverridesStore,
) -> None:
    """Re-enabling paper after disabling produces two windows, preserving
    the first as a closed historical record."""
    store.update_auto_trade(1, {"mode": "paper"})
    store.update_auto_trade(1, {"mode": "off"})
    store.update_auto_trade(1, {"mode": "paper"})
    subs = store.get_paper_subscriptions(1)
    assert len(subs) == 2
    # First window closed, second active.
    assert subs[0][1] is not None
    assert subs[1][1] is None


def test_paper_mode_stable_update_does_not_add_subscription(
    store: UserOverridesStore,
) -> None:
    """Updating other auto-trade fields while mode is unchanged must not
    open a new subscription window."""
    store.update_auto_trade(1, {"mode": "paper"})
    store.update_auto_trade(1, {"mode": "paper", "leverage_cap": 5.0})
    subs = store.get_paper_subscriptions(1)
    assert len(subs) == 1  # unchanged
    assert subs[0][1] is None  # still active


def test_paper_mode_transition_live_to_paper_opens_subscription(
    store: UserOverridesStore,
) -> None:
    """live → paper is a paper-enable transition; opens a window."""
    store.update_auto_trade(1, {"mode": "live"})
    assert store.get_paper_subscriptions(1) == []  # live doesn't open one
    store.update_auto_trade(1, {"mode": "paper"})
    subs = store.get_paper_subscriptions(1)
    assert len(subs) == 1
    assert subs[0][1] is None


def test_paper_mode_transition_paper_to_live_closes_subscription(
    store: UserOverridesStore,
) -> None:
    """paper → live closes the paper window."""
    store.update_auto_trade(1, {"mode": "paper"})
    store.update_auto_trade(1, {"mode": "live"})
    subs = store.get_paper_subscriptions(1)
    assert len(subs) == 1
    assert subs[0][1] is not None


def test_reset_paper_subscription_discards_history_and_opens_fresh(
    store: UserOverridesStore,
) -> None:
    """reset_paper_subscription deletes ALL prior subscription rows and
    opens a single new active one. This is the "start truly fresh"
    semantic — preserving closed windows would still admit trades
    closed inside them, defeating the bug-fix promise.
    """
    store.update_auto_trade(1, {"mode": "paper"})
    store.update_auto_trade(1, {"mode": "off"})
    store.update_auto_trade(1, {"mode": "paper"})
    # Two windows now (one closed, one active).
    assert len(store.get_paper_subscriptions(1)) == 2
    new_started_at = store.reset_paper_subscription(1)
    subs = store.get_paper_subscriptions(1)
    # Only the freshly-opened subscription remains.
    assert len(subs) == 1
    assert subs[0][0] == new_started_at
    assert subs[0][1] is None


def test_paper_subscriptions_isolated_between_users(
    store: UserOverridesStore,
) -> None:
    """One user's subscription windows must not leak into another user's
    view — the fresh-account bug fix depends on this isolation."""
    store.update_auto_trade(1, {"mode": "paper"})
    # User 2 stays off — should have no subscriptions.
    assert store.get_paper_subscriptions(2) == []
    # User 1 has exactly one.
    assert len(store.get_paper_subscriptions(1)) == 1


# ---------------------------------------------------------------------------
# Auto-pause (2026-05-24 — consecutive -2019 insufficient_margin tracker)
# ---------------------------------------------------------------------------


def test_is_user_auto_paused_false_for_new_user(
    store: UserOverridesStore,
) -> None:
    """Fresh user has no auto-trade row at all → not paused."""
    assert store.is_user_auto_paused(1) is False


def test_is_user_auto_paused_false_when_row_exists_unpaused(
    store: UserOverridesStore,
) -> None:
    """User who opted in but isn't paused returns False."""
    store.update_auto_trade(1, {"mode": "live"})
    assert store.is_user_auto_paused(1) is False


def test_pause_user_auto_trade_sets_reason_and_stamp(
    store: UserOverridesStore,
) -> None:
    """pause_user_auto_trade stamps paused_reason + paused_at."""
    store.update_auto_trade(1, {"mode": "live"})
    paused_at = store.pause_user_auto_trade(1, "insufficient_margin")
    assert paused_at is not None
    assert store.is_user_auto_paused(1) is True
    row = store.get_auto_trade(1)
    assert row["paused_reason"] == "insufficient_margin"
    assert row["paused_at"] == paused_at


def test_pause_returns_none_when_no_row(
    store: UserOverridesStore,
) -> None:
    """Can't pause a user who hasn't opted in — returns None (the
    dispatcher only fans out to users with rows, so this is just a
    defensive check)."""
    assert store.pause_user_auto_trade(99, "insufficient_margin") is None


def test_pause_is_idempotent_for_same_reason(
    store: UserOverridesStore,
) -> None:
    """Re-pausing for the same reason preserves the original timestamp."""
    store.update_auto_trade(1, {"mode": "live"})
    first = store.pause_user_auto_trade(1, "insufficient_margin")
    second = store.pause_user_auto_trade(1, "insufficient_margin")
    assert first == second  # same timestamp returned


def test_resume_clears_pause(
    store: UserOverridesStore,
) -> None:
    """resume_user_auto_trade nulls both pause columns."""
    store.update_auto_trade(1, {"mode": "live"})
    store.pause_user_auto_trade(1, "insufficient_margin")
    assert store.is_user_auto_paused(1) is True
    cleared = store.resume_user_auto_trade(1)
    assert cleared is True
    assert store.is_user_auto_paused(1) is False
    row = store.get_auto_trade(1)
    assert "paused_reason" not in row  # NULL → filtered out by _row_to_partial
    assert "paused_at" not in row


def test_resume_returns_false_when_not_paused(
    store: UserOverridesStore,
) -> None:
    """Idempotent: resuming a non-paused user is a no-op."""
    store.update_auto_trade(1, {"mode": "live"})
    assert store.resume_user_auto_trade(1) is False


def test_pause_isolated_between_users(
    store: UserOverridesStore,
) -> None:
    """Pausing user 1 must not pause user 2."""
    store.update_auto_trade(1, {"mode": "live"})
    store.update_auto_trade(2, {"mode": "live"})
    store.pause_user_auto_trade(1, "insufficient_margin")
    assert store.is_user_auto_paused(1) is True
    assert store.is_user_auto_paused(2) is False


# ---------------------------------------------------------------------------
# resolve_invalidation_mode_uid (PR-G: per-user invalidation mode)
# ---------------------------------------------------------------------------


def test_resolve_invalidation_mode_uid_falls_back_when_singleton_unset() -> None:
    """No store singleton → return the default unchanged (soft-fail)."""
    from src.api import user_overrides as _uo
    _uo.clear_singleton()
    assert _uo.resolve_invalidation_mode_uid("any-uid", "standard") == "standard"
    assert _uo.resolve_invalidation_mode_uid("any-uid", "tight") == "tight"


def test_resolve_invalidation_mode_uid_returns_default_when_user_unknown(
    store: UserOverridesStore, tmp_path,
) -> None:
    """Singleton registered but firebase_uid has no user row → return default."""
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.set_singleton(store)
    user_store = _users.UserStore(tmp_path / "users.sqlite")
    _users.set_singleton(user_store)
    try:
        assert _uo.resolve_invalidation_mode_uid("nonexistent-uid", "standard") == "standard"
    finally:
        _uo.clear_singleton()
        _users.set_singleton(None)
        user_store.close()


def test_resolve_invalidation_mode_uid_returns_user_mode(
    store: UserOverridesStore, tmp_path,
) -> None:
    """User with ``mode='loose'`` in invalidation settings → returns 'loose'."""
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.set_singleton(store)
    user_store = _users.UserStore(tmp_path / "users.sqlite")
    _users.set_singleton(user_store)
    try:
        user = user_store.get_or_create_by_firebase_uid(
            "test-inv-uid", "+15551112222",
        )
        store.update_invalidation(user.user_id, {"mode": "loose"})

        assert _uo.resolve_invalidation_mode_uid("test-inv-uid", "standard") == "loose"

        # User with no override gets the default.
        user_store.get_or_create_by_firebase_uid(
            "uid-no-inv-override", "+15553334444",
        )
        assert _uo.resolve_invalidation_mode_uid("uid-no-inv-override", "standard") == "standard"
    finally:
        _uo.clear_singleton()
        _users.set_singleton(None)
        user_store.close()


def test_resolve_invalidation_mode_uid_tight_via_shared_db(
    store: UserOverridesStore, db_path,
) -> None:
    """'tight' mode round-trips through the resolver when user rows share the
    same SQLite file (so FK constraints are satisfied)."""
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.set_singleton(store)
    # Open a UserStore on the SAME db file so FK references are valid.
    user_store = _users.UserStore(db_path)
    _users.set_singleton(user_store)
    try:
        user = user_store.get_or_create_by_firebase_uid("uid-tight-test", "+15550000099")
        store.update_invalidation(user.user_id, {"mode": "tight"})
        assert _uo.resolve_invalidation_mode_uid("uid-tight-test", "standard") == "tight"
    finally:
        _uo.clear_singleton()
        _users.set_singleton(None)
        user_store.close()
