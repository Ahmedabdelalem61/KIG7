==============
HR UAE Leaves
==============

Leave types and movement tracking for the HR UAE Admin platform.

Features
========

* Seeds the four UAE leave types: **Annual Leave**, **Special Leave**,
  **Medical Leave**, **Unpaid Leave** (the last flagged ``hr_uae_unpaid``
  so the payroll module can deduct from worked days).
* Extends ``hr.leave.type`` with:

  - ``hr_uae_status_code`` — maps the leave to the employee's UAE Status.
  - ``hr_uae_alert_days`` — alert HR after N days (Annual=20, Special=7).
  - ``hr_uae_unpaid`` — payroll deduction flag.

* Extends ``hr.leave`` with ``hr_uae_returned`` (used by ``hr_uae_payroll``
  to release held payslips) and an ``hr_uae_alert_sent`` guard.
* Daily cron sends a translatable e-mail to HR Manager users when an
  active leave reaches its alert threshold.
* SQL view ``hr.uae.movement.tracking`` unioning leaves, contract ends and
  project allocation transfers (from the audit log) for the **Movement
  Tracking** report.
