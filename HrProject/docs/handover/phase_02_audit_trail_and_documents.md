# Phase 2 - Audit Trail and Documents

## Objective

Show how the system controls document lifecycle and tracks sensitive HR changes after employee and contract setup.

This phase explains two things:

- how employee and contract changes are traceable,
- how employee documents are stored, monitored, and alerted before expiry.

## Scope

Included in this phase:

- audit logging on employee and contract changes
- employee audit tab and audit smart button
- central audit log menu
- audit print wizard
- document creation and maintenance
- document tab and document smart button
- document expiry states
- document search filters
- document access rules by role
- document expiry email alerts

Not included in this phase:

- leave alerts
- payroll hold logic
- flight workflow
- termination cleanup

## Modules and Screens in Scope

- `hr_uae_audit_trail`
- `hr_uae_documents`

Primary UI paths:

- `HR UAE Admin -> Employees -> Employees -> open employee`
- `HR UAE Admin -> Employees -> Documents`
- `HR UAE Admin -> Audit Trail -> Audit Log`
- `HR UAE Admin -> Audit Trail -> Print Audit Trail`
- `Employees app -> Employees -> Contracts -> open contract`

## Business Purpose

Explain this phase to the business owner in plain language:

1. HR data is no longer a black box; important changes are traceable.
2. Employee documents are stored on the employee record instead of being scattered in folders and sheets.
3. Expiry follow-up is proactive because the system classifies upcoming expiry and sends alerts.
4. Access is controlled so document owners only see their own records, while HR/Finance can work at company scope.

## What the Code Actually Does

### Audit trail

- `hr.employee` is audited.
- `hr.contract` is audited.
- other UAE modules can also inherit the same audit mixin.
- create, update, and delete actions generate log entries.
- log rows store:
  - changed model
  - target record id
  - linked employee
  - field name / label
  - old value
  - new value
  - change type
  - user
  - timestamp

### Documents

- Document model: `hr.uae.document`
- Fixed types:
  - Passport
  - Visa
  - Medical Examination
  - Photograph
  - Contract
  - Other
- Expiry logic computes:
  - `days_to_expiry`
  - `expiry_state`
- Expiry states:
  - `No Expiry`
  - `Expired`
  - `Expires < 30 days`
  - `Expires < 60 days`
  - `Expires < 90 days`
  - `OK`
- Daily cron sends expiry alerts to `HR Manager (UAE)` users for active documents expiring within 90 days.
- Documents are also audited through the audit mixin.

## Preconditions

Use these checks before recording:

1. Phase 1 data exists for at least one employee and one contract.
2. You are logged in as `admin` or a user with `HR Manager (UAE)` access.
3. Mail is configured enough for outgoing alert demonstration, or at minimum you can explain the cron/template behavior.
4. The demo employee has a user-linked owner only if you want to explain the `Document Owner` rule.

## Recommended Demo Data

Use the employee created in Phase 1.

Prepare at least three documents:

1. Passport
   - Name: `Passport P1234567`
   - Expiry: more than 90 days ahead

2. Visa
   - Name: `Visa 2026`
   - Expiry: within 20 days

3. Medical
   - Name: `Medical Certificate`
   - No expiry or a long future expiry

Prepare one audit-triggering change before or during recording:

- update employee roster, passport number, or rank
- update contract monthly allowance or annual ticket amount

## Recording Script

Target duration: `7-10 minutes`

### Step 1 - Start from the employee record

Open:

- `HR UAE Admin -> Employees -> Employees`
- open the Phase 1 demo employee

Show the smart buttons in the header:

- `Documents`
- `Audit`

Talking points:

- The employee is the operational entry point.
- From here HR can see attached documents and change history without leaving the record context.

Expected result:

- both smart buttons are visible for an HR manager
- document count reflects linked active documents
- audit count reflects logged changes

### Step 2 - Show the Documents tab on the employee

Open:

- `Documents` tab on the employee form

Create or edit documents inline from the one2many list.

Fields to point to:

- `Document Type`
- `Name`
- `Issue Date`
- `Expiry Date`
- `Days to Expiry`
- `Expiry State`

Talking points:

- This is the structured replacement for scattered files and manual expiry tracking.
- Documents are tied directly to the employee.
- Expiry is computed, not typed manually.

Expected result:

- expired or near-expiry rows are visually highlighted
- the list updates computed expiry values automatically

### Step 3 - Open the full Documents list

Use either:

- the `Documents` smart button on the employee, or
- `HR UAE Admin -> Employees -> Documents`

Show:

- tree view with employee, type, name, issue date, expiry date, days to expiry, expiry state
- search filters:
  - `Expired`
  - `Expires < 30d`
  - `Expires < 90d`
- group by:
  - employee
  - type
  - expiry state

Talking points:

- HR can work centrally across all employees, not only one record at a time.
- The search filters are the operational follow-up surface for expiring documents.

Expected result:

- filter results match the expiry dates you entered
- grouping works for operational review

### Step 4 - Open a single document form

Open one document form and show:

