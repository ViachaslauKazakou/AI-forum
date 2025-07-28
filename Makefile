.PHONY: help install run dev test clean db-up db-down db-reset format lint type-check

# Переменные
POETRY := poetry
DOCKER_COMPOSE := docker-compose

help: ## Показать это сообщение с помощью
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости через Poetry
	$(POETRY) install

run: ## Запустить приложение
	$(POETRY) run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev: db-up ## Запустить в режиме разработки (с базой данных)
	@echo "Ожидание запуска PostgreSQL..."
	@sleep 5
	$(POETRY) run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Запустить тесты
	$(POETRY) run pytest

clean: ## Очистить кэш и временные файлы
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

db-up: ## Запустить PostgreSQL в Docker
	$(DOCKER_COMPOSE) up -d postgres

db-down: ## Остановить PostgreSQL
	$(DOCKER_COMPOSE) down

db-reset: db-down ## Сбросить базу данных (удалить данные и пересоздать)
	docker volume rm ai-forum_postgres_data || true
	$(DOCKER_COMPOSE) up -d postgres

db-logs: ## Показать логи PostgreSQL
	$(DOCKER_COMPOSE) logs -f postgres

format: ## Отформатировать код с помощью Black
	$(POETRY) run black app/

lint: ## Проверить код с помощью flake8
	$(POETRY) run flake8 app/

type-check: ## Проверить типы с помощью mypy
	$(POETRY) run mypy app/

check: format lint type-check ## Запустить все проверки кода

shell: ## Открыть poetry shell
	$(POETRY) shell

update: ## Обновить зависимости
	$(POETRY) update

build: ## Собрать Docker образ для PostgreSQL
	$(DOCKER_COMPOSE) build postgres

status: ## Показать статус сервисов
	$(DOCKER_COMPOSE) ps

alembic-init: ## Инициализировать Alembic миграции
	$(POETRY) run alembic revision --autogenerate -m "Initial migration"

alembic-upgrade: ## Применить миграции
	$(POETRY) run alembic upgrade head

alembic-downgrade: ## Откатить миграции
	$(POETRY) run alembic downgrade -1

# AI Manager команды
ai-build: ## Собрать Docker образ AI Manager
	$(DOCKER_COMPOSE) -f docker-compose.ai.yml build

ai-up: ## Запустить AI Manager
	$(DOCKER_COMPOSE) -f docker-compose.ai.yml up -d

ai-down: ## Остановить AI Manager
	$(DOCKER_COMPOSE) -f docker-compose.ai.yml down

ai-logs: ## Показать логи AI Manager
	$(DOCKER_COMPOSE) -f docker-compose.ai.yml logs -f ai_manager

ai-restart: ai-down ai-up ## Перезапустить AI Manager

ai-clean: ## Очистить AI Manager данные
	$(DOCKER_COMPOSE) -f docker-compose.ai.yml down -v
	docker system prune -f


ai-dev: ## Запустить AI Manager локально для разработки
	cd ai_manager && $(POETRY) install && $(POETRY) run uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
