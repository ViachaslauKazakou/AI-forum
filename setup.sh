#!/bin/bash

# Скрипт для быстрой настройки проекта форума
set -e

echo "🚀 Настройка проекта AI-Forum..."

# Проверяем наличие Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry не найден. Пожалуйста, установите Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Пожалуйста, установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Проверяем наличие docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose не найден. Пожалуйста, установите docker-compose"
    exit 1
fi

echo "✅ Все необходимые инструменты найдены"

# Создаем виртуальное окружение с Poetry
echo "📦 Устанавливаем зависимости с Poetry..."
poetry install

# Копируем конфигурационный файл
if [ ! -f .env ]; then
    echo "⚙️ Создаем файл конфигурации .env..."
    cp .env.example .env
    echo "✅ Файл .env создан. При необходимости отредактируйте его."
fi

# Запускаем PostgreSQL
echo "🐘 Запускаем PostgreSQL в Docker..."
docker-compose up -d postgres

# Ждем запуска базы данных
echo "⏳ Ожидаем запуска PostgreSQL..."
sleep 10

# Проверяем статус
echo "📊 Проверяем статус сервисов..."
docker-compose ps

echo ""
echo "🎉 Настройка завершена!"
echo ""
echo "Для запуска приложения используйте:"
echo "  make dev          # Запуск в режиме разработки"
echo "  make run          # Запуск только приложения"
echo ""
echo "Полезные команды:"
echo "  make help         # Показать все доступные команды"
echo "  make db-logs      # Показать логи PostgreSQL"
echo "  make db-reset     # Сбросить базу данных"
echo ""
echo "Приложение будет доступно по адресу: http://localhost:8000"
