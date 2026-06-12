> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Deployment

## Topology

Dev, staging, and production use the same Docker Compose shape unless overridden externally: PostgreSQL 16, Odoo 18 web image built from `deploy/Dockerfile`, and nginx 1.27 publishing `${ODOO_PUBLISH_PORT:-8073}`.

## Services

| Service | Image/build | Ports | Resources | Notes |
|---|---|---|---|---|
| `db` | `postgres:16` | internal | cpus 3.0, memory 10G, shm 6GB | Env uses `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}`, `${POSTGRES_DB}` placeholders |
| `web` | `deploy/Dockerfile`, image `kig7-odoo18-web:18.0` | exposes 8069/8072 | cpus 6.0, memory 14G, shm 1536MB | Mounts `./HrProject` read-only and config read-only |
| `proxy` | `nginx:1.27-alpine` | `${ODOO_PUBLISH_PORT:-8073}:80` | cpus 1.0, memory 256M | Routes HTTP/websocket to Odoo |

Sources: [../../../docker-compose.yml](../../../docker-compose.yml), [../../../deploy/Dockerfile](../../../deploy/Dockerfile), [../../../deploy/nginx-odoo.conf](../../../deploy/nginx-odoo.conf).

## Environment Requirements

- Docker Compose v2.
- Odoo addons path includes standard Odoo, `/mnt/kig7-addons`, `/mnt/kig7-addons/thirdparty`, and design themes.
- Secrets must be provided outside docs/code as environment variables or deployment secret management.
- Staging DB name used operationally: `18c_hr_project_test`.

## Install / Upgrade / Test Commands

```bash
docker compose build web
docker compose up -d db web proxy
```

Module update pattern:

```bash
docker compose stop web
docker compose run --rm --no-deps web odoo -d <db> -u <modules> --stop-after-init --no-http --workers=0 --max-cron-threads=0
docker compose start web
```

Focused tests:

```bash
docker compose run --rm --no-deps web odoo -d <test-db> -i <modules> --test-enable --stop-after-init --no-http --workers=0 --max-cron-threads=0
```

## Backup And Restore

Backup:

```bash
docker compose exec db pg_dump -U ${POSTGRES_USER:-odoo} -Fc <db> > backup.dump
```

Restore:

```bash
docker compose exec -T db pg_restore -U ${POSTGRES_USER:-odoo} -d <db> --clean --if-exists < backup.dump
```

## Rollback

1. Stop web.
2. Restore the pre-deploy dump.
3. Check out the known-good git commit.
4. Rebuild/restart web and proxy.
5. Verify login and module state.

## Post-Deploy Verification

- HTTP 200 or login page at `/web/login` through nginx port 8073.
- Module update log has no traceback.
- FX cron exists and is active.
- Smoke: login, employee list, contract form Converted tab, payslip compute, dashboard load, access-role blocked apps.
