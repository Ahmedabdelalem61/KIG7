============================
HR UAE - Multi-currency Contracts
============================

Denominate an employment contract in any currency while payroll and accounting
stay in the **company currency** — no financials are broken.

How it works
============

* The contract gains a **Contract Currency** (default = company currency) and a
  set of *(Contract Currency)* amount fields (wage + housing / transportation /
  other allowances + annual ticket). These foreign amounts are the value the
  user enters and the **canonical** salary.
* The existing company-currency amounts (``wage`` …) stay **stored** and are a
  display/reporting mirror, refreshed at the current rate on save and by a daily
  cron — so lists, the payroll dashboard and reports stay current.
* **Payroll is authoritative and converts fresh every run**: the BASIC, housing,
  transport, other-allowance and unpaid-leave salary rules convert the foreign
  amount to the company currency at the **payslip period-end date**
  (``payslip.date_to``) via ``hr.payslip._hr_uae_company_amount``. So each
  payslip uses the rate of its own period — minimal FX gap, fair.
* The same conversion is applied to the **flight-ticket salary deduction**
  (at the deduction date) and to **salary adjustments** pushed to payslip inputs
  (at the target payslip date).
* **Default = company currency** ⇒ conversion is an identity and behaviour is
  exactly as before. Existing contracts are back-filled on install; the
  company-currency wage is never modified, so live data is safe.

Fail-safe
=========

Conversion goes through ``res.currency._hr_uae_to_company``. If a non-company
currency has **no exchange rate** defined on/before the date, payroll raises a
clear error instead of silently paying 1:1. Soft refreshes (display/cron) skip
instead of raising.

Prerequisite
============

Maintain ``res.currency`` rates (Accounting → Currencies), manually or with an
FX-provider module (e.g. OCA ``currency_rate_update``). Accuracy is only as good
as the configured rates.
