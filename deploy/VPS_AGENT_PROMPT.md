# Copy-paste prompt for the agent on the VPS

Use the block below as the **user message** for an agent that has shell access on the staging server (root in `docker` group is fine).

---

You are on a Linux VPS with Docker Engine and Docker Compose v2 already installed. Bring up **Odoo 18 + PostgreSQL** for the KIG7 HrProject stack.

### 1. Clone the public repo (no GitHub auth)

```bash
sudo mkdir -p /opt/kig7-odoo18 && sudo chown -R "$USER:$USER" /opt/kig7-odoo18
cd /opt/kig7-odoo18
git clone --branch staging https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git .
```

If `/opt/kig7-odoo18` is not empty, remove only stale content you are sure is disposable, or clone into a new directory.

### 2. Put the Odoo backup zip in place

The repo expects an **Odoo native backup** zip (contains `dump.sql`, `filestore/`, `manifest.json`). Default filename the restore script looks for:

`deploy/artifacts/18c_hr_project_test_2026-05-13_03-21-27.zip`

Either:

- Copy that file from the operator’s machine with `scp` into `/opt/kig7-odoo18/deploy/artifacts/`, **or**
- Download it to that path, **or**
- Place any path and export `ODOO_BACKUP_ZIP=/full/path/to/the.zip` before running the restore script.

### 3. Odoo master password (`admin_passwd`)

Do **not** put your real master password in a public GitHub repo. After clone, set it **only on this server** (the operator will tell you the value out-of-band, e.g. in a private message):

```bash
cd /opt/kig7-odoo18
nano configs/docker.odoo.conf
# set: admin_passwd = <value from operator>
```

Or a one-liner when `MASTER_PASS` is exported in the shell session (value not logged in git):

```bash
cd /opt/kig7-odoo18
sed -i "s/^admin_passwd = .*/admin_passwd = ${MASTER_PASS}/" configs/docker.odoo.conf
```

### 4. Postgres password in sync

```bash
cd /opt/kig7-odoo18
cp .env.example .env
# Edit .env: set a strong POSTGRES_PASSWORD
# Set configs/docker.odoo.conf db_password to the SAME value as POSTGRES_PASSWORD
```

### 5. Pull images and restore from the zip

```bash
cd /opt/kig7-odoo18
docker compose pull
bash deploy/restore_from_odoo_zip.sh
```

If the zip is not at the default path, run:

`ODOO_BACKUP_ZIP=/full/path/to/18c_hr_project_test_2026-05-13_03-21-27.zip bash deploy/restore_from_odoo_zip.sh`

### 6. Verify

```bash
docker compose ps
curl -sI "http://127.0.0.1:${ODOO_PUBLISH_PORT:-8073}/web/login" | head -5
```

Use the port from `.env` (`ODOO_PUBLISH_PORT`, default **8073**).

### 7. Login

Use an Odoo user that exists **inside the restored database**. The master password above is for **Manage databases** / neutralized DB operations, not the normal login password.

### Constraints

- Do **not** commit `.env`, backup zips, or edited secrets back to GitHub.
- If restore fails, capture `docker compose logs db` and `docker compose logs web` and fix before retrying (e.g. `docker compose down -v` only if a full reset is acceptable).

---

_End of prompt._
