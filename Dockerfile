# ============================================================
# ACEest Fitness & Gym - Dockerfile
# Task 5: Containerization with Docker
# ============================================================

# Stage 1: Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="ACEest DevOps Team"
LABEL version="3.2.4"
LABEL description="ACEest Fitness & Gym Management System"

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    APP_VERSION=3.2.4

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY tests/ tests/

# Create non-root user for security
RUN useradd -m -u 1000 aceest && \
    chown -R aceest:aceest /app

USER aceest

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Initialize DB and start app
CMD ["python", "-c", "from app import init_db; init_db()"] && \
    CMD ["python", "app.py"]

# Proper CMD with gunicorn for production
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 60 app:app"]
