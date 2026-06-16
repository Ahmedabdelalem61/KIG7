> Generated: 2026-06-17 · Commit: working tree · Source of truth: code

# Data-Driven Init

KIG7 fresh database initialization is handled as code-owned master data, not as manual post-install clicks. The goal is reproducibility: a clean database installed with `hr_uae_app,hr_uae_init_data` should recreate the shared setup that staging depends on, while transactional and per-employee records remain outside init modules.

## Seeding Ownership

| Data area | Seeded by feature modules | Seeded by `hr_uae_init_data` |
|---|---|---|
| Company currency and UAE base configuration | `hr_uae_base`, multicurrency modules | Company name `Kig7` for fresh parity |
| Rank, position, employee state | Feature master-data modules | No |
| Leave types, UAE calendar, 2026 holidays | Feature leave/calendar data | No |
| Payroll structures and UAE salary rules | Payroll feature modules | Four parity rules: `TICPR`, `EOSPRo`, `PEN_EE`, `PEN_ER` |
| Payroll categories | Feature payroll data | `Company` category for provision/pension rules |
| Analytic project accounts and sequences | Feature project/sequence data | No |
| Departments | Feature and project setup | `ABC Project`, `Finance`, `[PRJ-A] Project`, `[PRJ-B] Projec` |
| Access roles, demo users, crons, templates | Access, XLSX, FX, and reporting modules | No |
| Transactions, employees, contracts, payslips | Never | Never |

## Known Parity Notes

`PEN_ER` currently preserves the existing undefined-variable formula behavior from the source setup. Treat this as a known bug to fix through a payroll-rule change with tests, not as a checksum script adjustment.

`[PRJ-B] Projec` intentionally keeps the missing final `t` for parity with the existing database. Renaming it is a master-data migration and should be tracked as such.

## Fresh Rebuild

Use the shared Docker Compose stack from the repo root:

```bash
docker compose run --rm --no-deps web odoo -d <db> -i hr_uae_app,hr_uae_init_data --stop-after-init --no-http --workers=0 --max-cron-threads=0
```

The Windows live deployment uses the same module install set for its fresh stack.

## Checksum Approach

`deploy/checksum_master_data.py` fingerprints stable master-data entities and excludes volatile columns such as ids, create/write metadata, currency rates, sequence counters, and transaction tables. The shell wrapper compares two databases entity by entity and prints `PASS`, `FAIL`, or `SKIP`.

Run from the repo root:

```bash
bash deploy/checksum-master-data.sh 18c_hr_project_test kig7_init_probe
```

Differences reported by the checksum should be reviewed as real master-data drift unless the entity is explicitly skipped because its optional table is absent.
