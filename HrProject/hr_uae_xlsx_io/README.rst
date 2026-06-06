==========================
HR UAE - Excel Import/Export
==========================

Dynamic, configurable XLSX import/export for HR UAE data.

Where
=====

**HR UAE Admin > Configuration**

* **Excel Import / Export** — the console: pick a template, export current data
  (or an empty template), then validate and import an edited file.
* **Excel Templates** — define templates for *any* Odoo model and *any* of its
  fields (HR Manager only).

What it does
============

* **Export** writes a ``Data`` sheet (human header row + a hidden technical-name
  row + an ``ID`` column for round-trips) and an ``Instructions`` sheet listing
  every field, its type, whether it is importable/required and the allowed
  values / relation target.
* **Import** is safe by design:

  * Uses the **normal ORM** (``create`` / ``write``) — no SQL, no constraint
    bypass. Access rights, required fields, SQL/Python constraints and tracking
    all apply.
  * **All-or-nothing**: every row runs in its own savepoint; if *any* row fails
    the whole import is rolled back. Nothing is half-saved.
  * **Validate** runs the exact same logic but always rolls back, for a dry run.
  * Failures produce an on-screen summary plus a downloadable **error workbook**.

* **Matching on import**:

  1. The exported technical **ID** column wins.
  2. Otherwise the template's configured **match-key** fields are used; a
     duplicate match is rejected.
  3. Otherwise a new record is created (if the template allows it).

* **Relations** export as readable names and accept a name, ``id:<id>`` or
  ``xmlid:<module.record>`` on import (with an exact display-name fallback so
  code-prefixed analytic accounts round-trip cleanly). Blank cells are left
  unchanged on update.

Predefined templates
====================

Seeded from a data file (idempotent — user edits survive upgrades): Employees,
Contracts, Flight Tickets, Employee Documents, Salary Adjustments, Terminations
and an **export-only** Payroll Dashboard (payroll import is disabled).

Payroll columns
===============

Adds **Basic** (from the ``BASIC`` payslip line) and **Net** (mirrors Total to
Pay) to the payroll dashboard list and to the payroll export.

Requirements
============

Python ``openpyxl`` (already present in the runtime image).
