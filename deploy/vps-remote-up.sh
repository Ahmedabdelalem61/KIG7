#!/usr/bin/env bash
# From your dev machine (after the VPS has your public key in authorized_keys):
#   cd /path/to/KIG7
#   export KIG7_SSH_HOST=185.196.21.19 KIG7_SSH_USER=root
#   export KIG7_SSH_KEY="$HOME/.ssh/id_ed25519_kig7_deploy"
#   bash deploy/vps-remote-up.sh
#
# Installs / updates repo on staging, copies dump + filestore, runs restore.sh, smoke curl.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

HOST="${KIG7_SSH_HOST:-185.196.21.19}"
USER="${KIG7_SSH_USER:-root}"
KEY="${KIG7_SSH_KEY:-$HOME/.ssh/id_ed25519_kig7_deploy}"
INSTALL="${KIG7_INSTALL_DIR:-/opt/kig7-odoo18}"
BRANCH="${KIG7_GIT_BRANCH:-staging}"
REPO_URL="${KIG7_REPO_URL:-https://github.com/Amrorg26/KIG7.git}"

SSH=(ssh -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 "${USER}@${HOST}")
SCP=(scp -i "$KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15)

DUMP="deploy/artifacts/kig7_18c_hr_project_test.dump"
FS="deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz"
for f in "$DUMP" "$FS"; do
  if [[ ! -f "$f" ]]; then
    echo "Missing $f — export backup first (see deploy/README.md)."
    exit 1
  fi
done

if [[ ! -f "$KEY" ]]; then
  echo "Missing SSH private key: $KEY"
  exit 1
fi

echo "Testing SSH to ${USER}@${HOST}..."
if ! "${SSH[@]}" 'echo ok' >/dev/null; then
  echo "SSH failed. Add this public key to the server (${USER} authorized_keys or provider panel):"
  echo
  cat "${KEY}.pub" 2>/dev/null || true
  echo
  exit 1
fi

REMOTE_ART="/tmp/kig7-artifacts-$$"
echo "Uploading artifacts..."
"${SCP[@]}" "$DUMP" "${USER}@${HOST}:${REMOTE_ART}.dump"
"${SCP[@]}" "$FS" "${USER}@${HOST}:${REMOTE_ART}.tgz"

echo "Provisioning on server (branch ${BRANCH})..."
"${SSH[@]}" bash <<REMOTE
set -euo pipefail
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Engine + Compose v2, then re-run this script."
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "'docker compose' not available. Install the Compose plugin."
  exit 1
fi
mkdir -p "$INSTALL"
cd "$INSTALL"
if [[ -d src/.git ]]; then
  cd src
  git fetch origin "$BRANCH"
  git checkout "$BRANCH"
  git pull origin "$BRANCH"
else
  rm -rf src
  git clone --branch "$BRANCH" --depth 1 "$REPO_URL" src
  cd src
fi
mkdir -p deploy/artifacts
mv "${REMOTE_ART}.dump" deploy/artifacts/kig7_18c_hr_project_test.dump
mv "${REMOTE_ART}.tgz" deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz
if [[ ! -f .env ]]; then
  cp .env.example .env
fi
docker compose pull
bash deploy/restore.sh
docker compose ps
curl -sI -o /dev/null -w "%{http_code}" http://127.0.0.1:8073/web/login || true
echo
echo "Done. Odoo should listen on host port 8073 (see ODOO_PUBLISH_PORT in .env)."
REMOTE

echo "Remote provisioning finished."
