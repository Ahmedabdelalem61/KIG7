> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Operations Runbook

## Daily Checks

- `docker compose ps` shows `db`, `web`, and `proxy` healthy/running.
- `/web/login` responds through the published port.
- Review recent logs: `docker compose logs --since=24h web proxy db`.
- Confirm scheduled actions ran: FX update, contract currency refresh, document expiry, recurring adjustments.

## Cron Monitoring

Check Odoo Scheduled Actions for:

- `HR UAE: Update exchange rates (online)`
- `HR UAE: Refresh contract currency amounts`
- document expiry cron
- salary adjustment recurring cron
- master-data status recompute and leave alerts

## FX Failure Diagnosis

```bash
docker compose logs web | grep hr_uae_fx
```

If fetch failed, run the manual action "Update Exchange Rates (online)" or execute the model method from an Odoo shell. A payroll `UserError` saying no exchange rate exists means payroll refused to use a silent 1:1 conversion; add/import the missing rate on or before the payslip period-end date.

## Payroll Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| BASIC = 0 for foreign contract | Missing/soft display conversion or missing authoritative foreign amount | Check `wage_foreign`, contract currency, and rate |
| Payslip compute raises missing rate | No rate on/before `date_to` | Add rate or run FX updater |
| Flight deduction absent | Flight not own_account/booked/completed or outside deduction period | Check flight state/payment/date |
| Adjustment absent | Not approved, wrong mode dates, no matching draft/verify/on_hold slip | Review adjustment state and target |

## Logs

Use `docker compose logs web`, `docker compose logs proxy`, and `docker compose logs db`. Avoid printing secrets from environment/config output.

## Backup Verification

Periodically restore the latest dump into a disposable DB and verify `/web/login`, module list, employee count, and a sample payslip compute.

## Common Incidents

| Incident | Response |
|---|---|
| FX provider outage | Leave cron to retry; use manual rates if payroll is blocked |
| Failed module upgrade | Stop web, restore dump, check traceback, rerun update with focused modules |
| Role user sees Discuss/Calendar/Website | Update `hr_uae_access`, verify global rules active, clear browser cache/session |
| Default users still active with default credentials | Rotate passwords or archive users before production |
