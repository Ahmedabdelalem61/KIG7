#!/usr/bin/env bash
# Restore PostgreSQL custom dump + filestore into the Docker volumes used by docker-compose.yml.
# Run from repo root: bash deploy/restore.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DUMP="deploy/artifacts/kig7_18c_hr_project_test.dump"
FS="deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz"
if [[ ! -f "$DUMP" ]]; then
  echo "Missing $DUMP — copy pg_dump output there first."
  exit 1
fi
if [[ ! -f "$FS" ]]; then
  echo "Missing $FS — copy filestore tarball there first."
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

docker compose cp "$DUMP" db:/tmp/restore.dump

echo "Dropping existing DB if present..."
docker compose exec -T db dropdb -U odoo --if-exists 18c_hr_project_test 2>/dev/null || true

echo "Restoring (ignore harmless owner/ACL warnings)..."
docker compose exec -T db pg_restore -U odoo -d postgres --create --no-owner --no-acl --verbose /tmp/restore.dump 2>&1 | tail -80

docker compose up -d web
sleep 3

docker compose cp "$FS" web:/tmp/fs.tgz
docker compose exec -u root -T web bash -c 'mkdir -p /var/lib/odoo/filestore && tar -xzf /tmp/fs.tgz -C /var/lib/odoo/filestore && chown -R odoo:odoo /var/lib/odoo'

docker compose restart web
echo "Done. Open http://127.0.0.1:8073 (or the host port from docker-compose / .env)."
