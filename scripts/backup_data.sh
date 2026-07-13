#!/usr/bin/env bash
# Nightly encrypted backup of the engine data volume (F-02, audit 2026-07-10).
#
# Backs up EVERYTHING under /app/data in the 360scalp-v2-data volume:
#   * SQLite user DB(s) — snapshotted first via sqlite3's online backup API
#     (WAL-safe, consistent) into .backup_staging/ inside the volume, so the
#     tar never captures a torn hot copy.
#   * All JSON money-path state (cohort_edge_store, loss_streaks,
#     invalidation_records, paper books, signal_performance, ...).
#
# Output: a single AES-256-CBC (pbkdf2) encrypted tarball in $BACKUP_DIR,
# rotated to the newest $BACKUP_KEEP files.  The passphrase comes from the
# BACKUP_PASSPHRASE env var and must ALSO live in the owner's password
# manager — a backup nobody can decrypt is not a backup.
#
# Run on the VPS host (needs docker + openssl):
#   BACKUP_PASSPHRASE=... bash backup_data.sh
#
# Scheduled by .github/workflows/vps-backup.yml (nightly), which also pulls
# the encrypted file off-box as a GitHub artifact — the off-site copy that
# survives the VPS disk dying.
#
# Restore procedure: scripts/restore_data.sh + docs/DR_RUNBOOK.md.
#
# NOTE: Firestore (encrypted key blobs, kill switch, tunables) is NOT in
# scope here — it is Google-managed and durable.  docs/DR_RUNBOOK.md covers
# the recommended `gcloud firestore export` schedule separately.

set -euo pipefail

ENGINE_CONTAINER="${ENGINE_CONTAINER:-360scalp-v2-engine}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/360scalp-v2}"
BACKUP_KEEP="${BACKUP_KEEP:-14}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_FILE="${BACKUP_DIR}/360scalp-data-${STAMP}.tar.gz.enc"

if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
  echo "BACKUP_FAIL reason=missing_passphrase" >&2
  echo "Set BACKUP_PASSPHRASE (and keep the same value in the owner's password manager)." >&2
  exit 1
fi

if ! docker inspect "$ENGINE_CONTAINER" --format '{{.State.Running}}' 2>/dev/null | grep -q true; then
  echo "BACKUP_FAIL reason=engine_not_running container=$ENGINE_CONTAINER" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

# ── 1. Consistent SQLite snapshots inside the volume ────────────────────────
# Uses Python's stdlib sqlite3 backup API (present in the engine image) so a
# live WAL-mode DB is copied at a consistent point without locking writers.
docker exec -i "$ENGINE_CONTAINER" python3 - <<'PYEOF'
import glob, os, shutil, sqlite3

DATA = "/app/data"
STAGING = os.path.join(DATA, ".backup_staging")
shutil.rmtree(STAGING, ignore_errors=True)
os.makedirs(STAGING, exist_ok=True)

dbs = sorted(glob.glob(os.path.join(DATA, "**", "*.db"), recursive=True))
dbs = [p for p in dbs if ".backup_staging" not in p]
for src in dbs:
    dst = os.path.join(STAGING, os.path.relpath(src, DATA).replace(os.sep, "__"))
    with sqlite3.connect(f"file:{src}?mode=ro", uri=True) as conn, \
         sqlite3.connect(dst) as out:
        conn.backup(out)
    print(f"sqlite snapshot: {src} -> {dst}")
print(f"sqlite snapshots complete: {len(dbs)} db(s)")
PYEOF

# ── 2. Tar the data dir out of the container, encrypt on the host ───────────
# -h not needed; exclude WAL/SHM hot files (the staged .backup copies are the
# consistent versions of those DBs).
#
# The engine writes money-path JSON state (edge/cohort stores, invalidation
# records, signal_performance, …) to /app/data CONTINUOUSLY, so tar will very
# often see a file mtime/size change mid-read and return exit code 1
# ("file changed as we read it").  That is a WARNING, not corruption — the
# archive is valid and the SQLite DBs are already consistently snapshotted in
# step 1.  Only tar exit >=2 is a real error.  We must therefore NOT let
# `set -o pipefail` + `set -e` abort on tar's exit 1, and we check PIPESTATUS
# for both pipe stages explicitly (the verify step below is the real integrity
# gate for a genuinely truncated archive).
set +e
docker exec "$ENGINE_CONTAINER" tar -czf - \
    --warning=no-file-changed \
    --exclude='*.db-wal' --exclude='*.db-shm' \
    -C /app data \
  | openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt \
      -pass env:BACKUP_PASSPHRASE -out "$OUT_FILE"
# Capture BOTH stages in one statement — any command (incl. a plain
# assignment) resets PIPESTATUS, so reading [0] then [1] separately would
# lose the second (and trip `set -u`).
pipe_rc=("${PIPESTATUS[@]}")
set -e
tar_rc=${pipe_rc[0]}
enc_rc=${pipe_rc[1]}
if [ "$tar_rc" -gt 1 ]; then
  echo "BACKUP_FAIL reason=tar_error rc=$tar_rc file=$OUT_FILE" >&2
  rm -f "$OUT_FILE"
  exit 1
fi
if [ "$enc_rc" -ne 0 ]; then
  echo "BACKUP_FAIL reason=openssl_error rc=$enc_rc file=$OUT_FILE" >&2
  rm -f "$OUT_FILE"
  exit 1
fi
chmod 600 "$OUT_FILE"

# ── 3. Verify the artifact decrypts and lists as a sane tar ─────────────────
ENTRIES=$(openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
            -pass env:BACKUP_PASSPHRASE -in "$OUT_FILE" \
          | tar -tzf - | wc -l)
if [ "$ENTRIES" -lt 1 ]; then
  echo "BACKUP_FAIL reason=verify_empty file=$OUT_FILE" >&2
  rm -f "$OUT_FILE"
  exit 1
fi

# ── 4. Clean staging inside the volume, rotate old backups ──────────────────
docker exec "$ENGINE_CONTAINER" rm -rf /app/data/.backup_staging
ls -1t "$BACKUP_DIR"/360scalp-data-*.tar.gz.enc 2>/dev/null \
  | tail -n +$((BACKUP_KEEP + 1)) \
  | xargs -r rm -f

BYTES=$(stat -c%s "$OUT_FILE")
echo "BACKUP_OK file=$OUT_FILE bytes=$BYTES entries=$ENTRIES keep=$BACKUP_KEEP"
