#!/usr/bin/env python3
"""
Скрипт для запуска форум-приложения
"""

import uvicorn
import os
from pathlib import Path

# Добавляем корневую директорию в путь
current_dir = Path(__file__).parent
os.chdir(current_dir)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
