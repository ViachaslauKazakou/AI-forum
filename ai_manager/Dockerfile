# Multi-stage build для оптимизации размера образа
FROM python:3.11-bullseye as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    gcc \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry 2 с плагином export
RUN pip install --no-cache-dir poetry==2.1.3 poetry-plugin-export
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Рабочая директория
WORKDIR /app

# Копируем файлы Poetry для кэширования слоев
COPY ai_manager/pyproject.toml ai_manager/poetry.lock* ./

# Создаем виртуальное окружение и устанавливаем зависимости
RUN python -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --upgrade pip && \
    poetry install --only=main --no-root && \
    rm -rf $POETRY_CACHE_DIR

# Production stage
FROM python:3.11-bullseye

# Установка системных зависимостей для runtime
RUN apt-get update && apt-get install -y \
    curl \
    netcat-traditional \
    ca-certificates \
    gosu \
    wget \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Установка Ollama с проверкой архитектуры
RUN set -e; \
    ARCH=$(uname -m); \
    if [ "$ARCH" = "x86_64" ]; then \
    curl -fsSL https://ollama.ai/install.sh | sh; \
    else \
    echo "Unsupported architecture: $ARCH"; \
    exit 1; \
    fi

# Создание пользователя для безопасности
RUN groupadd -r aimanager && useradd -r -g aimanager aimanager

# Рабочая директория
WORKDIR /app

# Копируем виртуальное окружение из builder stage
ENV VIRTUAL_ENV=/app/.venv
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Копируем исходный код AI manager
COPY ai_manager/__init__.py ./ai_manager/
COPY ai_manager/api ./ai_manager/api/
COPY ai_manager/docker ./docker/

# Создание директорий с правильными правами
RUN mkdir -p /app/logs /app/ollama/models /home/aimanager/.ollama \
    && chown -R aimanager:aimanager /app /home/aimanager/.ollama

# Переменные окружения
ENV PYTHONPATH=/app
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_PORT=11434
ENV OLLAMA_MODELS=/app/ollama/models

# Экспозиция портов
EXPOSE 8080 11434

# Копируем и настраиваем скрипт запуска
COPY ai_manager/docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Точка входа
ENTRYPOINT ["/app/entrypoint.sh"]
