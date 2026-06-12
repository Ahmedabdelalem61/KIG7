> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Multicurrency Payroll Conversion Via Proxy

## Status

Accepted, 2026-06-12.

## Context

Payroll salary-rule XML can be overwritten or reverted by upgrades; KIG7 needs period-end conversion for wage and allowances.

## Decision

Inject `HrUaeFxContract` into the salary-rule localdict in `hr.payslip._compute_payslip_line`.

## Alternatives

Override every salary-rule XML formula; store converted payroll fields on contract; customize OCA payroll engine.

## Consequences

Positive: central conversion and upgrade-resistant salary rules. Negative: high-risk override of payslip compute path.

## Source Evidence

- [../../../hr_uae_multicurrency/models/hr_payslip.py](../../../hr_uae_multicurrency/models/hr_payslip.py)
- [../../../hr_uae_payroll/data/hr_salary_rule_data.xml](../../../hr_uae_payroll/data/hr_salary_rule_data.xml)
