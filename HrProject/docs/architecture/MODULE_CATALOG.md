> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Module Catalog

Status is source-verified from manifests where possible. Owner is HrProject Team unless marked OCA vendored. Risks are labeled as Inferred when they are not explicit code behavior.
## hr_uae_base

- Kind: Custom
- Purpose: Foundation, UAE defaults, root menu, base groups, USD company currency
- Manifest version: `18.0.1.1.0`
- Status: installable=None; application=None
- Owner: HrProject Team
- Depends: hr, hr_contract, resource
- Models defined: None
- Models extended: res.company
- Views/menus: 10 menu item(s)
- Crons: None
- Reports/actions: None found by XML scan
- Test count: 8; files: hr_uae_base/tests/test_base.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_base/__manifest__.py](../../hr_uae_base/__manifest__.py)

## hr_uae_master_data

- Kind: Custom
- Purpose: Employee master data: rank, position, status, passport/roster/project fields
- Manifest version: `18.0.1.0.3`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_base, hr_contract, hr_holidays, analytic
- Models defined: hr.uae.rank, hr.uae.position, hr.uae.employee.state
- Models extended: hr.contract, hr.employee
- Views/menus: 6 menu item(s)
- Crons: ir_cron_hr_uae_recompute_status
- Reports/actions: None found by XML scan
- Test count: 15; files: hr_uae_master_data/tests/test_master_data.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_master_data/__manifest__.py](../../hr_uae_master_data/__manifest__.py)

## hr_uae_audit_trail

- Kind: Custom
- Purpose: Audit mixin and audit log/reporting for HR records
- Manifest version: `18.0.1.0.1`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_master_data, mail
- Models defined: hr.uae.audit.log, hr.uae.audit.mixin, hr.uae.audit.report.wizard
- Models extended: hr.contract, hr.employee
- Views/menus: 2 menu item(s)
- Crons: None
- Reports/actions: action_report_employee_audit_trail
- Test count: 5; files: hr_uae_audit_trail/tests/test_audit_trail.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_audit_trail/__manifest__.py](../../hr_uae_audit_trail/__manifest__.py)

## hr_uae_documents

- Kind: Custom
- Purpose: Employee documents, expiry states, expiry alert cron
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_master_data, hr_uae_audit_trail, mail
- Models defined: hr.uae.document
- Models extended: hr.employee
- Views/menus: 1 menu item(s)
- Crons: ir_cron_hr_uae_document_expiry
- Reports/actions: None found by XML scan
- Test count: 3; files: hr_uae_documents/tests/test_documents.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_documents/__manifest__.py](../../hr_uae_documents/__manifest__.py)

## hr_uae_flights

- Kind: Custom
- Purpose: Flight ticket requests, ticket expenses, employee-paid deduction source
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_master_data, hr_uae_audit_trail, hr_expense
- Models defined: hr.uae.flight
- Models extended: None
- Views/menus: 1 menu item(s)
- Crons: None
- Reports/actions: action_report_hr_uae_flights
- Test count: 5; files: hr_uae_flights/tests/test_flights.py
- Risks: Inferred: low runtime risk; mostly data/aggregation.
- Source: [../../hr_uae_flights/__manifest__.py](../../hr_uae_flights/__manifest__.py)

## hr_uae_leaves

- Kind: Custom
- Purpose: Leave extensions, movement tracking, leave alerts
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_master_data, hr_uae_audit_trail, hr_holidays
- Models defined: hr.uae.movement.tracking
- Models extended: hr.leave
- Views/menus: 1 menu item(s)
- Crons: ir_cron_hr_uae_leave_alerts
- Reports/actions: None found by XML scan
- Test count: 6; files: hr_uae_leaves/tests/test_leaves.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_leaves/__manifest__.py](../../hr_uae_leaves/__manifest__.py)

## hr_uae_payroll

- Kind: Custom
- Purpose: UAE payroll structure, salary rules, payslip extensions, dashboards
- Manifest version: `18.0.1.0.8`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_master_data, hr_uae_audit_trail, hr_uae_leaves, hr_uae_flights, payroll
- Models defined: hr.uae.payroll.dashboard, hr.uae.payroll.live.dashboard
- Models extended: hr.contract, hr.employee, hr.leave, hr.payslip, hr.salary.rule, hr.uae.flight
- Views/menus: 2 menu item(s)
- Crons: None
- Reports/actions: action_report_hr_uae_payroll_dashboard
- Test count: 11; files: hr_uae_payroll/tests/test_payroll.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_payroll/__manifest__.py](../../hr_uae_payroll/__manifest__.py)

