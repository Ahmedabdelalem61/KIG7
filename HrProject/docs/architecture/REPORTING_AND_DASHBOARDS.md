> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Reporting And Dashboards

## Custom Dashboards

- `hr.uae.dashboard` is defined in `hr_uae_reports` and extended by project/department fields.
- `hr.uae.payroll.dashboard` and `hr.uae.payroll.live.dashboard` are defined in `hr_uae_payroll` and extended by project/department and XLSX modules.
- Payroll dashboard behavior includes `basic_amount` via grouped payroll data and `net`/`total_to_pay` mirror semantics per code comments/tests. Source: [../../hr_uae_payroll/models/hr_uae_payroll_dashboard.py](../../hr_uae_payroll/models/hr_uae_payroll_dashboard.py).

Intended access: HR Officer and HR Manager through custom HR UAE groups. Payroll & Accounting Manager deliberately has no `hr_uae_base` group, so custom dashboards/menus are blocked by design.

## Refresh Behavior

Dashboards use Odoo computed/query behavior rather than a separate external BI store. ⚠ Unverified: each dashboard field's `store=True/False` should be checked before changing refresh expectations.

## Reports

`hr_uae_reports` contains report actions and dashboard views for HR UAE records. Standard Odoo dashboards remain governed by their standard groups unless KIG7 explicitly restricts menus/rules.

## XLSX I/O

`hr_uae_xlsx_io` defines `hr.uae.xlsx.template`, `hr.uae.xlsx.template.line`, and `hr.uae.xlsx.import.wizard`. The module ships template data and tests for import/export. Ground-truth operational behavior: 7 templates, all-or-nothing ORM import with per-row savepoints, validate dry-run, error workbook, manager-only. Source to verify before changing: [../../hr_uae_xlsx_io/models/xlsx_template.py](../../hr_uae_xlsx_io/models/xlsx_template.py), [../../hr_uae_xlsx_io/wizards/xlsx_io_wizard.py](../../hr_uae_xlsx_io/wizards/xlsx_io_wizard.py).

Known caveat: xlsx contracts template uses company-currency wage; see [KNOWN_GAPS.md](KNOWN_GAPS.md).
