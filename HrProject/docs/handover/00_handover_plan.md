# KIG7 HR Project Handover Plan

This folder is for the material requested in the handover email. The goal is to package the project in a way that is easy for a new technical team and the business owner to review.

## Email Requirements Broken Into Tasks

| Task | Email requirement | Deliverable |
| --- | --- | --- |
| 1 | Overview of implemented work | Functional and technical summary by module and business flow |
| 2 | Access to environments | URL, admin access, server/host notes, approved DB access path, logs/config access notes |
| 3 | Source code and custom modules | Repo path, custom module list, dependency map, deployment/restore notes |
| 4 | Technical notes | Backups, cron jobs, third-party integrations, known issues, pending items |
| 5 | Workflow explanation | Standalone video recording script and test checklist per phase |

## Recommended Recording / Documentation Phases

The phases below follow the real module dependency order in the codebase and the old offline workflow sources in `Downloads`.

1. **Phase 0 - Foundation and Access**
   - Company defaults, AED/UAE setup, calendar, security groups, environment access, backup/restore path.
   - Main modules: `hr_uae_base`, deployment files.

2. **Phase 1 - Employee Creation, Contract, and Compensation Master Data**
   - Employee onboarding record, rank/position, roster, passport/visa data, project allocation, cost center, contract salary, monthly allowances, annual ticket benefit.
   - Main modules: `hr_uae_master_data`, standard `hr_contract`.

3. **Phase 2 - Audit Trail and Documents**
   - Employee/contract change logging, document ownership, expiry alerts.
   - Main modules: `hr_uae_audit_trail`, `hr_uae_documents`.

4. **Phase 3 - Leaves and Movement Tracking**
   - UAE leave types, return flag, alerts, status impact, movement reporting.
   - Main modules: `hr_uae_leaves`.

5. **Phase 4 - Flight Ticket Lifecycle**
   - Ticket request/booking/completion, expense creation, project linkage.
   - Main modules: `hr_uae_flights`.

6. **Phase 5 - Payroll Calculation and Hold Workflow**
   - UAE salary structure, monthly allowance consumption, unpaid leave deduction, flight deduction, hold-on-leave behavior, payroll dashboard.
   - Main modules: `hr_uae_payroll`.

7. **Phase 6 - Salary Adjustments**
   - Adjustment / allowance / deduction requests, approval, payslip input creation.
   - Main modules: `hr_uae_salary_adjustment`.

8. **Phase 7 - Termination**
   - Termination request, contract closure, payslip cancellation, employee archive.
   - Main modules: `hr_uae_termination`.

9. **Phase 8 - Reports and Dashboards**
   - Master data report, movement report, payroll report exposure, live dashboard.
   - Main modules: `hr_uae_reports`.

10. **Phase 9 - Technical Operations Handover**
   - Repo structure, module list, restore steps, upgrade commands, cron map, known issues.
   - Main sources: repo docs, deployment folder, server/runtime notes.

## Old Offline Sources Used

- `PAYROLL AND MASTER DATA (2) (1).xlsx`
  - Drives Phase 1 and Phase 5 structure.
- `CONTRACT TERMINATION.xlsx`
  - Drives Phase 7 structure.
- `HR SOFTWARE PROPOSAL.docx`
  - Confirms overall business scope and payroll hold requirement.

## Available Phase Docs

- [Phase 1 - Employee, Contract, and Compensation Master Data](./phase_01_employee_contract_master_data.md)
- [Phase 2 - Audit Trail and Documents](./phase_02_audit_trail_and_documents.md)

## Recommended Next Step

1. Record Phase 1.
2. Record Phase 2.
3. Then move to Phase 3: leaves and movement tracking.
