# Main Forum Application Dockerfile
FROM python:3.12-bullseye

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    ca-certificates \
    libpq-dev \
    gcc \
    postgresql-client \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements_pip.txt ./

# Устанавливаем основные зависимости
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements_pip.txt

# Копируем исходный код приложения
COPY app ./app/

# Создание директорий для логов
RUN mkdir -p /app/logs

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Экспозиция порта
EXPOSE 8000

# Команда запуска напрямую через Python
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
