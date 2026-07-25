"""Signup free trial (owner-approved 2026-07-25) — 7 days of Auto, opt-in.

What we pin (the promises the feature makes, and the ways it could quietly
break):

* **Dark-first.**  With SIGNUP_TRIAL_ENABLED off, the cohort is still
  measured (``shadow=1``) but no user is ever told an offer exists and no
  claim succeeds.  This is the whole safety property — a regression here
  would ship auto-execution to unpaid users without owner sign-off.
* **Opt-in.**  Nothing grants entitlement without an explicit claim.
* **One-shot.**  A user gets one trial ever; a double-tap never buys a
  second window, and a lapsed trialist is not re-offered.
* **Durability.**  The grant survives a Play-derived downgrade, because it
  lives in the reward ledger the entitlement composition already reads —
  this is what a naive "write tier onto the user row" implementation gets
  wrong.
* **New customers only.**  Anyone with paid history is excluded; a failed
  (never-paid) purchase does NOT exclude them.
* **Funnel truth.**  Rates are null rather than a fake 0% when the
  denominator is empty, and dark cohort rows stay distinguishable forever.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import config
from src.api.play_purchases import PlayPurchaseStore
from src.api.referral_rewards import ReferralRewardsService
from src.api.signup_trial import (
    INELIGIBLE_ALREADY_PAID,
    INELIGIBLE_ALREADY_TRIALLED,
    INELIGIBLE_OFFER_OFF,
    SignupTrialService,
)
from src.api.user_overrides import UserOverridesStore
from src.api.users import UserStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def stores(tmp_path):
    """Real SQLite stores sharing one file, as in production wiring."""
    db = tmp_path / "lumin.sqlite"
    return UserStore(db), UserOverridesStore(db), PlayPurchaseStore(db)


@pytest.fixture
def service(stores):
    users, overrides, purchases = stores
    rewards = ReferralRewardsService(
        user_store=users, overrides=overrides, play_purchases=purchases,
    )
    return SignupTrialService(
        user_store=users,
        overrides=overrides,
        rewards=rewards,
        play_purchases=purchases,
    )


@pytest.fixture
def offer_live(monkeypatch):
    """The owner has signed off — the user-visible flag is on."""
    monkeypatch.setattr(config, "SIGNUP_TRIAL_ENABLED", True)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MEASUREMENT_ENABLED", True)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_DAYS", 7)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_TIER", "auto")
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS", 0)


@pytest.fixture
def offer_dark(monkeypatch):
    """Shipped state: measuring, but invisible to every user."""
    monkeypatch.setattr(config, "SIGNUP_TRIAL_ENABLED", False)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MEASUREMENT_ENABLED", True)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_DAYS", 7)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_TIER", "auto")
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS", 0)


def _new_user(users: UserStore, phone: str = "+15550000010"):
    """A phone-verified, onboarded free user — the trial's target."""
    user = users.get_or_create_by_phone(phone)
    return users.update_profile(
        user.user_id, display_name="Trialist", accept_terms=True,
    )


# ---------------------------------------------------------------------------
# Dark-first: the flag that protects real capital
# ---------------------------------------------------------------------------


async def test_dark_measures_cohort_but_offers_nothing(stores, service, offer_dark):
    users, overrides, _ = stores
    user = _new_user(users)

    state = await service.state_for(user)

    # Measured...
    row = overrides.get_trial(user.user_id)
    assert row is not None
    assert row["shadow"] == 1, "dark-window cohort must be marked shadow"
    assert row["offered_at"] is None, "nobody was offered anything while dark"
    # ...but invisible.
    assert state["offer_available"] is False
    assert state["ineligible_reason"] == INELIGIBLE_OFFER_OFF
    assert state["claimed"] is False


