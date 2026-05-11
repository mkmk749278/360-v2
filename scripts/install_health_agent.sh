#!/usr/bin/env bash
# Install the VPS health check agent as a cron job.
# Run from the 360-v2 project root:
#   sudo bash scripts/install_health_agent.sh
#
# What this does:
#   - Adds two cron entries for the current user (or root if run via sudo):
#       Every 15 min  — alert-only mode  (Telegram only if issues found)
#       Every 6 hours — full report mode (always sends a Telegram summary)
#   - Creates /var/log/360-health-agent.log for cron output

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AGENT="$SCRIPT_DIR/vps_health_agent.py"
PYTHON="$(command -v python3 2>/dev/null || echo /usr/bin/python3)"
LOGFILE="/var/log/360-health-agent.log"

echo "=== 360-Scalping V2 — Health Agent Installer ==="
echo "Project : $PROJECT_DIR"
echo "Agent   : $AGENT"
echo "Python  : $PYTHON"
echo ""

if [[ ! -f "$AGENT" ]]; then
    echo "[ERROR] Agent script not found: $AGENT" >&2
    exit 1
fi

chmod +x "$AGENT"

# Create log file (ignore failure if not root)
touch "$LOGFILE" 2>/dev/null && chmod 644 "$LOGFILE" 2>/dev/null || true

REMOVE_MARKER="360-health-agent"
CRON_HEADER="# 360-Scalping V2 — VPS Health Agent"
CRON_BLOCK="$CRON_HEADER
# Alert-only every 15 minutes
*/15 * * * *       cd $PROJECT_DIR && $PYTHON $AGENT        >> $LOGFILE 2>&1
# Full report every 6 hours (midnight, 06:00, 12:00, 18:00 UTC)
0 0,6,12,18 * * *  cd $PROJECT_DIR && $PYTHON $AGENT --full >> $LOGFILE 2>&1"

EXISTING="$(crontab -l 2>/dev/null || true)"

if echo "$EXISTING" | grep -q "$REMOVE_MARKER"; then
    echo "[INFO] Updating existing cron entries..."
    CLEANED="$(echo "$EXISTING" | grep -v "$REMOVE_MARKER" | grep -v "$CRON_HEADER" | grep -v 'vps_health_agent')"
    (echo "$CLEANED"; echo ""; echo "$CRON_BLOCK") | crontab -
else
    echo "[INFO] Installing new cron entries..."
    (echo "$EXISTING"; echo ""; echo "$CRON_BLOCK") | crontab -
fi

echo ""
echo "[OK] Installed cron jobs:"
crontab -l | grep -A4 "$CRON_HEADER"
echo ""
echo "Log file : $LOGFILE"
echo ""
echo "Test run (stdout only, no Telegram):"
echo "  cd $PROJECT_DIR && python3 scripts/vps_health_agent.py --full --stdout"
echo ""
echo "Watch live cron output:"
echo "  tail -f $LOGFILE"
