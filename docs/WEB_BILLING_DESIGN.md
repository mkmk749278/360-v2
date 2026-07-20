# Web Billing (Phase 3) — Design for Owner Sign-off

*Status: **PROPOSAL — owner sign-off required before implementation.** Money-path,
dark-flag-first. Nothing in this doc ships live until the owner signs off on the
design and then, separately, on activation of each rail after a sandbox verification.*

*Author: CTE · Date: 2026-07-20 · Companion: `docs/PLAY_BILLING_ACTIVATION.md`
(the Play equivalent this mirrors), `WEB_PWA_CHANNEL.md` (lumin-app).*

---

## 1. Goal

The web PWA (`app.luminapp.org`) is live and free (signals, levels, charts,
sign-in). It cannot currently **sell** the two paid tiers because Google Play
Billing is an Android-only, app-store-bound rail. Phase 3 gives the web channel
its own payment rails so a web user can buy `assist` / `auto` and get the exact
same entitlement an Android buyer gets.

Owner direction (2026-07-20): **route by region and offer multiple rails** —
Razorpay for India, Stripe for the rest of the world, a crypto-transfer path,
and manual (owner-granted) subscriptions as the fallback.

### 1.1 Launch reality — solo operator, no business entity (decided 2026-07-20)

The owner is solo with **no registered business**. That reorders — but does not
change — the plan:

- **Razorpay & Stripe both require merchant KYC.** Razorpay is achievable as a
  **sole proprietorship** (personal PAN + bank account, no company registration),
  but still needs KYC + activation, and — the real risk — a **business-category
  review** that may flag a crypto-trading-signals app (both providers restrict
  trading-advice / crypto-adjacent businesses). Stripe India is harder still for a
  solo individual (typically wants a registered business). Neither is a "sign up
  today and charge tonight" path.
- **Crypto (NOWPayments) and manual have near-zero onboarding** — email + a wallet
  for the former, nothing for the latter — and no business entity required.

**Therefore the launch rails are CRYPTO (NOWPayments) + MANUAL. Razorpay and
Stripe stay designed-and-dark, activated later if/when the owner registers a
proprietorship and clears each provider's category review.** The architecture is
unchanged (all rails converge on `aset_tier`); only the **activation order** flips.
See §10.

### 1.2 No app-store billing tax or rules on the web channel

The PWA is a **website**, not an App Store / Play Store product, so neither Apple's
IAP mandate nor Google Play's Billing policy governs payments made on it — any
processor is allowed and there is no store cut. **The one compliance guardrail:**
Google Play forbids the *Play-distributed Android app* from steering users to
outside payment, so web/crypto billing **must never appear inside the Play build.**
This is already guaranteed structurally — billing is split at **compile time**
(`LUMIN_DISTRIBUTION`): the `play` build keeps Google Play Billing, the `web` build
gets these rails, and `web_billing_service.dart` is web-only (conditional import).
The Play app never sees the web rails. Compliant by construction, not by policy.

## 2. The one invariant that governs everything

**The engine is the single source of truth for entitlement, and there is exactly
one write path: `UserStore.aset_tier(user_id, tier, paid_until)`.**

Today three callers already write through it:

| Caller | File | Trigger |
|---|---|---|
| Play Billing verify | `src/api/billing_play.py` | app sends `purchaseToken`, engine verifies against Google |
| Internal billing grant (HMAC) | `src/api/server.py` `/internal/billing/grant` | trusted backend caller reports a paid user |
| Admin manual grant (owner) | `src/api/admin_grant_route.py` `/api/admin/grant-tier` | owner comps a user from Ops |

**Every new web rail funnels into this same path. No rail invents a parallel
entitlement store, a second "is the user paid?" flag, or its own tier math.** A
rail's only job is: *prove a payment happened, map it to `assist`/`auto` + an
expiry, and call the one write path.* This is the anti-scaffold rule applied to
billing — storage, grant, and the money-path consumption (`AUTO_TRADE_TIER_GATE`
in `signal_dispatch`) already exist and already consume the tier; we are only
adding new *provers*.

