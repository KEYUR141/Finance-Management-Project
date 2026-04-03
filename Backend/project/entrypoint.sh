#!/bin/bash

# Cloud Run Entrypoint Script
# This script runs migrations and seeds the database before starting the app

set -e  # Exit on any error

echo "Starting Finance Dashboard on Cloud Run..."

# Step 1: Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Step 2: Seed data from Excel
echo "Seeding data from Excel file..."
python manage.py seed_db

# Step 3: Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Step 4: Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  project.wsgi:application
