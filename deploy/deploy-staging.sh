#!/usr/bin/env bash
# Pre-deploy backup + git pull for KIG7 staging. Does not build/upgrade Odoo.
# Run from repo root: bash deploy/deploy-staging.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BRANCH="${KIG7_GIT_BRANCH:-staging}"
REMOTE="${KIG7_GIT_REMOTE:-origin}"

echo "==> Online backup before deploy"
bash deploy/backup-manage.sh deploy

echo "==> Fetch and pull ${REMOTE}/${BRANCH}"
git fetch "$REMOTE" "$BRANCH"
git checkout "$BRANCH"
git pull "$REMOTE" "$BRANCH"
git log -1 --oneline

echo "Done. Continue with: docker compose build web && docker compose up -d"
echo "Module upgrades: see deploy/VPS_RUNBOOK.md or your deploy checklist."
