> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Testing Strategy

## Existing Tests

| Module | Count | Tags/scenarios |
|---|---:|---|
| `hr_uae_base` | 8 | test_explicit_currency_survives_defaults, test_install_mode_bootstraps_code_currency, test_code_currency_is_usd, test_calendar_default_applies_outside_install, test_uae_calendar_seeded, test_aed_currency_active |
| `hr_uae_master_data` | 15 | test_analytic_plans_seeded, test_employee_create_auto_cost_center, test_employee_rename_syncs_cost_center, test_employee_archive_archives_cost_center, test_age_compute, test_visa_status_compute |
| `hr_uae_audit_trail` | 5 | test_create_logs_create_entry, test_write_logs_changes_with_old_and_new, test_skip_audit_context, test_format_many2one_uses_display_name, test_employee_audit_log_count |
| `hr_uae_documents` | 3 | test_create_document, test_expiry_states, test_employee_document_count |
| `hr_uae_flights` | 5 | test_create_with_sequence, test_currency_default_aed, test_book_creates_expense, test_cancel_clears_draft_expense, test_employee_change_syncs_project |
| `hr_uae_leaves` | 6 | test_leave_types_seeded, test_unpaid_flag, test_only_annual_holds_payroll, test_status_codes, test_alert_days, test_movement_tracking_view_exists |
| `hr_uae_payroll` | 11 | test_uae_structure_seeded, test_payslip_state_includes_on_hold, test_payslip_basic_net_from_lines, test_payslip_net_uses_payable_when_on_hold, test_contract_allowances_flow_into_monthly_payslip, test_compute_sheet_no_leave_no_hold |
| `hr_uae_salary_adjustment` | 4 | test_create_with_sequence, test_one_shot_workflow_pushes_input, test_one_shot_requires_target, test_range_pushes_to_matching_payslips |
| `hr_uae_termination` | 3 | test_create_with_sequence, test_activate_archives_and_cancels_payslips, test_close_after_active |
| `hr_uae_reports` | 2 | test_dashboard_record_creation_and_metrics, test_dashboard_action_returns_act_window |
| `hr_uae_project_department` | 14 | "post_install", "-at_install" |
| `hr_uae_xlsx_io` | 12 | "post_install", "-at_install" |
| `hr_uae_multicurrency` | 17 | "post_install", "-at_install" |
| `hr_uae_fx_rate_update` | 9 | "post_install", "-at_install" |
| `hr_uae_access` | 50 | "post_install", "-at_install", "hr_uae_access", "kig7_multicompany"; "post_install", "-at_install", "hr_uae_access", "kig7_idempotency"; "post_install", "-at_install", "hr_uae_access", "kig7_blocked"; "post_install", "-at_install", "hr_uae_access", "kig7_manager"; "post_install", "-at_install", "hr_uae_access", "kig7_payroll"; "post_install", "-at_install", "hr_uae_access", "kig7_officer"; "post_install", "-at_install", "hr_uae_access", "kig7_isolation" |
| `hr_uae_app` | 0 | None found |
| `hr_uae_backend_theme` | 0 | None found |
| `thirdparty/payroll` | 27 | test_change_state, test_init, test_update_attribute, test_worked_days_negative, test_leaves_positive, test_python_code_return_values |

Total rough test methods from code scan: 192. Ground truth supplied for KIG7-focused tests: 121 total across access, multicurrency, FX update, payroll, base, xlsx I/O, and project department. Difference is likely because the scan includes vendored OCA payroll and helper/manual tests. Treat the supplied 121 as the project acceptance count.

## Coverage By Workflow

- Security/access: strong coverage in `hr_uae_access` with role, blocked app, isolation, idempotency, and multicompany tags.
- Multicurrency: conversion, missing-rate, contract fields, salary adjustment conversion.
- FX update: fetch, failure, upsert, activation guards.
- Payroll: salary rules, allowances, deductions, dashboards.
- Base: company currency, calendar, groups, root menu.
- XLSX/project department: import/export and project allocation behavior.

## Classification

- Unit-like: currency helpers, computed fields, constraints.
- Integration: payslip compute, adjustment input creation, flight expense sync, XLSX import.
- Security: ACL/rule/menu isolation and role exclusivity.

## Commands

```bash
docker compose run --rm --no-deps web odoo -d <test-db> -i hr_uae_app --test-enable --stop-after-init --no-http --workers=0 --max-cron-threads=0
docker compose run --rm --no-deps web odoo -d <test-db> -u hr_uae_access --test-enable --stop-after-init --no-http --workers=0 --max-cron-threads=0
```

## Recommendations

- Recommendation: add explicit tests for dashboard field storage/refresh expectations.
- Recommendation: add end-to-end termination/EOS payroll tests if EOS calculation is business-critical.
- Recommendation: keep a multi-company capable test DB because staging currently skips second-company creation due to an account chart-template constraint.
