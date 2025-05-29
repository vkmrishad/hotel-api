#!/bin/sh
set -e

>&2 echo "🛠️ Running migrations..."
uv run python manage.py migrate --noinput

exec "$@"
