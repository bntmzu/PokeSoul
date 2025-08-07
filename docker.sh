#!/bin/bash

# PokeSoul Docker Management Script
# Provides convenient commands for managing the development and production environments
# Usage: ./docker.sh [command]

DOCKER_DIR="docker"
COMPOSE_FILE="$DOCKER_DIR/docker-compose.yml"
PROD_COMPOSE_FILE="$DOCKER_DIR/docker-compose.prod.yml"

case "$1" in
    "up"|"start")
        # Start development environment with build
        docker-compose -f "$COMPOSE_FILE" up --build
        ;;
    "up-d"|"start-d")
        # Start development environment in background
        docker-compose -f "$COMPOSE_FILE" up -d --build
        ;;
    "down"|"stop")
        # Stop development environment
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    "down-v"|"clean")
        # Stop and remove all data (volumes)
        docker-compose -f "$COMPOSE_FILE" down -v
        ;;
    "logs")
        # View application logs with follow
        docker-compose -f "$COMPOSE_FILE" logs -f web
        ;;
    "shell")
        # Open Django shell for debugging
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py shell
        ;;
    "test")
        # Run all tests with pytest
        docker-compose -f "$COMPOSE_FILE" exec web python -m pytest
        ;;
    "migrate")
        # Run database migrations
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py migrate
        ;;
    "load-data")
        # Load Pokemon data and quiz questions
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py load_top_pokemons --limit 100
        docker-compose -f "$COMPOSE_FILE" exec web python manage.py loaddata fixtures/question_set.json
        ;;
    "quality")
        # Run code quality checks with pre-commit
        docker-compose -f "$COMPOSE_FILE" exec web poetry run pre-commit run --all-files
        ;;
    "prod-up")
        # Start production environment
        docker-compose -f "$PROD_COMPOSE_FILE" up -d
        ;;
    "prod-down")
        # Stop production environment
        docker-compose -f "$PROD_COMPOSE_FILE" down
        ;;
    "rebuild")
        # Rebuild containers without cache
        docker-compose -f "$COMPOSE_FILE" down
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        docker-compose -f "$COMPOSE_FILE" up -d
        ;;
    "status")
        # Show container status
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    "db")
        # Connect to PostgreSQL database
        docker-compose -f "$COMPOSE_FILE" exec db psql -U pokesoul -d pokesoul
        ;;
    "redis")
        # Connect to Redis cache
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
