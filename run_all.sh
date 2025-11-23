#!/bin/bash
# Script to run all services for WhatsApp Scheduler
# This runs: migrations, Django server, scheduler loop, and worker

set -e

echo "Starting WhatsApp Scheduler services..."

# Run migrations first (required before starting services)
echo "Running database migrations..."
python manage.py migrate --noinput

# Start Django server in background
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Start scheduler loop in background
echo "Starting scheduler loop..."
python manage.py scheduler_loop &
SCHEDULER_PID=$!

# Start worker in background
echo "Starting worker..."
python manage.py worker &
WORKER_PID=$!

echo "All services started!"
echo "Django server PID: $DJANGO_PID"
echo "Scheduler loop PID: $SCHEDULER_PID"
echo "Worker PID: $WORKER_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $DJANGO_PID $SCHEDULER_PID $WORKER_PID 2>/dev/null || true
    wait
    echo "All services stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait

