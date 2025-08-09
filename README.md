# AI Forum - FastAPI приложение форума

Полнофункциональное веб-приложение форума, построенное на FastAPI с P## 🌐 Доступ к приложению

После запуска приложение будет доступно по следующим адресам:

- **Главная страница**: http://localhost:8000
- **API документация (Swagger)**: http://localhost:8000/docs
- **Создание топика**: http://localhost:8000/topics/create
- **API endpoints**: http://localhost:8000/api/topics
- **Админ-панель**: http://localhost:8000/admin/
- **Admin API документация**: http://localhost:8000/docs (секция Admin API)L базой данных.

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.12+
- Poetry (для управления зависимостями)
- Docker и Docker Compose
- Git

### Установка Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Или через pip
pip install poetry
```

## 📦 Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ViachaslauKazakou/AI-forum.git
cd AI-forum
```

### 2. Установка зависимостей через Poetry

```bash
# Создание виртуального окружения и установка зависимостей
poetry install

# Активация виртуального окружения
poetry shell
```

### 3. Остановка локального PostgreSQL (если запущен)

⚠️ **Важно!** Если у вас запущен локальный PostgreSQL на порту 5432, остановите его:

```bash
# Для Homebrew на macOS
brew services stop postgresql

# Для systemd на Linux
sudo systemctl stop postgresql

# Проверьте, что порт свободен
lsof -i :5432
```

### 4. Настройка базы данных PostgreSQL

#### Запуск PostgreSQL в Docker

```bash
# Запуск PostgreSQL контейнера
docker-compose up --build -d postgres

# Проверка статуса контейнера
docker-compose ps

# Ожидание готовности базы данных
docker-compose logs postgres
```

#### Проверка подключения к базе данных

```bash
# Проверка подключения (пароль: postgres)
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "\du"
```

### 5. Настройка переменных окружения

Файл `.env` уже настроен с правильными параметрами:

```env
DATABASE_URL=postgresql+asyncpg://docker:postgres@127.0.0.1:5433/postgres
SECRET_KEY=your-super-secret-key-for-development-only
DEBUG=True
```

### 6. Создание и применение миграций базы данных

```bash
# Создание первой миграции
poetry run alembic revision --autogenerate -m "Create topics and messages tables"

# Применение миграций
poetry run alembic upgrade head

# Проверка созданных таблиц
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "\dt"
```

### 7. Настройка VS Code (рекомендуется)

Проект включает готовую конфигурацию VS Code:

#### Автоматическая настройка:
- Файлы `.vscode/settings.json`, `.vscode/tasks.json`, `.vscode/launch.json` уже настроены
- Python интерпретатор автоматически указывает на `.venv/bin/python`
- Терминал автоматически активирует виртуальное окружение

#### Выбор интерпретатора (если нужно):
1. `Cmd+Shift+P` → `Python: Select Interpreter`
2. Выберите `.venv/bin/python`

#### Использование VS Code Tasks:
```
Cmd+Shift+P → Tasks: Run Task → Install Dependencies (Poetry)
Cmd+Shift+P → Tasks: Run Task → Run FastAPI (Poetry)
```

### 8. Запуск приложения

```bash
# Запуск FastAPI сервера
poetry run uvicorn app.main:app --reload
```

## 🌐 Доступ к приложению

После запуска приложение будет доступно по следующим адресам:

- **Главная страница**: http://localhost:8000
- **API документация (Swagger)**: http://localhost:8000/docs
- **Создание топика**: http://localhost:8000/topics/create
- **Админ-панель**: http://localhost:8000/admin/
- **API endpoints**: http://localhost:8000/api/topics

## 🗄️ Структура базы данных

### Таблицы

#### `users` - Пользователи
- `id` - Уникальный идентификатор (Primary Key)
- `username` - Имя пользователя (до 100 символов, уникальное)
- `firstname` - Имя (до 100 символов, опционально)
- `lastname` - Фамилия (до 100 символов, опционально)
- `password` - Хешированный пароль (до 255 символов)
- `email` - Email адрес (до 255 символов, уникальный)
- `user_type` - Тип пользователя (`mentor` или `mentee`)
- `status` - Статус пользователя (`pending`, `active`, `disabled`, `archive`, `deleted`)
- `created_at` - Дата создания

