#!/bin/sh
set -e

# If data/ is a freshly-mounted empty volume, seed it with the raw dataset
# baked into the image so the app has something to auto-ingest on startup
# (see app.admin.kb_admin.auto_bootstrap, invoked from app.main's startup
# event). On subsequent runs data/raw already has content, so this no-ops.
if [ -d "/srv/app/data/raw" ] && [ -z "$(ls -A /srv/app/data/raw 2>/dev/null)" ]; then
  echo "[entrypoint] data/raw is empty — seeding from the baked-in dataset."
  cp -r /srv/app/seed_data/raw/. /srv/app/data/raw/
fi

echo "[entrypoint] Creating database tables (idempotent) ..."
python scripts/init_db.py

if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
  echo "[entrypoint] Seeding roles/permissions and admin user ..."
  python scripts/seed_auth.py --admin-email "$ADMIN_EMAIL" --admin-password "$ADMIN_PASSWORD"
else
  echo "[entrypoint] Seeding roles/permissions (no ADMIN_EMAIL/ADMIN_PASSWORD set — skipping admin user creation) ..."
  python scripts/seed_auth.py
fi

echo "[entrypoint] Handing off to: $*"
exec "$@"
