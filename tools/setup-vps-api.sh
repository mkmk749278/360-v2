#!/usr/bin/env bash
# setup-vps-api.sh — Stand up the Lumin API behind nginx + Let's Encrypt.
#
# Idempotent.  Re-run after changes to refresh the nginx config or rotate
# the auth token (with --rotate-token).  Run on the VPS as root, AFTER
# the engine container is already deployed via deploy_vps.sh.
#
# Usage:
#   sudo bash tools/setup-vps-api.sh                # first-time setup
#   sudo bash tools/setup-vps-api.sh --rotate-token # mint a fresh token
#   sudo bash tools/setup-vps-api.sh --domain api.example.com --email me@example.com
#
# Required env or args:
#   --domain        DNS name pointing at this VPS (default api.luminapp.org)
#   --email         Email for Let's Encrypt registration / renewal alerts
#   --no-cert       Skip Let's Encrypt (HTTP-only — for testing on private nets)
#   --rotate-token  Generate a new API_AUTH_TOKEN and restart the engine
set -euo pipefail

# ─── Output helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'
BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅  $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $*${NC}"; }
err()  { echo -e "${RED}❌  $*${NC}" >&2; }
info() { echo -e "${CYAN}ℹ️   $*${NC}"; }
hdr()  { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════════${NC}"; \
         echo -e "${BOLD}${CYAN}  $*${NC}"; \
         echo -e "${BOLD}${CYAN}══════════════════════════════════════════════${NC}"; }

# ─── Defaults ──────────────────────────────────────────────────────────────────
DOMAIN="${API_DOMAIN:-api.luminapp.org}"
EMAIL="${API_LE_EMAIL:-}"
SKIP_CERT=false
ROTATE_TOKEN=false
ENGINE_DIR="${ENGINE_DIR:-/opt/360-v2}"
NGINX_SITE="lumin-api"

# ─── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --domain)       DOMAIN="$2"; shift 2 ;;
        --email)        EMAIL="$2"; shift 2 ;;
        --engine-dir)   ENGINE_DIR="$2"; shift 2 ;;
        --no-cert)      SKIP_CERT=true; shift ;;
        --rotate-token) ROTATE_TOKEN=true; shift ;;
        -h|--help)
            sed -n '2,15p' "$0"
            exit 0
            ;;
        *)
            err "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# ─── Pre-flight ────────────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    err "Run as root: sudo bash tools/setup-vps-api.sh"
    exit 1
fi

if [[ ! -d "$ENGINE_DIR" ]]; then
    err "Engine dir not found: $ENGINE_DIR"
    err "Run deploy_vps.sh first, then re-run this script."
    err "Or override with --engine-dir /path/to/repo"
    exit 1
fi

cd "$ENGINE_DIR"
if [[ ! -f docker-compose.yml ]] || [[ ! -f .env ]]; then
    err "$ENGINE_DIR is missing docker-compose.yml or .env"
    err "Run deploy_vps.sh first, then re-run this script."
    exit 1
fi

# ─── Helpers ───────────────────────────────────────────────────────────────────
upsert_env() {
    # upsert_env KEY VALUE  — set or update KEY=VALUE in .env (idempotent)
    local key="$1" val="$2"
    if grep -q "^${key}=" .env 2>/dev/null; then
        # Use a different delimiter because tokens may contain slashes
        sed -i "s|^${key}=.*|${key}=${val}|" .env
    else
        echo "${key}=${val}" >> .env
    fi
}

read_env() {
    # read_env KEY  — print current .env value for KEY (empty string if unset)
    local key="$1"
    grep -E "^${key}=" .env 2>/dev/null | head -1 | cut -d'=' -f2- || true
}

# ─── PHASE 1 — API auth token ──────────────────────────────────────────────────
hdr "PHASE 1 — API auth token"

