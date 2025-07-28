#!/bin/bash
set -e

echo "Запуск AI Manager контейнера..."

# Создание директорий для логов
mkdir -p /app/logs
mkdir -p /app/ollama/models

# Установка переменных окружения для Ollama
export OLLAMA_HOST=${OLLAMA_HOST:-0.0.0.0}
export OLLAMA_PORT=${OLLAMA_PORT:-11434}
export OLLAMA_MODELS=${OLLAMA_MODELS:-/app/ollama/models}

echo "Запуск Ollama сервера..."
ollama serve &
OLLAMA_PID=$!

# Ожидание запуска Ollama
echo "Ожидание готовности Ollama..."
sleep 10
while ! curl -f http://localhost:11434/api/tags >/dev/null 2>&1; do
    echo "Ожидание Ollama..."
    sleep 5
done
echo "Ollama готов!"

# Скачивание базовых моделей (если не существуют)
echo "Проверка наличия моделей..."

download_model_if_not_exists() {
    local model=$1
    if ! ollama list | grep -q "$model"; then
        echo "Скачивание модели $model..."
        ollama pull $model &
    else
        echo "Модель $model уже существует"
    fi
}

# Скачиваем основные модели в фоне
download_model_if_not_exists "llama3.2"
download_model_if_not_exists "phi3"
download_model_if_not_exists "gemma3:latest"
download_model_if_not_exists "mistral:latest"

# Функция graceful shutdown
cleanup() {
    echo "Получен сигнал завершения, останавливаем сервисы..."
    
    # Остановка FastAPI
    if [ ! -z "$FASTAPI_PID" ]; then
        kill -TERM $FASTAPI_PID
        wait $FASTAPI_PID
    fi
    
    # Остановка Ollama
    if [ ! -z "$OLLAMA_PID" ]; then
        kill -TERM $OLLAMA_PID
        wait $OLLAMA_PID
    fi
    
    echo "Все сервисы остановлены"
    exit 0
}

# Установка обработчика сигналов
trap cleanup SIGTERM SIGINT

echo "Запуск FastAPI сервера..."
cd /app
python -m uvicorn ai_manager.api.main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 1 \
    --log-level info \
    --access-log &

FASTAPI_PID=$!

echo "AI Manager запущен успешно!"
echo "FastAPI доступен на порту 8080"
echo "Ollama доступен на порту 11434"
echo "Логи записываются в /app/logs/"

# Мониторинг процессов
while true; do
    # Проверка работы Ollama
    if ! kill -0 $OLLAMA_PID 2>/dev/null; then
        echo "Ollama процесс остановлен, перезапуск..."
        ollama serve &
        OLLAMA_PID=$!
    fi
    
    # Проверка работы FastAPI
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "FastAPI процесс остановлен, перезапуск..."
        python -m uvicorn ai_manager.api.main:app \
            --host 0.0.0.0 \
            --port 8080 \
            --workers 1 \
            --log-level info \
            --access-log &
        FASTAPI_PID=$!
    fi
    
    sleep 180
done
