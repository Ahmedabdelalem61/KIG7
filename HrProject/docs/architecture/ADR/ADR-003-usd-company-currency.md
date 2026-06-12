> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# USD Code-Defined Company Currency

## Status

Accepted, 2026-06-12.

## Context

Staging and production need aligned company currency and stale company-currency rate rows corrupt conversions.

## Decision

Define `HR_UAE_COMPANY_CURRENCY_XMLID = "base.USD"`; force only during install; migrate existing DBs to USD and purge USD rates.

## Alternatives

Leave company currency database-defined; force currency every upgrade; use AED as company currency.

## Consequences

Positive: consistent payroll base. Negative: historical relabeling/finance review required for old data.

## Source Evidence

- [../../../hr_uae_base/models/res_company.py](../../../hr_uae_base/models/res_company.py)
- [../../../hr_uae_base/migrations/18.0.1.1.0/post-migration.py](../../../hr_uae_base/migrations/18.0.1.1.0/post-migration.py)
