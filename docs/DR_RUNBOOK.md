# Disaster Recovery Runbook

*Created from audit finding F-02 (2026-07-10). Rehearse this once per quarter —
a runbook that has never been executed is a hypothesis, not a plan.*

**Recovery target:** full stack rebuilt on a fresh VPS in **under 2 hours**,
with data loss bounded by the last nightly backup (**RPO ≤ 24h**, **RTO ≤ 2h**).

---

## What is protected, and how

| State | Where it lives | Protection |
|---|---|---|
| Open user positions | Binance (resting SL/TP orders) | Survive ANY engine outage — stops rest on the exchange. Reconciler cleans up on recovery |
| Encrypted Binance key blobs, kill switch, tunables, per-user disable flags | Firestore | Google-managed durability. Schedule `gcloud firestore export` monthly (below) for belt-and-braces |
| User settings / overrides / trade records (SQLite), JSON money-path state (cohort store, loss streaks, paper books, invalidation records, signal performance) | VPS data volume | **Nightly encrypted backup** — `.github/workflows/vps-backup.yml` → `scripts/backup_data.sh`; local rotation (14) + off-site GitHub artifact (30 days) |
| Code, config-as-code, docs | GitHub | Inherent |
| `.env` (secrets: tokens, KMS refs, API auth) | VPS only + **owner's password manager** | ⚠️ NOT in any repo, by design. The continuity pack (docs/CONTINUITY_PACK_TEMPLATE.md) MUST hold a current copy — without it this runbook fails at step 4 |

## Backup system — daily operation

- Nightly at 21:45 UTC the `💾 VPS Nightly Backup` workflow SSHes to the VPS,
  runs `scripts/backup_data.sh` (consistent SQLite snapshot → tar → AES-256
  encrypt → verify → rotate), and pulls the encrypted file into a GitHub
  artifact.
- **A failed backup files an `auto-detected` `severity:high` issue.** Treat it
  as a same-day fix.
- The passphrase is the `BACKUP_PASSPHRASE` repo secret **and** a password-
  manager entry. If you rotate it, rotate both, and remember old artifacts
  need the old passphrase.

### Quarterly restore drill (do not skip)

1. On the VPS (or any docker host):
   `BACKUP_PASSPHRASE=... bash scripts/restore_data.sh <file>` against a
   **scratch volume**: `DATA_VOLUME=drill-restore-test bash scripts/restore_data.sh ...`
2. Verify: the SQLite DB opens (`sqlite3 <db> 'PRAGMA integrity_check;'`),
   `signal_performance.json` parses, record counts look sane.
3. Log the drill date + result at the bottom of this file.

---

## Scenario A — VPS is lost (disk death, provider termination, region loss)

**Impact while down:** no new signals, no new auto-trades. Open positions are
protected by resting SL/TP orders on Binance. Auto-trade boots **globally
disabled** (fail-closed) on a fresh deploy, so recovery cannot surprise-trade.

1. **Provision** a fresh Ubuntu VPS (same provider or any). Install Docker +
   compose plugin. Point DNS/Cloudflare (`api.luminapp.org`) at the new IP
   **later** (step 8) — engine first.
2. **Restore access:** add your SSH key; update the `VPS_HOST` /
   `VPS_SSH_KEY` GitHub secrets so deploy + monitoring + backup workflows
   follow you to the new box.
3. **Clone the repo:** `git clone https://github.com/mkmk749278/360-v2 && cd 360-v2`.
4. **Recreate `.env`** from the continuity pack copy. Also place
   `firebase-service-account.json` into the data volume path it expects.
5. **Fetch the latest backup:** download the newest `vps-backup-*` artifact
   from the Actions tab (or copy from the old box if reachable).
6. **Restore the data volume** (stack not yet started, so the engine-running
   guard passes):
   ```bash
   docker volume create 360scalp-v2-data
   BACKUP_PASSPHRASE=... bash scripts/restore_data.sh 360scalp-data-<stamp>.tar.gz.enc
   ```
7. **Update the Binance IP whitelist**: every connected user's API key is
   IP-whitelisted to the OLD VPS IP (B18). Until keys are re-whitelisted to
   the new IP, signing will be rejected — this is expected and safe.
   Coordinate with users / regenerate connect flow as needed.
8. **Deploy:** `bash deploy.sh`. Verify all four containers healthy
   (`docker ps`, `docker logs 360scalp-v2-engine --tail 50`). Point
   Cloudflare at the new IP. Verify `https://api.luminapp.org/api/health`.
9. **Reconcile before re-enabling:** confirm the Reconciler ran clean, review
   open positions on Binance vs the app, THEN flip
   `auto_trade_globally_enabled` back on (ops dashboard → Control).
10. **Re-arm the safety net:** manually run the `💾 VPS Nightly Backup` and
    `🫀 VPS Liveness Watch` workflows once each; confirm green.

## Scenario B — data volume corrupted, VPS alive

`docker compose down`, then `restore_data.sh` with the newest good backup
(step 6 above), then `docker compose up -d`. The restore preserves the
corrupted state in `/data/.pre_restore_<stamp>` for forensics.

## Scenario C — Firestore data damaged

Firestore is the source of truth for key blobs + kill switch. Use Google
Cloud PITR / the monthly export:
```bash
# One-time setup (run from any gcloud-authed machine):
gsutil mb -l asia-south1 gs://<project>-firestore-exports
# Monthly (calendar reminder — or Cloud Scheduler):
gcloud firestore export gs://<project>-firestore-exports/$(date +%Y%m)
```
Restore via `gcloud firestore import`. Key blobs are useless without the KMS
key — which is exactly why they are safe to export.

## Scenario D — GCP account lost

The KMS master key is unexportable by design: **encrypted key blobs become
permanently undecryptable.** Recovery = every auto-trade user reconnects
their Binance key through the connect flow. This is acceptable-by-design
(non-custodial posture); communicate honestly, disable auto-trade globally
until reconnects complete.

## Post-restore checks (all scenarios)

- [ ] 4/4 containers healthy; signing socket present (`test -S /app/sock/signing.sock`)
- [ ] `/api/health` 200 via Cloudflare; app loads the Signals feed
- [ ] Reconciler log shows a clean pass; no naked positions
- [ ] Kill switch reads correctly from ops dashboard
- [ ] SQLite `PRAGMA integrity_check` = ok
- [ ] Nightly backup workflow green on the new box

---

## Drill log

| Date | Operator | Scenario | Result | Notes |
|---|---|---|---|---|
| _none yet — schedule the first drill_ | | | | |
