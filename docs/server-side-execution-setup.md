# Server-Side Execution — Operator Setup Guide

This doc is the **operator** runbook for provisioning the GCP plumbing
that the server-side execution stack (`OWNER_BRIEF §3.9` + `B18`)
depends on. Run these steps ONCE per environment (staging, prod).
Subsequent engine restarts pick the config up from env vars.

Status as of writing: this guide covers PR-1 (Firebase Admin SDK +
Cloud KMS + Firestore Admin SDK scaffolding). Downstream PRs (signing
service, connect flow, Position FSM) build on top of this foundation
without requiring additional GCP setup.

---

## 0. Prerequisites

- A GCP project (free tier is fine for solo + small beta).
- The `gcloud` CLI installed locally (or use the Cloud Console UI).
- A Firebase project linked to the same GCP project (already done for
  the existing Firebase Auth integration — same project).

The engine VPS already has a Firebase service account JSON on disk
(`FIREBASE_SERVICE_ACCOUNT_PATH`). The new setup reuses that
service account so we don't manage two sets of credentials.

---

## 1. Create the KMS keyring + key

```bash
# Pick a location.  Single-region is fine for v1 (OWNER_BRIEF §3.9
# decision queue, item 3 — owner picks one explicitly).  Use the
# region closest to the engine VPS for the lowest Decrypt latency.
export GCP_PROJECT_ID="your-gcp-project-id"
export GCP_KMS_LOCATION="us-central1"   # example — pick yours
export GCP_KMS_KEYRING="binance-keys"
export GCP_KMS_KEY_NAME="user-secret-kek"

# Create the keyring (idempotent — re-running on an existing keyring
# is a no-op error you can ignore).
gcloud kms keyrings create "$GCP_KMS_KEYRING" \
  --project="$GCP_PROJECT_ID" \
  --location="$GCP_KMS_LOCATION"

# Create the key.  Symmetric (AES-256), purpose ENCRYPT_DECRYPT.
# Enable automatic 90-day rotation — old key versions remain
# available for decryption, so existing per-user encrypted DEKs
# keep working after rotation.
gcloud kms keys create "$GCP_KMS_KEY_NAME" \
  --project="$GCP_PROJECT_ID" \
  --location="$GCP_KMS_LOCATION" \
  --keyring="$GCP_KMS_KEYRING" \
  --purpose=encryption \
  --rotation-period=90d \
  --next-rotation-time="$(date -u -d '+90 days' +%Y-%m-%dT%H:%M:%SZ)"
```

The key resource name is now:

```
projects/${GCP_PROJECT_ID}/locations/${GCP_KMS_LOCATION}/keyRings/${GCP_KMS_KEYRING}/cryptoKeys/${GCP_KMS_KEY_NAME}
```

---

## 2. Grant the engine's service account Decrypt + Encrypt permission

The engine's existing Firebase service account (used today by
`init_firebase_admin`) needs `cloudkms.cryptoKeyEncrypterDecrypter`
on the KMS key. Find the service-account email:

```bash
# The Firebase service account JSON contains a "client_email" field.
SA_EMAIL=$(jq -r '.client_email' /path/to/firebase-sa.json)
echo "$SA_EMAIL"   # e.g. firebase-adminsdk-abc12@PROJECT.iam.gserviceaccount.com
```

Grant the role at key scope (not project scope — minimum-privilege):