async def test_dark_claim_refuses_and_grants_nothing(stores, service, offer_dark):
    users, overrides, _ = stores
    user = _new_user(users)

    result = await service.claim(user)

    assert result["ok"] is False
    assert result["reason"] == INELIGIBLE_OFFER_OFF
    assert overrides.get_active_reward(user.user_id) is None
    assert users.get_by_id(user.user_id).tier == "free"


async def test_measurement_off_stamps_nothing(stores, service, monkeypatch):
    """The measurement flag is the only thing that silences the cohort."""
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MEASUREMENT_ENABLED", False)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_ENABLED", False)
    users, overrides, _ = stores
    user = _new_user(users)

    await service.state_for(user)

    assert overrides.get_trial(user.user_id) is None


# ---------------------------------------------------------------------------
# Opt-in claim
# ---------------------------------------------------------------------------


async def test_offer_is_never_auto_applied(stores, service, offer_live):
    """Reading the state must not grant anything — the tap does."""
    users, overrides, _ = stores
    user = _new_user(users)

    state = await service.state_for(user)

    assert state["offer_available"] is True
    assert state["days"] == 7
    assert state["tier"] == "auto"
    assert state["claimed"] is False
    assert overrides.get_active_reward(user.user_id) is None
    assert users.get_by_id(user.user_id).tier == "free"


async def test_claim_grants_seven_days_of_auto(stores, service, offer_live):
    users, overrides, _ = stores
    user = _new_user(users)

    result = await service.claim(user)

    assert result["ok"] is True
    assert result["active"] is True
    assert result["days_remaining"] == 7

    # Entitlement is live on the user row — this is what dispatch reads.
    row = users.get_by_id(user.user_id)
    assert row.tier == "auto"
    assert row.paid_until is not None
    delta = row.paid_until - datetime.now(timezone.utc)
    assert timedelta(days=6, hours=23) < delta <= timedelta(days=7)

    # And it is banked durably in the reward ledger, not just on the row.
    reward = overrides.get_active_reward(user.user_id)
    assert reward is not None and reward["tier"] == "auto"


async def test_state_stamps_offered_only_when_live(stores, service, offer_live):
    users, overrides, _ = stores
    user = _new_user(users)

    await service.state_for(user)

    assert overrides.get_trial(user.user_id)["offered_at"] is not None


# ---------------------------------------------------------------------------
# One-shot per user, forever
# ---------------------------------------------------------------------------


async def test_double_tap_never_buys_a_second_window(stores, service, offer_live):
    users, _, _ = stores
    user = _new_user(users)

    first = await service.claim(user)
    second = await service.claim(users.get_by_id(user.user_id))

    assert first["ok"] is True
    assert second["ok"] is False
    assert second["reason"] == INELIGIBLE_ALREADY_TRIALLED
    assert second["expires_at"] == first["expires_at"]


async def test_lapsed_trialist_is_not_re_offered(stores, service, offer_live):
    users, overrides, _ = stores
    user = _new_user(users)
    await service.claim(user)

    # Wind the window into the past, as it will be a week from now.
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    overrides._conn.execute(
        "UPDATE user_trials SET expires_at = ? WHERE user_id = ?",
        (past, user.user_id),
    )
    overrides._conn.execute(
        "UPDATE user_reward_grants SET expires_at = ? WHERE user_id = ?",
        (past, user.user_id),
    )

    state = await service.state_for(users.get_by_id(user.user_id))

    assert state["offer_available"] is False
    assert state["active"] is False
    assert state["claimed"] is True
    assert state["ineligible_reason"] == INELIGIBLE_ALREADY_TRIALLED


# ---------------------------------------------------------------------------
# Durability — the reason the grant lives in the reward ledger
# ---------------------------------------------------------------------------


async def test_trial_survives_a_play_derived_downgrade(stores, service, offer_live):
    """An RTDN revoke re-resolves entitlement from local ledgers; a running
    trial must come back out of that, not be flattened to free."""
    users, overrides, purchases = stores
    rewards = ReferralRewardsService(
        user_store=users, overrides=overrides, play_purchases=purchases,
    )
    user = _new_user(users)
    await service.claim(user)

    tier, paid_until = await rewards.resolve_entitlement(user.user_id)

    assert tier == "auto"
    assert paid_until is not None and paid_until > datetime.now(timezone.utc)


