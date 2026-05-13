# VPS runbook (185.196.21.19 or any host)

These steps assume **SSH access** with keys (see `SECURITY.md`). Do **not** store root passwords in repositories.

## 1. Install Docker (if missing)

Use your distribution’s Docker Engine + Compose v2 guide (Ubuntu/Debian: `docker.io` + `docker-compose-plugin` or Docker’s official repo).

## 2. Isolated install directory

```bash
sudo install -d -o "$USER" -g "$USER" /opt/kig7-odoo18
cd /opt/kig7-odoo18
```

## 3. Clone the branch you want

```bash
git clone --branch staging https://github.com/Amrorg26/KIG7.git src
cd src
# or: git clone --branch phase-one-branch https://github.com/Amrorg26/KIG7.git src
```

## 4. Artifacts (dump + filestore)

If `deploy/artifacts/*.dump` and `*.tgz` are **not** in the clone (gitignored), copy them from your workstation:

```bash
scp deploy/artifacts/kig7_18c_hr_project_test.dump deploy/artifacts/kig7_filestore_18c_hr_project_test.tgz user@server:/opt/kig7-odoo18/src/deploy/artifacts/
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
