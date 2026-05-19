"""Tests for src.execution.tripwires.

Five tripwire layers — each tested independently because each one
is a defensive boundary the FSM consults before placing orders.

What we pin:

* Symbol allowlist: empty → block all (safer default); set → allow
  only those; case-insensitive matching.
* Rate limiter: per-min and per-hour windows both enforced; trims
  old entries lazily; per-user isolation (one user's limit doesn't
  block another).
* Position cap: notional > cap raises; max-cap floor enforced so
  user can't opt themselves above the policy ceiling.
* Per-user circuit breaker: trips on threshold reached; the FIRST
  trip-event is signalled to the caller (so we only Telegram-alert
  once); manual reset clears state.
* Global circuit breaker: trips when threshold reached across all
  users; subsequent ``check`` calls raise; manual reset re-enables.
"""
from __future__ import annotations

import pytest

from src.execution import tripwires


@pytest.fixture(autouse=True)
def _reset_singletons():
    tripwires.reset_singletons_for_test()
    yield
    tripwires.reset_singletons_for_test()


# ---------------------------------------------------------------------------
# Symbol allowlist
# ---------------------------------------------------------------------------


def test_symbol_allowlist_empty_blocks_all() -> None:
    """Defensive default: empty allowlist blocks ALL orders.  Safer
    than accept-all when env var is misconfigured."""
    with pytest.raises(tripwires.SymbolNotAllowed):
        tripwires.assert_symbol_allowed("BTCUSDT", allowlist=set())


def test_symbol_allowlist_blocks_off_list() -> None:
    with pytest.raises(tripwires.SymbolNotAllowed):
        tripwires.assert_symbol_allowed(
            "DOGEUSDT", allowlist={"BTCUSDT", "ETHUSDT"}
        )


def test_symbol_allowlist_permits_on_list() -> None:
    # No exception.
    tripwires.assert_symbol_allowed(
        "BTCUSDT", allowlist={"BTCUSDT", "ETHUSDT"}
    )


def test_symbol_allowlist_is_case_insensitive() -> None:
    """Binance returns symbols in upper; engine code typically uses
    upper; but a defensive lower-case probe must still match."""
    tripwires.assert_symbol_allowed(
        "btcusdt", allowlist={"BTCUSDT"}
    )


def test_symbol_allowlist_loads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT, SOLUSDT")
    allowlist = tripwires._load_symbol_allowlist()
    assert allowlist == {"BTCUSDT", "ETHUSDT", "SOLUSDT"}


# ---------------------------------------------------------------------------
# Per-user symbol preference (PR E)
# ---------------------------------------------------------------------------


def _install_user_pref_singletons(
    *,
    firebase_uid: str = "fb-x",
    user_id: int = 1,
    symbol_preference,  # list[str] | None
) -> None:
    """Wire mocked user_overrides + users module singletons so the
    tripwire helpers find the firebase_uid → user_id mapping +
    symbol_preference row.  Pass ``symbol_preference=None`` to model
    "user hasn't set a preference"."""
    from unittest.mock import MagicMock
    from src.api import user_overrides as _uo
    from src.api import users as _users

    user = MagicMock(user_id=user_id)
    fake_user_store = MagicMock()
    fake_user_store.get_by_firebase_uid = MagicMock(return_value=user)
    _users.set_singleton(fake_user_store)

    override_dict = (
        {"symbol_preference": symbol_preference}
        if symbol_preference is not None
        else {}
    )
    fake_overrides_store = MagicMock()
    fake_overrides_store.get_auto_trade = MagicMock(return_value=override_dict)
    _uo.set_singleton(fake_overrides_store)


def test_user_pref_no_preference_falls_through() -> None:
    """Default = all engine-allowed symbols.  When the user has no
    row (or row with NULL symbol_preference), the gate is a no-op."""
    _install_user_pref_singletons(symbol_preference=None)
    try:
        tripwires.assert_symbol_in_user_preference("BTCUSDT", "fb-x")
    finally:
        _reset_pref_singletons()


def test_user_pref_blocks_off_list() -> None:
    """User picked [BTCUSDT].  ETHUSDT must be blocked."""
    _install_user_pref_singletons(symbol_preference=["BTCUSDT"])
    try:
        with pytest.raises(tripwires.SymbolNotInUserPreference):
            tripwires.assert_symbol_in_user_preference("ETHUSDT", "fb-x")
    finally:
        _reset_pref_singletons()


def test_user_pref_permits_on_list() -> None:
    _install_user_pref_singletons(symbol_preference=["BTCUSDT", "ETHUSDT"])
    try:
        tripwires.assert_symbol_in_user_preference("ETHUSDT", "fb-x")
    finally:
        _reset_pref_singletons()


def test_user_pref_empty_list_blocks_everything() -> None:
    """Empty list = explicit opt-out from auto-trade.  Every symbol
    blocks; doctrine-strict path for cautious users."""
    _install_user_pref_singletons(symbol_preference=[])
    try:
        with pytest.raises(tripwires.SymbolNotInUserPreference):
            tripwires.assert_symbol_in_user_preference("BTCUSDT", "fb-x")
    finally:
        _reset_pref_singletons()