#### `topics` - Темы форума
- `id` - Уникальный идентификатор (Primary Key)
- `title` - Заголовок темы (до 200 символов)
- `description` - Описание темы
- `user_id` - ID автора темы (Foreign Key -> users.id)
- `created_at` - Дата создания
- `updated_at` - Дата обновления
- `is_active` - Статус активности

#### `messages` - Сообщения
- `id` - Уникальный идентификатор (Primary Key)
- `content` - Содержание сообщения
- `author_name` - Имя автора (до 100 символов)
- `topic_id` - ID темы (Foreign Key -> topics.id)
- `user_id` - ID автора сообщения (Foreign Key -> users.id)
- `parent_id` - ID родительского сообщения (Foreign Key -> messages.id, для ответов)
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### Связи между таблицами

- **User → Topics**: Один пользователь может создать множество тем (One-to-Many)
- **User → Messages**: Один пользователь может написать множество сообщений (One-to-Many)
- **Topic → Messages**: Одна тема может содержать множество сообщений (One-to-Many)
- **Message → Message**: Сообщение может иметь родительское сообщение (Self-referencing)

## 🐳 Docker конфигурация

### PostgreSQL контейнер

Проект использует кастомную Docker конфигурацию для PostgreSQL:

- **Образ**: postgres:15-alpine
- **Порт**: 5433 (во избежание конфликтов с локальным PostgreSQL)
- **Пользователь**: docker
- **Пароль**: postgres
- **База данных**: postgres

### Переменные окружения

PostgreSQL настроен через файлы:
- `docker/postgres_db/.docker-env/dev/common.env`
- `docker/postgres_db/.docker-env/dev/postgres.env`

## 🛠️ Команды разработки

### VS Code Tasks (рекомендуемый способ)

Проект настроен для работы с VS Code tasks через Poetry. Доступные задачи в `.vscode/tasks.json`:

#### 🚀 Как использовать tasks:
1. **Через Command Palette**: `Cmd+Shift+P` → `Tasks: Run Task`
2. **Через меню**: `Terminal` → `Run Task...`
3. **Горячие клавиши**: `Cmd+Shift+B` (после настройки default build task)

#### 📋 Доступные задачи:

**Управление зависимостями:**
- `Install Dependencies (Poetry)` - Установка зависимостей через Poetry
- `Poetry Shell` - Активация Poetry shell
- `Poetry Update` - Обновление всех зависимостей

**Запуск приложения:**
- `Run FastAPI (Poetry)` - Запуск FastAPI сервера с автоперезагрузкой

**Тестирование и качество кода:**
- `Run Tests (Poetry)` - Запуск тестов через pytest
- `Format Code (Poetry)` - Форматирование кода через black
- `Lint Code (Poetry)` - Проверка стиля кода через flake8

**База данных:**
- `Run Alembic Migration (Poetry)` - Применение миграций БД

#### 💡 Пример использования:
```
1. Первая настройка:
   - Install Dependencies (Poetry)
   - Run Alembic Migration (Poetry)

2. Разработка:
   - Run FastAPI (Poetry) (работает в фоне)
   - Format Code (Poetry) (перед коммитом)
   - Run Tests (Poetry)
```

### Настройка VS Code

VS Code автоматически настроен для работы с Poetry:
- Python интерпретатор из `.venv/bin/python`
- Автоактивация виртуального окружения в терминале
- Форматирование через black при сохранении
- Линтинг через flake8 и mypy

### Управление базой данных

```bash
# Подключение к базе данных
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres

# Просмотр всех таблиц
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "\dt"

# Просмотр структуры конкретной таблицы
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "\d users"
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "\d topics"
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "\d messages"

# Проверка количества записей в таблицах
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "
SELECT 'users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'topics' as table_name, COUNT(*) as count FROM topics
UNION ALL
SELECT 'messages' as table_name, COUNT(*) as count FROM messages;
"

# удалить таблицу
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres
DROP TABLE table_name;

# Просмотр логов PostgreSQL
docker-compose logs postgres

# Перезапуск базы данных
docker-compose restart postgres

# Полная пересборка (удаление данных)
docker-compose down -v
docker-compose up --build -d postgres
```

