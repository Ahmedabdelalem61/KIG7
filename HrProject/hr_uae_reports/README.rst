==============
HR UAE Reports
==============

Consolidated reports and a modern dashboard for the HR UAE Admin platform.

Reports
=======

* **Master Data** – PDF dump of the proposal's Master Data table
  (rank, passport, roster, position, project, location, status, salary,
  DOB, age, nationality, date of joining, time of service, visa).
* **Movement Tracking** – PDF over the ``hr.uae.movement.tracking``
  SQL view (leaves, contract ends, project transfers).
* Re-uses the **Payroll Dashboard**, **Tickets** and **Termination**
  reports defined in their respective modules and exposes them under
  a single ``HR UAE Admin -> Reports`` menu.

Dashboard
=========

A live ``hr.uae.dashboard`` view shows:

* Active employee counts per status (Active / Vacation / Special Permit /
  Sick / Resigned / Terminated)
* Visas expiring within 30 / 60 / 90 days
* Payslips currently held due to vacation
* Salary adjustments awaiting HR Manager approval
* Open flight tickets and total flight cost
