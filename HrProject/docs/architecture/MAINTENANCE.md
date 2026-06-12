> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Maintenance

## Living-Doc Rules

- Code is the source of truth; read manifests/models/views/security/data/tests before editing docs.
- Start every markdown file with the generated header line and update commit/date when regenerating or materially editing.
- Use relative links from `docs/architecture/` to source as `../../module/file`; from `ADR/` use `../../../module/file`.
- Mark unclear behavior as `⚠ Unverified`, `Inferred:`, or `Recommendation:`.
- Do not include secrets, passwords, IPs, tokens, or DB credentials.
- Keep each document focused and below roughly 450 lines.

## Required Change Matrix

| Code change | Required docs/tests |
|---|---|
| Model/field | DATA_MODEL + BUSINESS_RULES |
| Workflow/action/state | BUSINESS_WORKFLOWS + UML_DIAGRAMS + USE_CASES |
| Security/group/ACL/rule/menu | SECURITY_ARCHITECTURE + access tests |
| Dependency/manifest | MODULE_DEPENDENCIES + architecture-map.yaml |
| Cron/API/integration | INTEGRATIONS + OPERATIONS_RUNBOOK |
| Deployment/config | DEPLOYMENT + UPGRADE_GUIDE |
| Salary rule/payroll formula | BUSINESS_RULES + TESTING_STRATEGY + payroll tests |
| Known production/staging fact | KNOWN_GAPS + relevant runbook |
| Architectural decision | ADR update or new ADR |

## Validation Steps

1. Headers match exactly.
2. Mermaid diagrams render.
3. Relative links resolve.
4. `grep` for secret-like values before commit.
5. Line counts stay within the focus limit.
6. Architecture map and traceability matrix match manifests/tests.
