#!/bin/sh
# Extract engine logs in [START, STOP) for the runtime truth report.
#
# Reads the persistent loguru file sink at /app/logs/engine_*.log inside the
# 360scalp-v2-engine container. The file sink retains 30 days at 50MB rotation
# vs Docker's json-file driver which caps at 30MB total and historically lost
# almost every periodic telemetry emission before the workflow could read
# them.
#
# Usage (server-side, via `docker exec`):
#   /tmp/360-monitor-scripts/extract_engine_logs.sh "<START>" ["<STOP>"]
#
# Args:
#   START  loguru-format timestamp (YYYY-MM-DD HH:MM:SS), inclusive lower bound
#   STOP   optional loguru-format timestamp, exclusive upper bound (default: open-ended)
#
# Exit: 0 on success (even when 0 lines emitted); 2 if no log files exist
#       (lets the caller fall back to `docker compose logs`).
set -eu

START="${1:?missing START arg}"
STOP="${2:-}"

# 0 lines is a valid result; absence of the file sink is not.
if ! ls /app/logs/engine_*.log >/dev/null 2>&1; then
    exit 2
fi

if [ -z "$STOP" ]; then
    awk -v start="$START" '/^[0-9]{4}-[0-9]{2}-[0-9]{2}/ && $0 >= start' /app/logs/engine_*.log
else
    awk -v start="$START" -v stop="$STOP" \
        '/^[0-9]{4}-[0-9]{2}-[0-9]{2}/ && $0 >= start && $0 < stop' /app/logs/engine_*.log
fi
