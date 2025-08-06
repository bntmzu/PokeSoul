#!/bin/bash

# PokeSoul Docker Management Script
# Usage: ./docker.sh [command]

DOCKER_DIR="docker"
COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"
PROD_COMPOSE_FILE="$DOCKER_DIR/docker-compose.prod.yml"

case "$1" in
    "up"|"start")
        docker-compose -f "$COMPOSE_FILE" up --build
        ;;
    "up-d"|"start-d")
        docker-compose -f "$COMPOSE_FILE" up -d --build
        ;;
    "down"|"stop")
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    "down-v"|"clean")
        docker-compose -f "$COMPOSE_FILE" down -v
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f web
        ;;
    "shell")
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py shell
        ;;
    "test")
        docker-compose -f "$COMPOSE_FILE" exec web python -m pytest
        ;;
    "migrate")
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py migrate
        ;;
    "load-data")
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py load_top_pokemons --limit 100
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py loaddata fixtures/question_set.json
        ;;
    "quality")
        docker-compose -f "$COMPOSE_FILE" exec web poetry run pre-commit run --all-files
        ;;
    "prod-up")
        docker-compose -f "$PROD_COMPOSE_FILE" up -d
        ;;
    "prod-down")
        docker-compose -f "$PROD_COMPOSE_FILE" down
        ;;
    "rebuild")
        docker-compose -f "$COMPOSE_FILE" down
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        docker-compose -f "$COMPOSE_FILE" up -d
        ;;
    "status")
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    "db")
        docker-compose -f "$COMPOSE_FILE" exec db psql -U pokesoul -d pokesoul
        ;;
    "redis")
        docker-compose -f "$COMPOSE_FILE" exec redis redis-cli
        ;;
    *)
        echo "PokeSoul Docker Management Script"
        echo ""
        echo "Usage: ./docker.sh [command]"
        echo ""
        echo "Commands:"
        echo "  up, start        - Start development environment"
        echo "  up-d, start-d    - Start development environment in background"
        echo "  down, stop       - Stop development environment"
        echo "  down-v, clean    - Stop and remove all data"
        echo "  logs             - View application logs"
        echo "  shell            - Open Django shell"
        echo "  test             - Run tests"
        echo "  migrate          - Run database migrations"
        echo "  load-data        - Load Pokemon data and quiz questions"
        echo "  quality          - Run code quality checks"
        echo "  prod-up          - Start production environment"
        echo "  prod-down        - Stop production environment"
        echo "  rebuild          - Rebuild containers without cache"
        echo "  status           - Show container status"
        echo "  db               - Connect to PostgreSQL"
        echo "  redis            - Connect to Redis"
        echo ""
        echo "Examples:"
        echo "  ./docker.sh up          # Start development"
        echo "  ./docker.sh load-data   # Load initial data"
        echo "  ./docker.sh test        # Run tests"
        ;;
esac