The tiers are fixed and shared with Play (no new tiers for web):

| Tier | Grants | Play price (reference) |
|---|---|---|
| `free` | signals, levels, charts, alerts | ₹0 |
| `assist` | + one-tap live take (`/api/manual-trade/take`, `/api/auto-trade/take`) | ₹1000/mo |
| `auto` | + hands-off server-side auto-execution | ₹2000/mo |

## 3. Architecture — rails converge on a shared verifier seam

```
                          app.luminapp.org (web PWA)
                                    │
                    GET /api/billing/web/config   ← region + enabled rails
                                    │
        ┌───────────────┬──────────┴───────────┬──────────────────┐
        ▼               ▼                       ▼                  ▼
   Razorpay (IN)    Stripe (RoW)          Crypto transfer     Manual (owner)
   Checkout/Sub     Checkout Session      (processor or        Ops → admin
        │               │                  on-chain watch)     grant-tier
        │ webhook        │ webhook               │ webhook/         │ (exists
        ▼               ▼                       ▼  confirm         ▼  already)
   ┌──────────────────────────────────────────────────────────────────┐
   │  WebBillingVerifier  (new: src/api/billing_web.py)                 │
   │  - verify provider signature / on-chain confirmation               │
   │  - idempotency: dedup on provider event id                         │
   │  - map product/plan → tier + paid_until                            │
   └───────────────────────────────┬──────────────────────────────────┘
                                    ▼
                     UserStore.aset_tier(user_id, tier, paid_until)
                                    ▼
        signal_dispatch tier gate · manual-take gate  (already consume tier)
```

Two engine entry points (both new, both in `src/api/billing_web.py`):

- **`POST /api/billing/web/checkout`** (authed, user JWT) — client asks the engine
  to *create* a checkout for a chosen tier+rail. Engine creates the provider-side
  order/session/subscription (server-side, secret keys never touch the client) and
  returns the handoff (Razorpay `order_id`+key_id, Stripe `checkout_url`, crypto
  address+amount). **The client never holds a provider secret; the engine never
  trusts a client-asserted price** — amount/tier come from engine config, not the
  request body.
- **Provider webhooks** (unauthed HTTP, signature-verified) — the async truth:
  `POST /api/billing/web/razorpay/webhook`, `/stripe/webhook`, `/crypto/webhook`.
  Each verifies the provider's signature, dedupes on event id, maps to tier, and
  writes `aset_tier`. **Webhooks are authoritative; the client "success" callback
  is UX only** (same doctrine as Play: the client can only *claim*, the server
  *proves*). This closes the tampered-client hole — a user cannot self-upgrade by
  faking a success redirect.

### 3.1 Region routing

`GET /api/billing/web/config` (public, pre-auth-capable like `/api/region`) uses
the existing `CF-IPCountry` detection to return which rails to surface:

At launch (crypto + manual only, cards dark), the response is the same everywhere:

```json
{
  "country_code": "IN",
  "rails": [
    {"id": "crypto", "currency": "USDT",
     "tiers": {"assist": {"amount": "15", "display": "$15/mo"},
               "auto":   {"amount": "25", "display": "$25/mo"}}},
    {"id": "manual", "contact": "..."}
  ]
}
```

When the card rails later activate, the region router adds `razorpay` (for `IN`, INR)
or `stripe` (rest, local currency) as the region-appropriate primary alongside crypto.

- **Launch:** crypto (USDT, **$15 assist / $25 auto, monthly**) offered
  **everywhere** — no jurisdiction exclusions (owner decision 2026-07-20). Manual is
  always available as "contact us"; the *grant* is owner-only.
- **Later:** `IN` → Razorpay primary; rest → Stripe primary; crypto stays offered
  alongside.
