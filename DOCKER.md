# Docker Setup for PokeSoul

This document provides instructions for running PokeSoul using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PokeSoul
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

3. **Access the application**
   - Web application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin
   - API schema: http://localhost:8000/swagger.json

## Services

### Web Application (Django)
- **Port**: 8000
- **Image**: Built from local Dockerfile
- **Environment**: Development mode with hot reload
- **Health Check**: HTTP endpoint check every 30s

### PostgreSQL Database
- **Port**: 5432
- **Database**: pokesoul
- **User**: pokesoul
- **Password**: pokesoul
- **Health Check**: Database connectivity check every 10s

### Redis Cache
- **Port**: 6379
- **Purpose**: Caching Pokemon data and match results
- **Health Check**: Redis ping every 10s

## 🐳 **Important: Django Commands in Docker**

**When using Docker, Django management commands MUST be executed inside the container:**

```bash
# ✅ CORRECT - Execute commands inside Docker container
docker-compose -f docker/docker-compose.yml exec web python manage.py [command]

# ❌ WRONG - These won't work because Django server is running in container
python manage.py [command]
```

### **Why This Matters:**
- **Django server** runs **inside the Docker container**
- **Database** is only accessible **within the Docker network**
- **Environment variables** are set **inside the container**
- **Dependencies** are installed **inside the container**

## Development Commands

### **Using docker.sh Script (Recommended)**

The `docker.sh` script simplifies Docker operations:

```bash
# Start services
./docker.sh up

# Load initial data
./docker.sh load-data

# Run tests
./docker.sh test

# Run code quality checks
./docker.sh quality

# View logs
./docker.sh logs

# Django shell
./docker.sh shell

# Database shell
./docker.sh db

# Redis shell
./docker.sh redis

# Stop services
./docker.sh down

# Clean slate (removes all data)
./docker.sh clean
```

### **Manual Docker Commands**

If you prefer direct Docker commands:

```bash
# Run in background
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f web

# Execute commands in container
docker-compose -f docker/docker-compose.yml exec web python manage.py shell
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate
docker-compose -f docker/docker-compose.yml exec web python manage.py loaddata fixtures/question_set.json
docker-compose -f docker/docker-compose.yml exec web python manage.py load_top_pokemons --limit 100

# Run tests
docker-compose -f docker/docker-compose.yml exec web python -m pytest

# Create superuser
docker-compose -f docker/docker-compose.yml exec web python manage.py createsuperuser

# Run code quality checks
docker-compose -f docker/docker-compose.yml exec web poetry run black .
docker-compose -f docker/docker-compose.yml exec web poetry run isort .
docker-compose -f docker/docker-compose.yml exec web poetry run flake8
docker-compose -f docker/docker-compose.yml exec web poetry run mypy
docker-compose -f docker/docker-compose.yml exec web poetry run pre-commit run --all-files

# Stop services
docker-compose -f docker/docker-compose.yml down

# Remove volumes (clean slate)
docker-compose -f docker/docker-compose.yml down -v

# Rebuild without cache
docker-compose -f docker/docker-compose.yml build --no-cache
```

## Environment Variables

The following environment variables are configured in docker-compose.yml:

```env
# Django settings
DEBUG=True
DJANGO_SETTINGS_MODULE=PokeSoul.settings
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database settings
DATABASE_URL=postgresql://pokesoul:pokesoul@db:5432/pokesoul

# Redis settings
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

## Production Deployment

For production deployment, use the production Docker Compose file:

```bash
# Set environment variables
export SECRET_KEY="your-secure-secret-key"
export ALLOWED_HOSTS="your-domain.com,www.your-domain.com"
export DB_PASSWORD="your-secure-db-password"

# Run production stack
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Production Features
- **Optimized image**: Uses `Dockerfile.prod` with only production dependencies
- **Gunicorn**: Production-grade WSGI server with 3 workers
- **Resource limits**: Memory and CPU constraints
- **Nginx**: Optional reverse proxy for SSL termination
- **Health checks**: Built-in monitoring for all services
- **Structured logging**: JSON logs for production monitoring

## Dockerfile Features

### Development Environment (Dockerfile)
- **Full dependencies**: Includes all development tools (Black, isort, Flake8, MyPy, etc.)
- **Volume mounting**: Live code changes without rebuilding
- **Non-root user**: Security best practice
- **Health checks**: Built-in monitoring
- **Poetry**: Modern dependency management

### Production Environment (Dockerfile.prod)
- **Optimized image**: Only production dependencies
- **Gunicorn**: Production-grade WSGI server
- **Resource limits**: Memory and CPU constraints
- **Alpine images**: Smaller footprint for databases

## Troubleshooting

### Database connection issues
```bash
docker-compose -f docker/docker-compose.yml exec db psql -U pokesoul -d pokesoul
```

### Redis connection issues
```bash
docker-compose -f docker/docker-compose.yml exec redis redis-cli
```

### View container status
```bash
docker-compose -f docker/docker-compose.yml ps
```

### Check health status
```bash
docker-compose -f docker/docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

### Rebuild containers
```bash
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up --build
```

### View resource usage
```bash
docker stats
```

## Logging & Monitoring

### **Log Files in Docker:**
- **Application logs**: Available in container logs
- **File logs**: Mounted to host for persistence (`./logs:/app/logs`)
- **JSON logs**: Structured format for monitoring tools
- **Auto-creation**: Log directory created automatically in containers

### **View Logs:**
```bash
# View application logs
docker-compose -f docker/docker-compose.yml logs -f web

# View specific service logs
docker-compose -f docker/docker-compose.yml logs -f db
docker-compose -f docker/docker-compose.yml logs -f redis

# View logs with timestamps
docker-compose -f docker/docker-compose.yml logs -f --timestamps web
```

### **Log Levels:**
- **DEBUG**: Detailed application logs (development)
- **INFO**: Performance metrics and request tracking
- **WARNING**: Non-critical issues
- **ERROR**: Application errors and exceptions

### **Performance Monitoring:**
The application automatically logs:
- Request duration and status codes
- Cache hits/misses with truncated hashes
- Matching algorithm performance
- API response times

## Performance Tips

1. **Use volumes for development**: Code changes are reflected immediately
2. **Health checks**: Ensure services are ready before starting dependent services
3. **Restart policies**: Services restart automatically on failure
4. **Resource limits**: Consider adding memory/CPU limits for production
5. **Log monitoring**: Use structured logs for performance analysis

## Security Notes

- Default passwords are for development only
- Change `SECRET_KEY` for production
- Consider using Docker secrets for sensitive data
- Non-root user in container for security
