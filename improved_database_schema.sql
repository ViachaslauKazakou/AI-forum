-- Улучшенная схема БД для ИИ-форума
-- Исправляет ошибки и добавляет недостающие поля

-- Пользователи
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    lastname VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Профили пользователей
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    city VARCHAR(100),
    country VARCHAR(100),
    tags TEXT[], -- массив интересов
    avatar_enabled BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user', -- user, moderator, admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ИИ-аватары пользователей
CREATE TABLE ai_avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100),
    personality TEXT, -- описание личности
    speech_pattern TEXT, -- стиль речи
    expertise TEXT, -- области знаний
    mood_variations JSONB, -- массив настроений
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    training_status VARCHAR(20) DEFAULT 'untrained', -- untrained, training, ready
    last_training_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Категории форума
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Темы (threads)
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, archived, locked
    is_pinned BOOLEAN DEFAULT FALSE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Сообщения (ИСПРАВЛЕННАЯ ВЕРСИЯ)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID REFERENCES threads(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id), -- может быть NULL для ИИ
    ai_avatar_id UUID REFERENCES ai_avatars(id), -- может быть NULL для людей
    parent_message_id UUID REFERENCES messages(id), -- для ответов
    content TEXT NOT NULL, -- ❗ ДОБАВЛЕНО: текст сообщения
    content_type VARCHAR(20) DEFAULT 'text', -- text, html, markdown
    status VARCHAR(20) DEFAULT 'published', -- published, moderated, waiting, rejected
    is_ai_generated BOOLEAN DEFAULT FALSE, -- ❗ ДОБАВЛЕНО: флаг ИИ сообщения
    mood VARCHAR(50), -- настроение ИИ при генерации
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ограничения: сообщение либо от пользователя, либо от ИИ
    CONSTRAINT check_author CHECK (
        (user_id IS NOT NULL AND ai_avatar_id IS NULL) OR
        (user_id IS NULL AND ai_avatar_id IS NOT NULL)
    )
);

-- Индексы для производительности
CREATE INDEX idx_messages_thread_id ON messages(thread_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_ai_avatar_id ON messages(ai_avatar_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_threads_category_id ON threads(category_id);

-- Журнал активности пользователей (опционально)
CREATE TABLE user_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50), -- login, post_message, create_thread, etc
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ИИ обучающие данные
CREATE TABLE ai_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_avatar_id UUID REFERENCES ai_avatars(id) ON DELETE CASCADE,
    source_message_id UUID REFERENCES messages(id),
    content_vector VECTOR(384), -- для embeddings (если используете pgvector)
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Очередь задач для ИИ
CREATE TABLE ai_task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ai_avatar_id UUID REFERENCES ai_avatars(id),
    task_type VARCHAR(50), -- generate_response, retrain_model, etc
    thread_id UUID REFERENCES threads(id),
    priority INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    scheduled_for TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