CURRENT_TOKEN="$(read_env API_AUTH_TOKEN)"
if [[ "$ROTATE_TOKEN" == "true" ]] || [[ -z "$CURRENT_TOKEN" ]]; then
    if [[ -z "$CURRENT_TOKEN" ]]; then
        info "No API_AUTH_TOKEN found — generating a fresh one."
    else
        warn "Rotating API_AUTH_TOKEN — clients with the old token will start getting 401."
    fi
    NEW_TOKEN="$(openssl rand -hex 32)"
    upsert_env API_AUTH_TOKEN "$NEW_TOKEN"
    ok "API_AUTH_TOKEN set in .env"
    echo
    echo -e "${BOLD}${YELLOW}YOUR NEW API TOKEN (store securely — only shown once):${NC}"
    echo
    echo "    $NEW_TOKEN"
    echo
else
    ok "Existing API_AUTH_TOKEN preserved (use --rotate-token to mint a new one)"
fi

upsert_env API_ENABLED true
upsert_env API_HOST 0.0.0.0
upsert_env API_PORT 8000
ok "API_ENABLED=true, API_HOST=0.0.0.0, API_PORT=8000"

# ─── PHASE 2 — nginx + certbot install ─────────────────────────────────────────
hdr "PHASE 2 — install nginx + certbot"

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
PKGS="nginx"
if [[ "$SKIP_CERT" == "false" ]]; then
    PKGS="$PKGS certbot python3-certbot-nginx"
fi
apt-get install -y -qq $PKGS >/dev/null
ok "nginx + certbot installed"

# Ensure nginx is enabled
systemctl enable nginx --quiet
systemctl start nginx

# ─── PHASE 3 — write nginx site config ─────────────────────────────────────────
hdr "PHASE 3 — nginx site for $DOMAIN"

# Rate-limit zone — 60 req/min/IP shared across all locations
# Lives in /etc/nginx/conf.d so it's loaded before sites.
cat > /etc/nginx/conf.d/lumin-api-ratelimit.conf <<'EOF_RATELIMIT'
# Lumin API rate limit — 60 requests/min/IP, burst 30 with no delay.
# Trade-off: tight enough to fend off scrapers, loose enough that a
# foreground app refreshing every 10s never hits the cap.
limit_req_zone $binary_remote_addr zone=lumin_api:10m rate=60r/m;
EOF_RATELIMIT

cat > "/etc/nginx/sites-available/$NGINX_SITE" <<EOF_SITE
# Lumin API — generated by tools/setup-vps-api.sh
# Don't hand-edit; re-run the script with new flags instead.
upstream lumin_api_upstream {
    server 127.0.0.1:8000;
    keepalive 16;
}

# Pre-cert HTTP server.  Once certbot runs it'll inject the 443 server
# block in place; the http→https redirect is added by certbot too.
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    # ACME challenges (lets-encrypt) need to reach the filesystem.
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        # Health-check stays cheap and unauthenticated.
        limit_req zone=lumin_api burst=30 nodelay;
        proxy_pass http://lumin_api_upstream;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 5s;

        # CORS preflight for the Lumin app.  GET/POST only — same as the
        # FastAPI app's CORS allow-list.  Browsers / WebView clients send
        # OPTIONS first; we answer them at the proxy layer to keep the
        # FastAPI handler chain short.
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            add_header 'Access-Control-Max-Age' 86400;
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Block obvious WordPress / vuln-scanner probes early so they don't
    # tie up FastAPI handlers.
    location ~* \\.(php|asp|aspx|jsp)\$ { return 444; }
    location ~ /\\.(git|env|svn|htaccess) { return 444; }

    access_log /var/log/nginx/lumin-api.access.log;
    error_log  /var/log/nginx/lumin-api.error.log warn;
}
EOF_SITE

# Activate site
ln -sf "/etc/nginx/sites-available/$NGINX_SITE" "/etc/nginx/sites-enabled/$NGINX_SITE"

# Remove default site if it exists (otherwise nginx serves the welcome page
# on the same IP and Let's Encrypt's HTTP-01 challenge can hit it instead).
if [[ -f /etc/nginx/sites-enabled/default ]]; then
    rm -f /etc/nginx/sites-enabled/default
    info "Removed default nginx site"
fi

# Validate + reload
if nginx -t 2>&1 | grep -q "successful"; then
    systemctl reload nginx
    ok "nginx reloaded with $NGINX_SITE site"
