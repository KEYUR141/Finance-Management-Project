# Official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY Backend/project/requirements.txt /app/

# Install Python dependencies including gunicorn for Cloud Run
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn whitenoise

# Copy project files
COPY Backend/project /app/

# Note: If you have finance_seed_v3.xlsx in Backend/project/, it will be copied automatically
# If the file doesn't exist, that's OK - seed_db.py will skip seeding gracefully

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Collect static files for Cloud Run
RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

# Expose port (Cloud Run uses PORT environment variable, default 8080)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\",\"8080\")}/', timeout=5)" || exit 1

# Run entrypoint script that starts Gunicorn
CMD ["/app/entrypoint.sh"]
