"""
Кастомные фильтры для Jinja2 шаблонов
"""
import bleach
import markdown
from markupsafe import Markup
import re


def safe_html(text):
    """
    Безопасная обработка HTML в сообщениях
    Разрешает только безопасные теги
    """
    if not text:
        return ""
    
    allowed_tags = [
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'hr',
        'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'div': ['class'],
        'span': ['class'],
        'pre': ['class'],
        'table': ['class'],
        'th': ['class'],
        'td': ['class']
    }
    
    # Очищаем HTML, оставляя только разрешенные теги
    clean_html = bleach.clean(
        text, 
        tags=allowed_tags, 
        attributes=allowed_attributes,
        strip=True
    )
    
    return Markup(clean_html)


def nl2br(text):
    """
    Преобразует переносы строк в <br> теги
    """
    if not text:
        return ""
    
    # Заменяем \n на <br>
    html_text = text.replace('\n', '<br>')
    return Markup(html_text)


def markdown_to_html(text):
    """
    Преобразует Markdown в HTML с поддержкой подсветки кода
    """
    if not text:
        return ""
    
    # Настройки Markdown с расширениями
    md = markdown.Markdown(
        extensions=[
            'nl2br',           # Автоматические переносы строк
            'codehilite',      # Подсветка кода
            'fenced_code',     # Блоки кода с ```
            'tables',          # Поддержка таблиц
            'toc',             # Оглавление
            'abbr',            # Аббревиатуры
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
            }
        }
    )
    
    # Преобразуем Markdown в HTML
    html = md.convert(text)
    
    # Очищаем HTML для безопасности
    allowed_tags = [
        'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'hr',
        'div', 'span', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'del', 'ins'  # Для зачеркнутого и подчеркнутого текста
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'div': ['class', 'id'],
        'span': ['class'],
        'pre': ['class'],
        'table': ['class'],
        'th': ['class'],
        'td': ['class'],
        'h1': ['id'],
        'h2': ['id'],
        'h3': ['id'],
        'h4': ['id'],
        'h5': ['id'],
        'h6': ['id']
    }
    
    clean_html = bleach.clean(
        html, 
        tags=allowed_tags, 
        attributes=allowed_attributes,
        strip=True
    )
    
    return Markup(clean_html)


def auto_link(text):
    """
    Автоматически превращает URL в ссылки
    """
    if not text:
        return ""
    
    # Регулярное выражение для поиска URL
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    
    def replace_url(match):
        url = match.group(0)
        return f'<a href="{url}" target="_blank" rel="noopener">{url}</a>'
    
    linked_text = url_pattern.sub(replace_url, text)
    return Markup(linked_text)


def truncate_words(text, length=50, suffix='...'):
    """
    Обрезает текст до указанного количества слов
    """
    if not text:
        return ""
    
    words = text.split()
    if len(words) <= length:
        return text
    
    return ' '.join(words[:length]) + suffix


def highlight_search(text, query):
    """
    Подсвечивает поисковые запросы в тексте
    """
    if not text or not query:
        return text
    
    # Экранируем специальные символы в запросе
    escaped_query = re.escape(query)
    
    # Подсвечиваем совпадения (регистронезависимо)
    pattern = re.compile(f'({escaped_query})', re.IGNORECASE)
    highlighted = pattern.sub(r'<mark>\1</mark>', text)
    
    return Markup(highlighted)


def format_file_size(size_bytes):
    """
    Форматирует размер файла в человекочитаемый вид
    """
    if not size_bytes:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def smart_content(text):
    """
    Умная обработка контента:
    1. Автоматические ссылки
    2. Переносы строк
    3. Безопасная очистка HTML
    """
    if not text:
        return ""
    
    # Сначала делаем автоссылки
    text_with_links = auto_link(text)
    
    # Затем переносы строк
    text_with_breaks = nl2br(text_with_links)
    
    # И наконец безопасная очистка
    return safe_html(text_with_breaks)
