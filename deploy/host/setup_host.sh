#!/usr/bin/env bash
# Host self-maintenance layer (docs/AUTONOMOUS_OPS.md, layer 0).
#
# Idempotent — safe to re-run after every change; each section checks
# before it acts. Run ONCE as root on the VPS, then re-run whenever this
# file changes:
#
#     sudo REPO_DIR=/path/to/360-v2 bash deploy/host/setup_host.sh
#
# Optional env:
#     REPO_DIR                  — where the repo lives on the VPS (required)
#     HEALTHCHECKS_HOST_PING_URL — healthchecks.io ping URL for the host-level
#                                 dead-man cron (skipped when unset)
#     SKIP_UFW=1                — skip the firewall section (e.g. provider
#                                 firewall already in front)
#
# What it installs, and why (audit S-7 — hardening as code):
#   1. 2G swap file            — buffer for memory spikes; without swap the
#                                OOM killer fires on the first spike.
#   2. earlyoom                — kills the largest *non-critical* process
#                                BEFORE the kernel OOM killer stalls the box;
#                                dockerd + the money-path containers are on
#                                the avoid list.
#   3. unattended-upgrades     — security patches without an operator.
#   4. fail2ban                — bans brute-force SSH sources.
#   5. ufw                     — deny inbound except SSH/80/443.
#   6. systemd unit            — the compose stack comes back after a host
#                                reboot even if Docker's restart policies
#                                are cleared by an upgrade.
#   7. nightly prune cron      — old images/build cache + journal vacuum so
#                                disk never creeps to full.
#   8. host dead-man cron      — pings healthchecks.io every 5 min from the
#                                HOST (independent of Docker), so total-box
#                                death pages the owner's phone in ~5 min.
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "ERROR: run as root (sudo)"; exit 1; }
REPO_DIR="${REPO_DIR:?ERROR: set REPO_DIR=/path/to/360-v2}"
[ -f "$REPO_DIR/docker-compose.yml" ] || { echo "ERROR: $REPO_DIR has no docker-compose.yml"; exit 1; }

say() { echo; echo "── $* ──────────────────────────────────────────"; }

export DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------- 1. swap
say "swap"
if swapon --show | grep -q .; then
    echo "swap already active — skipping"
else
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "2G swap created + persisted"
fi
# Prefer RAM; swap is a spike buffer, not working memory.
sysctl -w vm.swappiness=10 >/dev/null
grep -q '^vm.swappiness' /etc/sysctl.conf || echo 'vm.swappiness=10' >> /etc/sysctl.conf

# ------------------------------------------------------------ 2. earlyoom
say "earlyoom"
apt-get install -y -q earlyoom >/dev/null
# Protect the daemons whose death loses the most: docker itself, sshd (so
# the owner can always get in), and the signing/engine processes. earlyoom
# then prefers the largest unprotected process when memory runs out.
cat > /etc/default/earlyoom <<'EOF'
EARLYOOM_ARGS="-m 5 -s 10 --avoid '(^|/)(dockerd|containerd|sshd|systemd|signing_service)$' --prefer '(^|/)(python|node|redis-server)$'"
EOF
systemctl enable --now earlyoom >/dev/null
systemctl restart earlyoom
echo "earlyoom active ($(systemctl is-active earlyoom))"

# ------------------------------------------- 3. unattended security upgrades
say "unattended-upgrades"
apt-get install -y -q unattended-upgrades >/dev/null
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
systemctl enable --now unattended-upgrades >/dev/null 2>&1 || true
echo "unattended security upgrades enabled"

# ------------------------------------------------------------- 4. fail2ban
say "fail2ban"
apt-get install -y -q fail2ban >/dev/null
cat > /etc/fail2ban/jail.local <<'EOF'
[sshd]
enabled  = true
maxretry = 5
findtime = 10m
bantime  = 1h
EOF
systemctl enable --now fail2ban >/dev/null
systemctl restart fail2ban
echo "fail2ban active ($(systemctl is-active fail2ban))"

# ------------------------------------------------------------------ 5. ufw
say "ufw"
if [ "${SKIP_UFW:-0}" = "1" ]; then
    echo "SKIP_UFW=1 — skipping firewall section"
else
    apt-get install -y -q ufw >/dev/null
    ufw allow OpenSSH >/dev/null       # NEVER lock the owner out
    ufw allow 80/tcp  >/dev/null       # nginx → certbot renewals
    ufw allow 443/tcp >/dev/null       # nginx → api.luminapp.org
    ufw default deny incoming >/dev/null
    ufw default allow outgoing >/dev/null
    ufw --force enable >/dev/null
    echo "ufw enabled: deny inbound except OpenSSH/80/443"
fi

# --------------------------------------------------- 6. systemd compose unit
say "systemd unit (360scalp.service)"
sed "s|__REPO_DIR__|$REPO_DIR|g" "$REPO_DIR/deploy/host/360scalp.service" \
    > /etc/systemd/system/360scalp.service
systemctl daemon-reload
systemctl enable 360scalp.service >/dev/null
echo "360scalp.service installed + enabled (stack survives host reboots)"

# ------------------------------------------------------- 7. nightly prune
say "nightly prune cron"
cat > /etc/cron.d/360scalp-prune <<'EOF'
# Nightly disk hygiene (docs/AUTONOMOUS_OPS.md layer 0). The watchdog also
# prunes reactively at 92% — this keeps it from ever getting there.
# Images/build-cache older than 7 days; running containers + named volumes
# are never touched by these commands.
15 4 * * * root docker image prune -af --filter "until=168h" >/dev/null 2>&1; docker builder prune -af --filter "until=168h" >/dev/null 2>&1; journalctl --vacuum-size=200M >/dev/null 2>&1
EOF
chmod 644 /etc/cron.d/360scalp-prune
echo "nightly prune installed (04:15)"

# --------------------------------------------------- 8. host dead-man ping
say "host dead-man ping"
if [ -n "${HEALTHCHECKS_HOST_PING_URL:-}" ]; then
    cat > /etc/cron.d/360scalp-deadman <<EOF
# Host-level dead-man's switch: healthchecks.io pages the owner's phone
# when these pings stop — i.e. when the whole box (not just a container)
# is down. Independent of Docker on purpose.
*/5 * * * * root curl -fsS -m 10 "$HEALTHCHECKS_HOST_PING_URL" >/dev/null 2>&1
EOF
    chmod 644 /etc/cron.d/360scalp-deadman
    echo "dead-man ping installed (every 5 min)"
else
    echo "HEALTHCHECKS_HOST_PING_URL not set — skipped."
    echo "Create a check at https://healthchecks.io (free), then re-run:"
    echo "  sudo REPO_DIR=$REPO_DIR HEALTHCHECKS_HOST_PING_URL=https://hc-ping.com/<uuid> bash deploy/host/setup_host.sh"
fi

say "done"
echo "Verify: swapon --show; systemctl status earlyoom fail2ban 360scalp; ufw status"
