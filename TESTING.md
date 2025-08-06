# 🧪 Testing & Code Quality Guide

## Quick Commands

### **Using Docker (Recommended)**

```bash
# Run all tests in Docker
./docker.sh test

# Or manually:
docker-compose -f docker/docker-compose.yml exec web python -m pytest

# Run specific apps in Docker
docker-compose -f docker/docker-compose.yml exec web python -m pytest pokemons/tests/ -v
docker-compose -f docker/docker-compose.yml exec web python -m pytest matcher/tests/ -v

# Run code quality checks in Docker
./docker.sh quality

# Or manually:
docker-compose -f docker/docker-compose.yml exec web poetry run black .
docker-compose -f docker/docker-compose.yml exec web poetry run isort .
docker-compose -f docker/docker-compose.yml exec web poetry run flake8
docker-compose -f docker/docker-compose.yml exec web poetry run mypy
docker-compose -f docker/docker-compose.yml exec web poetry run pre-commit run --all-files
```

### **Local Development (Alternative)**

```bash
# Run all tests
poetry run pytest

# Run specific apps
poetry run pytest pokemons/tests/ -v
poetry run pytest matcher/tests/ -v

# Debug mode
poetry run pytest -vvv -s

# Code quality checks
poetry run black .
poetry run isort .
poetry run flake8
poetry run mypy

# Security check
poetry run bandit -r . -f json -o bandit-report.json

# Coverage report
poetry run coverage run -m pytest
poetry run coverage report
poetry run coverage html

# Pre-commit hooks (runs all checks)
poetry run pre-commit run --all-files
```

## 🐳 **Important: Testing in Docker**

**When using Docker, tests MUST be executed inside the container:**

```bash
# ✅ CORRECT - Execute tests inside Docker container
docker-compose -f docker/docker-compose.yml exec web python -m pytest

# ❌ WRONG - These won't work because Django is running in container
poetry run pytest
python -m pytest
```

### **Why This Matters:**
- **Django server** runs **inside the Docker container**
- **Database** is only accessible **within the Docker network**
- **Environment variables** are set **inside the container**
- **Dependencies** are installed **inside the container**

## Test Structure

**19 tests total:**
- **Pokemon App (8 tests)** - API, serializers, error handling
- **Matcher App (6 tests)** - matching algorithm
- **Admin Interface (5 tests)** - admin configuration

## Code Quality Tools

- **Black** (25.1.0): Code formatting
- **isort** (6.0.1): Import sorting
- **Flake8** (7.3.0): Code linting
- **MyPy** (1.17.1): Type checking
- **Bandit** (1.8.6): Security analysis
- **Coverage** (7.10.2): Test coverage
- **Pre-commit** (4.2.0): Automated code quality checks

## Configuration Files

- **`.flake8`**: Configures Flake8 linting rules and exclusions
- **`mypy.ini`**: Configures MyPy type checking with Django-specific settings
- **`.pre-commit-config.yaml`**: Defines pre-commit hooks for automated checks
- **`pyproject.toml`**: Contains tool configurations for Black, isort, and other tools

## Common Issues

### Database Connection
```bash
# Check if database is running
docker-compose -f docker/docker-compose.yml ps db

# Check database logs
docker-compose -f docker/docker-compose.yml logs db

# Or use docker.sh
./docker.sh status
./docker.sh logs
```

### Test Isolation
Tests use `@pytest.mark.django_db` for database access.

### Factory Issues
Ensure factory fields match model fields:
```python
PokemonFactory(name="test")  # name field must exist
```

### Docker Issues
```bash
# If tests fail in Docker, try rebuilding
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d --build
./docker.sh test

# If you need to reset everything
./docker.sh clean
./docker.sh up
./docker.sh test
```

---

**All tests passing! 🎉**
