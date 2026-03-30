#!/usr/bin/env bash
# deploy_vps.sh — One-click VPS deployment for 360-Crypto-Scalping V2
#
# Deploys the engine via Docker Compose on a fresh or existing VPS.
# Handles everything: prerequisites, Docker, Redis, .env, build, and start.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/mkmk749278/360-v2/main/deploy_vps.sh | sudo bash
#   — OR —
#   git clone https://github.com/mkmk749278/360-v2.git && cd 360-v2
#   chmod +x deploy_vps.sh
#   sudo ./deploy_vps.sh
#
# Flags:
#   --clean    Nuke all existing containers/images before building
#
# Required .env variables:
#   TELEGRAM_BOT_TOKEN           — Telegram bot token
#   TELEGRAM_ACTIVE_CHANNEL_ID   — Active Trading channel ID
#   TELEGRAM_ADMIN_CHAT_ID       — Admin chat ID

set -euo pipefail

# ─── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅  $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $*${NC}"; }
err()  { echo -e "${RED}❌  $*${NC}" >&2; }
info() { echo -e "${CYAN}ℹ️   $*${NC}"; }
hdr()  { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════════${NC}"; \
         echo -e "${BOLD}${CYAN}  $*${NC}"; \
         echo -e "${BOLD}${CYAN}══════════════════════════════════════════════${NC}"; }

# ─── Argument parsing ──────────────────────────────────────────────────────────
DO_CLEAN=false
for arg in "$@"; do
    case "$arg" in
        --clean) DO_CLEAN=true ;;
        *) echo "Usage: $0 [--clean]"; exit 1 ;;
    esac
done

# ─── Must run as root (or with sudo) ──────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "This script must be run as root (sudo bash deploy_vps.sh)"
    exit 1
fi

REAL_USER="${SUDO_USER:-root}"
if [[ "$REAL_USER" == "root" ]]; then
    DEPLOY_HOME="/root"
else
    DEPLOY_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6)"
fi

