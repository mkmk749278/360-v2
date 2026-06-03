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
# ---------------------------------------------------------------------------
echo "🔨 Building Docker image..."
docker compose "${COMPOSE_FILES[@]}" "${PROFILE_ARGS[@]}" build --no-cache

echo "🚀 Starting engine..."
docker compose "${COMPOSE_FILES[@]}" "${PROFILE_ARGS[@]}" up -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Status:"
docker compose "${COMPOSE_FILES[@]}" "${PROFILE_ARGS[@]}" ps
echo ""
echo "📋 Useful commands (single-process mode):"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml logs -f engine"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml restart engine"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml down"
echo "  docker compose -f docker-compose.yml -f docker-compose.singleprocess.yml up -d --build"
