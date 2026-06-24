# KIG7 Windows Two-Stack Deploy

A self-contained, one-click Windows 10/11 installer that sets up **everything**
(WSL2 + Docker Desktop + both Odoo systems) on a fresh machine, run by a
**non-technical operator**.

## For the operator (non-technical)

See **`READ-ME-FIRST.txt`** in this folder. In short:

1. Copy the whole project folder to the machine (e.g. `C:\KIG7`).
2. Put the two backup files in `deploy\windows\artifacts\`:
   `kig7_db.dump` and `kig7_filestore.tgz`.
3. **Double-click `INSTALL-KIG7.cmd`** and click **Yes** on the permission pop-up.
4. Wait. If the computer restarts, log back in — it **continues by itself**
   (an elevated Scheduled Task auto-resumes the install).
5. Open `http://localhost:8073` (staging) and `http://localhost:8074` (live).

## How it works (for the provider)

- **`INSTALL-KIG7.cmd`** — double-clickable launcher. Self-elevates via UAC and
  runs `Deploy-Kig7.ps1` with `-ExecutionPolicy Bypass`.
- **`Deploy-Kig7.ps1`** — a reboot-surviving **state machine** (stage file
  `.kig7-stage` + a `KIG7Resume` Scheduled Task that runs **elevated at next
  logon**, so reboots needed by WSL2/Docker are fully hands-free). It:
  1. Pre-flight (Windows build, virtualization, disk, RAM) — clear warnings.
  2. `wsl --install --no-distribution` (+ `wsl --update`).
  3. Installs Docker Desktop silently (winget, with direct-installer fallback,
     `--accept-license`), reboots when Windows requires it, auto-resumes.
  4. Waits for the Docker engine, then builds the image and brings up both
     stacks. Idempotent — safe to run again; it detects already-initialized DBs.

Manual run (advanced) from an elevated PowerShell:

```powershell
.\deploy\windows\Deploy-Kig7.ps1 -StagingPort 8073 -LivePort 8074
```

## What It Builds

- `kig7-staging`: restored from `artifacts/kig7_db.dump` + `kig7_filestore.tgz`, on port `8073`.
- `kig7-live`: initialized with **`-i hr_uae_init_data`** (the data module depends
  on the whole project, so this one install pulls every module + master data), on port `8074`.
- Both stacks reuse the repository Dockerfile, nginx config, Odoo config, and bind-mounted `HrProject` addons.
- If the staging backup files are absent, staging is skipped and **live still installs**.

Do not commit backup artifacts or real passwords.

## Logs

Each run writes a timestamped log next to the script by default:

```text
Deploy-Kig7-YYYYMMDD-HHMMSS.log
```

## Troubleshooting

| Symptom | Cause | Action |
|---|---|---|
| Missing artifact error | Staging dump or filestore tarball was not copied | Place the two required files under `deploy/windows/artifacts/` |
| Docker timeout | Docker Desktop did not start within 600 seconds | Start Docker Desktop manually and rerun with `-SkipDockerInstall` |
| Port already in use | Another process uses 8073 or 8074 | Pass `-StagingPort` or `-LivePort` with free ports |
| Odoo cannot connect to Postgres | Password/config mismatch | Align `POSTGRES_PASSWORD` env files with `configs/docker.odoo.conf` deployment values |
| Smoke test fails | Odoo is still starting or init failed | Check the timestamped deploy log and `docker compose -p <stack> logs web` |

## Tear Down

Stop a stack while keeping volumes:

```powershell
docker compose -p kig7-staging --env-file deploy\windows\staging.env down
docker compose -p kig7-live --env-file deploy\windows\live.env down
```

Remove containers and volumes:

```powershell
docker compose -p kig7-staging --env-file deploy\windows\staging.env down -v
docker compose -p kig7-live --env-file deploy\windows\live.env down -v
```
