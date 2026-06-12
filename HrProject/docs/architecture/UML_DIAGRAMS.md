> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# UML Diagrams

## Multicurrency Class Diagram

```mermaid
classDiagram
  class HrContract { contract_currency_id; wage_foreign; _hr_uae_apply_currency(); _hr_uae_cron_refresh_currency() }
  class HrPayslip { date_to; _compute_payslip_line(); _hr_uae_company_amount() }
  class HrUaeFxContract { __getattr__(); __getitem__() }
  class ResCurrency { _hr_uae_to_company(); _hr_uae_from_company(); _hr_uae_has_rate() }
  HrPayslip --> HrUaeFxContract
  HrUaeFxContract --> HrContract
  HrUaeFxContract --> ResCurrency
```

## XLSX Class Diagram

```mermaid
classDiagram
  class XlsxTemplate { model_name; line_ids }
  class XlsxTemplateLine { field_name; column_name; sequence }
  class XlsxImportWizard { template_id; file; action_validate(); action_import() }
  XlsxTemplate "1" --> "many" XlsxTemplateLine
  XlsxImportWizard --> XlsxTemplate
```

## Access Domain Diagram

```mermaid
classDiagram
  class ResUsers { groups_id; _check_kig7_single_role() }
  class KIG7Roles { HR Officer; HR Manager; Payroll Manager }
  class GlobalRules { discuss.channel; calendar.event; website.page }
  ResUsers --> KIG7Roles
  KIG7Roles --> GlobalRules
```

## State Diagrams

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> ToApprove: submit adjustment
  ToApprove --> Approved: HR Manager approve
  ToApprove --> Refused
  Approved --> Done: one-shot applied
  Approved --> Approved: range/recurring cron
```

```mermaid
stateDiagram-v2
  [*] --> draft
  draft --> booked: action_book
  booked --> completed: action_complete
  booked --> cancelled: action_cancel
  booked --> rescheduled: action_reschedule
  cancelled --> draft: reset
  rescheduled --> draft: reset
```

```mermaid
stateDiagram-v2
  [*] --> draft
  draft --> active: activate
  active --> closed: close
  draft --> draft: reset allowed
  active --> active: reset blocked
```

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Waiting: OCA payroll verify/on_hold states may apply
  Waiting --> Done: validate
  Waiting --> Cancel: cancel
  Draft --> Cancel: cancel
```

⚠ Unverified: exact OCA payslip state labels should be checked against the installed `thirdparty/payroll` views/model when changing payroll workflow.

## Employee Lifecycle Activity

```mermaid
flowchart TD
  A["Hire"] --> B["Employee master data"] --> C["Contract"] --> D["Leaves/documents/flights"] --> E["Payroll"] --> F["Termination"] --> G["Archive employee"]
```

## Payslip Compute With Conversion

```mermaid
sequenceDiagram
  participant Rule as Salary rule
  participant Slip as hr.payslip
  participant Proxy as HrUaeFxContract
  participant Currency as res.currency
  Slip->>Proxy: inject into localdict
  Rule->>Proxy: contract.wage
  Proxy->>Currency: _hr_uae_to_company(amount, company, date_to)
  Currency-->>Rule: converted amount or UserError
```

## Package Diagram

```mermaid
flowchart LR
  Base["hr_uae_base"] --> Master["hr_uae_master_data"] --> Audit["hr_uae_audit_trail"]
  Master --> Leaves["hr_uae_leaves"]
  Master --> Flights["hr_uae_flights"]
  Audit --> Docs["hr_uae_documents"]
  Leaves --> Payroll["hr_uae_payroll"]
  Flights --> Payroll
  Payroll --> Adjust["hr_uae_salary_adjustment"]
  Payroll --> Term["hr_uae_termination"]
  Payroll --> Multi["hr_uae_multicurrency"]
  Reports["hr_uae_reports"] --> Project["hr_uae_project_department"] --> Xlsx["hr_uae_xlsx_io"] --> Access["hr_uae_access"]
```