## hr_uae_salary_adjustment

- Kind: Custom
- Purpose: Approved adjustment/allowance/deduction inputs for payslips
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_payroll
- Models defined: hr.uae.salary.adjustment
- Models extended: None
- Views/menus: 1 menu item(s)
- Crons: ir_cron_hr_uae_adjustment_recurring
- Reports/actions: None found by XML scan
- Test count: 4; files: hr_uae_salary_adjustment/tests/test_salary_adjustment.py
- Risks: Inferred: low runtime risk; mostly data/aggregation.
- Source: [../../hr_uae_salary_adjustment/__manifest__.py](../../hr_uae_salary_adjustment/__manifest__.py)

## hr_uae_termination

- Kind: Custom
- Purpose: Termination/EOS workflow and downstream contract/payslip effects
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_payroll
- Models defined: hr.uae.termination
- Models extended: None
- Views/menus: 1 menu item(s)
- Crons: None
- Reports/actions: action_report_hr_uae_termination
- Test count: 3; files: hr_uae_termination/tests/test_termination.py
- Risks: Inferred: low runtime risk; mostly data/aggregation.
- Source: [../../hr_uae_termination/__manifest__.py](../../hr_uae_termination/__manifest__.py)

## hr_uae_reports

- Kind: Custom
- Purpose: Custom HR UAE dashboard and report actions
- Manifest version: `18.0.1.0.2`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_master_data, hr_uae_audit_trail, hr_uae_documents, hr_uae_leaves, hr_uae_flights, hr_uae_payroll, hr_uae_salary_adjustment, hr_uae_termination
- Models defined: hr.uae.dashboard
- Models extended: None
- Views/menus: 7 menu item(s)
- Crons: None
- Reports/actions: action_report_hr_uae_master_data, action_report_hr_uae_movement_tracking
- Test count: 2; files: hr_uae_reports/tests/test_dashboard.py
- Risks: Inferred: low runtime risk; mostly data/aggregation.
- Source: [../../hr_uae_reports/__manifest__.py](../../hr_uae_reports/__manifest__.py)

## hr_uae_project_department

- Kind: Custom
- Purpose: Project allocation and department extensions across HR transactions
- Manifest version: `18.0.1.0.1`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_reports, hr_uae_payroll, hr_uae_flights, hr_uae_documents, hr_uae_salary_adjustment, hr_uae_termination, hr_uae_leaves, hr_contract, hr_expense, hr_holidays
- Models defined: None
- Models extended: hr.contract, hr.department, hr.employee, hr.expense.sheet, hr.leave, hr.uae.dashboard, hr.uae.document, hr.uae.flight, hr.uae.payroll.dashboard, hr.uae.payroll.live.dashboard, hr.uae.salary.adjustment, hr.uae.termination, res.users
- Views/menus: 1 menu item(s)
- Crons: None
- Reports/actions: None found by XML scan
- Test count: 14; files: hr_uae_project_department/tests/test_project_department.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_project_department/__manifest__.py](../../hr_uae_project_department/__manifest__.py)

## hr_uae_xlsx_io

- Kind: Custom
- Purpose: Configurable XLSX exports/import wizard and templates
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_project_department
- Models defined: hr.uae.xlsx.template, hr.uae.xlsx.template.line, hr.uae.xlsx.import.wizard
- Models extended: hr.uae.payroll.dashboard
- Views/menus: 2 menu item(s)
- Crons: None
- Reports/actions: None found by XML scan
- Test count: 12; files: hr_uae_xlsx_io/tests/test_xlsx_io.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_xlsx_io/__manifest__.py](../../hr_uae_xlsx_io/__manifest__.py)

## hr_uae_multicurrency

- Kind: Custom
- Purpose: Contract-currency fields, strict payroll conversion, daily display refresh
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: hr_uae_payroll, hr_uae_salary_adjustment
- Models defined: None
- Models extended: hr.contract, hr.payslip, hr.uae.salary.adjustment, res.currency
- Views/menus: None found by XML scan
- Crons: ir_cron_hr_uae_refresh_currency
- Reports/actions: None found by XML scan
- Test count: 17; files: hr_uae_multicurrency/tests/test_multicurrency.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_multicurrency/__manifest__.py](../../hr_uae_multicurrency/__manifest__.py)

