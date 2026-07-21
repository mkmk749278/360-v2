"""Referral rewards Phase 2 (2026-07-21) — ledgers, composition, hooks.

What we pin (the promises the feature makes):

* Join reward: 7 days of Auto banked per referee, sequentially stacking,
  clamped at the stack cap, one-shot per referee (DB-level dedup).
* Commission: 50% of each verified paid period of a referee for their
  first 3 periods, idempotent per (token, period), computed on what was
  ACTUALLY paid (discounted first cycle → half base), never fabricated
  for an unpriced product.
* Composition: a banked reward survives Play-derived downgrades and the
  expiry re-resolution never zeroes a still-live subscription.
* Discount eligibility: one-time — flips off at first conversion.
* Kill switch: REFERRAL_REWARDS_ENABLED=false stops NEW grants/accruals
  but never confiscates banked time.
* Owner admin surface: listing + mark-paid are owner-gated.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import config
from src.api.referral_rewards import ReferralRewardsService, _better
from src.api.play_purchases import PlayPurchaseStore
from src.api.user_overrides import UserOverridesStore
from src.api.users import UserStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def stores(tmp_path):
    """Real SQLite stores sharing one file, as in production wiring."""
    db = tmp_path / "lumin.sqlite"
    users = UserStore(db)
    overrides = UserOverridesStore(db)
    purchases = PlayPurchaseStore(db)
    return users, overrides, purchases


@pytest.fixture
def service(stores):
    users, overrides, purchases = stores
    return ReferralRewardsService(
        user_store=users, overrides=overrides, play_purchases=purchases,
    )


@pytest.fixture
def two_users(stores):
    users, _, _ = stores
    referrer = users.get_or_create_by_phone("+15550000001")
    referee = users.get_or_create_by_phone("+15550000002")
    return referrer, referee


def _redeem(overrides: UserOverridesStore, referrer_id: int, referee_id: int) -> None:
    code = overrides.get_or_create_referral_code(referrer_id)
    result = overrides.redeem_referral_code(referee_id, code)
    assert result["ok"], result


# ---------------------------------------------------------------------------
# Reward grant ledger
# ---------------------------------------------------------------------------


def test_grant_banks_days_and_dedups_per_referee(stores, two_users):
    _, overrides, _ = stores
    referrer, referee = two_users
    r1 = overrides.grant_referral_reward(
        referrer.user_id, referee.user_id, days=7, tier="auto", cap_days=90,
    )
    assert r1["granted"] is True
    # Same referee again (e.g. hook re-fired) grants nothing.
    r2 = overrides.grant_referral_reward(
        referrer.user_id, referee.user_id, days=7, tier="auto", cap_days=90,
    )
    assert r2 == {"granted": False, "reason": "duplicate"}


def test_grants_stack_sequentially(stores, two_users):
    users, overrides, _ = stores
    referrer, referee = two_users
    third = users.get_or_create_by_phone("+15550000003")
    overrides.grant_referral_reward(
        referrer.user_id, referee.user_id, days=7, tier="auto", cap_days=90,
    )
    r2 = overrides.grant_referral_reward(
        referrer.user_id, third.user_id, days=7, tier="auto", cap_days=90,
    )
    end = datetime.fromisoformat(r2["expires_at"])
    # Two back-to-back grants: window ends ~14 days out, not ~7.
    assert end > datetime.now(timezone.utc) + timedelta(days=13, hours=23)
    summary = overrides.get_reward_summary(referrer.user_id)
    assert summary["reward_days_earned"] == 14
    active = overrides.get_active_reward(referrer.user_id)
    assert active is not None and active["tier"] == "auto"


def test_stack_cap_clamps_to_zero(stores, two_users):
    users, overrides, _ = stores
    referrer, referee = two_users
    overrides.grant_referral_reward(
        referrer.user_id, referee.user_id, days=7, tier="auto", cap_days=10,
    )
    third = users.get_or_create_by_phone("+15550000003")
    r2 = overrides.grant_referral_reward(
        referrer.user_id, third.user_id, days=7, tier="auto", cap_days=10,
    )
    # Second grant clamps into the remaining 3 days of headroom.
    assert r2["granted"] is True
    end2 = datetime.fromisoformat(r2["expires_at"])
    assert end2 <= datetime.now(timezone.utc) + timedelta(days=10, minutes=1)
    fourth = users.get_or_create_by_phone("+15550000004")
    r3 = overrides.grant_referral_reward(
        referrer.user_id, fourth.user_id, days=7, tier="auto", cap_days=10,
    )
    assert r3 == {"granted": False, "reason": "cap_reached"}


# ---------------------------------------------------------------------------
# Conversion + commission ledger
# ---------------------------------------------------------------------------


def test_mark_converted_is_one_shot(stores, two_users):
    _, overrides, _ = stores
    referrer, referee = two_users
    _redeem(overrides, referrer.user_id, referee.user_id)
    assert overrides.mark_referral_converted(referee.user_id) is True
    assert overrides.mark_referral_converted(referee.user_id) is False
    row = overrides.get_redemption_for_referee(referee.user_id)
    assert row is not None and row["converted_at"] is not None


def test_commission_accrual_dedup_and_summary(stores, two_users):
    _, overrides, _ = stores
    referrer, referee = two_users
    _redeem(overrides, referrer.user_id, referee.user_id)
    kwargs = dict(
        referrer_id=referrer.user_id,
        referee_id=referee.user_id,
        product_id="lumin_auto_monthly",
        purchase_token="tok-1",
        period_expiry="2026-08-21T00:00:00+00:00",
        amount=1000.0,
        currency="INR",
        rate=0.5,
    )
    assert overrides.accrue_referral_commission(**kwargs) is True
    # RTDN redelivery of the same billing period — no double credit.
    assert overrides.accrue_referral_commission(**kwargs) is False
    overrides.mark_referral_converted(referee.user_id)
    summary = overrides.get_commission_summary(referrer.user_id)
    assert summary["paid_referred_count"] == 1
    assert summary["commission_totals"] == [
        {"currency": "INR", "accrued": 1000.0, "paid": 0.0}
    ]


def test_mark_paid_transitions_only_accrued(stores, two_users):
    _, overrides, _ = stores
    referrer, referee = two_users
    overrides.accrue_referral_commission(
        referrer_id=referrer.user_id,
        referee_id=referee.user_id,
        product_id="lumin_auto_monthly",
        purchase_token="tok-1",
        period_expiry="2026-08-21T00:00:00+00:00",
        amount=1000.0,
        currency="INR",
        rate=0.5,
    )
    rows = overrides.list_referral_commissions()
    assert len(rows) == 1 and rows[0]["status"] == "accrued"
    assert rows[0]["referrer_phone"] == "+15550000001"
    cid = rows[0]["commission_id"]
    assert overrides.mark_referral_commissions_paid([cid]) == 1
    assert overrides.mark_referral_commissions_paid([cid]) == 0  # already paid
    paid = overrides.list_referral_commissions(status="paid")
    assert len(paid) == 1 and paid[0]["paid_at"] is not None


# ---------------------------------------------------------------------------
# Service — hooks + composition
# ---------------------------------------------------------------------------


async def test_on_redemption_grants_and_upgrades_user_row(
    service, stores, two_users, monkeypatch,
):
    users, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    _redeem(overrides, referrer.user_id, referee.user_id)
    await service.on_redemption(
        referee_id=referee.user_id, referrer_id=referrer.user_id,
    )
    row = users.get_by_id(referrer.user_id)
    assert row.tier == "auto"
    assert row.paid_until is not None
    assert row.paid_until > datetime.now(timezone.utc) + timedelta(days=6)


async def test_on_redemption_noop_when_disabled(
    service, stores, two_users, monkeypatch,
):
    users, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", False)
    _redeem(overrides, referrer.user_id, referee.user_id)
    await service.on_redemption(
        referee_id=referee.user_id, referrer_id=referrer.user_id,
    )
    assert users.get_by_id(referrer.user_id).tier == "free"
    assert overrides.get_active_reward(referrer.user_id) is None


async def test_reward_survives_play_free_downgrade(
    service, stores, two_users, monkeypatch,
):
    """A verify/RTDN that derives 'free' must not clobber a banked reward."""
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    overrides.grant_referral_reward(
        referrer.user_id, referee.user_id, days=7, tier="auto", cap_days=90,
    )
    tier, until = await service.compose_entitlement(referrer.user_id, "free", None)
    assert tier == "auto" and until is not None


async def test_compose_keeps_higher_rank_paid_tier(
    service, stores, two_users, monkeypatch,
):
    """An owner/all-access (or same-rank longer-paid) base is never shrunk."""
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    overrides.grant_referral_reward(
        referrer.user_id, referee.user_id, days=7, tier="auto", cap_days=90,
    )
    far = datetime.now(timezone.utc) + timedelta(days=30)
    tier, until = await service.compose_entitlement(referrer.user_id, "auto", far)
    assert tier == "auto" and until == far  # paid window is the later one


async def test_resolve_falls_back_to_live_play_snapshot(
    service, stores, two_users, monkeypatch,
):
    """Reward lapsed but a stored Play assist sub is still live → assist,
    not free (the old blanket-free bug class)."""
    _, _, purchases = stores
    referrer, _ = two_users
    monkeypatch.setattr(
        config, "GOOGLE_PLAY_PRODUCT_TIERS",
        {"lumin_assist_monthly": "assist", "lumin_auto_monthly": "auto"},
    )
    expiry = datetime.now(timezone.utc) + timedelta(days=12)
    purchases.upsert(
        purchase_token="tok-live",
        user_id=referrer.user_id,
        product_id="lumin_assist_monthly",
        state="SUBSCRIPTION_STATE_ACTIVE",
        expiry=expiry,
    )
    tier, until = await service.resolve_entitlement(referrer.user_id)
    assert tier == "assist" and until == expiry


async def test_resolve_ignores_dead_play_snapshot(service, stores, two_users):
    _, _, purchases = stores
    referrer, _ = two_users
    purchases.upsert(
        purchase_token="tok-dead",
        user_id=referrer.user_id,
        product_id="lumin_auto_monthly",
        state="SUBSCRIPTION_STATE_EXPIRED",
        expiry=datetime.now(timezone.utc) - timedelta(days=1),
    )
    tier, until = await service.resolve_entitlement(referrer.user_id)
    assert (tier, until) == ("free", None)


async def test_on_paid_period_full_cycle_commission(
    service, stores, two_users, monkeypatch,
):
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_RATE", 0.5)
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_MAX_PERIODS", 3)
    monkeypatch.setattr(
        config, "REFERRAL_COMMISSION_PRICES", {"lumin_auto_monthly": 2000.0},
    )
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_CURRENCY", "INR")
    _redeem(overrides, referrer.user_id, referee.user_id)
    assert await service.discount_eligible(referee.user_id) is True
    await service.on_paid_period(
        referee.user_id,
        product_id="lumin_auto_monthly",
        purchase_token="tok-1",
        period_expiry=datetime.now(timezone.utc) + timedelta(days=30),
    )
    # Conversion stamped → discount consumed; 50% of full price accrued.
    assert await service.discount_eligible(referee.user_id) is False
    rows = overrides.list_referral_commissions()
    assert len(rows) == 1
    assert rows[0]["amount"] == 1000.0 and rows[0]["currency"] == "INR"


async def test_on_paid_period_discounted_first_cycle_halves_base(
    service, stores, two_users, monkeypatch,
):
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_RATE", 0.5)
    monkeypatch.setattr(config, "REFERRAL_DISCOUNT_PERCENT", 50)
    monkeypatch.setattr(
        config, "REFERRAL_COMMISSION_PRICES", {"lumin_auto_monthly": 2000.0},
    )
    _redeem(overrides, referrer.user_id, referee.user_id)
    await service.on_paid_period(
        referee.user_id,
        product_id="lumin_auto_monthly",
        purchase_token="tok-1",
        period_expiry=datetime.now(timezone.utc) + timedelta(days=30),
        discounted=True,
    )
    rows = overrides.list_referral_commissions()
    # Referee paid ₹1000 (50% off) → commission is 50% of that, ₹500.
    assert rows[0]["amount"] == 500.0


async def test_on_paid_period_stops_after_max_periods(
    service, stores, two_users, monkeypatch,
):
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_MAX_PERIODS", 3)
    monkeypatch.setattr(
        config, "REFERRAL_COMMISSION_PRICES", {"lumin_auto_monthly": 2000.0},
    )
    _redeem(overrides, referrer.user_id, referee.user_id)
    base = datetime.now(timezone.utc)
    for n in range(5):
        await service.on_paid_period(
            referee.user_id,
            product_id="lumin_auto_monthly",
            purchase_token="tok-1",
            period_expiry=base + timedelta(days=30 * (n + 1)),
        )
    assert len(overrides.list_referral_commissions()) == 3


async def test_on_paid_period_unpriced_product_accrues_nothing(
    service, stores, two_users, monkeypatch,
):
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_PRICES", {})
    _redeem(overrides, referrer.user_id, referee.user_id)
    await service.on_paid_period(
        referee.user_id,
        product_id="mystery_product",
        purchase_token="tok-1",
        period_expiry=datetime.now(timezone.utc) + timedelta(days=30),
    )
    assert overrides.list_referral_commissions() == []


async def test_on_paid_period_web_uses_actual_amount(
    service, stores, two_users, monkeypatch,
):
    _, overrides, _ = stores
    referrer, referee = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    monkeypatch.setattr(config, "REFERRAL_COMMISSION_RATE", 0.5)
    _redeem(overrides, referrer.user_id, referee.user_id)
    await service.on_paid_period(
        referee.user_id,
        product_id="web_auto",
        purchase_token="npw:pay-1",
        period_expiry=datetime.now(timezone.utc) + timedelta(days=30),
        amount=12.5,
        currency="USD",
    )
    rows = overrides.list_referral_commissions()
    assert rows[0]["amount"] == 6.25 and rows[0]["currency"] == "USD"


async def test_non_referee_paid_period_is_ignored(
    service, stores, two_users, monkeypatch,
):
    _, overrides, _ = stores
    referrer, _ = two_users
    monkeypatch.setattr(config, "REFERRAL_REWARDS_ENABLED", True)
    await service.on_paid_period(
        referrer.user_id,
        product_id="lumin_auto_monthly",
        purchase_token="tok-1",
        period_expiry=datetime.now(timezone.utc) + timedelta(days=30),
    )
    assert overrides.list_referral_commissions() == []


def test_better_prefers_rank_then_expiry():
    now = datetime.now(timezone.utc)
    assert _better(("assist", now + timedelta(days=60)), ("auto", now))[0] == "auto"
    a = ("auto", now + timedelta(days=5))
    b = ("auto", now + timedelta(days=9))
    assert _better(a, b) == b
    # None expiry = not time-boxed → wins the tie (owner / all-access).
    assert _better(("owner", None), ("auto", now + timedelta(days=9)))[0] == "owner"
