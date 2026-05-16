# KIG7 Odoo 18 — Docker staging stack

Technical staging environment for **Odoo 18 Community** with custom addons under `HrProject/`, orchestrated by **Docker Compose v2**.

**Repository (private):** [Ahmedabdelalem61/KIG7-odoo18-staging](https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging) — branch `staging`

| Document | Contents |
|----------|----------|
| [`deploy/README.md`](deploy/README.md) | **Full service reference** — architecture, ports, volumes, deploy, upgrade, backup, restore |
| [`deploy/VPS_RUNBOOK.md`](deploy/VPS_RUNBOOK.md) | VPS provisioning, Git auth, first install |
| [`deploy/SECURITY.md`](deploy/SECURITY.md) | Secrets, access, backup data handling |

## Quick facts

| Item | Value |
|------|--------|
| Default install path (VPS) | `/opt/kig7-odoo18` |
| Compose file | `docker-compose.yml` (repo root) |
| Published HTTP port | `${ODOO_PUBLISH_PORT:-8073}` on host → nginx `proxy` → Odoo `web` |
| Database (staging) | `18c_hr_project_test` (see `configs/docker.odoo.conf`) |
| Odoo image | `odoo:18.0` extended by `deploy/Dockerfile` |
| Postgres image | `postgres:16` |
| Addons mount | `./HrProject` → `/mnt/kig7-addons` (read-only) |

## Minimal operator commands

```bash
cd /opt/kig7-odoo18
docker compose ps
docker compose logs -f web
curl -sI "http://127.0.0.1:${ODOO_PUBLISH_PORT:-8073}/web/login" | head -5
```

**Deploy code (with backup):** `bash deploy/deploy-staging.sh` then build/upgrade per [`deploy/README.md`](deploy/README.md).

**Daily backups:** systemd timer `kig7-odoo18-backup.timer` (05:00 UTC) — see deploy README § Backup management.

Branches **`staging`** and **`phase-one-branch`** share the same Docker layout.
