==========================
HR UAE Salary Adjustments
==========================

Salary adjustments / allowances / deductions with single-stage approval.

Features
========

* ``hr.uae.salary.adjustment`` model with three kinds:

  - **Adjustment** – generic positive correction (input code ``ADJ_ADJ``).
  - **Allowance** – paid to the employee (input code ``ADJ_ALW``).
  - **Deduction** – subtracted from payable (input code ``ADJ_DED``).

* Three application modes:

  - **One-shot** – pushed to a single chosen payslip.
  - **Range** – applied to all payslips with period inside the range.
  - **Recurring** – applied month-after-month from a start date until
    optional end date, via a daily cron.

* Workflow ``Draft -> To Approve -> Approved -> Done`` (or ``Refused``)
  with mandatory **HR Manager (UAE)** approval (single-level cycle).
* On approval, payslip inputs are created/updated on matching payslips
  so they show on the payslip itself; the salary structure rules
  ``ADJUSTMENTS`` (in ``hr_uae_payroll``) consume them.
* Tracked through ``hr_uae_audit_trail`` and ``mail.thread``.
