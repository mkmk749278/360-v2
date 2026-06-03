#!/usr/bin/env bash
# 360-Crypto-scalping-V2 — Docker deployment script
set -euo pipefail

echo "🚀 360-Crypto-scalping-V2 — Docker Deployment"
echo "==============================================="

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
DO_CLEAN=false
for arg in "$@"; do
    case "$arg" in
        --clean) DO_CLEAN=true ;;
        *) echo "❌ Unknown argument: $arg"; echo "Usage: $0 [--clean]"; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Termux is not supported for Docker deployment
# ---------------------------------------------------------------------------
if command -v termux-setup-storage &>/dev/null; then
    echo "❌ Termux detected. Docker deployment is not supported on Termux."
    echo "   Please deploy on a Linux VPS with Docker installed."
    exit 1
fi

# ---------------------------------------------------------------------------
# Check prerequisites
# ---------------------------------------------------------------------------
command -v docker >/dev/null 2>&1 || {
    echo "❌ Docker not installed. Install it with:"
    echo "   curl -fsSL https://get.docker.com | sh"
    exit 1
}
docker compose version >/dev/null 2>&1 || docker-compose version >/dev/null 2>&1 || {
    echo "❌ Docker Compose not installed."
    exit 1
}

# ---------------------------------------------------------------------------
# --clean: Docker-level cleanup before building
# ---------------------------------------------------------------------------
if [ "$DO_CLEAN" = true ]; then
    echo ""
    echo "🧹 --clean requested: performing Docker-level cleanup before build..."

    if [ -f docker-compose.yml ]; then
        echo "  Stopping existing services..."
        docker compose down 2>/dev/null || true
    fi

    # Remove any orphaned named containers
    if docker ps -a --format '{{.Names}}' | grep -q "^360scalp-v2-engine$"; then
        echo "  Removing container: 360scalp-v2-engine"
        docker stop 360scalp-v2-engine 2>/dev/null || true
        docker rm   360scalp-v2-engine 2>/dev/null || true
    fi

    # Remove project-specific images
    IMAGE_IDS=$(docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' \
        | grep -iE "(^|/)(360scalp|360-crypto-scalping)" | awk '{print $2}' | sort -u || true)
    if [ -n "$IMAGE_IDS" ]; then
        echo "  Removing 360scalp-related images..."
        echo "$IMAGE_IDS" | xargs -r docker rmi -f 2>/dev/null || true
    fi

    echo "  Pruning unused Docker resources..."
    docker system prune -af 2>/dev/null || true
    docker builder prune -af 2>/dev/null || true

    echo "✅ Docker-level cleanup complete."
    echo ""
fi

# ---------------------------------------------------------------------------
# Check .env exists
# ---------------------------------------------------------------------------
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your credentials before continuing."
    echo "   nano .env"
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate TELEGRAM_BOT_TOKEN is not still a placeholder
# ---------------------------------------------------------------------------
if grep -q "your_bot_token_here" .env 2>/dev/null; then
    echo "⚠️  TELEGRAM_BOT_TOKEN is still a placeholder. Please edit .env first."
    echo "   nano .env"
    exit 1
fi

# ---------------------------------------------------------------------------
# Create logs directory (for bind-mount fallback / local testing)
# ---------------------------------------------------------------------------
mkdir -p logs

# ---------------------------------------------------------------------------
# Compose file selection
#
# Two modes — selected by API_PROCESS_ISOLATED in .env:
#
#   false (default) — single-process: engine serves the API directly on
#     API_PORT.  We explicitly pass -f flags so Docker does NOT auto-merge
#     any hand-dropped docker-compose.override.yml on the VPS (explicit -f
#     disables that).  docker-compose.singleprocess.yml adds the engine's
#     host-port mapping which must be absent in the base file (otherwise it
#     would conflict with the 'api' service port in isolated mode).
#
#   true — isolated: engine publishes Redis snapshots (SnapshotWriter); the
#     separate 'api' container owns the host-port mapping and serves HTTP.
#     --profile isolated activates that service.  The base docker-compose.yml
#     has no ports on the engine service, so no conflict.
# ---------------------------------------------------------------------------
COMPOSE_FILES=(-f docker-compose.yml)
PROFILE_ARGS=()

if grep -qE '^API_PROCESS_ISOLATED=(true|1|yes)$' .env 2>/dev/null; then
    PROFILE_ARGS=(--profile isolated)
    echo "🔀 API_PROCESS_ISOLATED=true — isolated mode: 'api' container serves HTTP."
else
    COMPOSE_FILES+=(-f docker-compose.singleprocess.yml)
    echo "⚙️  API_PROCESS_ISOLATED=false — single-process mode: engine serves HTTP."
fi

# ---------------------------------------------------------------------------
# Build and start
#
# Cached build by default (fast — Docker layer cache).  A full no-cache
# rebuild is only forced under --clean, which is the "nuke and repave" path.
# Routing CI through this script (deploy.yml) means the default must stay
# cache-friendly or every push to main pays a multi-minute full rebuild.
# ---------------------------------------------------------------------------
BUILD_ARGS=()
if [ "$DO_CLEAN" = true ]; then
    BUILD_ARGS=(--no-cache)
fi

echo "🔨 Building Docker image..."
docker compose "${COMPOSE_FILES[@]}" "${PROFILE_ARGS[@]}" build "${BUILD_ARGS[@]}"

echo "🚀 Starting engine..."
# --remove-orphans cleans up containers from the *other* mode's profile so a
# single-process↔isolated switch never leaves a stale 'api' (or port-bound
# engine) container behind holding API_PORT.
docker compose "${COMPOSE_FILES[@]}" "${PROFILE_ARGS[@]}" up -d --remove-orphans

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Status:"
docker compose "${COMPOSE_FILES[@]}" "${PROFILE_ARGS[@]}" ps

# ---------------------------------------------------------------------------
# Post-deploy smoke check — poll the API health endpoint so a container that
# fails to come up is caught here instead of via a user screenshot.  Loopback
# only (nginx proxies the same port).  Non-fatal: the engine's healthcheck has
# a 60s start_period, so we warn rather than fail to avoid false negatives on a
# slow boot — but the loud banner makes a genuine failure impossible to miss.
# ---------------------------------------------------------------------------
_api_port="$(grep -E '^API_PORT=' .env 2>/dev/null | cut -d= -f2)"
_api_port="${_api_port:-8000}"
echo ""
echo "🩺 Health check on 127.0.0.1:${_api_port}/api/health (up to 90s)..."
_ok=false
for _i in $(seq 1 18); do
    if curl -fsS --max-time 5 "http://127.0.0.1:${_api_port}/api/health" >/dev/null 2>&1; then
        _ok=true
        break
    fi
    sleep 5
done
if [ "$_ok" = true ]; then
    echo "✅ API health 200 — deploy verified."
else
    echo "⚠️  API did not return 200 within 90s. Investigate:"
    echo "    docker compose ${COMPOSE_FILES[*]} ${PROFILE_ARGS[*]} ps"
    echo "    docker logs 360scalp-v2-api --tail 50"
    echo "    docker logs 360scalp-v2-engine --tail 50"
fi
echo ""
echo "📋 Useful commands (single-process mode):"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml logs -f engine"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml restart engine"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml down"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml up -d --build"
