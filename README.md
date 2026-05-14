# KIG7

Odoo **18** Community staging stack for **UAE HR** addons (`HrProject/`) with Docker.

**GitHub (private):** [Ahmedabdelalem61/KIG7-odoo18-staging](https://github.com/Ahmedabdelalem61/KIG7-odoo18-staging) — branch `staging`. The VPS (or any host) needs a **deploy key**, **PAT**, or another authenticated method to clone; see [`deploy/VPS_RUNBOOK.md`](deploy/VPS_RUNBOOK.md). A copy may also exist under `Amrorg26/KIG7`.

- **Docker**: `docker-compose.yml` + `deploy/Dockerfile` + `configs/docker.odoo.conf` + `.env.example`
- **Deploy / restore**: [`deploy/README.md`](deploy/README.md)
- **VPS steps**: [`deploy/VPS_RUNBOOK.md`](deploy/VPS_RUNBOOK.md)
- **Security**: [`deploy/SECURITY.md`](deploy/SECURITY.md)

Branches **`staging`** and **`phase-one-branch`** carry the same deployment layout; use either on the server.
