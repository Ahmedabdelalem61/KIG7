# Phase 1 - Employee, Contract, and Compensation Master Data

## Objective

Show how the system replaces the old Excel-based employee master data process with structured employee and contract records in Odoo.

This phase is the base for later phases. If employee and contract data are wrong here, payroll, leaves, flights, reports, and termination will all be wrong later.

## Scope

Included in this phase:

- HR reference setup used by onboarding
- Employee record creation
- UAE employee master data entry
- Project allocation and cost center linkage
- Contract creation
- Salary and monthly allowance entry
- Annual ticket benefit entry as a contract field

Not included in this phase:

- Payroll calculation run itself
- Leave workflow
- Flight booking
- Salary adjustments
- Termination

## Modules and Screens in Scope

- `hr_uae_base`
- `hr_uae_master_data`
- standard `hr` / `hr_contract`

Primary UI paths:

- `HR UAE Admin -> Configuration -> Ranks`
- `HR UAE Admin -> Configuration -> Positions`
- `HR UAE Admin -> Configuration -> Project allocations`
- `HR UAE Admin -> Configuration -> Cost centers (analytic)`
- `HR UAE Admin -> Employees -> Employees`
- `Employees app -> Employees -> Contracts`
  - or open the employee and use the `Contract` smart button

## Old Workflow Sources Behind This Phase

This phase mainly digitizes the old columns from:

- `PAYROLL AND MASTER DATA (2) (1).xlsx` -> `MASTER DATA`
- `PAYROLL AND MASTER DATA (2) (1).xlsx` -> `PAYROLL`

Examples of offline columns now captured in Odoo during this phase:

- Rank
- Applicant Name
- Passport No.
- Roster
- Position
- Project
- Location
- Status
- Salary
- Date of Birth
- Nationality
- Date of Joining
- Time of Service
- Notes and contract compensation context

## Preconditions

Use these checks before recording:

1. Log in as `admin` or a user with `HR Manager (UAE)` access.
2. Confirm the main company is UAE-based:
   - Country = `United Arab Emirates`
   - Currency = `AED`
   - Working schedule = `UAE Standard (Sat-Thu, 8h)`
3. Confirm seeded configuration exists:
   - ranks
   - positions
   - project allocations
4. Confirm the `UAE Standard` salary structure is available on contracts.

## Recommended Demo Data

Use one clean employee so the recording stays readable:

- Employee Name: `Demo Employee 01`
- Rank: `Officer`
- Position: `Operations`
- Roster: `14/14`
- Passport No.: `P1234567`
- Passport Expiry: any future date
- Visa Expiry: any future date
- Nationality: choose actual nationality
- Location: `United Arab Emirates`
- Project Allocation: any seeded site project allocation

Contract example:

- Start Date: first day of a month
- Working Schedule: `UAE Standard (Sat-Thu, 8h)`
- Wage: `3000`
- Housing Allowance: `1500`
- Transportation Allowance: `300`
- Other Allowances: `200`
- Annual Ticket Amount: `1200`
- Scheduled Pay: `Monthly`
- Salary Structure: `UAE Standard`

## What to Explain to the Business Owner

Keep the message simple:

1. Employee identity and operating data now live on the employee record.
2. Salary ownership lives on the contract, not on ad hoc spreadsheets.
3. Monthly allowances are entered on the contract because payroll reads contract compensation.
4. `Annual Ticket Amount` is also on the contract, but it is an annual benefit reference, not the booked ticket cost.
5. The system auto-creates a cost center for each employee, so reporting has a stable analytic base.

## Recording Script

Target duration: `6-10 minutes`

### Step 1 - Show the reference setup

Open:

- `HR UAE Admin -> Configuration -> Ranks`
- `HR UAE Admin -> Configuration -> Positions`
- `HR UAE Admin -> Configuration -> Project allocations`

Talking points:

- These are controlled master lists.
- Rank and position are standardized so reporting stays consistent.
- Project Allocation is the operational project dimension used later in payroll, flights, and reports.

Expected result:

- Seeded records are visible.
- Project allocation list shows ready-to-use HQ and site project values.

### Step 2 - Create the employee

Open:

- `HR UAE Admin -> Employees -> Employees`

Create a new employee and fill the normal employee header fields, then open the `UAE Master Data` tab.

Talking points:

- This is where the offline master-data sheet is now captured in structured form.
- The tab separates identification, employment, and analytic data.

