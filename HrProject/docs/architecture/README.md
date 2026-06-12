> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# KIG7 Architecture Documentation

KIG7 is an Odoo 18 Community HR platform under `HrProject/` with custom UAE HR master data, documents, flights, leaves, payroll, salary adjustments, terminations, reporting, XLSX I/O, multicurrency payroll conversion, FX-rate updates, and KIG7-specific role isolation. The codebase also vendors OCA `payroll` under `thirdparty/payroll` and runs via Docker Compose with nginx, Odoo, and PostgreSQL.

Owner: HrProject Team. Maintenance rules: [MAINTENANCE.md](MAINTENANCE.md).

## Index

- [System Overview](SYSTEM_OVERVIEW.md)
- [Module Catalog](MODULE_CATALOG.md)
- [Module Dependencies](MODULE_DEPENDENCIES.md)
- [Architecture](ARCHITECTURE.md)
- [Data Model](DATA_MODEL.md)
- [Business Workflows](BUSINESS_WORKFLOWS.md)
- [Business Rules](BUSINESS_RULES.md)
- [Use Cases](USE_CASES.md)
- [UML Diagrams](UML_DIAGRAMS.md)
- [Security Architecture](SECURITY_ARCHITECTURE.md)
- [Integrations](INTEGRATIONS.md)
- [Reporting and Dashboards](REPORTING_AND_DASHBOARDS.md)
- [Deployment](DEPLOYMENT.md)
- [Operations Runbook](OPERATIONS_RUNBOOK.md)
- [Testing Strategy](TESTING_STRATEGY.md)
- [Upgrade Guide](UPGRADE_GUIDE.md)
- [Decision Guide](DECISION_GUIDE.md)
- [Known Gaps](KNOWN_GAPS.md)
- [Glossary](GLOSSARY.md)
- [Architecture Map](architecture-map.yaml)
- [Traceability Matrix](traceability-matrix.csv)
- [ADRs](ADR/)

## Reading Orders

New developer: README -> SYSTEM_OVERVIEW -> MODULE_CATALOG -> DATA_MODEL -> BUSINESS_WORKFLOWS -> TESTING_STRATEGY -> DECISION_GUIDE.

AI agent: README -> DECISION_GUIDE -> MODULE_DEPENDENCIES -> SECURITY_ARCHITECTURE -> BUSINESS_RULES -> KNOWN_GAPS -> MAINTENANCE.

Operator: README -> DEPLOYMENT -> OPERATIONS_RUNBOOK -> INTEGRATIONS -> UPGRADE_GUIDE -> KNOWN_GAPS.
