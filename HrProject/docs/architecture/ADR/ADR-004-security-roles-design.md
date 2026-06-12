> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Three Exclusive KIG7 Roles And Global Deny Rules

## Status

Accepted, 2026-06-12.

## Context

KIG7 needs simplified business roles and must block Discuss/Calendar/Website despite additive ACLs and OR-ed group rules.

## Decision

Create three mutually exclusive roles; payroll role gets no hr_uae_base group; use global conditional deny rules.

## Alternatives

Use many overlapping groups; hide menus only; group-specific deny rules.

## Consequences

Positive: predictable isolation. Negative: requires careful implied-group regression tests.

## Source Evidence

- [../../../hr_uae_access/security/hr_uae_access_security.xml](../../../hr_uae_access/security/hr_uae_access_security.xml)
- [../../../hr_uae_access/models/res_users.py](../../../hr_uae_access/models/res_users.py)
- [../../../hr_uae_access/data/menu_restrictions.xml](../../../hr_uae_access/data/menu_restrictions.xml)
