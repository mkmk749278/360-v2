# Referral Rewards — Phase 2 (owner-approved 2026-07-21)

The invite screen's Phase 1 (stable code + "N friends joined" counter,
Session 34) gains real incentives. Owner decisions locked 2026-07-21:

| Incentive | What | Trigger |
|---|---|---|
| Referrer reward | **7 days of free Auto** per friend, stacking (cap 90 banked days) | Friend signs up **and redeems the code** (join, not payment) |
| Referee reward | **50% off the first billing cycle**, one time, both plans | First purchase after redeeming a code |
| Referrer commission | **50% of each verified paid billing period** of the referred user, **first 3 periods** (cross-channel) | Each verified paid period (Play verify/RTDN, web IPN) |

Growth over revenue: the owner's explicit stance is that user acquisition
matters more than early margin, which is why the reward triggers on *join*
and the commission is generous but period-capped and env-tunable.

## Architecture

- `src/api/referral_rewards.py` — orchestration: reward grants, commission
  accrual, and **entitlement composition**. The user row's
  `(tier, paid_until)` stays the single entitlement truth, but every write
  site now composes it from Play state ⊕ the reward ledger so a banked
  reward survives Play verify / RTDN / expiry rewrites (and a paying
  subscriber is never zeroed when a stacked reward lapses — the write
  sites re-resolve from the stored `play_purchases` snapshots instead of
  writing a blanket `free`).
- `src/api/user_overrides.py` — the ledgers: `user_reward_grants`
  (sequential stacking, DB-level one-shot per referee),
  `referral_commissions` (idempotent per `(purchase_token,
  period_expiry)`, so RTDN redeliveries never double-credit),
  `user_referral_redemptions.converted_at` (first paid purchase; while
  NULL the referee holds the one-time discount).
- Hooks are **event-driven only**: claim, Play verify, RTDN, web IPN, and
  the one-shot expiry transition. Nothing runs on scanner / tick / order
  hot paths (Cost Discipline).
- Commission is computed on **what the referee actually paid**: the web
  rail passes the confirmed USD amount; Play uses
  `REFERRAL_COMMISSION_PRICES` (keep in lockstep with Play Console
  prices), halved when the purchase used the referral offer
  (`offerDetails.offerId == REFERRAL_DISCOUNT_OFFER_ID`). An unpriced
  product accrues **nothing** (never fabricate money numbers).

## API surface

- `GET /api/referral/me` — Phase 1 fields + rewards/commission/discount
  state (all new fields defaulted; old clients unaffected).
- `POST /api/referral/claim` — unchanged semantics; now banks the
  referrer's reward and returns `discount_eligible` for the referee.
- `GET /api/referral/admin/commissions?status=accrued|paid` and
  `POST /api/referral/admin/commissions/mark-paid` — **owner-gated**
  payout ledger, consumed by the ops Referrals panel. Payouts are manual;
  mark rows paid after settling them.

## Config (env-overridable, `config/__init__.py`)

| Knob | Default | Meaning |
|---|---|---|
| `REFERRAL_REWARDS_ENABLED` | `true` | Kill switch. Off = no NEW grants/accruals/discounts; already-banked time is honoured. |
| `REFERRAL_REWARD_DAYS` | `7` | Days banked per join. |
| `REFERRAL_REWARD_TIER` | `auto` | Tier the reward grants. |
| `REFERRAL_REWARD_STACK_CAP_DAYS` | `90` | Max banked future window. |
| `REFERRAL_COMMISSION_RATE` | `0.5` | Commission fraction. |
| `REFERRAL_COMMISSION_MAX_PERIODS` | `3` | First N periods per referee. |
| `REFERRAL_COMMISSION_PRICES` | `lumin_assist_monthly:1000,lumin_auto_monthly:2000` | Play commission base (INR). |
| `REFERRAL_COMMISSION_CURRENCY` | `INR` | Currency of the above. |
| `REFERRAL_DISCOUNT_OFFER_ID` | `referral50` | Play Console offer id. |
| `REFERRAL_DISCOUNT_PERCENT` | `50` | Display + web-rail discount. |

## OWNER ACTION REQUIRED — Play Console offer

Play cannot be discounted server-side; the referee's 50% off on the Play
channel is a **subscription offer** the owner must create once:

1. Play Console → Monetise → Subscriptions → `lumin_assist_monthly` →
   Base plan → **Add offer**.
2. Offer ID: **`referral50`** (must match `REFERRAL_DISCOUNT_OFFER_ID`).
3. Eligibility: **Developer determined** (the app only surfaces/buys it
   when the engine says the user is discount-eligible).
4. Phases: **Single payment discount, 50% off, 1 billing period**, then
   the base price.
5. Repeat for `lumin_auto_monthly`. Activate both.

Until the offers exist, eligible referees simply see base prices on Play
(the app falls back gracefully); the web rail discount works immediately.

## Payout runbook

1. Ops → Referrals (or `GET /api/referral/admin/commissions?status=accrued`).
2. Pay the referrer manually (UPI/etc. — phone number is in the listing).
3. Select the settled rows → **Mark paid** (audited, PRG-confirmed).

## Anti-abuse posture

- Phone-OTP makes every fake "join" cost a unique working phone number.
- One redemption per account, ever (DB-level PK).
- Reward stacking capped (`REFERRAL_REWARD_STACK_CAP_DAYS`).
- Commission only on **verified** payments (Play Developer API / HMAC IPN),
  period-capped, idempotent per billing period.
- Self-referral rejected; payouts are manual so the owner reviews every
  settlement (terms reserve the right to forfeit abusive accounts —
  lumin-legal `terms.md`).
