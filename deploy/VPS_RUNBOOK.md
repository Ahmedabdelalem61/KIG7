# VPS runbook (185.196.21.19 or any host)

**Canonical repo (private):** `https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git` — branch `staging`. Anonymous `git clone` will fail; use a **deploy key**, **HTTPS + PAT**, or a **tarball** (§2a).

These steps assume **SSH access** with keys (see `SECURITY.md`). Do **not** store root passwords in repositories.

## 0. One-shot from your workstation (optional)

If your laptop has SSH key access to the server, generate a deploy key (once), add the **public** key to the server’s `authorized_keys`, then from the repo root:

```bash
export KIG7_SSH_HOST=185.196.21.19 KIG7_SSH_USER=root
export KIG7_SSH_KEY="$HOME/.ssh/id_ed25519_kig7_deploy"
bash deploy/vps-remote-up.sh
```

See `deploy/vps-remote-up.sh` for variables (`KIG7_INSTALL_DIR`, `KIG7_GIT_BRANCH`, etc.).

## 1. Install Docker (if missing)

Use your distribution’s Docker Engine + Compose v2 guide (Ubuntu/Debian: `docker.io` + `docker-compose-plugin` or Docker’s official repo).

## 2. Isolated install directory

```bash
sudo install -d -o "$USER" -g "$USER" /opt/kig7-odoo18
cd /opt/kig7-odoo18
```

## 2a. Private GitHub — why `git clone` says “Repository not found”

If **anonymous** `git clone https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git` (or another private URL) returns **Repository not found** / API **404**, GitHub is rejecting unauthenticated access. Your laptop can still clone because **GitHub credentials** are stored there (credential helper, SSH agent, or `gh auth`), while the VPS has **none**.

Pick **one** approach:

1. **Deploy key (recommended on servers)**  
   - On the VPS: `ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519_kig7_readonly`  
   - Repo **Settings → Deploy keys → Add deploy key**: paste `~/.ssh/id_ed25519_kig7_readonly.pub`, enable **read-only**.  
   - Clone (example: code directly under `/opt/kig7-odoo18`):

     ```bash
     cd /opt/kig7-odoo18
     GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519_kig7_readonly -o IdentitiesOnly=yes' \
       git clone --branch staging git@github.com:Ahmedabdelalem61/KIG7-odoo18-staging.git .
     ```

2. **HTTPS + personal access token (classic or fine‑grained with repo read)**  
   Do **not** commit the token. Avoid leaving it in shell history (e.g. use `read -s` into a variable, clone, then `unset`, or configure a one-off credential helper). Example pattern:

   `git clone --branch staging "https://x-access-token:${TOKEN}@github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git" .`

3. **Tarball from a machine that already has the repo** (no GitHub from VPS):

   On the laptop (inside a clone of `KIG7`):

   ```bash
   git archive --format=tar.gz --output=kig7-staging.tar.gz staging
   ```

   Copy `kig7-staging.tar.gz` to the server, then:

   ```bash
   cd /opt/kig7-odoo18 && tar -xzf /path/to/kig7-staging.tar.gz
   ```

   (This unpacks tracked files only — no `.git`; you can still run Docker; for `git pull` updates you would re‑ship a new archive or fix GitHub access.)

4. **Optional:** temporarily set the repository to **public** in GitHub settings if you accept the loss of confidentiality (not recommended if the repo contains DB backups).

## 3. Clone the branch you want

If you use **git** with credentials (deploy key, PAT, or cached login), either clone into a **`src` subfolder** (below) **or** into `.` as in §2a — in both cases, **run `docker compose` from the directory that contains `docker-compose.yml`**.

```bash
cd /opt/kig7-odoo18
git clone --branch staging https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git src
cd src
# or: git clone --branch phase-one-branch https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging.git src
```

HTTPS URLs require **authentication** for this private repo (credential helper on the server, or embed a PAT once per §2a). For **SSH** use `git@github.com:Ahmedabdelalem61/KIG7-odoo18-staging.git` with a deploy key.


## 3b. Automated backups (before deploy)

From repo root (where `docker-compose.yml` lives):

```bash
bash deploy/backup-manage.sh deploy   # or: bash deploy/deploy-staging.sh
```

Install the daily timer (05:00 UTC):

```bash
sudo cp deploy/systemd/kig7-odoo18-backup.{service,timer} /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now kig7-odoo18-backup.timer
```

See `deploy/README.md` § Backup management. Retention: 7 days; the newest set is always kept.

## 4. Artifacts (dump + filestore)

If `deploy/artifacts/*.dump` and `*.tgz` are **not** in the clone (gitignored), copy them from your workstation:

```bash
# If docker-compose.yml lives under .../src (default runbook layout):
scp deploy/artifacts/kig7_18c_hr_project_test.dump deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz user@server:/opt/kig7-odoo18/src/deploy/artifacts/

# If you cloned into /opt/kig7-odoo18 directly (no src/):
scp deploy/artifacts/kig7_18c_hr_project_test.dump deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz user@server:/opt/kig7-odoo18/deploy/artifacts/
```

## 5. Configure secrets

```bash
cp .env.example .env
# edit POSTGRES_PASSWORD; then set the same value for db_password in configs/docker.odoo.conf
```

## 6. Restore and start

```bash
docker compose pull
bash deploy/restore.sh
docker compose ps
curl -I http://127.0.0.1:8073
```

## 7. Optional: reverse proxy + TLS

Put Nginx or Caddy in front of `127.0.0.1:8073` with HTTPS and firewall rules — not included in this repo.

## 8. Smoke test in browser

Use SSH local forwarding if the port is not public:

```bash
ssh -L 8073:127.0.0.1:8073 user@SERVER
# open http://localhost:8073
```

Log in with a user that exists in the **restored** database.
