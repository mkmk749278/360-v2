"""Signup free trial — 7 days of the full product for a new customer.

Owner decision (AskUserQuestion 2026-07-25): *"offer 7 days free trial for
every new customer so that they can understand our services"*, resolved to

* **tier** — ``auto``, the full product.  Signals and levels have always been
  free here; the paywall is on automation, so a trial that unlocks anything
  less does not let a new customer understand what they are being asked to
  buy.
* **no payment method** — granted server-side, not through a Play trial
  offer, so it reaches every phone-verified signup rather than only the ones
  who already reached checkout with a card.
* **opt-in, never automatic** — the app shows a welcome offer and the user
  taps to activate.  A trial that starts silently is a trial the user does
  not know they are burning, and it would put auto-execution behind a
  consent the user never gave.

Dark-first (CLAUDE.md § Project Phase)
──────────────────────────────────────
This is a money-path change: a grant here puts server-side auto-execution on
the real capital of a user who has paid nothing.  So it ships with the two
flags the doctrine requires, and they are *not* the same flag:

* ``SIGNUP_TRIAL_MEASUREMENT_ENABLED`` — **ON** from the deploy.  Every
  eligible user is stamped into the ``user_trials`` funnel with ``shadow=1``,
  so ops → Trials shows the real would-be cohort the same day.  Grants
  nothing, changes no entitlement, invisible to users.
* ``SIGNUP_TRIAL_ENABLED`` — **OFF** until the owner signs off.  This is the
  user-visible effect: :meth:`state_for` stops reporting the offer as
  available and :meth:`claim` refuses.  Flipping it on is the whole decision.

Why the grant reuses the reward ledger
──────────────────────────────────────
Entitlement truth is a single ``(tier, paid_until)`` on the user row, and
Play verify / RTDN / the read-time expiry downgrade all rewrite it wholesale.
A trial written straight onto the user row would be silently erased by the
first RTDN.  So the trial is banked as a row in ``user_reward_grants``
(``source='signup_trial'``) — the same durable ledger referral rewards use —
and :class:`~src.api.referral_rewards.ReferralRewardsService` composes it
into every entitlement write site that already exists.  Nothing new has to
remember the trial; the composition already there picks it up, and dispatch
consumes it the moment the user row is rewritten.

Cost: eligibility is evaluated on profile reads (once per app foreground, not
a hot path) and short-circuited by a bounded in-process set so a returning
user costs zero SQLite reads after the first.  Claim and conversion are
one-shot events.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import config
from src.utils import get_logger

from .auth import effective_tier, tier_rank
from .billing_play import is_entitled_snapshot
from .play_purchases import PlayPurchaseStore
from .referral_rewards import ReferralRewardsService
from .user_overrides import UserOverridesStore
from .users import User, UserStore

log = get_logger("api.signup_trial")


# Reasons a user is not eligible.  Surfaced to the app so the welcome sheet
# can tell "you have already used this" from "the offer is not running".
INELIGIBLE_OFFER_OFF = "offer_not_available"
INELIGIBLE_ALREADY_TRIALLED = "already_trialled"
INELIGIBLE_ALREADY_PAID = "already_subscribed"
INELIGIBLE_ACCOUNT_TOO_OLD = "account_too_old"
INELIGIBLE_NOT_ONBOARDED = "not_onboarded"

# Play subscription states in which money never changed hands.  A snapshot in
# one of these is not paid history — the purchase was attempted and failed or
# was abandoned, so the user is still a new customer for trial purposes.
_NEVER_PAID_STATES = frozenset({
    "SUBSCRIPTION_STATE_PENDING",
    "SUBSCRIPTION_STATE_PENDING_PURCHASE_CANCELED",
    "SUBSCRIPTION_STATE_UNSPECIFIED",
    "",
})

# Bound on the "already stamped this user" short-circuit.  Small because its
# only job is collapsing repeat profile reads inside one process lifetime; a
# miss costs one indexed single-row SELECT, never a wrong answer.
_SEEN_CACHE_MAX = 4096


class SignupTrialService:
    """Eligibility policy, the opt-in claim, and the trial funnel.

    Config is read at call time (``config.SIGNUP_TRIAL_*``) so the owner can
    flip the offer live, retune the window, or change the tier with an env
    change plus restart — and so tests can monkeypatch it.
    """

    def __init__(
        self,
        *,
        user_store: UserStore,
        overrides: UserOverridesStore,
        rewards: ReferralRewardsService,
        play_purchases: Optional[PlayPurchaseStore] = None,
    ) -> None:
        self._users = user_store
        self._overrides = overrides
        self._rewards = rewards
        self._play = play_purchases
        # user_ids already present in the funnel table this process run.
        self._seen: set[int] = set()

    # ------------------------------------------------------------------
    # Flags
    # ------------------------------------------------------------------

    @property
    def offer_live(self) -> bool:
        """The user-visible flag: is the trial actually claimable?"""
        return bool(config.SIGNUP_TRIAL_ENABLED)

    @property
    def measuring(self) -> bool:
        """The measurement flag: are we stamping the eligible cohort?"""
        return bool(config.SIGNUP_TRIAL_MEASUREMENT_ENABLED)

    @property
    def days(self) -> int:
        return int(config.SIGNUP_TRIAL_DAYS)

    @property
    def tier(self) -> str:
        return str(config.SIGNUP_TRIAL_TIER)

    # ------------------------------------------------------------------
    # Eligibility
    # ------------------------------------------------------------------

    async def _has_paid_history(self, user_id: int) -> bool:
        """True when this user has ever held a verified paid subscription.

        A returning subscriber is not a new customer, and a currently-paying
        one has nothing to gain from a trial (the composition would just pick
        whichever window is stronger).  Checked against the stored Play
        snapshots — no Google call.

        A *lapsed* subscriber still counts: an EXPIRED snapshot means they
        once paid, which disqualifies them from a new-customer welcome offer.
        A purchase that never completed does NOT count — a user whose card
        was declined has paid nothing and is still a new customer.
        """
        if self._play is None:
            return False
        for purchase in await self._play.alist_for_user(user_id):
            if purchase.state in _NEVER_PAID_STATES:
                continue
            if purchase.state or is_entitled_snapshot(
                purchase.state, purchase.expiry
            ):
                return True
        return False

    def _account_too_old(self, user: User) -> bool:
        limit = int(config.SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS)
        if limit <= 0:  # 0 = no age limit (every never-paid free user)
            return False
        created = user.created_at
        if created is None:
            return False
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return created < datetime.now(timezone.utc) - timedelta(days=limit)

    async def _ineligible_reason(self, user: User) -> Optional[str]:
        """Why this user cannot be *newly* offered a trial, or None.

        Deliberately ignores both flags — this is the *policy* question, so
        the dark cohort is measured against exactly the rule that will apply
        when the offer goes live.  The flags are applied by the callers.
        """
        if user.needs_onboarding:
            # Mid-signup: they have no profile yet and the welcome sheet has
            # nowhere to land.  They become eligible on the next read.
            return INELIGIBLE_NOT_ONBOARDED
        if tier_rank(effective_tier(user.tier, user.paid_until)) >= tier_rank("assist"):
            return INELIGIBLE_ALREADY_PAID
        if await self._has_paid_history(user.user_id):
            return INELIGIBLE_ALREADY_PAID
        if self._account_too_old(user):
            return INELIGIBLE_ACCOUNT_TOO_OLD
        return None

    async def observe(self, user: User) -> Optional[Dict[str, Any]]:
        """Stamp ``user`` into the trial funnel if newly eligible.

        Called from the profile read — the one path every app session hits,
        including releases that know nothing about trials, which is what
        lets the cohort accumulate during the dark window.  Returns the
        funnel row when one exists (new or pre-existing), else None.

        Fail-open: measurement must never break a profile read, so a ledger
        error is recorded and swallowed (Hard Limits — counted, not silent).
        """
        if not self.measuring:
            return None
        try:
            if user.user_id in self._seen:
                return await self._overrides.aget_trial(user.user_id)
            existing = await self._overrides.aget_trial(user.user_id)
            if existing is not None:
                self._remember(user.user_id)
                return existing
            if await self._ineligible_reason(user) is not None:
                return None
            row = await self._overrides.aobserve_trial_eligibility(
                user.user_id,
                tier=self.tier,
                days=self.days,
                shadow=not self.offer_live,
            )
            self._remember(user.user_id)
            return row
        except Exception as exc:  # ledger hiccup — never break the read
            from src import fail_open
            fail_open.record("signup_trial.observe", exc)
            return None

    def _remember(self, user_id: int) -> None:
        if len(self._seen) >= _SEEN_CACHE_MAX:
            self._seen.clear()
        self._seen.add(user_id)

    # ------------------------------------------------------------------
    # App-facing state
    # ------------------------------------------------------------------

    async def state_for(self, user: User) -> Dict[str, Any]:
        """Everything ``GET /api/trial`` reports for ``user``.

        The app renders this and nothing else — it never decides on its own
        that a trial is available (the engine is the source of truth for
        anything money-adjacent the UI shows).  While the offer is dark,
        ``offer_available`` is False and the app shows no welcome sheet, even
        though the user is sitting in the measured cohort.
        """
        row = await self.observe(user)
        if row is None:
            row = await self._overrides.aget_trial(user.user_id)

        claimed_at = row.get("claimed_at") if row else None
        expires_at = row.get("expires_at") if row else None
        converted_at = row.get("converted_at") if row else None
        active, remaining = self._window(expires_at if claimed_at else None)

        if claimed_at is not None:
            reason: Optional[str] = None if active else INELIGIBLE_ALREADY_TRIALLED
        elif not self.offer_live:
            reason = INELIGIBLE_OFFER_OFF
        elif row is None:
            reason = await self._ineligible_reason(user) or INELIGIBLE_OFFER_OFF
        else:
            reason = None

        offer_available = (
            self.offer_live and row is not None and claimed_at is None
        )
        if offer_available:
            # Stamp the moment the offer is genuinely put in front of them —
            # offered→claimed is how we judge the welcome copy.
            try:
                await self._overrides.amark_trial_offered(user.user_id)
            except Exception as exc:
                from src import fail_open
                fail_open.record("signup_trial.mark_offered", exc)

        return {
            # Offer terms — the app owns the presentation copy, the engine
            # owns the numbers in it.
            "offer_available": offer_available,
            "days": self.days,
            "tier": self.tier,
            # Where this user stands.
            "claimed": claimed_at is not None,
            "active": active,
            "claimed_at": claimed_at,
            "expires_at": expires_at if claimed_at else None,
            "seconds_remaining": remaining,
            "days_remaining": (
                int(-(-remaining // 86400)) if remaining is not None else None
            ),
            "converted": converted_at is not None,
            "ineligible_reason": reason,
        }

    @staticmethod
    def _window(
        expires_at: Optional[str],
    ) -> Tuple[bool, Optional[int]]:
        """``(is_active, seconds_remaining)`` for a claimed trial expiry."""
        if not expires_at:
            return False, None
        try:
            expiry = datetime.fromisoformat(str(expires_at))
        except ValueError:
            return False, None
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        remaining = (expiry - datetime.now(timezone.utc)).total_seconds()
        if remaining <= 0:
            return False, 0
        return True, int(remaining)

    # ------------------------------------------------------------------
    # Claim (the opt-in tap)
    # ------------------------------------------------------------------

    async def claim(self, user: User) -> Dict[str, Any]:
        """Activate the trial for ``user`` — the welcome sheet's CTA.

        Always returns ``{"ok": ..., "reason": ..., **state}`` — the same
        state shape :meth:`state_for` produces, so one round trip both
        activates and refreshes the UI, and a refusal still tells the app
        exactly what to render.  The reason vocabulary is shared with
        ``ineligible_reason`` so the app needs a single mapping.

        Order matters: the ledger claim (which atomically burns the one-shot
        row AND banks the grant) happens first, and only then is the user row
        recomposed.  If the recompose fails the grant is still banked, so the
        next entitlement read repairs it — the opposite order could hand out
        a tier with nothing durable behind it.
        """
        if not self.offer_live:
            return await self._refused(user, INELIGIBLE_OFFER_OFF)

        # Materialise the funnel row if this is the user's first ever touch
        # (a brand-new signup can claim without a prior profile read).
        row = await self._overrides.aget_trial(user.user_id)
        if row is None:
            reason = await self._ineligible_reason(user)
            if reason is not None:
                return await self._refused(user, reason)
            row = await self._overrides.aobserve_trial_eligibility(
                user.user_id, tier=self.tier, days=self.days, shadow=False,
            )
            self._remember(user.user_id)
        elif row.get("claimed_at") is not None:
            return await self._refused(user, INELIGIBLE_ALREADY_TRIALLED)
        else:
            reason = await self._ineligible_reason(user)
            if reason is not None:
                return await self._refused(user, reason)

        result = await self._overrides.aclaim_trial(
            user.user_id, tier=self.tier, days=self.days,
        )
        if not result.get("claimed"):
            reason = str(result.get("reason") or INELIGIBLE_OFFER_OFF)
            if reason == "already_claimed":
                reason = INELIGIBLE_ALREADY_TRIALLED
            return await self._refused(user, reason)

        await self.apply_to_user_row(user.user_id)
        log.info(
            "signup trial activated: user_id={} tier={} days={} until={}",
            user.user_id, self.tier, self.days, result.get("expires_at"),
        )
        fresh = await self._users.aget_by_id(user.user_id)
        state = await self.state_for(fresh or user)
        return {"ok": True, "reason": None, **state}

    async def _refused(self, user: User, reason: str) -> Dict[str, Any]:
        """A refusal carrying the caller's current state, so the app can
        re-render from one response instead of following up with a read."""
        return {"ok": False, "reason": reason, **(await self.state_for(user))}

    async def apply_to_user_row(self, user_id: int) -> None:
        """Recompose + persist the user row so the freshly-banked trial
        becomes live entitlement.

        Goes through the existing composition rather than writing the tier
        directly: a user who somehow holds a stronger window (a stacked
        referral reward, a subscription bought seconds earlier) must keep it
        — :func:`referral_rewards._better` picks the survivor, so this can
        only ever improve the row.
        """
        user = await self._users.aget_by_id(user_id)
        if user is None:
            return
        current = effective_tier(user.tier, user.paid_until)
        current_until = user.paid_until if tier_rank(current) > 0 else None
        tier, until = await self._rewards.compose_entitlement(
            user_id, current, current_until,
        )
        if tier == (user.tier or "free") and until == user.paid_until:
            return
        await self._users.aset_tier(user_id, tier=tier, paid_until=until)
        log.info(
            "trial entitlement written: user_id={} tier={} until={}",
            user_id, tier, until.isoformat() if until else None,
        )

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    async def on_paid_period(self, user_id: int) -> None:
        """A verified paid period landed for ``user_id`` (any channel) —
        stamp the trial→paid conversion if they trialled.

        Runs regardless of both flags: once a trial has been claimed, its
        outcome is data we must not lose because someone later switched the
        offer off.  Fail-open — never block an entitlement write for a
        funnel stamp.
        """
        try:
            await self._overrides.amark_trial_converted(user_id)
        except Exception as exc:
            from src import fail_open
            fail_open.record("signup_trial.on_paid_period", exc)

    # ------------------------------------------------------------------
    # Ops
    # ------------------------------------------------------------------

    async def funnel(self, *, limit: int = 200) -> Dict[str, Any]:
        """The ops → Trials payload: flag state, funnel counters, rows.

        Flags travel with the numbers on purpose — a cohort of 400 means
        something completely different depending on whether those users were
        ever actually offered anything.
        """
        summary = await self._overrides.atrial_funnel_summary()
        rows = await self._overrides.alist_trials(limit=limit)
        return {
            "offer_live": self.offer_live,
            "measuring": self.measuring,
            "days": self.days,
            "tier": self.tier,
            "max_account_age_days": int(
                config.SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS
            ),
            "summary": summary,
            "trials": rows,
        }
