# Signup Free Trial — Activation Runbook

**Purpose.** Turn on the **7-day free trial for new customers**. The code is built and
wired end-to-end (engine ledger + endpoints, ops panel, app welcome offer); this runbook
covers the **decision + activation + verification** the code cannot do for itself.

**Owner decisions** (AskUserQuestion, 2026-07-25):

| Decision | Answer |
|---|---|
| Length | **7 days** |
| Tier | **`auto`** — the full product, hands-off server-side execution |
| Mechanism | **Server-granted**, no payment method, not a Play trial offer |
| Activation | **Opt-in** — the app shows a welcome offer, the user taps to start it |

**Why not a Play Console free-trial offer.** A Play trial only reaches users who already
reached checkout *with a card*. The owner asked for "every new customer", so the trial is
granted server-side against a phone-verified account instead. The trade-off is real and
accepted: there is no automatic conversion to paid at day 7 — the trialist must choose to
subscribe, which is what the day-5/day-1 in-app prompts exist for.

---

## What it actually gives away

Signals, levels and analysis have always been free here; the paywall is on **automation**.
So a trial grants the thing we sell:

- 7 days of **`auto`** — the engine dispatches orders server-side on the user's own
  Binance keys.
- The user must still connect a key (IP-whitelisted, withdraw-permission rejected) and
  arm auto-trade. **Blast-radius caps, the naked-position invariant and the kill switch
  apply to a trialist exactly as they do to a paying subscriber** — the trial changes
  entitlement, nothing about execution safety.
- A trialist who never connects a key experiences the app as a signals reader, which is
  the same as free. Read the ops funnel with that in mind: `claimed` is not `activated`.

---

## Ship state — it is DARK

Per `CLAUDE.md § Project Phase`, this is a money-path change and ships dark-first with
**two** flags. They are not the same flag:

| Env | Default at ship | Effect |
|---|---|---|
| `SIGNUP_TRIAL_MEASUREMENT_ENABLED` | **`true`** | Stamps the eligible cohort + the offer/claim/conversion funnel. Grants nothing, shows nothing. |
| `SIGNUP_TRIAL_ENABLED` | **`false`** | The user-visible effect: the offer becomes claimable and a claim writes entitlement. |

So from the moment this deploys, **ops → Trials fills with the real would-be cohort**
while no user sees anything. That is the number to read before deciding.

Additional tunables:

| Env | Default | Meaning |
|---|---|---|
| `SIGNUP_TRIAL_DAYS` | `7` | Length of the window. |
| `SIGNUP_TRIAL_TIER` | `auto` | `assist` or `auto`. |
| `SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS` | `0` | `0` = no age limit, so every never-paid free user gets the welcome offer once — **including the free users who signed up before this shipped**. Set to e.g. `7` to make it strictly a new-signup offer. |

> The default of `0` is a deliberate choice worth a second look before activation: it
> means the existing free base is offered a trial on their next app open. That is a
> one-time burst of trialists (good for conversion, and a real step up in how many
> accounts can arm auto-trade at once). If that burst is not wanted, set the age limit
> **before** flipping `SIGNUP_TRIAL_ENABLED`.

---

## Step 1 — Read the dark cohort (before activating)

Ops → **Trials**. Wait for a real window (a few days of app opens) and read:

- **Cohort** — how many users would be offered a trial. `cohort_dark` are the ones
  counted while the offer was off; they have been shown nothing.
- **Eligibility split** — the panel lists rows; spot-check that paying and lapsed
  subscribers are absent (they are excluded as "not new customers").

The question this answers: *how many accounts would gain the ability to arm auto-trade
if I flip this on today?* If that number is larger than you want to supervise at once,
set `SIGNUP_TRIAL_MAX_ACCOUNT_AGE_DAYS` first so the offer only reaches new signups.

## Step 2 — Activate

On the VPS:

```bash
# .env
SIGNUP_TRIAL_ENABLED=true
```

```bash
bash deploy.sh
```

Verify the flag is live (owner token):

```bash
curl -s -H "Authorization: Bearer $OPS_ENGINE_TOKEN" \
  https://<engine-host>/api/trial/admin/funnel | jq '{offer_live, measuring, tier, days}'
```

`offer_live` must be `true`. Ops → Trials shows the same, top of panel.

## Step 3 — Verify on a real device

1. Sign in with a phone that has **never** subscribed and has **never** trialled.
2. The welcome offer sheet appears on the Pulse tab.
3. Tap **Start my 7 free days** → the sheet closes, a trial chip appears with the
   countdown, and Settings → Subscription shows the trial window instead of the paywall.
4. Confirm on the engine that entitlement is real, not cosmetic:

```bash
curl -s -H "Authorization: Bearer $OPS_ENGINE_TOKEN" \
  https://<engine-host>/api/trial/admin/funnel | jq '.summary'
```

`claimed` and `active` both increment. The user row now carries `tier=auto` with
`paid_until` seven days out, which is what dispatch reads.

5. Tap again / restart the app → the second claim returns `already_trialled` and the
   window is unchanged. One trial per user, ever, enforced at DB level.

## Step 4 — Watch the first week

- Ops → Trials: `claimed / offered` is whether the welcome copy works;
  `converted / claimed` is whether the product does.
- The trial expires by the same path a lapsed subscription does (the read-time expiry
  downgrade re-resolves from the ledgers), so a trialist silently drops to `free` and
  auto-trade stops dispatching for them. No separate expiry job exists or is needed.

---

## Rollback

Set `SIGNUP_TRIAL_ENABLED=false` and redeploy. This stops **new** claims immediately.

It does **not** confiscate a running trial — banked grants live in `user_reward_grants`
and the entitlement composition keeps honouring them until they expire, exactly like
referral rewards. That is deliberate: revoking automation from under a user mid-window is
worse than letting at most 7 days run out. If a specific trial must be killed now, use
the kill switch (global) or delete that user's `signup_trial` grant row and let the next
entitlement read re-resolve.

---

## Where the pieces live

| Concern | File |
|---|---|
| Policy, flags, eligibility, claim | `src/api/signup_trial.py` |
| Funnel + grant ledger primitives | `src/api/user_overrides.py` (`user_trials`, `user_reward_grants`) |
| Entitlement composition (why a grant survives Play/RTDN) | `src/api/referral_rewards.py` |
| Endpoints (`/api/trial`, `/api/trial/claim`, `/api/trial/admin/funnel`) | `src/api/server.py` |
| Config | `config/__init__.py` § Signup free trial |
| Ops panel | `360ce-ops` → `app/routes/trials.py`, `/trials` |
| App welcome offer + countdown | `lumin-app` → `lib/features/trial/` |
| Tests | `tests/api/test_signup_trial.py` |
