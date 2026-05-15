# Firebase Auth Migration — Engine

**Status:** design — pending owner review
**Branch:** `feat/firebase-auth-engine`
**Companion:** `mkmk749278/lumin-app` branch `feat/firebase-auth-app`

---

## Goal

Replace the local HS256 JWT + in-memory OTP path used for consumer-app
authentication with **Firebase Authentication**. After migration:

- The Lumin app signs in via Firebase Phone Auth (SMS OTP) or via the
  existing @LuminProBot Telegram OTP fallback. In both cases the app
  ends up with a real `FirebaseAuth.instance.currentUser`.
- The engine validates Firebase ID tokens on every authenticated
  request — no local JWT minting for end-user requests anywhere.
- The static `API_AUTH_TOKEN` owner-bypass **stays** for ops tooling
  and CI — it's the only auth path that doesn't require a Firebase
  identity.
- Our SQLite `users` table remains the source of truth for `tier`,
  `paid_until`, `telegram_chat_id`, and the profile fields. Firebase
  owns identity (UID + phone); we own everything else.

---

## Why

1. **iOS reach without an Apple Developer Program enrollment.** Phone
   Auth via Firebase works identically on Flutter Web (which is the
   planned iOS path until company registration unblocks a native iOS
   app). One auth surface across Android + Web + future iOS.
