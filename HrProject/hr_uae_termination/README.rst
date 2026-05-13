==================
HR UAE Termination
==================

Contract termination workflow with auto cleanup of related records.

Features
========

* ``hr.uae.termination`` model carrying every column from the proposal's
  Contract Termination sheet (Roster, Name, Project, Passport, DOB, JD,
  Departure, Arrival, Time of Service, Note) plus a typed ``reason``
  selection covering resignation, vacation/special-permit no-return,
  medical, end of contract, dismissal, other.
* Workflow ``Draft -> Active -> Closed``.
* On **Activate**:

  - Closes the contract (and any other open contract) with ``date_end``.
  - Cancels future ``draft`` / ``verify`` / ``on_hold`` payslips so no
    further pay is generated for the terminated employee.
  - Archives the employee and forces ``hr_uae_status`` = *Terminated*
    with manual override flag.

* PDF report exactly matching the proposal's table layout.
* Tracked through ``hr_uae_audit_trail``.
