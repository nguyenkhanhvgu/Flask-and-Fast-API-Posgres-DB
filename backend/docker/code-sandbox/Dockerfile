# Dockerfile for Python code execution sandbox
FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r sandbox && useradd -r -g sandbox sandbox

# Install basic packages needed for common exercises
RUN pip install --no-cache-dir \
    requests==2.31.0 \
    numpy==1.24.3 \
    pandas==2.0.3 \
    matplotlib==3.7.2 \
    flask==2.3.3 \
    fastapi==0.104.1 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9

# Set working directory
WORKDIR /app

# Switch to non-root user
USER sandbox

# Default command (will be overridden)
CMD ["python"]