- Amounts come from engine config — the client renders what the engine says, never
  the reverse (card amounts in the provider's minor unit; crypto as a USDT string).
- Region is a **UX router, not a security control** (mirrors `region_routes.py`'s
  own caveat) — the webhook verifier is what actually protects entitlement.

## 4. Per-rail design

### 4.1 Razorpay (India)

- **Model:** Razorpay **Subscriptions** (recurring) so RBI e-mandate/auto-renew is
  handled by Razorpay, not us. Engine creates a subscription against a Razorpay
  Plan (`plan_id` per tier, in config). Client opens Razorpay Checkout with the
  returned `subscription_id`.
- **Truth:** webhook events `subscription.activated`, `subscription.charged`
  (renewal), `subscription.halted`/`cancelled`/`completed`. Signature: HMAC-SHA256
  of the raw body with the Razorpay **webhook secret** (`X-Razorpay-Signature`
  header). On `charged`/`activated` → `aset_tier(tier, paid_until = current_end)`.
  On halt/cancel/expire → downgrade to `free` at period end (mirror the Play RTDN
  downgrade logic in `server.py`).
- **RBI note:** recurring card mandates in India cap and pre-notify; Razorpay
  Subscriptions manages this. This is the main reason Razorpay > Stripe for the IN
  recurring case.

### 4.2 Stripe (rest of world)

- **Model:** Stripe **Checkout Session** in `subscription` mode against a Stripe
  Price per tier (`price_id` in config). Engine creates the session server-side,
  returns `checkout_url`; client redirects.
- **Truth:** webhook `checkout.session.completed` (first purchase) + `invoice.paid`
  (renewals) + `customer.subscription.deleted` (cancel). Signature: Stripe
  `Stripe-Signature` header verified with the endpoint signing secret (timestamped
  HMAC, replay-guarded). Same map → `aset_tier`.

### 4.3 Crypto transfer — NOWPayments (LAUNCH RAIL, decided 2026-07-20)

**Processor: NOWPayments.** Chosen over Coinbase Commerce and over a self-watched
address for two reasons: (1) **light onboarding** — email + a receiving wallet, no
business KYC, which a solo operator can actually complete; (2) it has an actual
**Subscriptions / recurring-billing product**, which Coinbase Commerce lacks
(Commerce is one-time charges only, forcing us to hand-roll the schedule).

**On "can it automatically manage subscriptions?" — the honest limit:** *no crypto
rail can silently auto-charge*, because there is **no on-chain pull/mandate**
primitive (nothing equivalent to a card mandate or UPI-autopay — funds cannot be
debited from a user's wallet on a schedule). What NOWPayments Subscriptions *does*
manage for us: it auto-generates a recurring **invoice each billing cycle, emails
the customer a payment link, tracks paid/unpaid, and fires a webhook** on payment.
So the lifecycle (schedule, invoicing, reminders, status) is managed; the customer
still actively **one-tap pays each cycle** from the emailed link. That is as close
to "managed recurring" as crypto allows, and it's why NOWPayments beats Commerce
here.

**Flow:** engine creates a NOWPayments subscription/invoice for the chosen tier
(server-side, API key never on the client) → user pays via the hosted NOWPayments
checkout → NOWPayments webhook (`payment.finished`/`confirmed`) → engine **verifies
the webhook signature** (HMAC over the raw body with the IPN secret) → `aset_tier(
tier, paid_until = now + billing_period)`. On a missed renewal the invoice simply
isn't paid, `paid_until` lapses, and the existing expiry reaper downgrades to
`free` — no on-chain action needed from us.

**UX:** the paywall/renewal card states the paid-through date and "we'll email you
a renewal link before {date}" — never implies a silent auto-charge.

*(Deferred, not chosen: a self-watched unique-address model — engine polls a chain
API for N confirmations. Rejected for v1: custody/reorg edge cases and an uncached
polling loop to cost-review. NOWPayments' signed webhook avoids both.)*

### 4.4 Manual subscription (owner)

**Already built** — `POST /api/admin/grant-tier` (`admin_grant_route.py`), owner-
gated, audited, writes `aset_tier` with a `duration_days` expiry. Phase 3 adds
*nothing* to the engine here beyond surfacing it in the web paywall as a "pay by
bank transfer / contact us" option whose fulfilment is the owner running the
existing Ops grant. Listed for completeness; it needs no new money-path code.

## 5. App side (lumin-app, web channel)

- **`lib/data/web_billing_service.dart`** — mirror of `play_billing_service.dart`,
  web-only (conditional import; Play channel keeps Play Billing untouched). Calls
  `/api/billing/web/config` → renders rails → on rail selection calls
  `/api/billing/web/checkout` → launches provider handoff (Razorpay Checkout JS /
  Stripe redirect / crypto address view) → on return, **polls the engine for
  entitlement** (`GET` current tier) rather than trusting the client callback, and
  calls `auth.applyEntitlement(tier, paidUntil)` once the webhook has landed.
- **Paywall/Upgrade page** — one page, region-adaptive, behind the existing tier
  gating UX. Renders "Signals are free · Upgrade for live/auto trading" with the
  rail(s) the config returns. No provider keys in the bundle (publishable/checkout
  keys only, which are safe by design; secret keys are engine-only).
- Repository seam: new methods on `LuminRepository` (both `MockRepository` and
  `HttpRepository`) — pages never do HTTP directly (repo convention).

## 6. Dark-first rollout & flags

Billing doesn't emit or score signals, so "dark-first" here means **default-OFF +
sandbox-verified + owner activation per rail**, not a shadow signal window:

| Flag | Default | Meaning |
|---|---|---|
| `WEB_BILLING_ENABLED` | **false** | master off-switch; all web billing endpoints 503 when false |
| `WEB_BILLING_CRYPTO_ENABLED` | false | crypto rail (NOWPayments) — **launch rail** |
| `WEB_BILLING_RAZORPAY_ENABLED` | false | India cards — later phase (needs merchant entity) |
| `WEB_BILLING_STRIPE_ENABLED` | false | RoW cards — later phase (needs merchant entity) |
| `WEB_BILLING_TEST_MODE` | true | use provider **sandbox/test keys**; must be flipped to false with live keys only after owner sign-off |

(Manual grant has no flag — it's the always-available owner-only `admin_grant_tier`
path, gated by owner auth, not a billing flag.)

Ops Control plane gets per-rail toggles (mirrors the existing
`play_billing_enabled` control), so activation is an owner action from
`ops.luminapp.org`, not a redeploy. Rails activate one at a time, each after a
sandbox end-to-end purchase is verified.

## 7. Security & correctness

- **Webhook signature verification is mandatory** on every rail; an unverified or
  replayed webhook is rejected and logged (never grants). Timestamp/replay window
  enforced where the provider supports it (Stripe, crypto processors).
- **Idempotency:** dedupe on provider event id (a `billing_events` table or Redis
  set) so a redelivered webhook doesn't double-write or double-count. `aset_tier`
  is idempotent on `(tier, paid_until)` anyway, but we still record processed ids.
- **No client-asserted amounts or tiers trusted** — tier→price is engine config;
  the checkout request only names a *tier id*, the engine sets the money.
- **Secrets** (Razorpay key-secret + webhook secret, Stripe secret + signing
  secret, crypto processor key) live in engine env only, never in the APK/web
  bundle, never logged, never in errors (Hard Limits, mirrors the Binance-secret
  discipline).
- **Entitlement expiry** reuses the existing defensive `paid_until` enforcement in
  `server.py` (Play users already get downgraded to `free` at expiry) — web grants
  ride the same reaper; no new expiry code path.

## 8. Cost

Webhooks and checkout creation are **per-purchase, low-frequency** — not a hot
path, no per-tick/scan/order reads. NOWPayments' signed webhook means no chain
polling loop (the reason the self-watched-address model was rejected, §4.3).
Idempotency store is a tiny table / short-TTL Redis set. No Cost-Discipline
hot-path concern.

## 9. Legal / compliance follow-ons (tracked, not blocking the design)

- `mkmk749278/lumin-legal`: `terms.md` currently states Google Play Billing as the
  billing model (corrected when B16 shipped). Web rails require a terms update to
  describe crypto (NOWPayments) billing, the manual-renewal model, refunds, and
  cancellation — **owner-sign-off legal change**, shipped alongside activation, not
  before. (Card-rail terms follow when Razorpay/Stripe activate.)
- **Launch-rail onboarding (owner task, light):** a NOWPayments account (email +
  receiving wallet, no business KYC) and the IPN/webhook secret. Manual needs
  nothing new.
- **Card-rail onboarding (owner task, later, heavier):** Razorpay (sole-prop KYC:
  personal PAN + bank) and/or Stripe accounts, plan/price objects, and — the real
  go/no-go — **confirming each provider permits our business category** (both
  restrict trading-advice / crypto-adjacent businesses; we present as a
  **signals/education subscription**, not an exchange). Until an entity exists and
  the category clears, these rails stay dark.

## 10. Proposed delivery order (after sign-off)

Each step is its own PR, engine + app paired where needed, each dark. **Order
reflects the solo-launch reality (§1.1): crypto + manual first, cards later.**

1. **Seam + config** — `billing_web.py` with the `WebBillingVerifier` interface,
   `/api/billing/web/config` (region + enabled rails), `/api/billing/web/checkout`,
   the flags, and the idempotency store, unit-tested with fake provider payloads.
   No live provider yet; all rails disabled → config returns manual-only. Ships
   behind master OFF.
2. **Crypto rail (NOWPayments) — LAUNCH** — checkout/subscription create + IPN
   webhook + signature verification tests, sandbox keys.
3. **App paywall + `web_billing_service.dart`** — region-adaptive UI, crypto +
   manual rails, entitlement poll-after-return. This is the point web users can
   actually pay.
4. **Legal + activation (launch rails)** — terms update for crypto/manual, live
   NOWPayments keys, owner activation from Ops after a sandbox purchase verifies.
5. **Razorpay rail (later, entity-gated)** — checkout + webhook + signature tests,
   sandbox keys. Activates only once the owner has a Razorpay merchant account and
   the category is cleared.
6. **Stripe rail (later, entity-gated)** — same shape.

Steps 1–4 are the shippable launch. 5–6 wait on merchant onboarding and don't
block anything.

## 11. Decisions — resolved 2026-07-20 + remaining

**Resolved with the owner:**
1. ~~Crypto processor?~~ → **NOWPayments** (light onboarding + real Subscriptions
   product; Coinbase Commerce lacks recurring). Self-watched address rejected.
2. ~~Recurring model?~~ → **NOWPayments managed recurring invoices** (auto-invoice +
   email each cycle, one-tap pay; no silent auto-debit possible on crypto). Cards,
   when they land, use provider auto-renew. Confirmed.
3. ~~Launch rails?~~ → **Crypto + manual first; Razorpay/Stripe dark until a
   merchant entity exists and category clears** (§1.1).

**Resolved 2026-07-20 (owner):**
- **A. Pricing:** crypto billed in **USDT — $15 (assist) / $25 (auto) per month.**
  (Independent of the Play ₹1000/₹2000; the web/crypto price is its own number.)
- **B. Crypto region scope:** **everywhere** — no jurisdiction exclusions. It's a
  website, not an app-store product; region stays UX-only.
- **C. Billing period:** **monthly.**

All Phase-3 launch decisions are now closed. No open owner questions remain for the
crypto + manual launch; card rails (§10 steps 5–6) reopen their own onboarding
questions only if/when the owner pursues a merchant entity.

---

*On sign-off, implementation proceeds in the order of §10, each PR dark and
owner-reviewed. No web billing endpoint serves a live charge until
`WEB_BILLING_TEST_MODE=false` is set per rail after its sandbox verification.*