### Управление миграциями

```bash
# Создание новой миграции
poetry run alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
poetry run alembic upgrade head

# Откат последней миграции
poetry run alembic downgrade -1

# Просмотр истории миграций
poetry run alembic history

# Просмотр текущей версии
poetry run alembic current

# Просмотр SQL для миграции (без выполнения)
poetry run alembic upgrade head --sql
```

### Очистка данных при изменении схемы

При добавлении внешних ключей к существующим таблицам с данными может потребоваться очистка:

```bash
# Очистка таблиц с сохранением структуры
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "DELETE FROM messages; DELETE FROM topics;"

# Или очистка с сбросом автоинкремента
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "
TRUNCATE TABLE messages, topics RESTART IDENTITY CASCADE;
"

# Проверка количества записей
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "
SELECT 'topics' as table_name, COUNT(*) as count FROM topics
UNION ALL
SELECT 'messages' as table_name, COUNT(*) as count FROM messages
UNION ALL  
SELECT 'users' as table_name, COUNT(*) as count FROM users;
"
```

### Пример создания миграции для добавления пользователей

```bash
# 1. Создаем миграцию для таблицы пользователей
poetry run alembic revision --autogenerate -m "Create users table"

# 2. Применяем миграцию
poetry run alembic upgrade head

# 3. Создаем миграцию для добавления связей user_id
poetry run alembic revision --autogenerate -m "Add user_id to topics and messages"

# 4. Применяем миграцию
poetry run alembic upgrade head
```

⚠️ **Важно**: При добавлении NOT NULL внешних ключей к таблицам с существующими данными необходимо сначала очистить данные или сделать поля nullable.

### Управление зависимостями

```bash
# Добавление новой зависимости
poetry add package_name

# Добавление зависимости для разработки
poetry add --group dev package_name

# Обновление зависимостей
poetry update

# Просмотр установленных пакетов
poetry show
```

## 🚦 Решение проблем

### Проблема: "role 'docker' does not exist"

**Причина**: Локальный PostgreSQL конфликтует с Docker контейнером

**Решение**:
1. Остановите локальный PostgreSQL: `brew services stop postgresql`
2. Убедитесь, что порт свободен: `lsof -i :5432`
3. Перезапустите Docker контейнер: `docker-compose restart postgres`

### Проблема: "Connection refused"

**Причина**: PostgreSQL контейнер не запущен или не готов

**Решение**:
1. Проверьте статус: `docker-compose ps`
2. Проверьте логи: `docker-compose logs postgres`
3. Дождитесь статуса "healthy"

### Проблема: "ModuleNotFoundError: No module named 'dotenv'"

**Причина**: python-dotenv не установлен в Poetry окружении

**Решение**:
```bash
poetry add python-dotenv
```

### Проблема: "Foreign key constraint fails"

**Причина**: Попытка добавить NOT NULL внешний ключ к таблице с существующими данными

**Решение**:
```bash
# Очистите данные перед применением миграции
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "DELETE FROM messages; DELETE FROM topics;"

# Или временно сделайте поле nullable в миграции
# user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
```

### Проблема: "Table already exists"

**Причина**: Попытка создать таблицу, которая уже существует

**Решение**:
```bash
# Проверьте текущее состояние базы
poetry run alembic current
poetry run alembic history

# Синхронизируйте состояние без применения миграций
poetry run alembic stamp head
```

### Проблема: Ошибка при импорте enum типов

**Причина**: Неправильный импорт или определение enum типов

**Решение**:
1. Убедитесь, что файл `app/models/pydantic_models.py` содержит enum типы
2. Проверьте импорт в `app/models/models.py`:
```python
from app.models.pydantic_models import UserRole, Status
```

## 📁 Структура проекта

