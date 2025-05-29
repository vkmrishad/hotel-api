# Variables
COMPOSE = docker-compose
COMPOSE_FILE = docker-compose.yml
PROJECT_NAME = hotel-api

# Targets

# Build production Docker images
build:
	@echo "🔵 Building production image"
	$(COMPOSE) build

# Start containers
up:
	@echo "🟢 Starting services..."
	$(COMPOSE) up -d

# Stop containers
down:
	@echo "🔴 Stopping services..."
	$(COMPOSE) down

# Help
help:
	@echo "Available commands:"
	@echo "  make build           Build production Docker image"
	@echo "  make build_dev       Build dev Docker image (with --reload)"
	@echo "  make up              Start all services"
	@echo "  make down            Stop all services"


# Aliases
b: build 			# Build production images
u: up 				# Start containers
d: down 			# Stop containers
h: help 			# Show help

.PHONY: build up down help
