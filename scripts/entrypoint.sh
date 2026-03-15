#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for database..."
# You can add a 'sleep' or database check here if needed

echo "Applying database migrations..."
# --noinput ensures the process doesn't wait for user confirmation
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Execute the main container command (passed as arguments)
exec "$@"