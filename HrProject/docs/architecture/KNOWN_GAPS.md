> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Known Gaps

| Gap | Impact | Suggested action |
|---|---|---|
| Untested modules or zero local tests for `hr_uae_app` and `hr_uae_backend_theme` | Packaging/theme regressions may be caught only manually | Add smoke tests or documented manual checks |
| Multi-company test skip on staging because second company cannot be created due to account chart-template constraint | Multi-company record rules/dashboard behavior not fully exercised | Maintain a separate test DB capable of second-company creation |
| Discuss root menu archived on staging | Menu state may differ from fresh installs | Document/admin-check menu state during deploy |
| 34 historical payslips re-labeled USD after currency switch; values not restated | Historical reports may show USD labels on old AED values | Add audit note in finance reporting; avoid recomputing old slips without review |
| Vendored OCA payroll upgrade path | Upstream API/view/state changes can break KIG7 payroll | Pin version and run payroll test suite before deploy |
| Menu-restriction re-apply scope | Mail/calendar/website upgrades may restore menu groups until `hr_uae_access` updates | Include `hr_uae_access` in relevant upgrade runs |
| XLSX contracts template uses company-currency wage | Foreign contract values may be confusing in exports/imports | Add foreign-currency columns or warning in template |
| Default KIG7 passwords in noupdate users | Unauthorized access risk | Rotate/archive before production; never print defaults |
| Free FX provider accuracy and availability | Payroll blocked or rates inaccurate | Allow manual rate review and maintain fallback process |
| `PEN_ER` salary rule references an undefined variable | Employer pension computation can fail or compute incorrectly when evaluated | Fix the rule formula with payroll tests and record the master-data migration |
| `[PRJ-B] Projec` department typo is intentionally seeded | Fresh init preserves the existing typo for parity | Rename through an explicit data migration if business approves |
| Windows env files contain placeholder passwords | Deployment will fail or be insecure if placeholders are used unchanged | Replace placeholders out of git and align with `configs/docker.odoo.conf` |
| Backup dump and filestore artifacts are not in git | One-click staging restore cannot run until artifacts are supplied | Store `kig7_db.dump` and `kig7_filestore.tgz` securely under `deploy/windows/artifacts/` on the target host |
