============
HR UAE Admin
============

Umbrella module that installs the entire HR UAE Admin platform in a
single click.

Proposal checklist (Word doc coverage): see ``docs/PROPOSAL_REQUIREMENTS.rst``.

Installs and pulls in the following modules:

* ``hr_uae_base`` – UAE country, calendar, AED, security groups, root menu.
* ``hr_uae_master_data`` – employee master data (rank, passport, roster,
  project allocation, cost center, status, visa, …).
* ``hr_uae_audit_trail`` – field-level audit log with employee tab + report.
* ``hr_uae_documents`` – typed documents with expiry alerts and per-owner
  record rules.
* ``hr_uae_leaves`` – 4 UAE leave types, movement tracking, vacation /
  special-permit alerts.
* ``hr_uae_flights`` – flight tickets on top of ``hr.expense``.
* ``hr_uae_payroll`` – UAE salary structure and hold-during-vacation
  payroll logic.
* ``hr_uae_salary_adjustment`` – adjustments / allowances / deductions
  with single-stage HR Manager approval.
* ``hr_uae_termination`` – contract termination workflow with auto-archive.
* ``hr_uae_reports`` – consolidated PDF reports and live dashboard.

After installation:

1. Set company country to ``United Arab Emirates``; the base module sets
   AED currency and the UAE working calendar automatically.
2. Open ``HR UAE Admin -> Configuration`` to review ranks / positions.
3. Open ``HR UAE Admin -> Dashboard`` for the live overview.
