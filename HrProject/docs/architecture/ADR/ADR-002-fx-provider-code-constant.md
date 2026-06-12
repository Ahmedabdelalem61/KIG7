> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# FX Provider As Code Constant

## Status

Accepted, 2026-06-12.

## Context

FX provider choice is operationally important and should not drift per database.

## Decision

Use `DEFAULT_FX_URL` constant and no `ir.config_parameter`.

## Alternatives

Database config parameter; system parameter per company; manual-only rates.

## Consequences

Positive: deterministic deploys. Negative: provider changes require code deploy.

## Source Evidence

- [../../../hr_uae_fx_rate_update/models/res_currency.py](../../../hr_uae_fx_rate_update/models/res_currency.py)
