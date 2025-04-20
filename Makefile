# Makefile para o projeto Quantum Chatbot

PROJECT_NAME=chatbot-agentic-quantum-backend
APP_CONTAINER_NAME=$(PROJECT_NAME)-app-1

## ────────────────────────────── Docker ────────────────────────────── ##

up-dev:
	docker compose -f docker/docker-compose.dev.yml -f docker-compose.yml up --build -d

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

restart:
	make down && make up-dev

## ────────────────────────────── Banco ─────────────────────────────── ##

init-db:
	docker exec -it $(APP_CONTAINER_NAME) python -m app.helpers.functions.create_tables

reset-db:
	docker rm -f $(PROJECT_NAME)-postgres-1 || true \
	&& docker volume rm $(PROJECT_NAME)_postgres_data || true \
	&& docker compose -f docker-compose.yml up -d postgres

## ────────────────────────────── Util ─────────────────────────────── ##

shell:
	docker exec -it $(APP_CONTAINER_NAME) bash

rebuild:
	docker compose -f docker/docker-compose.dev.yml -f docker-compose.yml build --no-cache

clean:
	docker system prune -af && docker volume prune -f