else
    err "nginx config test failed:"
    nginx -t
    exit 1
fi

# ─── PHASE 4 — Let's Encrypt cert ──────────────────────────────────────────────
hdr "PHASE 4 — Let's Encrypt cert"

if [[ "$SKIP_CERT" == "true" ]]; then
    warn "Skipping cert (--no-cert) — API will be HTTP-only on $DOMAIN"
elif [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    ok "Cert already exists for $DOMAIN — certbot will auto-renew"
else
    if [[ -z "$EMAIL" ]]; then
        warn "No --email given — using --register-unsafely-without-email"
        certbot --nginx -n --agree-tos --register-unsafely-without-email -d "$DOMAIN"
    else
        certbot --nginx -n --agree-tos --email "$EMAIL" -d "$DOMAIN"
    fi
    ok "Cert provisioned for $DOMAIN"
fi

# ─── PHASE 5 — restart engine to pick up API_ENABLED ───────────────────────────
hdr "PHASE 5 — restart engine"

if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    docker compose up -d --build engine 2>&1 | tail -10
    ok "engine container rebuilt + restarted"
elif command -v docker-compose &>/dev/null; then
    docker-compose up -d --build engine 2>&1 | tail -10
    ok "engine container rebuilt + restarted"
else
    warn "Docker not found — restart the engine manually so .env changes take effect"
fi

# Give the engine a moment to bind to port 8000
sleep 5

# ─── PHASE 6 — smoke test ──────────────────────────────────────────────────────
hdr "PHASE 6 — smoke test"

TOKEN="$(read_env API_AUTH_TOKEN)"
SCHEME="https"
[[ "$SKIP_CERT" == "true" ]] && SCHEME="http"

# Health endpoint — no auth
HEALTH_URL="$SCHEME://$DOMAIN/api/health"
info "GET $HEALTH_URL"
HEALTH_CODE="$(curl -ks -o /tmp/api-health.json -w '%{http_code}' "$HEALTH_URL" || echo 000)"
if [[ "$HEALTH_CODE" == "200" ]]; then
    ok "health: $HEALTH_CODE — $(cat /tmp/api-health.json)"
else
    err "health check FAILED: HTTP $HEALTH_CODE"
    err "  body: $(cat /tmp/api-health.json 2>/dev/null || echo '<empty>')"
    err "  Check: docker compose logs engine | tail -50"
    exit 1
fi

# Pulse endpoint — auth required
PULSE_URL="$SCHEME://$DOMAIN/api/pulse"
info "GET $PULSE_URL  (with bearer)"
PULSE_CODE="$(curl -ks -o /tmp/api-pulse.json -w '%{http_code}' \
    -H "Authorization: Bearer $TOKEN" "$PULSE_URL" || echo 000)"
if [[ "$PULSE_CODE" == "200" ]]; then
    ok "pulse: $PULSE_CODE — auth working"
else
    err "pulse check FAILED: HTTP $PULSE_CODE"
    err "  body: $(cat /tmp/api-pulse.json 2>/dev/null || echo '<empty>')"
    exit 1
fi

# ─── Done ──────────────────────────────────────────────────────────────────────
hdr "✅  Lumin API is live"

cat <<EOF_DONE

API base URL:    ${SCHEME}://$DOMAIN/api
Health:          ${SCHEME}://$DOMAIN/api/health   (no auth)
Pulse:           ${SCHEME}://$DOMAIN/api/pulse    (Bearer auth)

Auth header for Lumin app:
    Authorization: Bearer \$(grep ^API_AUTH_TOKEN= $ENGINE_DIR/.env | cut -d= -f2-)

Logs:
    /var/log/nginx/lumin-api.access.log
    /var/log/nginx/lumin-api.error.log
    docker compose logs -f engine

Next steps:
  1. Save the token shown above in your password manager.
  2. Configure Lumin v0.0.5 with the base URL + token (Menu → API keys).
  3. To rotate the token later:  sudo bash tools/setup-vps-api.sh --rotate-token

EOF_DONE
