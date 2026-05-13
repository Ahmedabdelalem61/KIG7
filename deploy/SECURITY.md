# Security checklist (staging VPS)

1. **Rotate any password that was shared in chat, email, or tickets** (host root, Postgres, Odoo admin users).
2. Prefer **SSH public keys** for server access; disable root password login when keys work (`PermitRootLogin prohibit-password` or use a sudo user).
3. Keep **`.env` out of Git** (already gitignored). Copy from `.env.example` on the server only.
4. Change **`POSTGRES_PASSWORD`** and the matching `db_password` in `configs/docker.odoo.conf` before any internet-exposed deployment.
5. **`admin_passwd`** in `docker.odoo.conf` is the Odoo “master password” for database operations; treat it like a secret in production.
6. After restore, log in with **existing users from the dump** (or reset one admin via Odoo shell). The literal login `admin` / `admin` only applies if that user exists in the restored database with that password.
