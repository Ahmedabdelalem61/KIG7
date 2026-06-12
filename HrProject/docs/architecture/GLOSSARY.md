> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Glossary

| Term | Meaning in this codebase |
|---|---|
| Basic / BASIC | Salary rule code for base wage; reads `contract.wage`, converted by multicurrency proxy when needed. |
| NET | Salary rule code summing BASIC, allowances, and deductions. |
| Allowances | Housing, transport, other allowances on contract; foreign fields are authoritative under multicurrency. |
| Annual ticket | Contract/flight-related monetary concept for ticket allowance/flight tickets. |
| EOS | End of service; termination workflow exists, detailed EOS formula is ⚠ Unverified in surveyed code. |
| Adjustment kinds | `adjustment`, `allowance`, `deduction`; map to payslip input codes. |
| Adjustment modes | `one_shot`, `range`, `recurring`. |
| Payslip | OCA payroll document for employee salary period. |
| Payslip run | Batch grouping of payslips. |
| Salary structure/rules | OCA payroll objects defining rule sequence, categories, Python amount formulas. |
| Contract currency | Currency selected on contract for authoritative wage/allowance entry. |
| Company currency | USD by code policy for KIG7. |
| Period-end rate | Rate on or before payslip `date_to`, used for payroll conversion. |
| Rate convention | Units of target currency per 1 company-currency unit in `res.currency.rate.rate`. |
| Record rule | Odoo domain rule applied after ACLs. Global rules are AND-ed. |
| ACL | Odoo model-level create/read/write/unlink permission. ACLs are additive. |
| Implied group | Odoo group membership automatically granted by another group. |
| XMLID | Stable external identifier for Odoo data records. |
| noupdate | Odoo data records not overwritten on module upgrade by default. |
| Cron | Odoo scheduled action. |
| Wizard | Transient model for guided import/export/action flows. |
| Audit mixin | Custom mixin logging selected HR model changes. |
