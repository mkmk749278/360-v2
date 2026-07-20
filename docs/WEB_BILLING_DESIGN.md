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

```json
{
  "country_code": "IN",
  "currency": "INR",
  "rails": [
    {"id": "razorpay", "tiers": {"assist": {"amount": 100000, "display": "₹1000/mo"},
                                  "auto":   {"amount": 200000, "display": "₹2000/mo"}}},
    {"id": "crypto",  "tiers": {"assist": {"amount_usdt": "12", ...}, ...}},
    {"id": "manual",  "contact": "..."}
  ]
}
```

- India (`IN`) → Razorpay primary. Rest → Stripe primary. Crypto offered in both
  (subject to a per-region enable flag — some jurisdictions we may not want crypto
  in). Manual is always available as "contact us" but the *grant* is owner-only.
- Amounts are in the provider's minor unit (paise/cents) and come from engine
  config — the client renders what the engine says, never the reverse.
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

### 4.3 Crypto transfer

Two candidate implementations — **owner to pick one at sign-off**:

- **(A) Hosted processor (recommended): Coinbase Commerce or NOWPayments.** They
  give us a hosted checkout + a signed webhook on confirmation, so we never watch
  the chain ourselves or hold funds custody logic. Engine verifies the webhook
  signature exactly like the card rails → `aset_tier(paid_until = now + 30d)`
  (crypto is a **fixed-period pass, not auto-renewing** — no mandate exists on
  chain; the user re-pays to extend). Lowest build + lowest risk.
- **(B) Self-watched address.** Engine issues a unique address/amount per order,
  polls a chain API for N confirmations, then grants. More moving parts, custody
  and reorg edge cases, an uncached polling loop to cost-review. Not recommended
  for v1.

Either way crypto grants a **time-boxed pass**, and the UI states "renew manually
before {date}" — there is no silent renewal.

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
| `WEB_BILLING_RAZORPAY_ENABLED` | false | India rail |
| `WEB_BILLING_STRIPE_ENABLED` | false | RoW rail |
| `WEB_BILLING_CRYPTO_ENABLED` | false | crypto rail |
| `WEB_BILLING_TEST_MODE` | true | use provider **sandbox/test keys**; must be flipped to false with live keys only after owner sign-off |

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
path, no per-tick/scan/order reads. The only loop to avoid is crypto option (B)'s
chain polling, which is another reason (A) is recommended. Idempotency store is a
tiny table / short-TTL Redis set. No Cost-Discipline hot-path concern.

## 9. Legal / compliance follow-ons (tracked, not blocking the design)

- `mkmk749278/lumin-legal`: `terms.md` currently states Google Play Billing as the
  billing model (corrected when B16 shipped). Web rails require a terms update to
  describe Razorpay/Stripe/crypto billing, refunds, and cancellation — **owner-
  sign-off legal change**, shipped alongside activation, not before.
- Provider onboarding is an **owner task**: Razorpay + Stripe accounts, KYC, plan/
  price objects, and — importantly — confirming each provider permits our business
  category. (Both Razorpay and Stripe restrict some crypto-adjacent businesses; we
  present as a **signals/education subscription**, not an exchange, but this must be
  confirmed at account setup. Flagged as a real go/no-go item.)

## 10. Proposed delivery order (after sign-off)

Each step is its own PR, engine + app paired where needed, each dark:

1. **Seam + config** — `billing_web.py` skeleton with the verifier interface,
   `/api/billing/web/config`, flags, idempotency store, `WebBillingVerifier` unit-
   tested with fake provider payloads. (No live provider yet; all rails "disabled"
   in config → endpoint returns manual-only.) *Off-money-path-ish: ships behind
   master OFF.*
2. **Razorpay rail** — checkout create + webhook + signature tests, sandbox keys.
3. **Stripe rail** — same shape, sandbox keys.
4. **Crypto rail** — processor (A) integration + webhook.
5. **App paywall + `web_billing_service.dart`** — region-adaptive UI, entitlement
   poll-after-return.
6. **Legal + activation** — terms update, live keys, per-rail owner activation
   from Ops after each sandbox verification.

## 11. Decisions needed from owner (sign-off gate)

1. **Crypto:** hosted processor (A, recommended) vs self-watched address (B)? If
   (A): Coinbase Commerce or NOWPayments?
2. **Recurring vs pass:** cards = recurring subscription (proposed). Crypto =
   fixed 30-day pass (proposed, no on-chain mandate exists). Confirm.
3. **Pricing parity:** keep ₹1000/₹2000 for India; what USD for Stripe (₹ ≈ $12 /
   $24 at current rate — round to $11.99 / $23.99?), and crypto amount (USDT peg to
   the USD price)?
4. **Crypto region scope:** offer crypto everywhere, or exclude specific
   jurisdictions?
5. **Provider category confirmation** — owner to confirm Razorpay & Stripe accept
   our business at onboarding (§9).

---

*On sign-off, implementation proceeds in the order of §10, each PR dark and
owner-reviewed. No web billing endpoint serves a live charge until
`WEB_BILLING_TEST_MODE=false` is set per rail after its sandbox verification.*
