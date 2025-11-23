#!/bin/bash
# Production startup script for single pod deployment
# This script runs all required services in a single container

set -e

echo "=== WhatsApp Scheduler Startup ==="

# Wait for database to be ready (if using external DB)
if [ -n "$DATABASE_URL" ] || [ -n "$DB_HOST" ]; then
    echo "Waiting for database to be ready..."
    python manage.py migrate --check || {
        echo "Database not ready, running migrations..."
        python manage.py migrate
    }
else
    # SQLite - just run migrations
    echo "Running migrations..."
    python manage.py migrate
fi

# Collect static files (if needed)
if [ "$COLLECT_STATIC" = "true" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Start all services using a process manager or background processes
echo "Starting services..."

# Start scheduler loop in background
python manage.py scheduler_loop &
SCHEDULER_PID=$!

# Start worker in background  
python manage.py worker &
WORKER_PID=$!

# Start Django server (foreground - this keeps the container alive)
echo "Starting Django server on 0.0.0.0:${PORT:-8000}..."
exec python manage.py runserver 0.0.0.0:${PORT:-8000}

