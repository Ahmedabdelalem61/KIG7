# Copy-paste prompt for the agent on the VPS

Use the block below as the **user message** for an agent that has shell access on the staging server (root in `docker` group is fine).

---

You are on a Linux VPS with Docker Engine and Docker Compose v2 already installed. Bring up **Odoo 18 + PostgreSQL** for the KIG7 HrProject stack.

### 1. Clone the private GitHub repo (auth required)

The repo **Ahmedabdelalem61/KIG7-odoo18-staging** is **private**. Pick **one**:

**A — Deploy key (recommended)**  
1. On the VPS: `ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519_kig7_readonly`  
2. In GitHub: repo **Settings → Deploy keys → Add deploy key** (read-only), paste `~/.ssh/id_ed25519_kig7_readonly.pub`  
3. Clone:

```bash
sudo mkdir -p /opt/kig7-odoo18 && sudo chown -R "$USER:$USER" /opt/kig7-odoo18
cd /opt/kig7-odoo18
GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_kig7_readonly -o IdentitiesOnly=yes' \
  git clone --branch staging git@github.com:Ahmedabdelalem61/KIG7-odoo18-staging.git .
```

**B — HTTPS + PAT** (fine-grained or classic with repo read): use `read -s TOKEN`, then  
`git clone --branch staging "https://x-access-token:${TOKEN}@github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git .`  
then `unset TOKEN`.

If `/opt/kig7-odoo18` is not empty, remove only disposable content first, or clone into a new directory.

### 2. Odoo backup zip

The default backup zip is **tracked in git** at `deploy/artifacts/18c_hr_project_test_2026-05-13_03-21-27.zip` after a successful clone. If it is missing, copy it with `scp` or set `ODOO_BACKUP_ZIP` to a full path before restore.

### 3. Odoo master password (`admin_passwd`)

Do **not** commit your real master password into **git** (it would be visible to anyone with repo access). After clone, set it **only on this server** (the operator will tell you the value out-of-band, e.g. in a private message):

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

- Do **not** commit `.env` or local-only secrets. The staging DB zip may already be in the repo; do not add new sensitive blobs without team agreement.
- If restore fails, capture `docker compose logs db` and `docker compose logs web` and fix before retrying (e.g. `docker compose down -v` only if a full reset is acceptable).

---

_End of prompt._
