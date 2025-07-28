# AI Manager

AI Manager для форума с поддержкой Ollama и FastAPI

## Возможности

- Интеграция с Ollama для локальных LLM моделей
- REST API на FastAPI для взаимодействия с AI
- Контейнеризация с Docker
- Управление ресурсами и мониторинг

## Установка и запуск

### С помощью Docker

```bash
# Сборка и запуск
docker-compose -f docker-compose.ai.yml up --build

# Остановка
docker-compose -f docker-compose.ai.yml down
```

### Локальная разработка

```bash
cd ai_manager
poetry install
poetry run uvicorn api.main:app --reload --port 8080
```

## API Endpoints

- `GET /health` - Проверка состояния
- `GET /models` - Список доступных моделей
- `POST /generate` - Генерация ответа от AI
- `GET /status` - Статус API

## Использование

После запуска API доступно по адресу: http://localhost:8080
Документация Swagger: http://localhost:8080/docs
