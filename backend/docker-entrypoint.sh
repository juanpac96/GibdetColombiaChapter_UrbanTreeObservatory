#!/bin/bash
set -e

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files if not in debug mode
if [ "$DEBUG" != "1" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Start server
echo "Starting server..."
exec "$@"
