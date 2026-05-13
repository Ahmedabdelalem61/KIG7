# KIG7 — Odoo 18 Docker staging (HrProject)

## What is in this repo

- **`HrProject/`** — UAE HR addons + `thirdparty` + `design-themes` (same layout as local dev).
- **`configs/docker.odoo.conf`** — Odoo options for the **official `odoo:18.0` image** (paths and `db_host=db`).
- **`configs/host-hr_project.conf.reference`** — original developer `addons_path` on a full Odoo tree (reference only; not used in Docker).
- **`docker-compose.yml`** — Postgres 16 + Odoo 18.
- **`deploy/artifacts/`** — place `*.dump` + `*.tgz` here before restore (files are gitignored once present).

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
3. Clone and enter the repo (use branch `staging` or `phase-one-branch` — same Docker layout):

   ```bash
   sudo mkdir -p /opt/kig7-odoo18 && sudo chown "$USER:$USER" /opt/kig7-odoo18
   cd /opt/kig7-odoo18
   git clone --branch staging https://github.com/Amrorg26/KIG7.git .
   # or: git clone --branch phase-one-branch https://github.com/Amrorg26/KIG7.git .
   ```

4. Copy **artifacts** if they are not in the clone (gitignored): use `scp`/`rsync` of `kig7_*.dump` and `kig7_*.tgz` into `deploy/artifacts/`.

5. Environment:

   ```bash
   cp .env.example .env
   # edit .env: set a strong POSTGRES_PASSWORD, then mirror it in configs/docker.odoo.conf (db_password)
   ```

6. **First-time**: build/pull images and restore:

   ```bash
   docker compose pull
   bash deploy/restore.sh
   ```

7. **Smoke test**: `curl -I http://127.0.0.1:8073` (or the port in `.env`). Logs: `docker compose logs -f web`.

8. **Login**: use an Odoo user that exists **in the restored database**. If you need to reset the `admin` user password, use Odoo shell on the `web` container.

## Fresh stack (wipe data)

```bash
docker compose down -v
docker compose pull
bash deploy/restore.sh
```

## Branches

- **`staging`** and **`phase-one-branch`** — same deployment assets; pick either on the server clone.

## Payroll live dashboard SQL fix

The ambiguous `GROUP BY code` in `hr.uae.payroll.live.dashboard` is fixed in `HrProject/hr_uae_payroll/models/hr_uae_payroll_live_dashboard.py` (`GROUP BY sr.id, sr.name, sr.code`). Ensure your checkout includes that change before reporting dashboard errors.