- employee
- type
- issue and expiry dates
- computed days and expiry state
- file attachments
- note
- chatter

Talking points:

- The document record stores both metadata and files.
- Chatter makes document handling traceable.
- This is more structured than storing attachments only on the employee without a typed lifecycle.

Expected result:

- files can be attached
- chatter is present because the model inherits `mail.thread`

### Step 5 - Explain document access control

Show the business rule verbally, and only demo with users if you have them ready:

- `Document Owner`: sees only documents for employees where `employee.user_id == current user`
- `HR Manager`: sees all company documents
- `Finance`: has company-level read access

Talking points:

- Access is not fully open to everyone.
- This matters because passport, visa, and contract files are sensitive.

Expected result:

- user visibility depends on role
- owner scope is narrower than HR manager scope

### Step 6 - Show the Audit Trail tab on the employee

Return to the employee and open:

- `Audit Trail` tab

Fields to point to:

- `Changed At`
- `Model`
- `Field`
- `Old Value`
- `New Value`
- `Change Type`
- `Changed By`

Talking points:

- This is field-level traceability, not just a generic note.
- It helps explain who changed what and when.
- Employee-linked changes coming from contract or document activity can also be traced through the linked employee context.

Expected result:

- at least one logged update is visible
- entries show human-readable values, not raw ids

### Step 7 - Trigger a live audit entry

Make a simple change during the recording, for example:

- change employee roster, or
- change employee rank, or
- change contract housing allowance

Save the record and reopen the employee audit tab or the audit smart button.

Talking points:

- Changes are logged automatically; HR does not need to manually maintain a change register.

Expected result:

- a new audit line appears with old and new values
- many2one values display using labels rather than ids

### Step 8 - Open the central Audit Log menu

Open:

- `HR UAE Admin -> Audit Trail -> Audit Log`

Show:

- filters for `Created`, `Updated`, `Deleted`
- group by:
  - employee
  - changed by
  - model
  - change type
  - date

Talking points:

- The employee view is the local trace.
- The Audit Log menu is the global review surface for HR management.

Expected result:

- the central log shows activity across records
- filters and groups help narrow investigations

### Step 9 - Show the Print Audit Trail wizard

Open:

- `HR UAE Admin -> Audit Trail -> Print Audit Trail`

Show the wizard fields:

- employee
- date from
- date to

Talking points:

- When needed, audit data can be printed and shared in a bounded date range.
- This is useful for internal review or management follow-up.

Expected result:

- wizard opens in a modal
- print action is available

### Step 10 - Explain the expiry alert automation

Show or explain:

- there is a daily cron for document expiry alerts
- it sends alerts for active documents expiring within 90 days
- recipients are users in `HR Manager (UAE)`

Talking points:

- This moves document follow-up from reactive to proactive.
- The alert logic is based on typed document expiry, not manual reminders.

Expected result:

- business owner understands that alerting is automated even if email sending is not demonstrated live

## Test Checklist

### Functional checks

1. Employee form shows `Documents` smart button and `Documents` tab.
2. Employee form shows `Audit` smart button and `Audit Trail` tab for HR managers.
3. Creating a document computes `days_to_expiry` and `expiry_state`.
4. Document list filters return the expected records by expiry state.
5. Document form accepts file attachments.
6. Updating employee data creates audit entries.
7. Updating contract data creates audit entries linked to the employee context.
8. Audit entries show readable old/new values.
9. `Print Audit Trail` wizard opens and accepts employee/date range input.

### Security checks

1. `Document Owner` user only sees their own employee documents.
2. `HR Manager` can manage all company documents.
3. `Finance` can read company documents.
4. Global audit visibility stays within allowed company scope.

### Automation checks

1. A document with expiry in 20 days gets state `Expires < 30 days`.
2. A document with expiry in 50 days gets state `Expires < 60 days`.
3. A document with expiry in 80 days gets state `Expires < 90 days`.
4. A past expiry gets state `Expired`.
5. No-expiry documents remain `No Expiry`.

## Business Points to Say Clearly

- Audit trail protects accountability.
- Documents are managed as records, not just uploaded files.
- Expiry follow-up is visible and filterable.
- Sensitive visibility is role-based.
- This phase supports compliance and operational discipline around employee records.

## Technical Notes for the Handover

- Audit trail is implemented by reusable mixin `hr.uae.audit.mixin`.
- The mixin logs `create`, `write`, and `unlink`.
- Employee and contract are already wired into that mixin.
- Document records also inherit the audit mixin and `mail.thread`.
- Document alerts are driven by cron `model._cron_expiry_alert()`.
- Audit retention helper exists as `_gc_old_logs(retention_days=730)`.

## Completion Criteria for Phase 2

Phase 2 is complete when you can demonstrate all of the following:

1. employee documents can be created and viewed,
2. expiry state is computed correctly,
3. central document follow-up is filterable,
4. employee and contract changes produce audit entries,
5. audit data can be reviewed per employee and globally,
6. the business owner understands who can see which documents and why.

## Next Phase

After this phase, the logical next recording is:

- Phase 3: leaves and movement tracking
