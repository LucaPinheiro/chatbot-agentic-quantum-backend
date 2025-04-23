PROJECT_NAME=chatbot-agentic-quantum-backend
APP_CONTAINER_NAME=docker-app-1
STAGE ?=local

## ────────────────────────────── Docker ────────────────────────────── ##

up:
	docker compose -f docker/docker-compose.dev.yml -f docker-compose.yml up --build -d

down:
	docker compose -f docker/docker-compose.dev.yml -f docker-compose.yml down

logs:
	docker compose logs -f --tail=100

ps:
	docker compose ps

restart:
	make down && make up

status:
	@echo "\n📦 Containers:" && docker ps --format "table {{.Names}}	{{.Status}}	{{.Ports}}" \
	&& echo "\n💾 Volumes:" && docker volume ls

## ────────────────────────────── Banco ─────────────────────────────── ##

init-db:
	docker exec -e STAGE=$(STAGE) -e PYTHONPATH=/app -it $(APP_CONTAINER_NAME) \
		python -m app.helpers.functions.create_tables

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
