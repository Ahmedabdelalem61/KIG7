> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Decision Guide

## Impact Analysis Checklist

| Change type | Inspect | Run | Update docs |
|---|---|---|---|
| Model/field | models, views, security, tests | focused module tests | DATA_MODEL, BUSINESS_RULES |
| Workflow | model actions, views, crons, salary rules | workflow tests | BUSINESS_WORKFLOWS, UML_DIAGRAMS, USE_CASES |
| Security | groups, ACL CSV, record rules, menus, users | `hr_uae_access` tests | SECURITY_ARCHITECTURE |
| Dependency | manifests, install order, app aggregator | module update | MODULE_DEPENDENCIES, architecture-map.yaml |
| Cron/API | data XML, model method, logs | cron/manual tests | INTEGRATIONS, OPERATIONS_RUNBOOK |
| Deployment | compose, Dockerfile, nginx, config | smoke deploy | DEPLOYMENT, UPGRADE_GUIDE |

## Safe Extension Points

- Add fields through `_inherit` with focused views and ACL/rule updates.
- Add salary inputs/rules with tests that compute a payslip.
- Add XLSX templates through module data and template-line tests.
- Add crons with non-raising failure behavior where business-safe.

## High-Risk Areas

- `HrUaeFxContract` and `hr.payslip._compute_payslip_line`.
- `hr.contract._hr_uae_apply_currency` and authoritativeness of foreign fields.
- `res.currency.rate.rate` semantics and company-currency no-rate invariant.
- KIG7 implied-groups wiring and global deny rules.
- Contract form xpaths around wage/currency fields.
- Vendored OCA payroll upgrades.

## Questions Before Implementing

- Is this persisted data, computed display data, or payroll-authoritative data?
- Which role should see and mutate it?
- Does it affect payslip computation or historical payslips?
- Does it need a migration for existing records?
- Which cron/API failure behavior is acceptable?
- Which docs and tests prove the change?

## Change To Doc Traceability

Every code change should update [MAINTENANCE.md](MAINTENANCE.md)'s matrix. If docs cannot be verified from code, mark `⚠ Unverified`, `Inferred:`, or `Recommendation:`.
