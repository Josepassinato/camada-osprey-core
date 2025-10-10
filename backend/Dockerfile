# Backend Dockerfile para OSPREY Immigration Platform
FROM python:3.11-slim

# Metadata
LABEL maintainer="OSPREY Support <support@osprey.com>"
LABEL description="OSPREY Immigration Platform Backend API"
LABEL version="2.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Create virtual environment and install Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Emergent Integrations (if needed)
RUN pip install --no-cache-dir emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ || echo "Emergent integrations not available"

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r osprey && useradd -r -g osprey -u 1001 osprey

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/uploads /app/cache \
    && chown -R osprey:osprey /app

# Switch to non-root user
USER osprey

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/production/system/health || exit 1

# Expose port
EXPOSE 8001

# Environment variables with defaults
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV LOG_LEVEL=info

# Start command
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "${PORT:-8001}", "--workers", "1"]