async def test_claim_never_downgrades_a_stronger_existing_window(
    stores, service, offer_live,
):
    """A user who subscribed seconds before tapping keeps the longer window."""
    users, _, _ = stores
    user = _new_user(users)
    far = datetime.now(timezone.utc) + timedelta(days=30)
    users.set_tier(user.user_id, tier="auto", paid_until=far)

    await service.claim(users.get_by_id(user.user_id))

    assert users.get_by_id(user.user_id).paid_until == far


# ---------------------------------------------------------------------------
# New customers only
# ---------------------------------------------------------------------------


async def test_paying_user_is_not_offered_a_trial(stores, service, offer_live):
    users, _, _ = stores
    user = _new_user(users)
    users.set_tier(
        user.user_id,
        tier="auto",
        paid_until=datetime.now(timezone.utc) + timedelta(days=30),
    )

    state = await service.state_for(users.get_by_id(user.user_id))

    assert state["offer_available"] is False
    assert state["ineligible_reason"] == INELIGIBLE_ALREADY_PAID


async def test_lapsed_subscriber_is_not_a_new_customer(stores, service, offer_live):
    users, _, purchases = stores
    user = _new_user(users)
    purchases.upsert(
        purchase_token="tok-expired",
        user_id=user.user_id,
        product_id="lumin_auto_monthly",
        state="SUBSCRIPTION_STATE_EXPIRED",
        expiry=datetime.now(timezone.utc) - timedelta(days=5),
    )

    state = await service.state_for(user)

    assert state["offer_available"] is False
    assert state["ineligible_reason"] == INELIGIBLE_ALREADY_PAID


async def test_failed_purchase_still_counts_as_a_new_customer(
    stores, service, offer_live,
):
    """A declined card is not paid history — they never gave us money."""
    users, _, purchases = stores
    user = _new_user(users)
    purchases.upsert(
        purchase_token="tok-pending",
        user_id=user.user_id,
        product_id="lumin_auto_monthly",
        state="SUBSCRIPTION_STATE_PENDING",
        expiry=None,
    )

    state = await service.state_for(user)

    assert state["offer_available"] is True


async def test_account_age_limit_excludes_older_signups(
    stores, service, offer_live, monkeypatch,
):
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS", 7)
    users, _, _ = stores
    user = _new_user(users)
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    users._conn.execute(
        "UPDATE users SET created_at = ? WHERE user_id = ?", (old, user.user_id),
    )

    state = await service.state_for(users.get_by_id(user.user_id))

    assert state["offer_available"] is False
    assert state["ineligible_reason"] == "account_too_old"


async def test_mid_signup_user_is_deferred_not_burned(stores, service, offer_live):
    """No profile yet → no offer, but they stay eligible for later."""
    users, overrides, _ = stores
    user = users.get_or_create_by_phone("+15550000099")  # never onboarded

    state = await service.state_for(user)

    assert state["offer_available"] is False
    assert state["ineligible_reason"] == "not_onboarded"
    assert overrides.get_trial(user.user_id) is None


# ---------------------------------------------------------------------------
# Funnel / ops surface
# ---------------------------------------------------------------------------


async def test_conversion_is_stamped_on_a_paid_period(stores, service, offer_live):
    users, overrides, _ = stores
    user = _new_user(users)
    await service.claim(user)

    await service.on_paid_period(user.user_id)

    assert overrides.get_trial(user.user_id)["converted_at"] is not None


async def test_conversion_ignores_users_who_never_trialled(stores, service, offer_live):
    users, overrides, _ = stores
    user = _new_user(users)
    await service.state_for(user)  # eligible, but never claimed

    await service.on_paid_period(user.user_id)

    assert overrides.get_trial(user.user_id)["converted_at"] is None


