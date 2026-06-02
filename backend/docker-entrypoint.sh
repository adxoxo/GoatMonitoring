#!/bin/sh
# Runs on every backend container start (production).
# Applies migrations and collects static, then execs the CMD (Gunicorn).
set -e

echo "==> Applying database migrations"
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Starting: $*"
exec "$@"
