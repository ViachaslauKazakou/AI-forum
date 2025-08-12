#!/bin/bash

# AI Forum Development Helper Script
# Этот скрипт помогает управлять средой разработки

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода информации
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Функция для вывода успеха
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Функция для вывода предупреждения
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Функция для вывода ошибки
error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Показать помощь
show_help() {
    echo "AI Forum Development Helper"
    echo ""
    echo "Использование: ./dev.sh [command]"
    echo ""
    echo "Команды:"
    echo "  setup         - Настройка среды разработки"
    echo "  start         - Запуск инфраструктуры для разработки"
    echo "  stop          - Остановка инфраструктуры"
    echo "  restart       - Перезапуск инфраструктуры"
    echo "  logs          - Показать логи всех сервисов"
    echo "  status        - Показать статус сервисов"
    echo "  clean         - Очистка volumes и контейнеров"
    echo "  debug         - Запуск приложения в режиме отладки"
    echo "  celery        - Запуск Celery worker локально"
    echo "  shell         - Подключение к контейнеру postgres"
    echo "  migrate       - Запуск миграций базы данных"
    echo "  test          - Запуск тестов"
    echo "  format        - Форматирование кода (black, isort)"
    echo "  lint          - Проверка кода (flake8)"
    echo "  help          - Показать эту справку"
    echo ""
}

# Настройка среды разработки
setup_dev() {
    info "Настройка среды разработки..."
    
    # Создаем .env.local если его нет
    if [ ! -f ".env.local" ]; then
        info "Создание .env.local..."
        cp .env.dev .env.local
        warning "Проверьте настройки в .env.local"
    fi
    
    # Запускаем инфраструктуру
    info "Запуск инфраструктуры..."
    docker-compose -f docker-compose.dev.yml up -d postgres rabbitmq redis
    
    # Ждем запуска PostgreSQL
    info "Ожидание запуска PostgreSQL..."
    sleep 10
    
    success "Среда разработки настроена!"
    info "Доступные сервисы:"
    info "  - PostgreSQL: localhost:5433"
    info "  - RabbitMQ Management: http://localhost:15672 (guest/guest)"
    info "  - Redis: localhost:6379"
}

# Запуск инфраструктуры
start_dev() {
    info "Запуск инфраструктуры для разработки..."
    docker-compose -f docker-compose.dev.yml up -d
    success "Инфраструктура запущена!"
}

# Остановка инфраструктуры
stop_dev() {
    info "Остановка инфраструктуры..."
    docker-compose -f docker-compose.dev.yml down
    success "Инфраструктура остановлена!"
}

# Перезапуск инфраструктуры
restart_dev() {
    info "Перезапуск инфраструктуры..."
    docker-compose -f docker-compose.dev.yml restart
    success "Инфраструктура перезапущена!"
}

# Показать логи
show_logs() {
    docker-compose -f docker-compose.dev.yml logs -f
}

# Показать статус
show_status() {
    docker-compose -f docker-compose.dev.yml ps
}

# Очистка
clean_dev() {
    warning "Это удалит все контейнеры и volumes!"
    read -p "Продолжить? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Очистка..."
        docker-compose -f docker-compose.dev.yml down -v
        docker-compose -f docker-compose.dev.yml rm -f
        success "Очистка завершена!"
    fi
}

# Запуск в режиме отладки
debug_app() {
    info "Запуск приложения в режиме отладки..."
    info "Откройте VS Code и используйте конфигурацию 'AI Forum: Local Development'"
    info "Убедитесь, что инфраструктура запущена (./dev.sh start)"
}

# Запуск Celery worker
run_celery() {
    info "Запуск Celery worker локально..."
    PYTHONPATH=. python run_celery.py
}

# Подключение к PostgreSQL
connect_shell() {
    info "Подключение к PostgreSQL..."
    docker-compose -f docker-compose.dev.yml exec postgres psql -U docker -d postgres
}

# Миграции
run_migrations() {
    info "Запуск миграций..."
    PYTHONPATH=. python -m alembic upgrade head
}

# Тесты
run_tests() {
    info "Запуск тестов..."
    PYTHONPATH=. python -m pytest tests/ -v
}

# Форматирование кода
format_code() {
    info "Форматирование кода..."
    black app/ tests/
    isort app/ tests/
    success "Код отформатирован!"
}

# Проверка кода
lint_code() {
    info "Проверка кода..."
    flake8 app/ tests/
    success "Проверка завершена!"
}

# Основная логика
case "${1:-help}" in
    setup)
        setup_dev
        ;;
    start)
        start_dev
        ;;
    stop)
        stop_dev
        ;;
    restart)
        restart_dev
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    clean)
        clean_dev
        ;;
    debug)
        debug_app
        ;;
    celery)
        run_celery
        ;;
    shell)
        connect_shell
        ;;
    migrate)
        run_migrations
        ;;
    test)
        run_tests
        ;;
    format)
        format_code
        ;;
    lint)
        lint_code
        ;;
    help|*)
        show_help
        ;;
esac
