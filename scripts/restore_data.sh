#!/usr/bin/env bash
# Restore the engine data volume from an encrypted backup produced by
# scripts/backup_data.sh.  Companion to docs/DR_RUNBOOK.md — read that first.
#
# Usage (on the VPS host):
#   BACKUP_PASSPHRASE=... bash restore_data.sh /var/backups/360scalp-v2/360scalp-data-<stamp>.tar.gz.enc
#
# Safety:
#   * REFUSES to run while the engine container is running (a restore under a
#     live engine corrupts both worlds).  Stop the stack first:
#       cd /path/to/360-v2 && docker compose down
#   * Restores into the named volume 360scalp-v2-data via a throwaway
#     container; the previous contents are moved aside to /data/.pre_restore_<stamp>
#     inside the volume, NOT deleted — so a bad restore is reversible.
#   * The staged SQLite snapshots (from .backup_staging/, name-mangled with
#     "__") are moved back over their live paths, replacing any torn hot
#     copies the tar may also contain.

set -euo pipefail

BACKUP_FILE="${1:-}"
DATA_VOLUME="${DATA_VOLUME:-360scalp-v2-data}"
ENGINE_CONTAINER="${ENGINE_CONTAINER:-360scalp-v2-engine}"
HELPER_IMAGE="${HELPER_IMAGE:-alpine:3.20}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "usage: BACKUP_PASSPHRASE=... bash restore_data.sh <backup.tar.gz.enc>" >&2
  exit 1
fi
if [ -z "${BACKUP_PASSPHRASE:-}" ]; then
  echo "RESTORE_FAIL reason=missing_passphrase" >&2
  exit 1
fi
if docker inspect "$ENGINE_CONTAINER" --format '{{.State.Running}}' 2>/dev/null | grep -q true; then
  echo "RESTORE_FAIL reason=engine_running — stop the stack first (docker compose down)" >&2
  exit 1
fi

# Decrypt + verify before touching the volume.
TMP_TAR="$(mktemp /tmp/360scalp-restore-XXXXXX.tar.gz)"
trap 'rm -f "$TMP_TAR"' EXIT
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 \
  -pass env:BACKUP_PASSPHRASE -in "$BACKUP_FILE" -out "$TMP_TAR"
ENTRIES=$(tar -tzf "$TMP_TAR" | wc -l)
if [ "$ENTRIES" -lt 1 ]; then
  echo "RESTORE_FAIL reason=archive_empty" >&2
  exit 1
fi
echo "archive verified: $ENTRIES entries"

# Move current contents aside, unpack the backup, promote staged SQLite
# snapshots over their live paths.
docker run --rm -i \
  -v "$DATA_VOLUME":/data \
  -v "$TMP_TAR":/restore.tar.gz:ro \
  "$HELPER_IMAGE" sh -s <<SHEOF
set -eu
mkdir -p /data/.pre_restore_${STAMP}
find /data -mindepth 1 -maxdepth 1 ! -name '.pre_restore_*' \
  -exec mv {} /data/.pre_restore_${STAMP}/ \;
tar -xzf /restore.tar.gz -C /tmp
cp -a /tmp/data/. /data/
# Promote consistent SQLite snapshots (path__mangled under .backup_staging).
if [ -d /data/.backup_staging ]; then
  for snap in /data/.backup_staging/*; do
    [ -f "\$snap" ] || continue
    rel=\$(basename "\$snap" | sed 's|__|/|g')
    mkdir -p "/data/\$(dirname "\$rel")"
    mv "\$snap" "/data/\$rel"
    # Torn hot-copy sidecars must not survive next to a restored snapshot.
    rm -f "/data/\${rel}-wal" "/data/\${rel}-shm"
    echo "promoted sqlite snapshot -> /data/\$rel"
  done
  rm -rf /data/.backup_staging
fi
echo "restore unpacked; previous contents preserved in /data/.pre_restore_${STAMP}"
SHEOF

echo "RESTORE_OK from=$BACKUP_FILE previous=/data/.pre_restore_${STAMP}"
echo "Next: docker compose up -d, then verify per docs/DR_RUNBOOK.md §Post-restore checks."
