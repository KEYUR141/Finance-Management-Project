#!/bin/bash

# Cloud Run Entrypoint Script
# Keep startup fast: migrations/seeding should run as one-off jobs, not at boot.

set -e  # Exit on any error

echo "Starting Finance Dashboard on Cloud Run..."

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT:-8080}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8080} \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  project.wsgi:application
