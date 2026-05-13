==============
HR UAE Payroll
==============

Payroll integration for the UAE HR Admin platform.

Features
========

* New salary structure ``UAE Standard`` (code ``UAE``) with rules:

  - ``BASIC`` – contract wage.
  - ``HOUSING`` and ``TRANSPORT`` allowance placeholders.
  - ``UNPAID`` – auto-deducts unpaid leave days from the wage.
  - ``FLIGHT_DED`` – consumes ``FLIGHT_DED`` payslip inputs from
    employee-paid flights.
  - ``ADJUSTMENTS`` – consumes ``ADJ_ALW``, ``ADJ_DED`` and ``ADJ_ADJ``
    payslip inputs from the salary-adjustment module.
  - ``NET`` – sum of categories.

* Adds ``on_hold`` state to ``hr.payslip``.
  When ``compute_sheet`` runs, if the employee has an open Annual or
  Special Leave overlapping the payslip period, the payslip moves to
  ``on_hold`` with:

  - ``hr_uae_payable_now`` = pro-rata of worked days before the leave
    started.
  - ``hr_uae_held_amount`` = remainder.

* Confirming a held payslip is blocked. HR releases the hold either
  manually or automatically by toggling ``hr_uae_returned`` on the leave.
* Read-only model ``hr.uae.payroll.dashboard`` reproducing the proposal's
  Payroll Excel table (No., Rank, Name, Passport, Roster, Position,
  Project, Location, Status, Salary, Total/Worked/Deducted Days, Hold,
  Total to Pay, Notes) plus PDF report.