def test_user_pref_is_case_insensitive() -> None:
    _install_user_pref_singletons(symbol_preference=["btcusdt"])
    try:
        tripwires.assert_symbol_in_user_preference("BTCUSDT", "fb-x")
    finally:
        _reset_pref_singletons()


def test_user_pref_falls_through_when_singletons_missing() -> None:
    """Boot order / test harnesses without bootstrap → no preference
    resolution available.  Soft-fail = let the symbol through (engine-
    wide cap is the actual security floor)."""
    _reset_pref_singletons()
    tripwires.assert_symbol_in_user_preference("BTCUSDT", "fb-x")


def test_effective_allowlist_intersects_with_user_pref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Engine allowlist = {BTC, ETH, SOL}; user_pref = {BTC, ETH, XRP}.
    Effective = {BTC, ETH} (XRP not on engine cap can never widen)."""
    monkeypatch.setenv(
        "TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT,SOLUSDT"
    )
    _install_user_pref_singletons(
        symbol_preference=["BTCUSDT", "ETHUSDT", "XRPUSDT"]
    )
    try:
        effective = tripwires.effective_allowed_symbols_for_user("fb-x")
        assert effective == ["BTCUSDT", "ETHUSDT"]
    finally:
        _reset_pref_singletons()


def test_effective_allowlist_returns_engine_full_when_no_pref(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT,SOLUSDT"
    )
    _install_user_pref_singletons(symbol_preference=None)
    try:
        effective = tripwires.effective_allowed_symbols_for_user("fb-x")
        assert effective == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    finally:
        _reset_pref_singletons()


def _reset_pref_singletons() -> None:
    from src.api import user_overrides as _uo
    from src.api import users as _users
    _uo.clear_singleton()
    _users.set_singleton(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


def test_rate_limiter_allows_orders_below_per_min_threshold() -> None:
    """5 orders, default per_min=5 — last one is at the boundary
    (raises).  Verify we get exactly 5 successes before the rate
    limit fires."""
    fake_clock_value = [0.0]

    def fake_clock():
        return fake_clock_value[0]

    rl = tripwires.RateLimiter(per_min=5, per_hour=30, clock=fake_clock)
    # First 5 orders, each at t=0 (well within the 60s window).
    for i in range(5):
        rl.check_and_record("fb-x")
    # 6th order at the same instant → rate limit.
    with pytest.raises(tripwires.RateLimitExceeded):
        rl.check_and_record("fb-x")


def test_rate_limiter_per_min_window_slides() -> None:
    """After the per-min window slides, fresh capacity is available."""
    t = [0.0]
    rl = tripwires.RateLimiter(per_min=5, per_hour=30, clock=lambda: t[0])
    # 5 orders at t=0.
    for _ in range(5):
        rl.check_and_record("fb-x")
    # Advance 61s — per-min window has slid past.
    t[0] = 61.0
    # 6th order now succeeds (within per-hour, fresh per-min window).
    rl.check_and_record("fb-x")


def test_rate_limiter_per_hour_blocks_burst_within_hour() -> None:
    """30 orders/hour — verify the hour cap fires even if each per-
    minute window had spare capacity."""
    t = [0.0]
    rl = tripwires.RateLimiter(per_min=5, per_hour=30, clock=lambda: t[0])
    for i in range(30):
        # Space them out so per-min never trips: 5 every 61s.
        if i > 0 and i % 5 == 0:
            t[0] += 61.0
        rl.check_and_record("fb-x")
    # 31st order — same effective time, per-hour cap fires.
    t[0] += 1.0
    with pytest.raises(tripwires.RateLimitExceeded):
        rl.check_and_record("fb-x")


def test_rate_limiter_per_user_isolation() -> None:
    """User A's burst must NOT block user B."""
    t = [0.0]
    rl = tripwires.RateLimiter(per_min=5, per_hour=30, clock=lambda: t[0])
    for _ in range(5):
        rl.check_and_record("fb-A")
    with pytest.raises(tripwires.RateLimitExceeded):
        rl.check_and_record("fb-A")
    # User B is unaffected.
    rl.check_and_record("fb-B")
    rl.check_and_record("fb-B")


# ---------------------------------------------------------------------------
# Position cap
# ---------------------------------------------------------------------------


def test_position_cap_blocks_above_user_cap() -> None:
    with pytest.raises(tripwires.PositionCapExceeded):
        tripwires.assert_position_cap(notional_usd=600.0, cap_usd=500.0)


def test_position_cap_permits_at_or_below_cap() -> None:
    tripwires.assert_position_cap(notional_usd=500.0, cap_usd=500.0)
    tripwires.assert_position_cap(notional_usd=100.0, cap_usd=500.0)


def test_position_cap_enforces_system_max() -> None:
    """User configured $5000 cap, but system max is $2000 — the
    effective cap is $2000.  Catches a malicious / buggy user-
    settings write that tries to opt above the policy floor."""
    with pytest.raises(tripwires.PositionCapExceeded):
        tripwires.assert_position_cap(
            notional_usd=2500.0,
            cap_usd=5000.0,  # user tried to opt up
            max_cap_usd=2000.0,
        )


