# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Install poetry
RUN pip install poetry==1.8.0

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Configure poetry to not create virtual env and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and shared prompt assets
COPY compass/ ./compass/
COPY prompts/ ./prompts/

# Create data directory
RUN mkdir -p data

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AWS_REGION=us-east-1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/healthcheck')" || exit 1

# Run the application
CMD ["uvicorn", "compass.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
