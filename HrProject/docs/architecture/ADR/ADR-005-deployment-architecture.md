> Generated: 2026-06-12 · Commit: 11ca9f9 · Source of truth: code

# Docker Compose With Nginx

## Status

Accepted, 2026-06-12.

## Context

KIG7 needs repeatable Odoo 18 deployment with PostgreSQL and websocket proxying.

## Decision

Use Compose services: `db`, `web`, `proxy`; nginx publishes 8073 and routes HTTP/websocket to Odoo.

## Alternatives

Bare-metal Odoo service; managed database; direct Odoo port exposure.

## Consequences

Positive: reproducible and simple staging/prod parity. Negative: Compose orchestration limits versus Kubernetes/managed HA.

## Source Evidence

- [../../../../docker-compose.yml](../../../../docker-compose.yml)
- [../../../../deploy/nginx-odoo.conf](../../../../deploy/nginx-odoo.conf)
- [../../../../deploy/Dockerfile](../../../../deploy/Dockerfile)