```bash
gcloud kms keys add-iam-policy-binding "$GCP_KMS_KEY_NAME" \
  --project="$GCP_PROJECT_ID" \
  --location="$GCP_KMS_LOCATION" \
  --keyring="$GCP_KMS_KEYRING" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

This is the operative IAM property that makes the threat model work
(per `OWNER_BRIEF §3.9`): the engine VM can call `Encrypt` and
`Decrypt` on this one key. It cannot list other keys, cannot export
the master key material, cannot modify the IAM policy.

When the signing service ships in PR-4 it will run as a separate
Linux user on the engine VPS, but for v1 it uses the SAME service
account credentials as the main engine — isolation comes from the
Linux user / Unix socket boundary, not from a separate GCP identity.
(Future hardening: split the IAM so only the signing-service Linux
user can call KMS.)

---

## 3. Grant the service account Firestore read/write permission

The encrypted key blobs live in Firestore (`users/{uid}/binance_key/current`).
The same service account needs `roles/datastore.user` at project
scope:

```bash
gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.user"
```

## 3a. Deploy Firestore Security Rules (added in PR-3)

The rules file (`firestore.rules`) at the repo root is the **last-line
defence** between a stolen Firebase client ID token and the encrypted-
key blob store. It denies ALL client access to `users/{uid}/binance_key/**`
(only the engine's Admin SDK can touch it), allows owners to read their
own positions / orders / anomalies subcollections, and locks down the
global `kill_switch` document entirely. See `firestore.rules` for the
full per-collection contract.

Install the Firebase CLI (one-time):

```bash
npm install -g firebase-tools     # requires Node.js
firebase login
firebase use --add                # select your Firebase project
```

Deploy the rules:

```bash
cd /path/to/360-v2
firebase deploy --only firestore:rules
```

Verify in the Firebase Console → Firestore → Rules tab that the new
rules are live (the deploy CLI prints "compile succeeded" + a checksum;
the console shows the deployed text).

The rules are also pinned structurally by
`tests/security/test_firestore_rules_structure.py` — a future edit
that accidentally widens access (drops the deny-all default, grants
client write to `binance_key`, etc.) fails CI before it can ship.

### Re-deploying after a rules change

Any time `firestore.rules` is edited and merged to `main`, redeploy:

```bash
firebase deploy --only firestore:rules
```

For solo scale we deploy manually. A future hardening would wire this
into the GitHub Actions deploy workflow so push-to-main also pushes
rules — guarded by a `FIREBASE_TOKEN` GitHub secret.

---

## 4. Set engine environment variables

Add to the engine's `.env` (or wherever the VPS reads its env from):

```ini
# Existing — already set if Firebase Auth is enabled
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=/secrets/firebase-sa.json

# New — server-side execution custody (OWNER_BRIEF §3.9 + B18)
GCP_KMS_PROJECT_ID=your-gcp-project-id
GCP_KMS_LOCATION=us-central1
GCP_KMS_KEYRING=binance-keys
GCP_KMS_KEY_NAME=user-secret-kek
```

When all four `GCP_KMS_*` vars are set, the engine boot logs:

```
KMS client initialised: key=projects/.../cryptoKeys/user-secret-kek, ...
Firestore keystore initialised: service_account=...
```

When any are missing, boot logs `KMS client skipped (GCP_KMS_* env
vars not set)` and continues without server-side execution
(the engine still serves signals; only the new subsystem is offline).
This matches the Firebase Admin init pattern — adding the new
subsystem doesn't risk crashing engine boot if the GCP plumbing isn't
ready.

---

## 5. Verify the wire

After deploy, smoke-test the KMS round-trip from the engine VPS:

```bash
docker compose exec engine python3 -c "
from src.security import kms_client, envelope_crypto
import base64

c = kms_client.get_client()
dek = envelope_crypto.generate_dek()
wrapped = c.encrypt(dek)
print(f'KMS wrap OK ({len(wrapped)} bytes ciphertext)')

unwrapped = c.decrypt(wrapped)
assert unwrapped == dek, 'round-trip failed'
print('KMS unwrap OK — round-trip verified')
"
```

If this prints `KMS wrap OK ... KMS unwrap OK`, the foundation is
live. Subsequent PRs (connect flow, signing service, FSM workers)
plug into this without further GCP setup.

---

## Cost estimate at solo scale (50 active users)

| Item | Monthly |
|---|---|
| Cloud KMS — key storage | $0.06 |
| Cloud KMS — operations (~10k Decrypt/day at 50 users × ~7 trades/day × signing-service caching) | ~$3 |
| Firestore — reads + writes at this volume | Free tier |
| **Total add-on cost** | **~$3-5/mo** |

The 90-day automatic key rotation is included; rotation generates a
new key VERSION but the resource name stays the same, so existing
encrypted DEKs continue to decrypt against older versions
transparently. No engine-side migration required at rotation time.

---

## Disaster-recovery notes

- **If the KMS key is accidentally deleted**: every user's encrypted
  DEK becomes permanently unrecoverable. Plaintext API secrets
  cannot be recovered from the encrypted blobs. Users would need to
  generate new Binance API keys and re-connect. **Set a Cloud KMS
  delete protection policy on the key** (Cloud Console → Key → Edit
  → "Prevent destruction") to make this take 30 days of explicit
  ops action rather than a single CLI mistake.
- **If the service-account JSON is leaked**: the leaker can
  Decrypt encrypted DEKs IF they can also read the Firestore
  ciphertext. Rotation procedure: revoke the service-account key,
  issue a new one, redeploy with the new JSON. Encrypted DEKs are
  unaffected by service-account rotation — only KMS-key rotation
  changes the wrap.
- **If Firestore is breached**: the attacker has ciphertext + encrypted
  DEKs. Without the service-account JSON they cannot call KMS to
  unwrap. This is the property the architecture is designed around.

See `OWNER_BRIEF §3.9` for the full threat model and the blast-
radius caps that operate even in the worst case.
