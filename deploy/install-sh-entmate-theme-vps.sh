#!/usr/bin/env bash
# Pull staging on VPS and install/upgrade sh_entmate_theme (replace hr_uae_backend_theme).
# Run on the server from the directory that contains docker-compose.yml:
#   bash deploy/install-sh-entmate-theme-vps.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

BRANCH="${KIG7_GIT_BRANCH:-staging}"
REMOTE="${KIG7_GIT_REMOTE:-origin}"
DB="${KIG7_DB_NAME:-18c_hr_project_test}"

echo "==> Backup before theme deploy"
bash deploy/backup-manage.sh deploy

echo "==> Git pull ${REMOTE}/${BRANCH}"
git fetch "$REMOTE" "$BRANCH"
git checkout "$BRANCH"
git pull "$REMOTE" "$BRANCH"
git log -1 --oneline

echo "==> Stop web, upgrade modules"
docker compose stop web
docker compose run --rm -T web odoo -c /etc/odoo/odoo.conf \
  -i sh_entmate_theme \
  -u hr_uae_app,sh_entmate_theme \
  -d "$DB" --stop-after-init

echo "==> Optional: uninstall old backend theme if still installed"
docker compose run --rm -T web odoo -c /etc/odoo/odoo.conf \
  --uninstall hr_uae_backend_theme \
  -d "$DB" --stop-after-init || true

echo "==> Start stack"
docker compose up -d web
docker compose restart proxy
sleep 15
curl -sI "http://127.0.0.1:${ODOO_PUBLISH_PORT:-8073}/web/login" | head -3
echo "Done."
