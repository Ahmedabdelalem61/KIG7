================================================================================
HR SOFTWARE PROPOSAL — Requirement traceability (Word document)
================================================================================

Source document: ``HR SOFTWARE PROPOSAL (1).docx``. This file maps proposal
themes to the ``hr_uae_*`` modules and notes deliberate limits.

--------------------------------------------------------------------------
Business rules (global)
--------------------------------------------------------------------------

**AED-only payroll & single HR Manager approval** — Implemented (user
decisions during design). Currency defaults via ``hr_uae_base``; salary
adjustments use one-stage approval (``hr_uae_salary_adjustment``).

**UAE working calendar & country metadata** — Implemented.
``hr_uae_base`` seeds Sat–Thu calendar, public holidays as calendar leaves,
and AED-oriented company defaults.

**Two analytic dimensions** — Implemented.
``hr_uae_master_data``: *Project allocation* and *Cost Center* plans;
cost center auto-created per employee name; project selectable.

--------------------------------------------------------------------------
Master Data Module (core database)
--------------------------------------------------------------------------

+------------------------------+-------------------------------------------+
| Proposal need                | Implementation                            |
+==============================+===========================================+
| Rank, passport, roster,      | ``hr_uae_master_data`` on ``hr.employee`` |
| position, project, salary    | + contract wage / structure               |
+------------------------------+-------------------------------------------+
| Location & nationality       | ``location_id``; nationality uses standard ``country_id`` |
|                              | (``res.country``)                         |
+------------------------------+-------------------------------------------+
| Status (active, vacation,    | ``hr_uae_status`` computed + manual       |
| resignation, sick, etc.)     | override + cron refresh                   |
+------------------------------+-------------------------------------------+
| DOJ, age, time of service,   | ``first_contract_date`` (standard), ``age``, |
| visa expiry / alerts         | ``time_of_service``, ``visa_expire`` / ``visa_status`` |
+------------------------------+-------------------------------------------+
| Sync to payroll / leave /    | Odoo relational model + computed payslip  |
| tickets                      | inputs & expense links (same employee /   |
|                              | project where applicable).                |
+------------------------------+-------------------------------------------+
| Historical tracking          | ``hr_uae_audit_trail``                    |
+------------------------------+-------------------------------------------+

**PDF / Excel “Master Data” report** — Implemented under
``hr_uae_reports`` (proposal tables mirrored as closely as practical).

--------------------------------------------------------------------------
Audit trail
--------------------------------------------------------------------------

Field-level log with old/new, user, time; employee smart-button + wizard /
PDF report — ``hr_uae_audit_trail``. Employee-linked contracts and documents
included via mixin.

--------------------------------------------------------------------------
Flight Ticket Management (over expenses)
--------------------------------------------------------------------------

Linked to employee & project allocation; booking lifecycle; expense product;
ticket attachment on expense; payroll deduction rule ``FLIGHT_DED`` —
``hr_uae_flights``. Agency text field; **“Updated Master?”** flag as
``updated_master``. Matches proposal intent.

--------------------------------------------------------------------------
Leave & movement
--------------------------------------------------------------------------

**Four leave types only** — Annual, Special, Medical, Unpaid —
``hr_uae_leaves/data/hr_leave_type_data.xml``. Unpaid ties to payroll rule.

**Alerts** — Annual: **20** days after start; Special: **7** days —
``hr_uae_alert_days`` on leave types + cron email.

**Movement tracking report / PDF** — SQL view ``hr.uae.movement.tracking``
(leaves, contract ends, project changes from audit log).

The proposal “vacation tracking” spreadsheet has separate columns for
**departure from site, visa requested / arrived, return ticket, return-to-site
dates**. In Odoo these already live on existing records:

  * Departure / arrival dates → ``hr.uae.flight`` (purpose = ``vacation`` /
    ``special_permit``) — same employee + project allocation.
  * Visa state → ``hr.employee`` (``visa_expire``, computed ``visa_status``).
  * Returned to site → ``hr.leave.hr_uae_returned`` flag.

We deliberately **don't** duplicate them on ``hr.leave``.

**Payroll hold until return** — ``hr_uae_payroll`` extends payslip with hold
state and **Returned** on ``hr.leave``.

**Balances / accrual** — Standard Odoo allocations + contract-linked leave
types; unpaid deduction via salary rule.

--------------------------------------------------------------------------
Payroll integration
--------------------------------------------------------------------------

OCA ``payroll`` + UAE structure (Basic, Housing, Transport, unpaid, flight
deduction, adjustments, NET). Salary adjustments with modes one-shot /
range / recurring — ``hr_uae_salary_adjustment``.

**Payroll dashboard (Excel-like)** — ``hr.uae.payroll.dashboard`` SQL view:
columns aligned to the proposal sheet; ``total_days`` = calendar span of the
payslip period; ``worked_days`` = sum of payslip worked-days lines (resource
calendar driven when payroll computes lines); ``extra_payment`` feeds from
positive **ADJUSTMENTS** line; ``deduction`` aggregates **DED** category lines;
``total_to_pay`` uses NET line when present else wage / hold split.

--------------------------------------------------------------------------
Documents
--------------------------------------------------------------------------

Typed documents, expiry, cron alerts, mail template, access rules —
``hr_uae_documents``.

--------------------------------------------------------------------------
Termination
--------------------------------------------------------------------------

Termination workflow, archive employee, close contracts, cancel future
payslips — ``hr_uae_termination`` + PDF report.

--------------------------------------------------------------------------
Dashboard & umbrella install
--------------------------------------------------------------------------

Live metrics — ``hr_uae_reports`` dashboard transient. One-click install —
``hr_uae_app``.

--------------------------------------------------------------------------
Out of scope / platform limits (explicit)
--------------------------------------------------------------------------

- **Native mobile app** — Proposal mentions phone app; standard Odoo web UI;
  public website uses **Kea** design theme (``theme_kea`` + ``theme_common`` from
  ``odoo/design-themes`` 18.0, vendored under ``thirdparty/design-themes``).
  **Back office** uses free OCA **``web_responsive``** (``OCA/web`` 18.0,
  vendored under ``thirdparty/web_responsive``) for a better responsive backend
  (app menu, sticky headers, mobile layout)—not a color "skin", but the de-facto
  Community standard for backend UX.
- **Automatic chart of accounts** — Full accounting chart not auto-installed;
  analytic plans are seeded for HR costing.
- **“Bonus” column** on payroll dashboard — Reserved (0) unless you add a
  dedicated salary rule / input type later.

When upgrading after adding leave logistics fields or dashboard SQL changes,
run ``-u hr_uae_leaves,hr_uae_payroll`` (or ``-u hr_uae_app``) on your database.
