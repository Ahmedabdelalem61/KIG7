# KIG7 — Odoo 18 Docker staging (HrProject)

## What is in this repo

- **`HrProject/`** — UAE HR addons + `thirdparty` + `design-themes` (same layout as local dev).
- **`configs/docker.odoo.conf`** — Odoo options (paths and `db_host=db`); used by the **web** service built from [`deploy/Dockerfile`](Dockerfile) (extends `odoo:18.0`).
- **`configs/host-hr_project.conf.reference`** — original developer `addons_path` on a full Odoo tree (reference only; not used in Docker).
- **`docker-compose.yml`** — Postgres 16 + Odoo 18 (`web` image built from `deploy/Dockerfile`).
- **`deploy/artifacts/`** — place `*.dump` + `*.tgz` here before restore (files are gitignored once present). The **Odoo UI backup** zip `18c_hr_project_test_2026-05-13_03-21-27.zip` is **committed** in this repo for easy VPS clone (contains real DB data — restrict repo access; repo is **private**).

## Restore from Odoo UI backup (`.zip` with `dump.sql` + `filestore/`)

Place the zip under `deploy/artifacts/` (default name `18c_hr_project_test_2026-05-13_03-21-27.zip`) or set `ODOO_BACKUP_ZIP` to its path, then from repo root:

```bash
docker compose pull db
docker compose build web
bash deploy/restore_from_odoo_zip.sh
```

Use `ODOO_DB_NAME` if the database name inside the zip differs from `18c_hr_project_test`. For `pg_dump -Fc` + `.tgz` filestore instead, use `deploy/restore.sh`.

## Local backup export (already done once for this bundle)

From a machine that has the dev DB and filestore:

```bash
export PGPASSWORD=...
pg_dump -h localhost -U USER -Fc -f deploy/artifacts/kig7_18c_hr_project_test.dump 18c_hr_project_test
tar -czf deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz -C ~/.local/share/Odoo-Community/filestore 18c_hr_project_test
```

## Run on the VPS (separate folder, e.g. `/opt/kig7-odoo18`)

1. **Do not paste production passwords into chat.** Use SSH keys. See `deploy/SECURITY.md`.
2. Install Docker Engine + Compose plugin (distro docs).
3. Clone and enter the repo (branch `staging` or `phase-one-branch`). The GitHub repo is **private** — use a **deploy key** or **HTTPS + PAT** on the server (see `deploy/VPS_RUNBOOK.md` §2a). Example with an existing credential helper:

   ```bash
   sudo mkdir -p /opt/kig7-odoo18 && sudo chown "$USER:$USER" /opt/kig7-odoo18
   cd /opt/kig7-odoo18
   git clone --branch staging https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git .
   # or: git clone --branch phase-one-branch https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git .
   ```

4. **Backup files:** the committed Odoo **`.zip`** is already under `deploy/artifacts/` after clone. For **`pg_dump -Fc` + `.tgz`** only, copy those into `deploy/artifacts/` (they stay gitignored) and use `deploy/restore.sh` instead of `restore_from_odoo_zip.sh`.

5. Environment:

   ```bash
   cp .env.example .env
   # edit .env: set a strong POSTGRES_PASSWORD, then mirror it in configs/docker.odoo.conf (db_password)
   ```

6. **First-time**: pull images and restore (pick one):

   **From Odoo `.zip`** (`dump.sql` + `filestore/` in `deploy/artifacts/`):

   ```bash
   docker compose pull db
   docker compose build web
   bash deploy/restore_from_odoo_zip.sh
   ```

   **From `pg_dump -Fc` + filestore `.tgz`:**

   ```bash
   docker compose pull db
   docker compose build web
   bash deploy/restore.sh
   ```

7. **Smoke test**: `curl -I http://127.0.0.1:8073` (or the port in `.env`). Logs: `docker compose logs -f web`.

8. **Login**: use an Odoo user that exists **in the restored database**. If you need to reset the `admin` user password, use Odoo shell on the `web` container.

## Fresh stack (wipe data)

```bash
docker compose down -v
docker compose pull db
docker compose build web
bash deploy/restore_from_odoo_zip.sh
# or: bash deploy/restore.sh
```

## Branches

- **`staging`** and **`phase-one-branch`** — same deployment assets; pick either on the server clone.

## Payroll live dashboard SQL fix

The ambiguous `GROUP BY code` in `hr.uae.payroll.live.dashboard` is fixed in `HrProject/hr_uae_payroll/models/hr_uae_payroll_live_dashboard.py` (`GROUP BY sr.id, sr.name, sr.code`). Ensure your checkout includes that change before reporting dashboard errors.