async def test_funnel_reports_flags_beside_the_numbers(stores, service, offer_live):
    users, _, _ = stores
    claimed = _new_user(users, "+15550000021")
    await service.claim(claimed)
    await service.state_for(_new_user(users, "+15550000022"))  # offered only

    funnel = await service.funnel()

    assert funnel["offer_live"] is True
    assert funnel["measuring"] is True
    assert funnel["tier"] == "auto"
    assert funnel["days"] == 7
    assert funnel["summary"]["cohort"] == 2
    assert funnel["summary"]["offered"] == 2
    assert funnel["summary"]["claimed"] == 1
    assert funnel["summary"]["active"] == 1
    assert funnel["summary"]["converted"] == 0
    assert funnel["summary"]["claim_rate"] == pytest.approx(0.5)
    assert len(funnel["trials"]) == 2


async def test_empty_funnel_rates_are_null_not_zero(stores, service, offer_dark):
    """An unmeasured rate rendering as a real 0% would misreport the offer
    as failing when it has simply never run."""
    users, _, _ = stores
    _new_user(users)

    funnel = await service.funnel()

    assert funnel["summary"]["claim_rate"] is None
    assert funnel["summary"]["conversion_rate"] is None


async def test_dark_cohort_stays_distinguishable_after_going_live(
    stores, service, monkeypatch,
):
    """Rows observed while dark keep shadow=1 forever — we never actually
    offered those users anything on the day we counted them."""
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MEASUREMENT_ENABLED", True)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_DAYS", 7)
    monkeypatch.setattr(config, "SIGNUP_TRIAL_TIER", "auto")
    monkeypatch.setattr(config, "SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS", 0)
    users, _, _ = stores

    monkeypatch.setattr(config, "SIGNUP_TRIAL_ENABLED", False)
    dark_user = _new_user(users, "+15550000031")
    await service.state_for(dark_user)

    monkeypatch.setattr(config, "SIGNUP_TRIAL_ENABLED", True)
    live_user = _new_user(users, "+15550000032")
    await service.state_for(live_user)

    summary = (await service.funnel())["summary"]
    assert summary["cohort_dark"] == 1
    assert summary["cohort_live"] == 1
    # The dark user can still claim once the offer goes live — being counted
    # early must not cost them the offer.
    assert (await service.claim(dark_user))["ok"] is True


# ---------------------------------------------------------------------------
# Ledger primitives
# ---------------------------------------------------------------------------


def test_trial_appends_to_a_running_referral_window(stores):
    """Both sources write ``user_reward_grants``.  A trial claimed while a
    referral reward runs must APPEND its full 7 days, not overlap into them
    and not be clamped away — the offer promises 7 days of Auto."""
    users, overrides, _ = stores
    user = _new_user(users)
    friend = users.get_or_create_by_phone("+15550000042")

    overrides.grant_referral_reward(
        user.user_id, friend.user_id, days=7, tier="auto", cap_days=90,
    )
    overrides.observe_trial_eligibility(
        user.user_id, tier="auto", days=7, shadow=False,
    )
    result = overrides.claim_trial(user.user_id, tier="auto", days=7)

    assert result["claimed"] is True
    ends = datetime.fromisoformat(result["expires_at"])
    assert timedelta(days=13, hours=23) < (
        ends - datetime.now(timezone.utc)
    ) <= timedelta(days=14), "trial should start where the referral ends"


def test_a_refused_claim_never_burns_the_users_one_trial(stores):
    """The claim stamp and the grant land together or not at all."""
    users, overrides, _ = stores
    user = _new_user(users)

    result = overrides.claim_trial(user.user_id, tier="auto", days=7)

    assert result["claimed"] is False
    assert result["reason"] == "not_eligible"
    assert overrides.get_trial(user.user_id) is None
    assert overrides.get_active_reward(user.user_id) is None
