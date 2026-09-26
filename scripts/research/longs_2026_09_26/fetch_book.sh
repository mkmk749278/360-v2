#!/usr/bin/env bash
# The delivered book, one UTC day at a time, from the engine's unauthenticated
# /api/track-record/signals (limit is 200 per call, so a day per call keeps
# every day untruncated — the script reports any day that was).
# curl, not Python: Cloudflare answers urllib's default client with 403.
set -euo pipefail
: "${LONGS_DATA_DIR:=$HOME/longs_research_data}"
mkdir -p "$LONGS_DATA_DIR/days"
for i in $(seq 0 119); do
  d=$(date -u -d "2026-09-26 -$i day" +%F)
  f="$LONGS_DATA_DIR/days/$d.json"
  [ -s "$f" ] && continue
  for a in 1 2 3; do
    curl -sS -m 40 -o "$f" \
      "https://api.luminapp.org/api/track-record/signals?days=365&date=$d&limit=200" && break
    sleep 2
  done
done
python3 - "$LONGS_DATA_DIR" <<'PY'
import glob, json, os, sys
d = sys.argv[1]
rows, trunc = [], []
for f in sorted(glob.glob(os.path.join(d, "days", "*.json"))):
    p = json.load(open(f))
    rows += p["items"]
    if p.get("truncated"):
        trunc.append(os.path.basename(f))
json.dump(rows, open(os.path.join(d, "rows.json"), "w"))
print(len(rows), "rows; truncated days:", trunc or "none")
PY
