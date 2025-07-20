-- Скрипт инициализации базы данных для форума
-- Этот файл выполняется при первом запуске контейнера PostgreSQL

-- Создаем базу данных для форума (если она еще не создана)
-- CREATE DATABASE forum_db; -- Эта команда уже выполняется через переменную окружения

-- Создаем пользователя для приложения (если он еще не создан)
-- CREATE USER forum_user WITH PASSWORD 'forum_password'; -- Уже создается через переменные окружения

-- Предоставляем права пользователю
GRANT ALL PRIVILEGES ON DATABASE forum_db TO forum_user;

-- Подключаемся к базе данных форума
\c forum_db;

-- Предоставляем права на схему public
GRANT ALL ON SCHEMA public TO forum_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO forum_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO forum_user;

-- Устанавливаем права по умолчанию для будущих объектов
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO forum_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO forum_user;
