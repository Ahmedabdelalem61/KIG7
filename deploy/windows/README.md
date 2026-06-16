# KIG7 Windows Two-Stack Deploy

This folder contains a Windows PowerShell deployment wrapper for the shared Docker Compose stack at `../../docker-compose.yml`.

## Prerequisites

- Windows 10/11 with administrator access.
- PowerShell 7 or Windows PowerShell.
- WSL2 and Docker Desktop. The script enables WSL2 features and installs Docker Desktop unless `-SkipDockerInstall` is used.
- Staging backup artifacts copied to:
  - `artifacts/kig7_db.dump`
  - `artifacts/kig7_filestore.tgz`

Do not commit backup artifacts or real passwords.

## Run

From an elevated PowerShell prompt:

```powershell
Set-Location <repo-root>
.\deploy\windows\Deploy-Kig7.ps1
```

Optional ports:

```powershell
.\deploy\windows\Deploy-Kig7.ps1 -StagingPort 8073 -LivePort 8074 -LogDir .\deploy\windows
```

## What It Builds

- `kig7-staging`: restored from `artifacts/kig7_db.dump` and `artifacts/kig7_filestore.tgz`, published on port `8073` by default.
- `kig7-live`: initialized with `-i hr_uae_app,hr_uae_init_data`, published on port `8074` by default.
- Both stacks reuse the repository Dockerfile, nginx config, Odoo config, and bind-mounted `HrProject` addons.

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