## hr_uae_fx_rate_update

- Kind: Custom
- Purpose: Online FX updater for active currencies
- Manifest version: `18.0.1.0.0`
- Status: installable=None; application=None
- Owner: HrProject Team
- Depends: base
- Models defined: None
- Models extended: res.currency
- Views/menus: None found by XML scan
- Crons: ir_cron_hr_uae_fx_update
- Reports/actions: None found by XML scan
- Test count: 9; files: hr_uae_fx_rate_update/tests/test_fx_rate_update.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_fx_rate_update/__manifest__.py](../../hr_uae_fx_rate_update/__manifest__.py)

## hr_uae_access

- Kind: Custom
- Purpose: KIG7 mutually exclusive roles, menu restrictions, blocked app rules
- Manifest version: `18.0.1.0.0`
- Status: installable=None; application=None
- Owner: HrProject Team
- Depends: hr_uae_xlsx_io, calendar, website
- Models defined: None
- Models extended: res.users
- Views/menus: None found by XML scan
- Crons: None
- Reports/actions: None found by XML scan
- Test count: 50; files: hr_uae_access/tests/test_multicompany.py, hr_uae_access/tests/test_idempotency.py, hr_uae_access/tests/test_blocked_apps.py, hr_uae_access/tests/test_hr_manager.py, hr_uae_access/tests/test_payroll_manager.py, hr_uae_access/tests/test_hr_officer.py, hr_uae_access/tests/test_isolation.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_access/__manifest__.py](../../hr_uae_access/__manifest__.py)

## hr_uae_app

- Kind: Custom
- Purpose: Aggregator app for the KIG7 HR stack
- Manifest version: `18.0.1.0.0`
- Status: installable=True; application=True
- Owner: HrProject Team
- Depends: hr_uae_base, hr_uae_master_data, hr_uae_audit_trail, hr_uae_documents, hr_uae_leaves, hr_uae_flights, hr_uae_payroll, hr_uae_salary_adjustment, hr_uae_termination, hr_uae_reports, sh_entmate_theme, rebranding, web_responsive
- Models defined: None
- Models extended: None
- Views/menus: None found by XML scan
- Crons: None
- Reports/actions: None found by XML scan
- Test count: 0; files: None
- Risks: Inferred: low runtime risk; mostly data/aggregation.
- Source: [../../hr_uae_app/__manifest__.py](../../hr_uae_app/__manifest__.py)

## hr_uae_backend_theme

- Kind: Custom
- Purpose: Backend branding/theme customizations
- Manifest version: `18.0.1.0.7`
- Status: installable=True; application=False
- Owner: HrProject Team
- Depends: web, hr_uae_base
- Models defined: None
- Models extended: ir.http, res.config.settings, res.users
- Views/menus: 1 menu item(s)
- Crons: None
- Reports/actions: None found by XML scan
- Test count: 0; files: None
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../hr_uae_backend_theme/__manifest__.py](../../hr_uae_backend_theme/__manifest__.py)

## thirdparty/payroll

- Kind: OCA vendored
- Purpose: Vendored OCA payroll for Odoo 18 Community
- Manifest version: `18.0.1.3.0`
- Status: installable=None; application=True
- Owner: OCA / HrProject Team
- Depends: hr_contract, hr_holidays, mail
- Models defined: hr.payslip, hr.payslip.run, hr.salary.rule, hr.payroll.structure, hr.payslip.input, hr.payslip.line
- Models extended: hr.contract, hr.employee, hr.salary.rule, res.config.settings
- Views/menus: 9 menu item(s)
- Crons: None
- Reports/actions: action_contribution_register, action_report_payslip, payslip_details_report
- Test count: 27; files: thirdparty/payroll/tests/test_hr_payslip_change_state.py, thirdparty/payroll/tests/test_browsable_object.py, thirdparty/payroll/tests/test_hr_payslip_worked_days.py, thirdparty/payroll/tests/test_hr_salary_rule.py, thirdparty/payroll/tests/test_hr_payroll_cancel.py, thirdparty/payroll/tests/test_payslip_flow.py
- Risks: Inferred: upgrade/test risk rises with inherited shared Odoo models.
- Source: [../../thirdparty/payroll/__manifest__.py](../../thirdparty/payroll/__manifest__.py)
