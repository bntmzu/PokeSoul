# 🌟 PokeSoul

Find the Pokémon that truly reflects your inner world — one question at a time.

This project started as a way to practice Django and working with APIs, but somewhere along the way, I got really into it. I wanted it to feel fun, flexible, and easy to grow, so I built the architecture with future ideas in mind. And some of those ideas are already on the way: a deeper and more personal questionnaire, real Pokémon voice playback, and a cozy little habitat visualization to show where your Pokémon truly belongs! :)

## 👨‍💻 **For Reviewers - Quick Start**

**Want to test the project? Just run:**
```bash
git clone https://github.com/bntmzu/PokeSoul.git
cd PokeSoul
./docker.sh up
```

**Load initial data:**
```bash
./docker.sh load-data
```

**Then visit:** http://localhost:8000

**Run tests:** `./docker.sh test`

**Run code quality checks:** `./docker.sh quality`

---

## 🎯 Features

- **Personality Quiz**: 16 carefully crafted questions to understand your unique traits
- **Intelligent Matching**: Advanced algorithm that considers types, colors, habitats, and abilities
- **Beautiful UI**: Modern, responsive design with spring gradient theme
- **REST API**: Full API with OpenAPI/Swagger JSON schema
- **Caching**: Redis-based caching for improved performance
- **Docker Support**: Complete containerization with PostgreSQL and Redis
- **Health Checks**: Built-in monitoring for all services

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/bntmzu/PokeSoul.git
   cd PokeSoul
   ```

2. **Run with Docker Compose**
   ```bash
   ./docker.sh up
   ```

3. **Load initial data**
   ```bash
   ./docker.sh load-data
   ```

4. **Access the application**
   - Web application: http://localhost:8000
   - Admin interface: http://localhost:8000/admin
   - API schema: http://localhost:8000/swagger.json

### Local Development

1. **Install dependencies**
   ```bash
   poetry install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run migrations**
   ```bash
   poetry run python manage.py migrate
   ```

4. **Load Pokemon data**
   ```bash
   poetry run python manage.py load_top_pokemons --limit 100
   poetry run python manage.py loaddata fixtures/question_set.json
   ```

5. **Start the server**
   ```bash
   poetry run python manage.py runserver
   ```

6. **Run code quality checks**
   ```bash
   poetry run pre-commit run --all-files
   ```

## 🧪 Testing & Code Quality

```bash
# Run all tests
poetry run pytest
```

## 🐳 Docker Commands

### **Important: Django Commands in Docker**

When using Docker, Django management commands must be executed **inside the container**:

```bash
# ✅ CORRECT - Execute commands inside Docker container
docker-compose -f docker/docker-compose.yml exec web python manage.py [command]

# Examples:
docker-compose -f docker/docker-compose.yml exec web python manage.py loaddata fixtures/question_set.json
docker-compose -f docker/docker-compose.yml exec web python manage.py load_top_pokemons --limit 100
docker-compose -f docker/docker-compose.yml exec web python manage.py shell
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate

# ❌ WRONG - These won't work because Django server is running in container
python manage.py loaddata fixtures/question_set.json
python manage.py load_top_pokemons --limit 100
```

### **Using docker.sh Script**

The `docker.sh` script simplifies Docker commands:

```bash
# Load data (executes the correct Docker commands)
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
# Start services
docker-compose -f docker/docker-compose.yml up -d

# Load quiz questions
docker-compose -f docker/docker-compose.yml exec web python manage.py loaddata fixtures/question_set.json

# Load Pokemon data
docker-compose -f docker/docker-compose.yml exec web python manage.py load_top_pokemons --limit 100

# Run migrations
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate

# Django shell
docker-compose -f docker/docker-compose.yml exec web python manage.py shell

# View logs
docker-compose -f docker/docker-compose.yml logs web

# Stop services
docker-compose -f docker/docker-compose.yml down
```

## 📁 Project Structure

```
PokeSoul/
├── core/                    # Quiz functionality
│   ├── migrations/         # Database migrations
│   ├── templates/          # HTML templates
│   └── tests/             # Test files
├── pokemons/               # Pokemon data management
│   ├── migrations/         # Database migrations
│   ├── tests/             # Test files
│   └── management/        # Custom commands
├── matcher/                # Matching algorithm
│   ├── migrations/         # Database migrations
│   ├── tests/             # Test files
│   └── cache.py           # Redis caching
├── fixtures/               # Initial data
│   └── question_set.json  # Quiz questions
├── templates/              # Base templates

├── docker/                # Docker configuration files
│   ├── Dockerfile        # Development container configuration
│   ├── Dockerfile.prod   # Production container configuration
│   ├── docker-compose.yml # Development setup
│   └── docker-compose.prod.yml # Production setup
├── pyproject.toml         # Dependencies
├── poetry.lock            # Locked versions
├── pytest.ini            # Test configuration
├── .flake8               # Flake8 configuration
├── mypy.ini              # MyPy configuration
├── .pre-commit-config.yaml # Pre-commit hooks
├── .dockerignore         # Docker ignore patterns
├── docker.sh             # Docker management script
└── README.md              # Project documentation
```

