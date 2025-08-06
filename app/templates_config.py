"""
Общий объект Jinja2Templates с кастомными фильтрами
"""
from fastapi.templating import Jinja2Templates
from app.template_filters import (
    safe_html, nl2br, markdown_to_html, auto_link, 
    truncate_words, highlight_search, format_file_size, smart_content
)

# Создаем общий объект templates
templates = Jinja2Templates(directory="app/templates")

# Регистрируем кастомные фильтры
templates.env.filters['safe_html'] = safe_html
templates.env.filters['nl2br'] = nl2br
templates.env.filters['markdown'] = markdown_to_html
templates.env.filters['auto_link'] = auto_link
templates.env.filters['truncate_words'] = truncate_words
templates.env.filters['highlight_search'] = highlight_search
templates.env.filters['format_file_size'] = format_file_size
templates.env.filters['smart_content'] = smart_content
