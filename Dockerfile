# Main Forum Application Dockerfile
FROM python:3.11-bullseye

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY app ./app/
COPY alembic.ini ./
COPY migrations ./migrations/

# Создание директорий для логов
RUN mkdir -p /app/logs

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Экспозиция порта
EXPOSE 8000

# Команда запуска
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
