# KIG7 Odoo 18 web image — extends the official image so deploys are reproducible
# and extra OS packages can be added in one place. Addons stay bind-mounted from
# the repo (see docker-compose.yml); this layer is runtime/deps only.
#
# Build from repo root:
#   docker compose build web
#   docker compose up -d

FROM odoo:18.0

USER root

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        fontconfig \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f

USER odoo