Fields to show on screen:

- `Rank`
- `Position`
- `Roster`
- `Passport`
- `Passport Expiry`
- `Visa Expiry`
- `Country`
- `Location`
- `Project Allocation`

Expected result:

- The employee saves successfully.
- The `UAE Master Data` tab is available.

### Step 3 - Show the automatic cost center behavior

Still on the employee form, look at:

- `UAE Master Data -> Analytic -> Cost Center`

Talking points:

- The system auto-creates a cost center for the employee.
- This reduces manual setup and keeps analytics aligned with the employee record.

Expected result:

- `Cost Center` is auto-filled after the employee is saved.
- The generated cost center name matches the employee name.

### Step 4 - Show computed master-data fields

On the same `UAE Master Data` tab, point out:

- `Age`
- `Time of Service`
- `Visa Status`
- `UAE Status`

Talking points:

- Some fields are computed, not typed manually.
- `Visa Status` is derived from expiry date.
- `Time of Service` comes from the employment timeline.
- `UAE Status` is designed to reflect lifecycle state and later reacts to leaves/termination workflows.

Expected result:

- Computed fields display values without manual duplication.

### Step 5 - Create the contract

Open the employee's contract from the `Contract` smart button or go to:

- `Employees app -> Employees -> Contracts`

Create the contract and fill:

- employee
- start date
- working schedule
- wage
- housing allowance
- transportation allowance
- other allowances
- annual ticket amount
- scheduled pay
- salary structure

On the form, point to:

- `Salary Information`
- `Yearly Benefits`

Talking points:

- Contract is the source of truth for compensation.
- Wage and monthly allowances belong here because payroll consumes contract compensation.
- `Annual Ticket Amount` is a contract benefit value, separate from the flight booking module.

Expected result:

- Monetary fields display in company/contract currency.
- Main company contracts use UAE defaults and the `UAE Standard` structure.

### Step 6 - Return to the employee and show the readonly mirrors

Go back to the employee and open:

- `UAE Master Data -> Employment`

Show these readonly fields:

- `Contract Wage`
- `Housing Allowance`
- `Transportation Allowance`
- `Other Allowances`
- `Annual Ticket Amount`

Talking points:

- These values are shown on the employee only for visibility.
- Ownership remains on the contract.
- This avoids double entry and inconsistent salary data.

Expected result:

- The employee shows the same values from the active contract.

## Test Checklist

Use this after recording or during a handover walkthrough.

### Functional checks

1. `Ranks` and `Positions` are visible under `HR UAE Admin -> Configuration`.
2. `Project allocations` are visible and selectable on employees.
3. Creating an employee auto-creates a cost center.
4. Renaming the employee updates the linked cost center name.
5. Archiving the employee archives the linked cost center.
6. Contract form shows:
   - `Housing Allowance`
   - `Transportation Allowance`
   - `Other Allowances`
   - `Annual Ticket Amount`
7. Employee form shows readonly mirrors of those contract values.

### Business checks

1. Master data once kept in Excel is now stored on structured records.
2. Compensation ownership is on the contract.
3. Monthly allowances are ready for payroll use later.
4. Annual ticket benefit is stored without changing flight booking prices.

### Boundary checks

1. If there is no active contract, employee compensation mirror fields should be empty.
2. `Annual Ticket Amount` should not create a payroll entry by itself in this phase.
3. Project Allocation should come only from the `Project Allocation` analytic plan.
4. Cost Center should come only from the `Cost Center` analytic plan.

## Technical Notes for the Handover

- Employee custom fields are mainly implemented in `hr_uae_master_data`.
- Cost center auto-creation is implemented on employee create/write logic.
- Compensation extensions are on `hr.contract`.
- Employee compensation fields are readonly related fields to the contract.
- Monthly allowances are designed for payroll consumption later.
- `Annual Ticket Amount` is informational contract benefit data unless a future payroll/business rule explicitly consumes it.

## Completion Criteria for Phase 1

Phase 1 is complete when you can demonstrate all of the following in one pass:

1. master setup values exist,
2. a new employee can be created,
3. cost center is auto-generated,
4. a contract can be created with wage and allowances,
5. annual ticket amount is visible on the contract,
6. employee form reflects the active contract values readonly.

## Next Phase

After this phase, the logical next recording is:

- Phase 2: audit trail and document lifecycle
