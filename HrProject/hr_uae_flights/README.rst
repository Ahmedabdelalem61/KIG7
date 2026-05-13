==============
HR UAE Flights
==============

Flight ticket management built on top of ``hr.expense``.

Features
========

* ``hr.uae.flight`` model carrying every column of the proposal's Tickets
  sheet (passport, DOJ, time of service, DOB, requested date, ticket no.,
  from / to, ticket price, extra charges, total, departure & arrival date
  + time, month, sent ticket, agency, refundable, updated master flag,
  notes, project allocation).
* Booking workflow: Draft -> Booked -> Completed / Cancelled / Rescheduled.
* On booking, automatically creates a linked ``hr.expense`` of product
  ``Flight Ticket`` and copies analytic distribution from the project
  allocation. Native Odoo ``payment_mode`` (Paid by Company / Paid by
  Employee) drives whether the cost ends up on a company invoice or
  funnels back to payroll (next phase).
* PDF report listing tickets with all key columns.
* Auto-tracked through ``hr_uae_audit_trail``.
