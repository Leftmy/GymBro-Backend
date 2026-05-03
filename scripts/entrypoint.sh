#!/bin/sh

set -e

echo "Waiting for database..."

until nc -z db 5432; do
  echo "DB is unavailable - sleeping"
  sleep 2
done

echo "Database is up!"

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --no-input

exec "$@"