hdr "🚀  360-Crypto-Scalping V2 — One-Click VPS Deployment"

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 1 — CLEAN (optional)
# ──────────────────────────────────────────────────────────────────────────────
if [ "$DO_CLEAN" = true ]; then
    hdr "PHASE 1 — CLEAN (--clean requested)"

    # Stop old systemd services from previous installs
    for svc in "360scalp-top50" "360-crypto-engine" "crypto-signal-engine" "360-crypto"; do
        if systemctl is-active --quiet "$svc" 2>/dev/null; then
            info "Stopping service: $svc"
            systemctl stop "$svc" 2>/dev/null || true
            systemctl disable "$svc" 2>/dev/null || true
        fi
    done

    # Stop Docker services
    if command -v docker &>/dev/null; then
        if [ -f docker-compose.yml ]; then
            docker compose down 2>/dev/null || true
        fi
        # Remove 360scalp containers
        if docker ps -a --format '{{.Names}}' | grep -q "360scalp"; then
            docker ps -a --format '{{.Names}}' | grep "360scalp" | while read -r c; do
                docker stop "$c" 2>/dev/null || true
                docker rm "$c" 2>/dev/null || true
            done
        fi
        # Remove project images
        IMAGE_IDS=$(docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' \
            | grep -iE "360scalp|360-crypto" | awk '{print $2}' | sort -u || true)
        if [ -n "$IMAGE_IDS" ]; then
            echo "$IMAGE_IDS" | xargs -r docker rmi -f 2>/dev/null || true
        fi
        docker system prune -af 2>/dev/null || true
        docker builder prune -af 2>/dev/null || true
    fi

    # Flush Redis
    if command -v redis-cli &>/dev/null; then
        redis-cli -n 0 FLUSHDB 2>/dev/null || true
    fi

    ok "Cleanup complete"
fi

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 2 — INSTALL PREREQUISITES
# ──────────────────────────────────────────────────────────────────────────────
hdr "PHASE 2 — INSTALL PREREQUISITES"

# Update packages
info "Updating system packages …"
if command -v apt-get &>/dev/null; then
    apt-get update -qq
    apt-get install -y -qq git curl >/dev/null 2>&1
elif command -v yum &>/dev/null; then
    yum install -y -q git curl >/dev/null 2>&1
fi
ok "System packages ready"

# Install Docker if not present
if ! command -v docker &>/dev/null; then
    info "Installing Docker …"
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    ok "Docker installed"
else
    ok "Docker already installed ($(docker --version | head -c 40))"
fi

# Verify Docker Compose
if ! docker compose version &>/dev/null && ! docker-compose version &>/dev/null; then
    err "Docker Compose not available. Please install Docker Compose V2."
    exit 1
fi
ok "Docker Compose available"

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 3 — PROJECT FILES
# ──────────────────────────────────────────────────────────────────────────────
hdr "PHASE 3 — PROJECT FILES"

# If we're not already inside the repo, clone it
if [ ! -f "docker-compose.yml" ] || [ ! -f "src/main.py" ]; then
    PROJECT_DIR="$DEPLOY_HOME/360-v2"
    if [ -d "$PROJECT_DIR" ]; then
        info "Updating existing clone at $PROJECT_DIR …"
        cd "$PROJECT_DIR"
        git pull --ff-only 2>/dev/null || true
    else
        info "Cloning repository into $PROJECT_DIR …"
        git clone https://github.com/mkmk749278/360-v2.git "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
    ok "Project files ready at $PROJECT_DIR"
else
    PROJECT_DIR="$(pwd)"
    ok "Already inside project directory: $PROJECT_DIR"
fi

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 4 — ENVIRONMENT CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
hdr "PHASE 4 — ENVIRONMENT CONFIGURATION"

if [ ! -f ".env" ]; then
    cp .env.example .env
    info ".env created from .env.example"
    echo ""
    warn "╔══════════════════════════════════════════════════════════════╗"
    warn "║  IMPORTANT: Edit .env with your credentials before restart  ║"
    warn "║                                                             ║"
    warn "║  Required:                                                  ║"
    warn "║    TELEGRAM_BOT_TOKEN=your_bot_token                        ║"
    warn "║    TELEGRAM_ACTIVE_CHANNEL_ID=your_channel_id               ║"
    warn "║    TELEGRAM_ADMIN_CHAT_ID=your_admin_chat_id                ║"
    warn "║                                                             ║"
    warn "║  Run: nano $PROJECT_DIR/.env                                ║"
    warn "╚══════════════════════════════════════════════════════════════╝"
    echo ""
else
    ok ".env already exists"
fi

# Validate bot token is not a placeholder
if grep -q "your_bot_token_here" .env 2>/dev/null; then
    warn "TELEGRAM_BOT_TOKEN is still a placeholder — edit .env before the engine can send signals"
fi

# Ensure TOP50 mode is configured
if ! grep -q "TOP50_FUTURES_ONLY" .env 2>/dev/null; then
    echo "" >> .env
    echo "# Top-50 futures-only mode" >> .env
    echo "TOP50_FUTURES_ONLY=true" >> .env
    echo "TOP50_FUTURES_COUNT=50" >> .env
    info "Added TOP50 configuration to .env"
fi

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 5 — BUILD & START
# ──────────────────────────────────────────────────────────────────────────────
hdr "PHASE 5 — BUILD & START"

mkdir -p logs

info "Building Docker image (this may take 1–2 minutes) …"
if [ "$DO_CLEAN" = true ]; then
    docker compose build --no-cache
else
    docker compose build
fi

info "Starting engine …"
docker compose up -d

# Wait for containers to start
sleep 3

# ──────────────────────────────────────────────────────────────────────────────
# DEPLOYMENT SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
hdr "DEPLOYMENT COMPLETE 🎉"

echo ""
echo -e "${BOLD}Service Status:${NC}"
docker compose ps
echo ""

echo -e "${BOLD}Configuration:${NC}"
echo -e "  Project:  ${CYAN}$PROJECT_DIR${NC}"
echo -e "  Env file: ${CYAN}$PROJECT_DIR/.env${NC}"
echo ""

echo -e "${BOLD}Management Commands:${NC}"
echo -e "  ${GREEN}View logs    :${NC}  docker compose logs -f engine"
echo -e "  ${GREEN}Restart      :${NC}  docker compose restart engine"
echo -e "  ${GREEN}Stop         :${NC}  docker compose down"
echo -e "  ${GREEN}Rebuild      :${NC}  docker compose up -d --build"
echo -e "  ${GREEN}Status       :${NC}  docker compose ps"
echo -e "  ${GREEN}Clean deploy :${NC}  sudo bash deploy_vps.sh --clean"
echo ""

ok "Engine is running! Check logs: docker compose logs -f engine"
