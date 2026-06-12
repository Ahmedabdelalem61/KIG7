> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Upgrade Guide

## Safe Module Upgrade Process

1. Take a `pg_dump` before any module update.
2. Review changed manifests, migrations, views, security XML/CSV, and noupdate data.
3. Stop web and run module update with `--stop-after-init --no-http --workers=0 --max-cron-threads=0`.
4. Restart web only after a clean update log.
5. Run focused tests for changed modules and smoke tests for payroll/access.

## When Migrations Are Required

Use migrations for stored data policy changes that cannot be safely represented by normal data files. Example: `hr_uae_base` migration `18.0.1.1.0` deletes blocking journal entries, switches companies to USD, and purges stale USD rates.

## Odoo-Version Risks

- OCA payroll must match Odoo 18 Community APIs.
- View XPath customizations can break when upstream views change, especially contract wage row/Converted tab areas.
- Menu XMLIDs for mail/calendar/website can change.
- `noupdate` records do not clear omitted fields on upgrade; use explicit clears like `[(5, 0, 0)]` when needed.
- Menu restrictions re-apply only when `hr_uae_access` is updated.

## Pre-Upgrade Checklist

- Read `__manifest__.py` dependency/data changes.
- Read model field changes and migrations.
- Read security XML/CSV and implied groups.
- Read salary rule XML and `noupdate` records.
- Confirm backup restore was tested recently.

## Post-Upgrade Test Command

```bash
docker compose run --rm --no-deps web odoo -d <db> -u <modules> --test-enable --stop-after-init --no-http --workers=0 --max-cron-threads=0
```

## Breaking-Change Checklist

- Payroll conversion still wraps `_compute_payslip_line` correctly.
- `_hr_uae_apply_currency` preserves authoritative foreign values.
- Rate convention remains provider-compatible.
- KIG7 implied groups still match role design.
- Contract form xpaths still render.
- Vendored OCA payroll changes do not alter state names or rule localdict semantics.