# ---------------------------------------------------------------------------
# Per-user circuit breaker
# ---------------------------------------------------------------------------


def test_per_user_breaker_does_not_trip_under_threshold() -> None:
    breaker = tripwires.PerUserCircuitBreaker(threshold=3, window_s=300.0)
    assert breaker.record_rejection("fb-x") is False
    assert breaker.record_rejection("fb-x") is False
    # Verify check() doesn't raise.
    breaker.check("fb-x")


def test_per_user_breaker_trips_at_threshold_and_signals_fresh_trip() -> None:
    """The first time the breaker trips, ``record_rejection`` returns
    True so the caller (FSM) knows to persist + Telegram-alert.
    Subsequent rejections after the trip return False (we don't want
    to alert again)."""
    breaker = tripwires.PerUserCircuitBreaker(threshold=3, window_s=300.0)
    breaker.record_rejection("fb-x")
    breaker.record_rejection("fb-x")
    assert breaker.record_rejection("fb-x") is True  # the trip
    assert breaker.record_rejection("fb-x") is False  # already tripped
    with pytest.raises(tripwires.UserAutoDisabled):
        breaker.check("fb-x")


def test_per_user_breaker_window_slides() -> None:
    """Rejections outside the window are forgotten — a slow trickle
    of failures doesn't accumulate forever."""
    t = [0.0]
    breaker = tripwires.PerUserCircuitBreaker(
        threshold=3, window_s=300.0, clock=lambda: t[0]
    )
    breaker.record_rejection("fb-x")
    breaker.record_rejection("fb-x")
    # Advance 301s — the first two timestamps fall outside the window.
    t[0] = 301.0
    # Third rejection — fresh start, breaker does NOT trip.
    assert breaker.record_rejection("fb-x") is False


def test_per_user_breaker_reset_clears_state() -> None:
    breaker = tripwires.PerUserCircuitBreaker(threshold=3, window_s=300.0)
    for _ in range(3):
        breaker.record_rejection("fb-x")
    # Verify tripped.
    with pytest.raises(tripwires.UserAutoDisabled):
        breaker.check("fb-x")
    breaker.reset("fb-x")
    # After reset, check passes + counter is cleared.
    breaker.check("fb-x")
    # New rejection doesn't immediately re-trip.
    assert breaker.record_rejection("fb-x") is False


def test_per_user_breaker_isolation() -> None:
    """One user tripping does NOT trip another."""
    breaker = tripwires.PerUserCircuitBreaker(threshold=3, window_s=300.0)
    for _ in range(3):
        breaker.record_rejection("fb-A")
    with pytest.raises(tripwires.UserAutoDisabled):
        breaker.check("fb-A")
    # User B is unaffected.
    breaker.check("fb-B")


# ---------------------------------------------------------------------------
# Global circuit breaker
# ---------------------------------------------------------------------------


def test_global_breaker_does_not_trip_under_threshold() -> None:
    g = tripwires.GlobalCircuitBreaker(threshold=10, window_s=60.0)
    for _ in range(9):
        assert g.record_rejection() is False
    g.check()  # no raise


def test_global_breaker_trips_at_threshold_and_signals_first_trip() -> None:
    g = tripwires.GlobalCircuitBreaker(threshold=10, window_s=60.0)
    for _ in range(9):
        g.record_rejection()
    assert g.record_rejection() is True  # 10th → trip
    assert g.record_rejection() is False  # already tripped
    with pytest.raises(tripwires.GlobalKillSwitchEngaged):
        g.check()


def test_global_breaker_window_slides() -> None:
    """Rejections outside the 60s window age out — a slow drip
    doesn't accumulate."""
    t = [0.0]
    g = tripwires.GlobalCircuitBreaker(
        threshold=10, window_s=60.0, clock=lambda: t[0]
    )
    for _ in range(9):
        g.record_rejection()
    # Advance 61s — all 9 timestamps slide out.
    t[0] = 61.0
    assert g.record_rejection() is False
    assert g.is_tripped is False


def test_global_breaker_reset_re_enables() -> None:
    g = tripwires.GlobalCircuitBreaker(threshold=3, window_s=60.0)
    for _ in range(3):
        g.record_rejection()
    assert g.is_tripped is True
    g.reset()
    assert g.is_tripped is False
    g.check()  # no raise


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------


def test_singletons_are_lazy_and_idempotent() -> None:
    """Multiple calls return the same instance."""
    assert tripwires.rate_limiter() is tripwires.rate_limiter()
    assert tripwires.per_user_breaker() is tripwires.per_user_breaker()
    assert tripwires.global_breaker() is tripwires.global_breaker()


def test_reset_singletons_drops_state() -> None:
    rl_a = tripwires.rate_limiter()
    tripwires.reset_singletons_for_test()
    rl_b = tripwires.rate_limiter()
    assert rl_a is not rl_b