```
AI-forum/
├── app/
│   ├── __init__.py
│   ├── main.py              # Точка входа FastAPI
│   ├── database.py          # Конфигурация базы данных
│   ├── crud.py              # CRUD операции
│   ├── api.py               # API роуты
│   ├── web.py               # HTML роуты
│   ├── models/              # Модели данных
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy модели (User, Topic, Message)
│   │   └── pydantic_models.py # Pydantic схемы и Enum типы
│   ├── schemas.py           # API схемы (deprecated, заменены на models/)
│   └── templates/           # Jinja2 шаблоны
│       ├── base.html
│       ├── index.html
│       ├── topic.html
│       └── create_topic.html
├── docker/
│   └── postgres_db/         # Docker конфигурация PostgreSQL
│       └── .docker-env/
│           └── dev/
│               ├── common.env
│               └── postgres.env
├── migrations/              # Alembic миграции
│   ├── versions/           # Файлы миграций
│   ├── env.py              # Конфигурация Alembic
│   ├── script.py.mako      # Шаблон миграций
│   └── README
├── docker-compose.yml       # Docker Compose конфигурация
├── pyproject.toml          # Poetry конфигурация и зависимости
├── alembic.ini             # Alembic конфигурация
├── .env                    # Переменные окружения
├── .env.example            # Пример файла окружения
├── Makefile                # Команды для разработки
└── README.md               # Этот файл
```

## Возможности

- **Главная страница**: Список всех тем форума
- **Страница темы**: Отображение 20 последних сообщений в теме
- **API для создания тем**: Добавление новых тем
- **API для сообщений**: Добавление сообщений и ответов на сообщения
- **База данных**: PostgreSQL с SQLAlchemy и asyncpg
- **Фронтенд**: FastAPI Templates с Jinja2 и Bootstrap
- **Админ-панель**: Полное управление пользователями, темами и сообщениями
- **CRUD API**: Полный REST API для всех операций
- **Современная архитектура**: SQLAlchemy 2.0 с типизацией

## Требования

- Python 3.8+
- Poetry (для управления зависимостями)
- Docker и docker-compose (для PostgreSQL)

## Быстрая установка

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd AI-forum
```

2. Запустите скрипт автоматической настройки:
```bash
./setup.sh
```

3. Запустите приложение:
```bash
make dev
```

Приложение будет доступно по адресу: http://localhost:8000

## Ручная установка

### Установка Poetry
```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### Настройка проекта
```bash
# Установка зависимостей
poetry install

# Создание файла конфигурации
cp .env.example .env

# Запуск PostgreSQL
docker-compose up -d postgres

# Запуск приложения
poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Использование Makefile

Проект включает Makefile для удобного управления:

```bash
make help          # Показать все доступные команды
make install       # Установить зависимости
make run           # Запустить приложение
make dev           # Запустить в режиме разработки (с БД)
make test          # Запустить тесты
make db-up         # Запустить PostgreSQL
make db-down       # Остановить PostgreSQL
make db-reset      # Сбросить базу данных
make db-logs       # Показать логи PostgreSQL
make format        # Отформатировать код
make lint          # Проверить код
make type-check    # Проверить типы
make check         # Запустить все проверки
```

## Docker

### PostgreSQL
Проект включает настроенный PostgreSQL в Docker:

```bash
# Запустить PostgreSQL
docker-compose up -d postgres

# Посмотреть логи
docker-compose logs -f postgres

# Остановить
docker-compose down

# Сбросить данные
docker-compose down -v
```

### Настройки PostgreSQL
- **База данных**: forum_db
- **Пользователь**: forum_user
- **Пароль**: forum_password
- **Порт**: 5432

```
app/
├── __init__.py          # Инициализация пакета
├── main.py             # Главный файл приложения
├── database.py         # Настройки базы данных
├── models.py           # SQLAlchemy модели
├── schemas.py          # Pydantic схемы
├── crud.py             # CRUD операции
├── api.py              # API роуты
├── web.py              # Web роуты для HTML страниц
└── templates/          # HTML шаблоны
    ├── base.html
    ├── index.html
    ├── topic.html
    └── create_topic.html
