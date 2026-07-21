"""Referral rewards (Phase 2, owner-approved 2026-07-21) — the incentive
layer on top of Phase 1's invite tracking.

The deal (owner decisions, AskUserQuestion 2026-07-21)
──────────────────────────────────────────────────────
* Referrer: ``REFERRAL_REWARD_DAYS`` (7) of free ``REFERRAL_REWARD_TIER``
  (Auto) per friend who **joins** with their code — granted on redemption,
  stacking sequentially, capped at ``REFERRAL_REWARD_STACK_CAP_DAYS``.
* Referee: one-time 50%-off first billing cycle on either plan — on Play
  via the developer-determined offer ``REFERRAL_DISCOUNT_OFFER_ID``, on the
  web rail priced server-side at checkout.
* Referrer commission: ``REFERRAL_COMMISSION_RATE`` (50%) of each verified
  paid billing period of a referred user, for that user's first
  ``REFERRAL_COMMISSION_MAX_PERIODS`` (3) periods, counted across channels.
  Accrued to ``referral_commissions``; the owner pays out manually and
  flips rows to ``paid`` from the ops Referrals panel.

Why composition exists
──────────────────────
Entitlement truth is a single ``(tier, paid_until)`` on the user row,
rewritten wholesale by Play verify, RTDN and the read-time expiry
downgrade.  A banked reward must survive those rewrites, so every
entitlement write site routes through this service:

* :meth:`compose_entitlement` — overlay the active reward grant on a
  freshly-derived base (Play verify / RTDN / web-rail grant paths).
* :meth:`resolve_entitlement` — re-derive the base locally from the stored
  ``play_purchases`` snapshots (no Google call) + reward ledger; used where
  the old code wrote a blanket ``free`` (RTDN token-gone revoke, expiry
  downgrade), so e.g. a paying Assist user is not zeroed the moment a
  stacked Auto reward lapses — and vice-versa.

Cost: every method here runs on an event (claim, verify, RTDN, the one-shot
expiry transition) — never on a scanner / tick / order hot path.  All reads
are single-row/short indexed SQLite queries on the local file.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import config
from src.utils import get_logger

from .auth import effective_tier, tier_rank
from .billing_play import is_entitled_snapshot
from .play_purchases import PlayPurchaseStore
from .user_overrides import UserOverridesStore
from .users import UserStore

log = get_logger("api.referral_rewards")

Entitlement = Tuple[str, Optional[datetime]]


def _parse_dt(raw: Any) -> Optional[datetime]:
    if not raw:
        return None
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    try:
        ts = datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def _better(a: Entitlement, b: Entitlement) -> Entitlement:
    """Pick the stronger of two entitlements.

    Higher tier rank wins outright; on equal rank the later expiry wins,
    with ``None`` (not time-boxed — owner / all-access / free) treated as
    unbounded.  ``free`` always carries ``None`` so it only wins against
    nothing.
    """
    rank_a, rank_b = tier_rank(a[0]), tier_rank(b[0])
    if rank_a != rank_b:
        return a if rank_a > rank_b else b
    if a[1] is None:
        return a
    if b[1] is None:
        return b
    return a if a[1] >= b[1] else b


class ReferralRewardsService:
    """Event-driven referral reward/commission orchestration.

    Config is read at call time (``config.REFERRAL_*``) so ops can retune
    rates/days with an env change + restart and tests can monkeypatch.
    """

    def __init__(
        self,
        *,
        user_store: UserStore,
        overrides: UserOverridesStore,
        play_purchases: Optional[PlayPurchaseStore] = None,
    ) -> None:
        self._users = user_store
        self._overrides = overrides
        self._play = play_purchases

    # ------------------------------------------------------------------
    # Flags / eligibility
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return bool(config.REFERRAL_REWARDS_ENABLED)

    async def discount_eligible(self, user_id: int) -> bool:
        """True while the user joined via a code and has never completed a
        verified paid purchase — the one-time 50%-off window."""
        if not self.enabled:
            return False
        redemption = await self._overrides.aget_redemption_for_referee(user_id)
        return redemption is not None and redemption.get("converted_at") is None

    # ------------------------------------------------------------------
    # Event hooks
    # ------------------------------------------------------------------

    async def on_redemption(self, *, referee_id: int, referrer_id: int) -> None:
        """A join with a code just landed → bank the referrer's reward days
        and upgrade their user row if the reward improves it right now."""
        if not self.enabled:
            return
        result = await self._overrides.agrant_referral_reward(
            referrer_id,
            referee_id,
            days=int(config.REFERRAL_REWARD_DAYS),
            tier=str(config.REFERRAL_REWARD_TIER),
            cap_days=int(config.REFERRAL_REWARD_STACK_CAP_DAYS),
        )
        if not result.get("granted"):
            return
        await self._rewrite_user_row(referrer_id)

    async def on_paid_period(
        self,
        user_id: int,
        *,
        product_id: str,
        purchase_token: str,
        period_expiry: Optional[datetime],
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        discounted: bool = False,
    ) -> None:
        """A verified paid billing period landed for ``user_id`` (any
        channel).  If they are a referee: stamp the first conversion and
        accrue the referrer's commission for this period.

        ``amount`` is the ACTUAL amount paid when the channel knows it (web
        rail); ``None`` means "compute from the configured Play prices",
        halved when ``discounted`` (the referee's 50%-off first cycle —
        commission is a share of what was actually paid, never of the list
        price).  Unknown product with no amount → accrue nothing and WARN;
        we never fabricate money numbers.
        """
        if not self.enabled:
            return
        redemption = await self._overrides.aget_redemption_for_referee(user_id)
        if redemption is None:
            return
        first = await self._overrides.amark_referral_converted(user_id)
        if first:
            log.info(
                "referral conversion: referee_id={} referrer_id={} product={}",
                user_id, redemption["referrer_id"], product_id,
            )
        periods = await self._overrides.acount_commission_periods(user_id)
        if periods >= int(config.REFERRAL_COMMISSION_MAX_PERIODS):
            return
        if period_expiry is None:
            # No billing-period identity → no idempotency key.  Skip rather
            # than risk double-crediting on an RTDN redelivery.
            log.warning(
                "referral commission skipped (no period expiry): "
                "referee_id={} product={}", user_id, product_id,
            )
            return
        rate = float(config.REFERRAL_COMMISSION_RATE)
        if amount is None:
            base = config.REFERRAL_COMMISSION_PRICES.get(product_id)
            if base is None:
                log.warning(
                    "referral commission skipped (no configured price): "
                    "referee_id={} product={}", user_id, product_id,
                )
                return
            if discounted:
                base *= 1.0 - float(config.REFERRAL_DISCOUNT_PERCENT) / 100.0
            commission = base * rate
            cur = str(config.REFERRAL_COMMISSION_CURRENCY)
        else:
            commission = float(amount) * rate
            cur = str(currency or config.REFERRAL_COMMISSION_CURRENCY)
        await self._overrides.aaccrue_referral_commission(
            referrer_id=int(redemption["referrer_id"]),
            referee_id=int(user_id),
            product_id=product_id,
            purchase_token=purchase_token,
            period_expiry=period_expiry.astimezone(timezone.utc).isoformat(),
            amount=round(commission, 2),
            currency=cur,
            rate=rate,
        )

    # ------------------------------------------------------------------
    # Entitlement composition
    # ------------------------------------------------------------------

    async def compose_entitlement(
        self,
        user_id: int,
        base_tier: str,
        base_paid_until: Optional[datetime],
    ) -> Entitlement:
        """Overlay the user's active reward grant on a freshly-derived
        base entitlement.  Grants banked while the programme was enabled
        are honoured even if it has since been switched off — the flag
        stops NEW rewards, it does not confiscate granted time."""
        reward = await self._overrides.aget_active_reward(user_id)
        base: Entitlement = ((base_tier or "free").lower(), base_paid_until)
        if reward is None:
            return base
        return _better(base, (str(reward["tier"]), _parse_dt(reward["expires_at"])))

    async def resolve_entitlement(self, user_id: int) -> Entitlement:
        """Re-derive entitlement from local ledgers only (no Google call):
        the best still-entitled stored Play snapshot + the reward ledger.
        Used where a blanket ``free`` used to be written."""
        base: Entitlement = ("free", None)
        if self._play is not None:
            tiers = config.GOOGLE_PLAY_PRODUCT_TIERS
            for purchase in await self._play.alist_for_user(user_id):
                if not is_entitled_snapshot(purchase.state, purchase.expiry):
                    continue
                tier = tiers.get(purchase.product_id, "auto") if tiers else "auto"
                base = _better(base, (tier, purchase.expiry))
        return await self.compose_entitlement(user_id, base[0], base[1])

    async def _rewrite_user_row(self, user_id: int) -> None:
        """Recompute + persist a user's row after a reward grant, keeping
        the row the single entitlement truth every consumer already reads.
        Never downgrades: the current effective row is one of the compose
        candidates."""
        user = await self._users.aget_by_id(user_id)
        if user is None:
            return
        current = effective_tier(user.tier, user.paid_until)
        current_until = user.paid_until if tier_rank(current) > 0 else None
        tier, until = await self.compose_entitlement(user_id, current, current_until)
        if tier == (user.tier or "free") and until == user.paid_until:
            return
        await self._users.aset_tier(user_id, tier=tier, paid_until=until)
        log.info(
            "referral reward applied to user row: user_id={} tier={} until={}",
            user_id, tier, until.isoformat() if until else None,
        )

    # ------------------------------------------------------------------
    # Invite-screen stats
    # ------------------------------------------------------------------

    async def stats_extras(self, user_id: int) -> Dict[str, Any]:
        """Everything ``GET /api/referral/me`` reports beyond Phase 1 —
        assembled here so the endpoint stays a thin composition."""
        if not self.enabled:
            return {"rewards_enabled": False}
        reward = await self._overrides.aget_reward_summary(user_id)
        commission = await self._overrides.aget_commission_summary(user_id)
        return {
            "rewards_enabled": True,
            "reward_days_per_invite": int(config.REFERRAL_REWARD_DAYS),
            "reward_tier": str(config.REFERRAL_REWARD_TIER),
            **reward,
            **commission,
            "commission_rate": float(config.REFERRAL_COMMISSION_RATE),
            "commission_max_periods": int(config.REFERRAL_COMMISSION_MAX_PERIODS),
            "discount_eligible": await self.discount_eligible(user_id),
            "discount_offer_id": str(config.REFERRAL_DISCOUNT_OFFER_ID),
            "discount_percent": int(config.REFERRAL_DISCOUNT_PERCENT),
        }
