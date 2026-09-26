#!/usr/bin/env bash
# The engine's own records, via the ops read-only guest tier. Needs a code the
# owner mints on ops Control -> Access; it expires, so this is a one-off pull.
#   signal_performance.json  every closed signal, with dispatch time, the
#                            first price the monitor observed, MFE/MAE and
#                            both stop distances (structural and shipped)
#   signal_history.json      the LAST 500 signals only, with the exact TP1,
#                            entry zone and validity window. A later rerun sees
#                            a different 500 — the report's §11.3 window is
#                            14–25 Sep 2026.
set -euo pipefail
: "${LONGS_DATA_DIR:=$HOME/longs_research_data}"
: "${OPS_GUEST_CODE:?set OPS_GUEST_CODE to an ops guest code}"
cd "$LONGS_DATA_DIR"
rm -f cj.txt
curl -sS -m 30 -c cj.txt -b cj.txt -X POST "https://ops.luminapp.org/guest?json=1" \
  --data-urlencode "code=$OPS_GUEST_CODE"; echo
curl -sS -m 300 -b cj.txt -o sigperf.json "https://ops.luminapp.org/data/download/signal_performance"
curl -sS -m 300 -b cj.txt -o sighist.json "https://ops.luminapp.org/data/download/signal_history"
rm -f cj.txt
python3 -c "import json; print(len(json.load(open('sigperf.json'))), 'closed records;', len(json.load(open('sighist.json'))), 'history rows')"