2. **SMS deliverability without a custom provider.** Firebase Phone
   Auth uses Google's SMS infrastructure — higher deliverability than
   AuthKey/Twilio shims we'd otherwise have to build and maintain. The
   Telegram OTP fallback (B13's free path) survives intact via a
   custom-token bridge described below.
3. **Drop a self-maintained crypto surface.** Our HS256 implementation
   is correct but every line of crypto we own is a liability. Google's
   ID-token verification + JWKS rotation is one less thing to keep
   right.
4. **Auto-refresh is free.** Firebase SDK refreshes the ID token
   client-side. Our `refresh_token` endpoint and 7-day window become
   dead code — removed in this PR's code phase.

---

## Non-goals (this PR)

- Migrating ops tooling away from `API_AUTH_TOKEN`. Static token stays
  for CI / VPS scripts / 360 CE Ops.
- Migrating the @LuminProBot billing-webhook authenticator
  (`BILLING_WEBHOOK_SECRET` HMAC). Server-to-server, unchanged.
- Touching the engine's signal pipeline, scanner, evaluator, or
  Telegram routing. Auth-only PR.
- Web build. Lumin Android is the first migration target; web follows
  in a later session against the same engine endpoints.

---

## Architecture — before vs after

### Before

```
Lumin app ──── POST /api/auth/anonymous ───────────► engine
              ◄── { access_token: <our-HS256-JWT> }
        
        ── Authorization: Bearer <our-HS256-JWT> ──► engine
              src/api/auth.py:decode_token() verifies HMAC

        OTP path:
        ── POST /api/auth/phone/issue   { phone } ──► engine
              src/api/otp.py.issue() → otp_delivery (SMS / Telegram)
        ── POST /api/auth/phone/verify  { phone, code } ──► engine
              src/api/otp.py.verify() → mint_user_token() → JWT
```

### After

```
Lumin app ─── FirebaseAuth.verifyPhoneNumber(phone) ─► Firebase
              (Google handles SMS via reCAPTCHA/SafetyNet)
              ◄── ID token (RS256, ~1h, auto-refreshed)

        ── Authorization: Bearer <Firebase ID token> ──► engine
              src/api/firebase_auth.py:verify_id_token()
              → look up users.firebase_uid → User
              → tier/paid_until from users table

        Telegram OTP fallback (preserves B13 free path):
        ── POST /api/auth/telegram-otp/issue  { phone } ──► engine
              src/api/otp.py.issue() → @LuminProBot delivers code
        ── POST /api/auth/telegram-otp/verify { phone, code } ──► engine
              src/api/otp.py.verify() → look up or create user
              → firebase_admin.auth.create_custom_token(firebase_uid)
              ◄── { custom_token }
        Lumin app:
              FirebaseAuth.instance.signInWithCustomToken(custom_token)
              → real Firebase session, same path as SMS thereafter

        Owner / ops:
        ── Authorization: Bearer <API_AUTH_TOKEN> ──────► engine
              (static-token bypass, unchanged)
```

---

## Schema delta

One column added to the `users` table via the existing
`_migrate_schema()` `ALTER TABLE ADD COLUMN` path in
`src/api/users.py` — no migration tooling, no row rewrite.

```sql
ALTER TABLE users ADD COLUMN firebase_uid TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_firebase_uid
    ON users(firebase_uid) WHERE firebase_uid IS NOT NULL;
```

Partial unique index — existing rows have NULL until first Firebase
sign-in, at which point the column is populated by phone-match.

### Migration of existing testers + owner

On first Firebase sign-in by an existing user:

1. App sends Firebase ID token → engine
2. Engine verifies token, extracts `firebase_uid` + `phone_number`
3. Engine looks up `users WHERE firebase_uid = ?` — miss
4. Engine looks up `users WHERE phone_e164 = ?` — hit (existing row)
5. Engine `UPDATE users SET firebase_uid = ? WHERE user_id = ?`
6. Returns existing `User` with original `user_id`, `tier`, etc.

No manual ops step. The 5 testers + owner transition transparently on
their first sign-in after they install the post-migration Lumin APK.

---

## New env vars

Added to `.env.example` (the existing template is missing the auth
section entirely — this PR documents the gap):

```bash
# ══════════════════════════════════════════════════════════════════════
# Multi-user auth (Phase 2 + Phase 4 Firebase migration)
# ══════════════════════════════════════════════════════════════════════

# Owner phone — bootstrapped as user_id=1, tier=owner on first boot.
OWNER_PHONE_E164=

# Static admin token — bypasses Firebase ID-token validation for ops /
# CI / 360 CE Ops. Keep this secret; it's the only way to mutate
# engine state without a Firebase identity.
API_AUTH_TOKEN=

# Legacy local-JWT signing secret. Kept during the transition window
# while Lumin app versions < firebase-cutover still authenticate via
# /api/auth/anonymous and /api/auth/phone/*. Removed once all clients
# are on the post-migration APK (see "Transition" below).
API_JWT_SECRET=

# Billing webhook HMAC secret (used by @LuminProBot → engine).
BILLING_WEBHOOK_SECRET=

# ══════════════════════════════════════════════════════════════════════
# Firebase Authentication
# ══════════════════════════════════════════════════════════════════════

# Firebase project ID — find in Firebase Console > Project Settings.
FIREBASE_PROJECT_ID=

# Path to the service account JSON. Used by firebase-admin to:
#   - Verify ID tokens (RS256 via Google JWKS)
#   - Mint custom tokens for the Telegram-OTP fallback path
# Service account needs the "Firebase Authentication Admin" role.
# Store the JSON outside the repo; the docker-compose mount maps it
# in. Default path matches the existing data/ convention.
FIREBASE_SERVICE_ACCOUNT_PATH=/data/firebase-service-account.json

# Feature flag — when true, engine accepts Firebase ID tokens.
# Defaults to false so the live system keeps the legacy path until the
# config flip is intentional. Set to true once tester APKs ship with
# Firebase support.
FIREBASE_AUTH_ENABLED=false
```

---

## Code changes (preview — not in this PR)

### New module: `src/api/firebase_auth.py`

- `init_firebase_admin(service_account_path: str, project_id: str)`
  → called once at boot from `src/bootstrap.py` after `UserStore`
- `verify_id_token(id_token: str) -> dict` → wraps
  `firebase_admin.auth.verify_id_token`, raises `AuthError` on
  invalid / expired / wrong-project
- `create_custom_token(firebase_uid: str) -> str` → wraps
  `firebase_admin.auth.create_custom_token`, used by the
  Telegram-OTP-verify endpoint

### `src/api/users.py`

- Add `"firebase_uid"` to `_PROFILE_COLUMNS` tuple → `_migrate_schema`
  picks it up
- Add `firebase_uid: Optional[str]` field to `User` dataclass
- Add `get_or_create_by_firebase_uid(firebase_uid, phone_e164)`
  method: looks up by UID, falls back to phone-match-and-backfill,
  finally creates new row
- `_row_to_user` reads the new column defensively

### `src/api/auth.py`

- Keep existing `mint_token` / `decode_token` / `refresh_token`
  during transition window
- Tier constants unchanged
- After cutover (separate PR), remove `mint_token`,
  `mint_user_token`, `refresh_token` — they're no longer used

### `src/api/server.py` (where the FastAPI app + `Depends` live)

- New `Depends(get_current_user)` that tries in order:
  1. `Authorization: Bearer <API_AUTH_TOKEN>` (literal compare) →
     returns synthetic owner `User`
  2. If `FIREBASE_AUTH_ENABLED=true`: verify Firebase ID token,
     resolve to `User` via `get_or_create_by_firebase_uid`
  3. Fall back to existing HS256 `decode_token` path
  4. 401 if all paths reject

### New endpoint: `POST /api/auth/telegram-otp/verify`

```python
# Request
{
  "phone_e164": "+15551234567",
  "code": "123456"
}

# Response 200
{
  "custom_token": "<Firebase custom token>",
  "user_id": 42,
  "tier": "free",
  "paid_until": null,
  "needs_onboarding": true
}

# Response 400
{ "detail": "wrong_code" | "expired" | "too_many_attempts" | ... }
```

The custom token is single-use; the app calls
`signInWithCustomToken(custom_token)` immediately to land a Firebase
session.

### `src/api/otp_delivery.py`

- **Strip non-Telegram providers** (AuthKey / Twilio / etc. — verified
  list at PR-code time). Firebase handles SMS now; engine-side SMS
  delivery is dead weight.
- Keep Telegram delivery via the existing @LuminProBot integration.

### `requirements.txt`

```
firebase-admin>=6.0.0,<7.0.0
```

This pulls in `google-auth`, `google-cloud-firestore`,
`pyjwt[crypto]`, `cachecontrol` transitively. All standard, no
heavy ML deps.

---

## Transition strategy

**Per owner call: feature-flag both auth modes during transition.**

Engine accepts three auth headers simultaneously while
`FIREBASE_AUTH_ENABLED=true`:

| Header | Used by | Status |
|---|---|---|
| `Bearer <API_AUTH_TOKEN>` (static) | Ops tooling, CI, 360 CE Ops | Permanent |
| `Bearer <Firebase ID token>` (RS256) | Post-migration Lumin app | Permanent post-cutover |
| `Bearer <local HS256 JWT>` | Pre-migration Lumin app versions | Transition only |

Flow:
1. Land this engine PR with `FIREBASE_AUTH_ENABLED=false` default
2. Configure Firebase project, drop service account JSON on VPS
3. Set `FIREBASE_AUTH_ENABLED=true` in prod `.env`, restart engine
4. Land Lumin app PR (`feat/firebase-auth-app`) — testers update APK
5. Once all 5 testers + owner have signed in via Firebase
   (observable in logs as `firebase_uid` populated on every row), a
   follow-up PR strips the legacy HS256 path entirely

Roll-back during transition: flip `FIREBASE_AUTH_ENABLED=false`,
restart. Engine reverts to HS256-only — Lumin apps on either version
keep working (post-Firebase apps cache the last successful local-JWT
they fetched at sign-in via the legacy `/api/auth/anonymous` endpoint
kept alive specifically for this fallback during the transition).

---

## Risks

| Risk | Mitigation |
|---|---|
| Firebase SMS quota exhaustion (Spark tier: 10/day) | Telegram OTP path absorbs overflow; upgrade to Blaze before public launch |
| `google-services.json` checked into a public repo by mistake | App-side concern (`feat/firebase-auth-app` design covers it); engine only needs the service account JSON which is mounted, not committed |
| Service account JSON leaked from VPS | `chmod 600`, mount as Docker secret, never logged. Same blast radius as `BILLING_WEBHOOK_SECRET` today. |
| ID token validation latency (RS256 verify + JWKS fetch) | JWKS cached by firebase-admin; first-token latency ~50ms, cached <1ms |
| Existing tester sees "phone not recognized" on first Firebase login | Engine backfills `firebase_uid` by phone-match — they sign in with same phone, land on same `user_id`, same tier, same Binance keys. Verified by integration test below. |
| Clock skew on VPS rejecting ID tokens | NTP sync (already in deploy.sh); firebase-admin allows 30s skew tolerance |
| Custom-token misuse (Telegram-OTP-verify endpoint forging arbitrary identities) | Endpoint only mints custom token after our OTP store has validated the code; 5-attempt cap and 5-min TTL on the engine side prevent brute force |

---

## Verification plan

### Unit tests

- `tests/test_firebase_auth.py` (new):
  - `verify_id_token` round-trip with `firebase_admin.auth.verify_id_token` mocked
  - `create_custom_token` returns a parseable JWT for a given UID
- `tests/test_users_firebase.py` (new):
  - `get_or_create_by_firebase_uid` creates new row when UID + phone are both new
  - Looks up existing row by UID when UID matches
  - Backfills `firebase_uid` on existing row when phone matches but UID is new
  - Raises on phone collision (different UID, same phone) — shouldn't happen but defensive
- Existing `tests/test_otp.py` continues to pass (OTP store unchanged for Telegram path)

### Integration tests

- `tests/test_auth_dependency.py` (new):
  - Static `API_AUTH_TOKEN` bypass works regardless of `FIREBASE_AUTH_ENABLED`
  - Firebase ID token accepted when flag is on, rejected when off
  - Legacy HS256 token accepted in both modes during transition
- `tests/test_telegram_otp_verify.py` (new):
  - Happy path: issue → verify → custom token returned
  - Wrong code: 400, attempts decrement
  - Expired: 400 with `expired` detail

### Manual verification on staging

1. `FIREBASE_AUTH_ENABLED=true` on staging `.env`
2. Sign in via web Firebase Auth emulator with test phone
   `+15555555555` → engine accepts ID token, creates new user row
3. Set tier via SQL: `UPDATE users SET tier='paid', paid_until='2027-01-01' WHERE user_id=<n>`
4. Re-sign-in → ID token still valid, tier reflects update
5. Telegram-OTP path: issue via `/api/auth/telegram-otp/issue`,
   collect code from bot, verify via
   `/api/auth/telegram-otp/verify` → custom token returned, app
   exchanges via `signInWithCustomToken` → identical post-state to
   SMS path

### Production readiness

- `FIREBASE_AUTH_ENABLED=false` is the default — landing this PR is a
  no-op on the prod auth surface until the flag is flipped
- Owner reviews this design doc; on approval, code commits land on
  this same branch, then PR merges to `main` and auto-deploys
- After deploy verification (engine boots cleanly with
  firebase-admin imported), owner flips the flag in prod `.env` and
  restarts

---

## Open items for owner

1. **Firebase project not yet created.** Per side-conversation, owner
   needs to:
   - Create a Firebase project in Firebase Console
   - Enable Phone Auth provider (initially on Spark tier; 10
     verifications/day cap)
   - Generate a service account JSON with "Firebase Authentication
     Admin" role
   - Drop the JSON on the VPS at `/data/firebase-service-account.json`
     (or a path of choice, documented in `.env.example`)
   - Register the Lumin Android SHA-256 signing certificate
     fingerprint in Firebase Console (required for Phone Auth on
     Android — without it, the SDK fails with
     `auth/missing-app-credential`)
2. **Confirm `otp_delivery.py` provider strip list.** PR-code phase
   will list the providers currently in the file; owner confirms which
   to keep (Telegram is the only one the design assumes survives).
3. **Acceptable post-cutover legacy-removal timeline.** Suggest one
   week after all testers confirm sign-in works via Firebase.

---

## Companion app PR

Engine cannot be exercised end-to-end without the Lumin app changes.
See `mkmk749278/lumin-app` PR on branch `feat/firebase-auth-app` for
the corresponding app-side design.