```

## API Endpoints

### Пользователи
- `GET /api/admin/users` - Получить список всех пользователей
- `POST /api/admin/users` - Создать нового пользователя
- `GET /api/admin/users/{user_id}` - Получить пользователя по ID
- `PUT /api/admin/users/{user_id}` - Обновить пользователя
- `DELETE /api/admin/users/{user_id}` - Удалить пользователя

### Темы
- `GET /api/topics` - Получить список активных тем
- `GET /api/admin/topics` - Получить все темы (включая неактивные)
- `POST /api/admin/topics` - Создать новую тему (требует user_id)
- `GET /api/admin/topics/{topic_id}` - Получить тему по ID
- `PUT /api/admin/topics/{topic_id}` - Обновить тему
- `DELETE /api/admin/topics/{topic_id}` - Удалить тему
- `GET /api/topics/{topic_id}/messages` - Получить сообщения темы

### Сообщения
- `GET /api/admin/messages` - Получить все сообщения
- `POST /api/admin/messages` - Создать новое сообщение или ответ (требует user_id)
- `GET /api/admin/messages/{message_id}` - Получить сообщение по ID
- `PUT /api/admin/messages/{message_id}` - Обновить сообщение
- `DELETE /api/admin/messages/{message_id}` - Удалить сообщение

## Web Pages

- `/` - Главная страница со списком тем
- `/topics/{topic_id}` - Страница темы с сообщениями
- `/create-topic` - Форма создания новой темы

### Админ-панель
- `/admin/` - Главная страница админ-панели с статистикой
- `/admin/users` - Управление пользователями
- `/admin/users/create` - Создание нового пользователя
- `/admin/users/{user_id}/edit` - Редактирование пользователя
- `/admin/topics` - Управление темами
- `/admin/topics/create` - Создание новой темы
- `/admin/topics/{topic_id}/edit` - Редактирование темы
- `/admin/messages` - Управление сообщениями
- `/admin/messages/{message_id}/edit` - Редактирование сообщения

### Планируется
- `/login` - Страница входа
- `/register` - Страница регистрации

## Схема базы данных

### Модели SQLAlchemy

Проект использует новейшие возможности SQLAlchemy 2.0:
- `Mapped[Type]` для типизации полей
- `mapped_column()` вместо `Column()`
- `relationship()` с правильной типизацией
- Enum типы для ролей и статусов пользователей

### Enum типы

```python
class UserRole(str, PyEnum):
    mentor = "admin"  # Ментор (администратор)
    mentee = "user"   # Ментии (пользователь)

class Status(str, PyEnum):
    pending = "pending"    # Ожидает подтверждения
    active = "active"      # Активный
    disabled = "disabled"  # Отключен
    archive = "archive"    # Архивирован
    deleted = "deleted"    # Удален
