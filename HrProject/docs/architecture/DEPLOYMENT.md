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

## Windows Two-Stack One-Click Deploy

Windows deployments can run staging and live side by side from the same repository using Compose project names:

| Stack | Compose project | Port | Database source |
|---|---|---:|---|
| Staging | `kig7-staging` | `8073` | Restored backup dump and filestore |
| Live | `kig7-live` | `8074` | Fresh init with `-i hr_uae_app,hr_uae_init_data` |

Entry point: [../../../deploy/windows/Deploy-Kig7.ps1](../../../deploy/windows/Deploy-Kig7.ps1).

The script validates/builds Compose, restores staging from `deploy/windows/artifacts/kig7_db.dump` and `deploy/windows/artifacts/kig7_filestore.tgz`, initializes the live database, starts both nginx proxies, and smoke-tests `/web/login` on both ports. Timestamped logs are written under `deploy/windows/` by default.

Backups remain external to git. Before production use, copy the current database dump and filestore archive to secure storage, keep `POSTGRES_PASSWORD` aligned with [../../../configs/docker.odoo.conf](../../../configs/docker.odoo.conf), and rotate any default KIG7 user passwords.

Rollback is stack-specific: stop the affected project with `docker compose -p <project> --env-file deploy/windows/<env>.env down`, restore the prior dump/filestore for staging or recreate live from a known-good code revision, then rerun the script. Use `down -v` only when intentionally deleting that stack's database and filestore volumes.
