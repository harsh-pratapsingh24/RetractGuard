# syntax=docker/dockerfile:1
# -----------------------------------------------------------------------------
# RetractGuard Production Dockerfile (Multi-Stage Build)
# Stage 1: Build Vite React Frontend
# Stage 2: Python Backend Runtime with ML Models & Retraction Watch Index
# -----------------------------------------------------------------------------

# Stage 1: Frontend Build
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Runtime
FROM python:3.11-slim AS runtime

# Install system dependencies (build essentials, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend, models, data, reports, and source
COPY src/ ./src/
COPY backend/ ./backend/
COPY models/ ./models/
COPY data/ ./data/
COPY reports/ ./reports/

# Copy built frontend assets from Stage 1 into the location expected by Flask
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    PYTHONPATH=/app

# Expose server port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start Flask with Gunicorn WSGI in production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "backend.app:app"]