## 🔧 Troubleshooting

### **Why Django Commands Must Run in Container**

- **Django server** runs **inside the Docker container**
- **Database** is only accessible **within the Docker network**
- **Environment variables** are set **inside the container**
- **Dependencies** are installed **inside the container**

### Database Connection Issues
```bash
# Check if database is running
./docker.sh status

# Check database logs
docker-compose -f docker/docker-compose.yml logs db

# Connect to database
./docker.sh db
```

### Redis Connection Issues
```bash
# Check if Redis is running
./docker.sh status

# Check Redis logs
docker-compose -f docker/docker-compose.yml logs redis

# Connect to Redis
./docker.sh redis
```

### Application Issues
```bash
# Check application logs
./docker.sh logs

# Restart application
./docker.sh rebuild

# Rebuild containers
./docker.sh rebuild
```

### Common Docker Issues

```bash
# If containers won't start
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose.yml up -d --build

# If data loading fails
docker-compose -f docker/docker-compose.yml exec web python manage.py migrate
docker-compose -f docker/docker-compose.yml exec web python manage.py loaddata fixtures/question_set.json

# If you need to reset everything
./docker.sh clean
./docker.sh up
./docker.sh load-data
```

## 📚 API Documentation

The API is documented using Swagger/OpenAPI. The JSON schema is available at:
- http://localhost:8000/swagger.json

### Viewing API Documentation

Since the Swagger UI doesn't render properly in the browser, you can:

1. **Use online Swagger UI:**
   - Go to https://editor.swagger.io/
   - Copy the JSON from http://localhost:8000/swagger.json
   - Paste it into the editor to view the interactive documentation

2. **Use Swagger UI locally:**
   - Download Swagger UI from https://github.com/swagger-api/swagger-ui
   - Open `dist/index.html` in your browser
   - Set the URL to `http://localhost:8000/swagger.json`

### Key Endpoints

- `GET /api/pokemons/` - List all Pokemon
- `GET /api/pokemons/{id}/` - Get specific Pokemon
- `POST /api/matcher/match/` - Match Pokemon for user profile

## 🎨 UI/UX

- **Responsive Design**: Works on desktop and mobile
- **Spring Gradient Theme**: Beautiful green-to-yellow gradients
- **Bootstrap 5**: Modern, accessible components
- **Interactive Quiz**: Smooth progression through questions
- **Detailed Results**: Comprehensive Pokemon information display

## 🔧 Configuration

### Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Database

- **PostgreSQL**: Primary database
- **Redis**: Caching layer
- **Migrations**: Django ORM migrations

## 🚀 Production Deployment

For production deployment, use the production Docker Compose file:

```bash
# Set environment variables
export SECRET_KEY="your-secure-secret-key"
export ALLOWED_HOSTS="your-domain.com,www.your-domain.com"
export DB_PASSWORD="your-secure-db-password"

# Run production stack
./docker.sh prod-up
```

### Environment Setup

- Set `DEBUG=False` for production
- Configure proper `SECRET_KEY`
- Set up SSL/TLS termination
- Configure database backups
- Set up monitoring and logging

## 🐳 Docker Features

### Development Environment
- **Full Dependencies**: Includes all development tools (Black, isort, Flake8, MyPy, etc.)
- **Volume Mounting**: Live code changes without rebuilding
- **Health Checks**: All services have built-in health monitoring
- **Non-root User**: Security best practices

### Production Environment
- **Optimized Image**: Uses `Dockerfile.prod` with only production dependencies
- **Gunicorn**: Production-grade WSGI server
- **Resource Limits**: Memory and CPU constraints
- **Alpine Images**: Smaller footprint
- **Volume Persistence**: Data survives container restarts

## 📈 Performance Notes

- **First Run**: Pokemon data loading time depends on API response
- **Subsequent Runs**: Fast startup with cached data
- **Resource Usage**: Standard Docker container requirements



## 🤝 Contributing

1. Fork the [repository](https://github.com/bntmzu/PokeSoul.git)
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the [Docker documentation](DOCKER.md)
- Review the [testing guide](TESTING.md)

---

**Made with ❤️ for Pokemon fans everywhere!**
