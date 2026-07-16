# Google Play Billing — Activation Runbook (B16)

**Purpose.** Turn on the two-tier auto-trade subscription paywall in production. The
code is already built and wired end-to-end on both the engine and the Lumin app (Sessions
32–33); this runbook covers the **configuration + activation + verification** that the
code cannot do for itself. Follow it top-to-bottom — later steps assume earlier ones.

**Doctrine.** Signals + entry/SL/TP + analysis are **FREE**. The paywall is *trade
automation only*, positioned as automation **software** run on the user's own exchange
keys (never investment advice — this framing is load-bearing for Google Play Payments
policy). Tier ladder: `free < assist < auto`.

| Product ID | Tier | Price | What it unlocks |
|---|---|---|---|
| `lumin_assist_monthly` | `assist` | ₹1000/mo | One-tap "take trade" (order placed **client-side** on the user's keys) |
| `lumin_auto_monthly` | `auto` | ₹2000/mo | Hands-off **server-side** auto-execution |

> These IDs are hard-wired in three places that MUST stay in lockstep: the Play Console
> products, the app (`lumin-app/lib/features/settings/pages/subscription_page.dart`
> `kAssistMonthlyId` / `kAutoMonthlyId`), and the engine env
> (`GOOGLE_PLAY_ASSIST_PRODUCT_IDS` / `GOOGLE_PLAY_AUTO_PRODUCT_IDS`, which default to
> exactly these values in `config/__init__.py`).

---

## Prerequisites (already done)

- ✅ **Merchant / payments profile verified** (BillDesk, Google's India disbursement
  provider). This is what unblocks selling in-app products. Confirmed via the Play Console
  Payments profile — note this is the *payout* account, **not** the subscription products.
- ✅ Lumin app live on the production track, package **`org.luminapp.lumin`**.
- ✅ Firebase Auth in production (the engine maps the app's Firebase ID token → user row).

## Blocker confirmed at time of writing

**No subscription products exist yet** — Play Console → *Monetize with Play → Products →
Subscriptions* is on its empty "Create subscription" state. Until the two products exist
and are **Active**, the app's `loadProducts()` returns empty and the Subscription page
shows "No subscription plans are available right now." **Step 1 is therefore mandatory
and first.**

---

## Step 1 — Create the two subscription products (Play Console)

Play Console → **Monetize with Play → Products → Subscriptions → Create subscription**.

For **each** product:

1. **Product ID** — `lumin_assist_monthly`, then `lumin_auto_monthly`. Exact match, no
   typos (the ID is immutable once created).
2. **Name / benefits** — describe the *automation software* benefit, not signal access or
   returns. Suggested:
   - Assist: "Assist — one-tap trade automation. Take any Lumin signal in a single tap;
     the order is placed on your own connected exchange account."
   - Auto: "Auto — hands-off trade automation. Every eligible signal is executed
     automatically on your own connected exchange account, with per-agent and risk
     controls."
3. **Base plan** — create one **auto-renewing** base plan, billing period **monthly**.
   - Assist base-plan price: **₹1000** (India). Auto: **₹2000**.
   - Set availability to the same region(s) as the app's in-region gate.
4. **Activate** the product and the base plan (a product with only draft plans is not
   purchasable).

Do **not** add free trials or intro offers in v1 unless the owner decides to — keep the
first activation minimal and verifiable.

---

## Step 2 — Financial features declaration + listing/data-safety framing

Play Console → **Policy → App content**:

1. **Financial features declaration** — declare the app as applicable and complete it
   consistent with the automation-software framing.
2. **Store listing + Data safety** — ensure copy reads as *market-analytics / trade
   automation*, never "trading signals to profit" or "investment advice." This keeps the
   subscription inside Play's billing policy for financial-adjacent apps.

> Business Rule B16 change already recorded in `OWNER_BRIEF.md`; this step is the Play
> Console reflection of it.

---

## Step 3 — Service account with Android Publisher access

The engine verifies every purchase against the Google Play Developer API using a service
account (separate trust scope from the Firebase Auth SA).

1. **GCP** → create a service account (or reuse a dedicated one) and generate a JSON key.
2. **Google Play Console → Users and permissions → API access** → link the GCP project
   and grant this service account **View financial data / Manage orders and
   subscriptions** (enough to call `purchases.subscriptionsv2.get` and acknowledge).
3. Place the JSON **outside the repo** on the VPS (the docker-compose mount maps it in),
   e.g. `/data/google-play-service-account.json`. Never commit it; it is never logged.
   - If left unset, `GOOGLE_PLAY_SERVICE_ACCOUNT_PATH` falls back to
     `FIREBASE_SERVICE_ACCOUNT_PATH`. Prefer a **separate** SA so the two trust scopes stay
     independent.

**Activation gate the code enforces:** the verifier is constructed only when
`GOOGLE_PLAY_BILLING_ENABLED=true` **and** `GOOGLE_PLAY_PACKAGE_NAME` is set
(`src/api/main.py`), and `is_configured()` is true only when the package name is set and
the service account is loadable (`src/api/billing_play.py`). Until both hold,
`/api/billing/play/verify` returns **503 "play billing not configured"**.

---

## Step 4 — Real-Time Developer Notifications (RTDN)

RTDN keeps entitlement live after the foreground purchase moment — renewals, cancellations,
expiries, refunds. Without it, a lapsed subscriber would only downgrade on the next
verify/refresh (the read-time expiry check is the backstop, not a substitute).

1. **GCP Pub/Sub** → create a topic (e.g. `lumin-play-rtdn`).
2. Create a **push subscription** on that topic whose endpoint is the engine's RTDN URL:
   ```
   https://api.luminapp.org/api/billing/play/rtdn/<GOOGLE_PLAY_RTDN_PATH_SECRET>
   ```
   - The `{secret}` path segment is an unguessable shared secret (defence-in-depth, in
     addition to — not instead of — OIDC).
   - Enable **OIDC authentication** on the push subscription; the token audience must equal
     `GOOGLE_PLAY_RTDN_AUDIENCE` (set it to the full RTDN endpoint URL). The engine verifies
     the Pub/Sub OIDC bearer against this audience (`_verify_pubsub_oidc` in
     `src/api/server.py`).
3. **Play Console → Monetization setup → Real-time developer notifications** → enter the
   Pub/Sub topic name and **Send test notification** to confirm delivery.

Grant Play's service agent
(`google-play-developer-notifications@system.gserviceaccount.com`) the **Pub/Sub
Publisher** role on the topic if the console prompts for it.

---

## Step 5 — Engine VPS `.env` + redeploy

Add/confirm these in the VPS `.env` (documented in `.env.example`):

```bash
GOOGLE_PLAY_BILLING_ENABLED=true
GOOGLE_PLAY_PACKAGE_NAME=org.luminapp.lumin
GOOGLE_PLAY_SERVICE_ACCOUNT_PATH=/data/google-play-service-account.json
# Product-ID envs default to the correct values; set explicitly only to override:
# GOOGLE_PLAY_ASSIST_PRODUCT_IDS=lumin_assist_monthly
# GOOGLE_PLAY_AUTO_PRODUCT_IDS=lumin_auto_monthly
GOOGLE_PLAY_RTDN_AUDIENCE=https://api.luminapp.org/api/billing/play/rtdn/<secret>
GOOGLE_PLAY_RTDN_PATH_SECRET=<same-secret-as-in-the-URL>
```

Redeploy: `bash deploy.sh`. Confirm the boot log line:

```
Play billing enabled: package=org.luminapp.lumin configured=True
```

`configured=False` means the service account did not load — fix before proceeding.

> The tier-gate on the money path is separate and already live: server-side auto-execution
> requires `AUTO_TRADE_TIER_GATE_ENABLED=true` (default on) — leave it on.

---

## Step 6 — End-to-end verification (the go-live gate)

Do **not** open the products to production until this passes on a **real device** via an
internal-testing track (license testers can purchase without being charged).

1. **Products load:** open the app's Subscription page → both Assist and Auto render with
   Play-formatted prices (₹1000 / ₹2000). Empty list ⇒ Step 1 products not Active, or IDs
   mismatched.
2. **Assist purchase:** buy Assist → snackbar "Assist plan active" → the one-tap "take
   trade" control unlocks **immediately** (no app restart — see the app-side reactivity
   fix). Engine log shows `Play verify: … → tier=assist`.
3. **Auto purchase:** buy Auto → auto-trade settings unlock; connect a Binance key and
   confirm a dispatched signal places a server-side order (or is correctly gated when mode
   ≠ live).
4. **Restore purchases:** reinstall / clear data → "Restore purchases" re-entitles the
   account.
5. **RTDN downgrade:** cancel the subscription in Google Play → confirm an RTDN arrives and
   the user downgrades to `free` (engine log via `_handle_rtdn`; `users.tier` flips).
6. **Server-truth backstop:** confirm a lapsed `paid_until` downgrades at read time even
   before RTDN (`_resolve_user_tier` in `signal_dispatch.py`).

Only after all six pass: promote the products / open the paywall to production.

---

## Verified wiring (audit trail — 2026-07-16)

Confirmed by reading the code + running the suites; recorded here so activation isn't
re-litigated:

- **No scaffold.** The verify path both **stores** entitlement (`_apply_play_entitlement`
  → `UserStore.aset_tier`, the source of truth) **and** the money path **consumes** it
  (`signal_dispatch._resolve_user_tier` → `auth.can_auto` before any server-side order,
  fail-closed, expiry-aware, 30 s cached per Cost Discipline). RTDN reuses the same
  `_apply_play_entitlement`.
- **Product-ID lockstep** holds across app, engine defaults, and this doc.
- **Tests green:** `test_two_tier_entitlement`, `api/test_billing_play`,
  `api/test_billing_callback`, `api/test_admin_grant_route`, `api/test_users`,
  `api/test_users_firebase` → **91 passed**.

## Related surfaces (not required for basic activation)

- **Owner comp / manual grant:** `POST /api/admin/grant-tier` (owner-gated, expiring) —
  for testers/influencers without a real purchase. Ops UI at `ops.luminapp.org`.
- **Bot webhook grant:** `POST /internal/billing/grant` (HMAC-signed,
  `BILLING_WEBHOOK_SECRET`) — pre-pay a tier before first OTP.
- **Legal:** confirm `lumin-legal` ToS carries auto-renew / billing / cancel terms aligned
  with the in-app disclaimer (owner-owned copy).
