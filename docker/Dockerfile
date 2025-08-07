# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables for Django and Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=PokeSoul.settings
ENV POETRY_VERSION=1.8.0

# Set work directory
WORKDIR /app

# Install system dependencies for PostgreSQL and build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for dependency management
RUN pip install "poetry==$POETRY_VERSION"

# Copy poetry files for dependency installation
COPY ../pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment (use system Python)
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --no-interaction

# Copy project source code
COPY .. .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser

# Set proper permissions for the application
RUN chown -R appuser:appuser /app

# Switch to non-root user for security
USER appuser

# Expose port for web server
EXPOSE 8000

# Health check to ensure application is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
