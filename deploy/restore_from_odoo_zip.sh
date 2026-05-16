#!/usr/bin/env bash
# Restore from an Odoo "native" backup zip (dump.sql + filestore/ + manifest.json).
# Default zip path matches the bundle name used for VPS handoff; override with ODOO_BACKUP_ZIP.
# Run from repo root: bash deploy/restore_from_odoo_zip.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ZIP="${ODOO_BACKUP_ZIP:-deploy/artifacts/18c_hr_project_test_2026-05-16_local.zip}"
DB_NAME="${ODOO_DB_NAME:-18c_hr_project_test}"

if [[ ! -f "$ZIP" ]]; then
  echo "Missing backup zip: $ZIP"
  echo "Copy your Odoo .zip into deploy/artifacts/ or set ODOO_BACKUP_ZIP to the full path."
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"

if [[ ! -f "$TMP/dump.sql" ]]; then
  echo "Invalid Odoo backup: no dump.sql in zip"
  exit 1
fi
if [[ ! -d "$TMP/filestore" ]]; then
  echo "Invalid Odoo backup: no filestore/ directory in zip"
  exit 1
fi

docker compose up -d db
echo "Waiting for Postgres..."
for _ in $(seq 1 60); do
  if docker compose exec -T db pg_isready -U odoo -d postgres >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

docker compose exec -T db dropdb -U odoo --if-exists "$DB_NAME" 2>/dev/null || true
docker compose exec -T db createdb -U odoo "$DB_NAME"

docker compose cp "$TMP/dump.sql" db:/tmp/dump.sql
echo "Loading dump.sql (this may take several minutes)..."
docker compose exec -T db psql -U odoo -d "$DB_NAME" -v ON_ERROR_STOP=1 -f /tmp/dump.sql

docker compose up -d web
sleep 3

docker compose cp "$TMP/filestore" web:/tmp/odoo_zip_filestore
docker compose exec -u root -T web bash -c "
set -e
mkdir -p /var/lib/odoo/filestore
rm -rf /var/lib/odoo/filestore/${DB_NAME}
mkdir -p /var/lib/odoo/filestore/${DB_NAME}
cp -a /tmp/odoo_zip_filestore/. /var/lib/odoo/filestore/${DB_NAME}/
chown -R odoo:odoo /var/lib/odoo/filestore
rm -rf /tmp/odoo_zip_filestore
"

docker compose restart web
echo "Done. Open http://127.0.0.1:${ODOO_PUBLISH_PORT:-8073} — set admin_passwd in configs/docker.odoo.conf if needed."
