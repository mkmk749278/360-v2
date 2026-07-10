# Continuity Pack — TEMPLATE

*Audit finding F-04 (2026-07-10). Bus factor is 1: one person holds every
credential. This template lists exactly what must live in a sealed password-
manager vault (e.g. Bitwarden/1Password "emergency access" or a shared vault
with a trusted person) so the system can be operated, halted, or handed over
without the owner.*

> ⚠️ **Never fill this file in inside the repo.** It is a checklist of what
> goes IN the vault. Secrets in git are a hard-limit violation.

## Vault contents checklist

### 1. Halt & operate
- [ ] Ops dashboard URL + password (`OPS_AUTH_TOKEN`) + TOTP secret/QR
- [ ] Link to `docs/SAFE_HALT_RUNBOOK.md` (the 5-minute stop procedure)
- [ ] VPS: provider account login, host/IP, SSH user, SSH private key

### 2. Rebuild (pairs with docs/DR_RUNBOOK.md)
- [ ] Complete current `.env` file for 360-v2 (copy on every change — set a
      calendar reminder; a stale `.env` is the most likely DR failure point)
- [ ] `firebase-service-account.json`
- [ ] `BACKUP_PASSPHRASE` (decrypts all off-site backups)
- [ ] GitHub account access (owner of mkmk749278 repos) + recovery codes

### 3. Vendor accounts
- [ ] Google Cloud (KMS + Firestore + Play Console) login + 2FA recovery codes
- [ ] Cloudflare account (api.luminapp.org, ops.luminapp.org DNS)
- [ ] Google Play Console (app `org.luminapp.lumin`) + the Play signing info
- [ ] Telegram bot tokens / channel admin (mirror channel)
- [ ] Domain registrar for luminapp.org

### 4. People & instructions
- [ ] Name + contact of the designated emergency operator (the person given
      vault emergency access)
- [ ] One-page instruction: "If I am unreachable for more than N days:
      (1) execute SAFE_HALT_RUNBOOK, (2) post the in-app notice, (3) contact
      <engineer/firm> for hand-over using this vault"
- [ ] Statement of user obligations: subscriptions to pause/refund via Play
      Console if service is permanently down

## Maintenance rules

- Update the vault **within 24h** of rotating any credential in it.
- Test emergency access once per quarter (same cadence as the DR drill —
  do them together).
- Log completed reviews here in the repo (dates only, never contents):

| Date | Reviewed by | Vault complete? |
|---|---|---|
| _none yet_ | | |