```

### Topics (Темы)
- id (Primary Key)
- title (Название)
- description (Описание)
- user_id (Foreign Key -> Users, автор темы)
- created_at (Дата создания)
- updated_at (Дата обновления)
- is_active (Активная тема)

### Messages (Сообщения)
- id (Primary Key)
- content (Содержимое)
- author_name (Имя автора)
- topic_id (Foreign Key -> Topics)
- user_id (Foreign Key -> Users, автор сообщения)
- parent_id (Foreign Key -> Messages, для ответов)
- created_at (Дата создания)
- updated_at (Дата обновления)

## Конфигурация

Настройки приложения задаются через переменные окружения в файле `.env`:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/forum_db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Разработка

Для разработки рекомендуется использовать автоматическую перезагрузку:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Миграции базы данных

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📜 Лицензия

Этот проект распространяется под лицензией MIT.

## 🆘 Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории GitHub.

## 🔧 Дополнительная информация

### Современный синтаксис SQLAlchemy 2.0

Проект использует новейшие возможности SQLAlchemy:
- `Mapped[Type]` для типизации полей
- `mapped_column()` вместо `Column()`
- `relationship()` с правильной типизацией
- Enum типы для ролей и статусов пользователей

### Планы развития

- ✅ Базовая структура форума
- ✅ Система пользователей с ролями
- ✅ Связи между пользователями, темами и сообщениями
- ✅ Полнофункциональная админ-панель с CRUD операциями
- ✅ API для управления всеми сущностями
- 🔄 Аутентификация и авторизация
- ⏳ Система прав доступа для админ-панели
- ⏳ Веб-интерфейс для регистрации/входа
- ⏳ Система уведомлений
- ⏳ Поиск по форуму

### Следующие шаги

1. ~~Завершить миграцию базы данных с добавлением user_id полей~~ ✅
2. ~~Создать полнофункциональную админ-панель~~ ✅
3. ~~Реализовать CRUD API для всех сущностей~~ ✅
4. Реализовать систему аутентификации JWT
5. Добавить авторизацию для админ-панели
6. Обновить API endpoints для работы с пользователями
7. Добавить веб-формы для регистрации и входа
8. Внедрить систему ролей и прав доступа

### Удалить записи из докер контейнера

```
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "DELETE FROM messages; DELETE FROM topics;"
```

## 🐇 RabbitMQ + Celery (брокер задач)

Ниже — минимальные инструкции для запуска RabbitMQ как брокера Celery и проверки работы очередей. Доменные статусы/результаты задач хранятся в таблице `tasks` (PostgreSQL), RabbitMQ отвечает за доставку задач воркерам.

### 1) Запуск RabbitMQ (Docker)

```bash
# Запустить RabbitMQ с панелью управления (5672 — AMQP, 15672 — UI)
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3-management

# Проверить, что контейнер запущен
docker ps --filter name=rabbitmq
```

Панель управления: http://localhost:15672 (логин/пароль: guest/guest)

Остановить/удалить:
```bash
docker stop rabbitmq && docker rm rabbitmq
```

### 2) Настройки окружения

В `.env` добавьте (или оставьте по умолчанию):
```env
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```

Проверьте, что FastAPI и воркер используют одинаковый `RABBITMQ_URL`.

### 3) Запуск Celery-воркера

Виртуальное окружение активируйте через Poetry или используйте `poetry run`:
```bash
# В отдельном терминале
poetry run celery -A app.celery_tasks:celery_app worker -l info
```

Опционально: задать конкуренцию и имя воркера
```bash
poetry run celery -A app.celery_tasks:celery_app worker -l info -c 4 -n ai-forum@%h
```

### 4) Постановка задач

Эндпоинт админки ставит задачу в очередь и создает запись в таблице `tasks`:
- POST `/admin/messages/ai/create` с параметрами `topic_id`, `user_id`

Поток:
1) FastAPI создает запись в `tasks` (status=pending)
2) Отправляет ID записи в Celery (`process_task.delay(task_id)`)
3) Воркер обновляет статус: processing → completed/failed

### 5) Просмотр очередей и задач

- Веб-панель RabbitMQ: http://localhost:15672 → Queues → видны очереди, сообщения, потребители
- Логи воркера Celery: терминал с `celery ... -l info`
- Проверка таблицы `tasks`:
```bash
PGPASSWORD=postgres psql -h 127.0.0.1 -p 5433 -U docker -d postgres -c "SELECT id, status, started_at, completed_at FROM tasks ORDER BY id DESC LIMIT 20;"
```

### 6) Частые проблемы

- Воркер не подключается:
  - Проверьте `RABBITMQ_URL`
  - Убедитесь, что порт 5672 открыт, контейнер запущен (`docker ps`)
- Задачи не потребляются:
  - Проверьте логи воркера
  - Убедитесь, что импорт `process_task` выполняется (см. `app/celery_tasks.py`)
- Зависимости:
  - Текущих зависимостей Poetry (celery, kombu) достаточно для RabbitMQ (амqp-драйвер тянется транзитивно)

### 7) Полезные команды RabbitMQ

```bash
# Просмотр очередей через CLI
docker exec -it rabbitmq rabbitmqctl list_queues name messages consumers

# Просмотр обменников
docker exec -it rabbitmq rabbitmqctl list_exchanges name type

# Просмотр биндингов
docker exec -it rabbitmq rabbitmqctl list_bindings
```
