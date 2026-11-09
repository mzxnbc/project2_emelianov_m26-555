"""Функции для работы с файлами базы данных."""

import json
from pathlib import Path

from primitive_db.constants import DATA_DIR
from primitive_db.decorators import log_time


@log_time
def load_metadata(filepath):
    """Загрузить метаданные базы данных."""
    path = Path(filepath)

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@log_time
def save_metadata(filepath, data):
    """Сохранить метаданные базы данных."""
    path = Path(filepath)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)



@log_time
def load_table_data(table_name):
    """Загрузить записи указанной таблицы."""
    path = Path(DATA_DIR) / f"{table_name}.json"

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@log_time
def save_table_data(table_name, data):
    """Сохранить записи указанной таблицы."""
    path = Path(DATA_DIR)
    path.mkdir(parents=True, exist_ok=True)

    file_path = path / f"{table_name}.json"

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
