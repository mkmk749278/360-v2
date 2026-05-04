#!/usr/bin/env bash
# Termux SSH setup for GitHub — one-time configuration.
#
# After running this once and pasting the public key into GitHub, every
# `git pull` / `git push` from Termux is silent — no username, no token,
# no expiry.  Replaces the HTTPS + Personal-Access-Token flow which
# requires re-entering credentials.
#
# Usage:
#   curl -fsSLO https://raw.githubusercontent.com/mkmk749278/360-v2/main/tools/termux-git-ssh-setup.sh
#   bash termux-git-ssh-setup.sh
#
# What it does:
#   1. Installs openssh in Termux (idempotent)
#   2. Generates an ed25519 SSH key if one doesn't exist
#   3. Prints the public key for you to paste into GitHub once
#   4. Switches your existing 360-v2 + lumin-app remotes from HTTPS to SSH
#   5. Tests the connection
#
# Designed to be safe to re-run.
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}━━━ Termux GitHub SSH setup ━━━${NC}"
echo

# 1) Install openssh ----------------------------------------------------
if ! command -v ssh-keygen >/dev/null 2>&1; then
  echo "→ Installing openssh in Termux…"
  pkg install -y openssh
else
  echo -e "${GREEN}✓${NC} openssh already installed"
fi

# 2) Ensure ~/.ssh exists with correct permissions ----------------------
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

KEY_PATH="$HOME/.ssh/id_ed25519"
PUB_PATH="${KEY_PATH}.pub"

# 3) Generate key if missing -------------------------------------------
if [ -f "$KEY_PATH" ]; then
  echo -e "${GREEN}✓${NC} SSH key already exists at $KEY_PATH"
else
  echo "→ Generating ed25519 SSH key (no passphrase — pushes will be silent)…"
  # -N "" = no passphrase.  Trade-off: anyone with the phone unlocked can
  # push.  Acceptable on a personal phone; reconsider for shared devices.
  ssh-keygen -t ed25519 -C "$(whoami)@termux-$(date +%Y%m%d)" \
    -f "$KEY_PATH" -N "" >/dev/null
  echo -e "${GREEN}✓${NC} Key generated"
fi

# 4) Configure SSH client to use the key for github.com ----------------
SSH_CONFIG="$HOME/.ssh/config"
touch "$SSH_CONFIG"
chmod 600 "$SSH_CONFIG"

if ! grep -q "Host github.com" "$SSH_CONFIG" 2>/dev/null; then
  echo "→ Adding github.com block to ~/.ssh/config…"
  cat >> "$SSH_CONFIG" <<EOF

Host github.com
  HostName github.com
  User git
  IdentityFile ${KEY_PATH}
  IdentitiesOnly yes
EOF
  echo -e "${GREEN}✓${NC} ~/.ssh/config updated"
else
  echo -e "${GREEN}✓${NC} github.com already in ~/.ssh/config"
fi

# 5) Print the public key -----------------------------------------------
echo
echo -e "${YELLOW}━━━ ACTION REQUIRED — paste this into GitHub ━━━${NC}"
echo
echo "Open in your phone browser:"
echo -e "  ${CYAN}https://github.com/settings/ssh/new${NC}"
echo
echo "Title:  Termux phone (any name you'll remember)"
echo "Key type:  Authentication Key"
echo "Key:  paste the line below (everything after this →)"
echo
echo -e "${GREEN}$(cat "$PUB_PATH")${NC}"
echo
echo "Then tap 'Add SSH key' on GitHub."
echo

read -r -p "Press Enter once you've added the key on GitHub… "

# 6) Test the connection ------------------------------------------------
echo
echo "→ Testing SSH connection to GitHub…"
# `ssh -T` returns a non-zero exit code on success too — GitHub doesn't
# allow shell sessions, so we just look for the welcome string.
if ssh -T -o StrictHostKeyChecking=accept-new git@github.com 2>&1 | grep -q "successfully authenticated"; then
  echo -e "${GREEN}✓${NC} SSH authentication works"
else
  echo -e "${RED}✗${NC} SSH test failed.  Likely causes:"
  echo "  - Public key not yet added on GitHub"
  echo "  - Wrong account selected when adding the key"
  echo
  echo "Re-run this script after fixing.  The key is already generated;"
  echo "the script will skip generation and just retry the test."
  exit 1
fi

# 7) Switch existing repo remotes from HTTPS to SSH --------------------
switch_remote() {
  local repo_dir="$1"
  if [ ! -d "$repo_dir/.git" ]; then
    return  # not cloned, skip silently
  fi
  local current
  current=$(git -C "$repo_dir" remote get-url origin 2>/dev/null || echo "")
  if [ -z "$current" ]; then
    return
  fi
  # Already SSH? No-op.
  if [[ "$current" == git@github.com:* ]]; then
    echo -e "${GREEN}✓${NC} $repo_dir already uses SSH remote"
    return
  fi
  # Convert https://github.com/owner/repo(.git) → git@github.com:owner/repo.git
  if [[ "$current" =~ ^https://github\.com/([^/]+)/(.+)$ ]]; then
    local owner="${BASH_REMATCH[1]}"
    local repo="${BASH_REMATCH[2]%.git}"
    local new_url="git@github.com:${owner}/${repo}.git"
    git -C "$repo_dir" remote set-url origin "$new_url"
    echo -e "${GREEN}✓${NC} $repo_dir remote → $new_url"
  fi
}

echo
echo "→ Updating local repo remotes to SSH (silent if not cloned)…"
switch_remote "$HOME/360-v2"
switch_remote "$HOME/lumin-app"

echo
echo -e "${GREEN}━━━ Done ━━━${NC}"
echo
echo "From now on, in either repo:"
echo "  git pull           # silent"
echo "  git push           # silent"
echo "  git fetch          # silent"
echo
echo "If you clone a NEW repo, use the SSH URL not HTTPS:"
echo "  git clone git@github.com:mkmk749278/<repo>.git"
echo
echo "(Or for any repo: tap the green Code button on GitHub → SSH tab)"
