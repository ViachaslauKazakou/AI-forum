# AI Forum - Development Setup

## Режимы запуска

### 1. Production режим
```bash
docker-compose up -d
```
Приложение доступно на: http://localhost:8000

### 2. Debug режим (через Docker)
```bash
# Сначала запускаем основную инфраструктуру
docker-compose up -d

# Затем запускаем debug версию приложения
docker-compose -f docker-compose.dev.yml up -d
```

Debug приложение доступно на: http://localhost:8001
Debug порт для VS Code: 5678

### 3. Local режим (для отладки в VS Code)
```bash
# Запускаем только инфраструктуру
docker-compose up -d rabbitmq

# В VS Code используем конфигурацию "FastAPI Server (Uvicorn)"
```

## Отладка в VS Code

### Для Docker Debug режима:
1. Запустите debug контейнер: `docker-compose -f docker-compose.dev.yml up -d`
2. В VS Code выберите конфигурацию "AI Forum: Docker Debug"
3. Нажмите F5 для подключения к debugpy

### Для Local режима:
1. Запустите инфраструктуру: `docker-compose up -d rabbitmq`
2. В VS Code выберите конфигурацию "FastAPI Server (Uvicorn)"
3. Нажмите F5 для запуска с отладкой

## Доступные сервисы

- **Основное приложение**: http://localhost:8000
- **Debug приложение**: http://localhost:8001
- **Flower (Celery monitoring)**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## Полезные команды

```bash
# Просмотр логов
docker-compose logs -f forum_app

# Просмотр логов debug контейнера
docker-compose -f docker-compose.dev.yml logs -f forum_app_debug

# Остановка всех сервисов
docker-compose down
docker-compose -f docker-compose.dev.yml down

# Пересборка debug образа
docker-compose -f docker-compose.dev.yml build forum_app_debug
```
