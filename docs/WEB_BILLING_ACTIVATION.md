# Web Billing — Activation & Operations Runbook

*Companion to `docs/WEB_BILLING_DESIGN.md`. How to turn the PWA crypto (NOWPayments)
subscription rail on/off, how secrets reach the engine, and how to verify it end to
end. Written 2026-07-20 after the rail went live.*

---

## TL;DR state machine

The rail is **dark by default**. It's controlled by env flags on the VPS `.env`
(+ two secrets injected from GitHub). Live when **all** of:

- `WEB_BILLING_ENABLED=true`
- `WEB_BILLING_CRYPTO_ENABLED=true`
- `NOWPAYMENTS_API_KEY` set (valid)
- `NOWPAYMENTS_IPN_SECRET` set (valid, matches the NOWPayments dashboard)
- `WEB_BILLING_TEST_MODE=false` for **live** payments (`true` → sandbox API)

`/api/billing/web/config` returns the crypto rail only when enabled **and** the API
key is present; otherwise it returns **manual-only** and checkout 503s.

## How secrets reach the engine (important)

**GitHub secrets do NOT reach the engine directly.** The engine reads its `.env` on
the VPS. `.github/workflows/deploy.yml` **injects** the two NOWPayments secrets into
`.env` on every deploy (same pattern as Binance/OpenAI):

```
NOWPAYMENTS_API_KEY      ← GitHub secret on mkmk749278/360-v2
NOWPAYMENTS_IPN_SECRET   ← GitHub secret on mkmk749278/360-v2
```

So **editing these two keys directly in `.env` on the box does not stick** — the next
deploy overwrites them from the GitHub secrets. To change a secret:

1. `gh secret set NOWPAYMENTS_API_KEY --repo mkmk749278/360-v2` (paste with the
   dashboard **copy button** — never hand-type, a stray char breaks verification)
2. Trigger a deploy: `gh workflow run deploy.yml --repo mkmk749278/360-v2`

The flag values (`WEB_BILLING_*`) are **not** injected — they live in `.env` and
persist across deploys (`git reset --hard` doesn't touch the ignored `.env`).

⚠️ **The secrets must be on `360-v2` (the engine repo), NOT `lumin-app`.** The app
build's secrets are unrelated; the deploy that matters reads `360-v2`'s secrets.

## Enable (sandbox first, then live)

On the VPS (`/root/360-v2`):

```bash
# flags (persist in .env)
sed -i 's/^WEB_BILLING_ENABLED=.*/WEB_BILLING_ENABLED=true/'          .env
sed -i 's/^WEB_BILLING_CRYPTO_ENABLED=.*/WEB_BILLING_CRYPTO_ENABLED=true/' .env
sed -i 's/^WEB_BILLING_TEST_MODE=.*/WEB_BILLING_TEST_MODE=true/'      .env   # sandbox
bash deploy.sh
```

Sandbox needs a **separate** key + IPN secret from `sandbox.nowpayments.io` (a
production key returns `403 INVALID_API_KEY` against the sandbox API). Set those as
the GitHub secrets while testing, then swap back to production keys for go-live.

Go live: set `WEB_BILLING_TEST_MODE=false` (+ production keys in the GitHub secrets),
redeploy.

## Disable (kill switch)

```bash
sed -i 's/^WEB_BILLING_CRYPTO_ENABLED=.*/WEB_BILLING_CRYPTO_ENABLED=false/' .env
bash deploy.sh
```
Paywall drops to manual-only instantly. Reversible.

## Verify — the four checks (no real payment needed)

```bash
# 1. Flags applied on the running engine
curl -s https://api.luminapp.org/api/billing/web/config
#    want: "enabled":true, "test_mode":false, a "crypto" rail with $15/$25

# 2. API key valid against NOWPayments (invoice creation)
KEY=$(grep '^NOWPAYMENTS_API_KEY=' .env | cut -d= -f2-)
curl -s -o /dev/null -w "%{http_code}\n" -X POST https://api.nowpayments.io/v1/invoice \
  -H "x-api-key: $KEY" -H "Content-Type: application/json" \
  -d '{"price_amount":15,"price_currency":"usd","order_id":"diagtest"}'
#    want: 200 or 201   (403 INVALID_API_KEY = wrong/empty/sandbox-vs-prod key)

# 3. Webhook armed (IPN secret present)
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  https://api.luminapp.org/api/billing/web/crypto/webhook \
  -H 'Content-Type: application/json' -d '{}'
#    want: 401 (present) — 503 means NOWPAYMENTS_IPN_SECRET is empty

# 4. IPN secret VALUE matches the dashboard (catches stray chars — see below)
S=$(grep '^NOWPAYMENTS_IPN_SECRET=' .env | cut -d= -f2-)
echo "ipn: len=${#S} first4=${S:0:4} last4=${S: -4}"
#    compare first4/last4/len against the dashboard's IPN secret
```

**Check #3 (401) only proves the secret is *present*, not *correct*** — a wrong
secret also returns 401. Check #4 is what confirms the value. A real payment is the
only 100% confirmation (it exercises the actual signature).

### The stray-character trap (2026-07-20 incident)

The IPN secret was set with a **trailing `w`** (`…M28r` typed as `…M28rw`, len 33 not
32). Checks #1–#3 all passed, but a real payment would have **failed signature
verification → money taken, no tier granted**. Caught by comparing `.env` `last4`
(`28rw`) against the dashboard's shown tail (`M28r`). **Always re-copy secrets with
the dashboard copy button, and run check #4.**

## The real end-to-end test (final confirmation)

1. `app.luminapp.org` → Settings → Subscription → **Pay with crypto**
2. Pay the invoice (USDT). On a real (non-sandbox) run this is a real charge.
3. Confirm the grant on the VPS:
   ```bash
   docker logs 360scalp-v2-api --tail 30 | grep billing_web
   # want:  web billing GRANT: user_id=… tier=assist paid_until=…
   ```
4. The app unlocks the tier (auto-poll, or "I've paid — check now").

If the payment lands but there's **no GRANT line**, the webhook rejected it →
IPN-secret mismatch (redo check #4 / re-copy the secret).

## Reference

- Design + rails + entitlement invariant: `docs/WEB_BILLING_DESIGN.md`
- Engine code: `src/api/billing_web.py` (verifier, checkout, webhook)
- Config: `config/__init__.py` (`WEB_BILLING_*`, `NOWPAYMENTS_*`)
- App: `lumin-app` `lib/data/web_billing_service.dart`,
  `lib/features/settings/pages/web_paywall_page.dart`
- Pricing: $15 assist / $25 auto, USDT, monthly, offered everywhere.
- Tiers granted: the existing `assist` / `auto` via `UserStore.aset_tier` — no new
  entitlement concepts.
