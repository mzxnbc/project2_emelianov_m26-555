"""Основная логика управления таблицами."""

from pathlib import Path

from primitive_db.constants import DATA_DIR, ID_COLUMN, SUPPORTED_TYPES


def create_table(metadata, table_name, columns):
    """Создать новую таблицу с указанными колонками."""
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует.")

    if not table_name:
        raise ValueError("Название таблицы не может быть пустым.")

    table_columns = {ID_COLUMN: "int"}

    for column_name, column_type in columns:
        if column_name == ID_COLUMN:
            raise ValueError(
                f"Колонка '{ID_COLUMN}' создаётся автоматически."
            )

        if column_name in table_columns:
            raise ValueError(f"Колонка '{column_name}' уже существует.")

        if column_type not in SUPPORTED_TYPES:
            raise ValueError(
                f"Тип '{column_type}' не поддерживается. "
                f"Допустимые типы: {', '.join(SUPPORTED_TYPES)}."
            )

        table_columns[column_name] = column_type

    metadata[table_name] = table_columns
    return metadata


def drop_table(metadata, table_name):
    """Удалить таблицу и её файл с данными."""
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    file_path = Path(DATA_DIR) / f"{table_name}.json"

    if file_path.exists():
        file_path.unlink()

    del metadata[table_name]
    return metadata


def insert_record(metadata, table_name, values, records):
    """Добавить новую запись в таблицу."""
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    columns = metadata[table_name]
    user_columns = [name for name in columns if name != ID_COLUMN]

    if len(values) != len(user_columns):
        raise ValueError(
            "Количество значений не совпадает с количеством колонок."
        )

    record = {}

    for column_name, value in zip(user_columns, values):
        column_type = columns[column_name]

        if column_type == "int":
            try:
                record[column_name] = int(value)
            except ValueError as error:
                raise ValueError(
                    f"Некорректное значение: {value}"
                ) from error

        elif column_type == "bool":
            if str(value).lower() not in ("true", "false"):
                raise ValueError(f"Некорректное значение: {value}")

            record[column_name] = str(value).lower() == "true"

        elif column_type == "str":
            record[column_name] = str(value)

    next_id = max((row[ID_COLUMN] for row in records), default=0) + 1
    record[ID_COLUMN] = next_id

    return record


def select_records(metadata, table_name, records, condition=None):
    """Получить записи таблицы с учётом условия."""
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    if condition is None:
        return records

    column_name, operator, value = condition

    if column_name not in metadata[table_name]:
        raise ValueError(f"Колонка '{column_name}' не существует.")

    column_type = metadata[table_name][column_name]

    if column_type == "int":
        try:
            value = int(value)
        except ValueError as error:
            raise ValueError(
                f"Некорректное значение: {value}"
            ) from error

    elif column_type == "bool":
        if str(value).lower() not in ("true", "false"):
            raise ValueError(f"Некорректное значение: {value}")

        value = str(value).lower() == "true"

    operators = {
        "=": lambda left, right: left == right,
        "!=": lambda left, right: left != right,
        ">": lambda left, right: left > right,
        "<": lambda left, right: left < right,
        ">=": lambda left, right: left >= right,
        "<=": lambda left, right: left <= right,
    }

    if operator not in operators:
        raise ValueError(f"Оператор '{operator}' не поддерживается.")

    return [
        record
        for record in records
        if operators[operator](record[column_name], value)
    ]


def update_record(metadata, table_name, records, column_name, value, condition):
    """Изменить значения в записях таблицы."""
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    columns = metadata[table_name]

    if column_name not in columns:
        raise ValueError(f"Колонка '{column_name}' не существует.")

    condition_column, operator, condition_value = condition

    if condition_column not in columns:
        raise ValueError(f"Колонка '{condition_column}' не существует.")

    def convert_value(column, raw_value):
        column_type = columns[column]

        if column_type == "int":
            try:
                return int(raw_value)
            except ValueError as error:
                raise ValueError(
                    f"Некорректное значение: {raw_value}"
                ) from error

        if column_type == "bool":
            if str(raw_value).lower() not in ("true", "false"):
                raise ValueError(f"Некорректное значение: {raw_value}")

            return str(raw_value).lower() == "true"

        return str(raw_value)

    value = convert_value(column_name, value)
    condition_value = convert_value(condition_column, condition_value)

    if column_name == ID_COLUMN:
        raise ValueError("Нельзя изменять ID.")

    operators = {
        "=": lambda left, right: left == right,
        "!=": lambda left, right: left != right,
        ">": lambda left, right: left > right,
        "<": lambda left, right: left < right,
        ">=": lambda left, right: left >= right,
        "<=": lambda left, right: left <= right,
    }

    if operator not in operators:
        raise ValueError(f"Оператор '{operator}' не поддерживается.")

    updated = 0

    for record in records:
        if operators[operator](record[condition_column], condition_value):
            record[column_name] = value
            updated += 1

    return records, updated


def delete_records(metadata, table_name, records, condition):
    """Удалить записи по заданному условию."""
    if table_name not in metadata:
        raise KeyError(f"Таблица '{table_name}' не существует.")

    column_name, operator, value = condition

    if column_name not in metadata[table_name]:
        raise ValueError(f"Колонка '{column_name}' не существует.")

    column_type = metadata[table_name][column_name]

    if column_type == "int":
        try:
            value = int(value)
        except ValueError as error:
            raise ValueError(
                f"Некорректное значение: {value}"
            ) from error

    elif column_type == "bool":
        if str(value).lower() not in ("true", "false"):
            raise ValueError(f"Некорректное значение: {value}")

        value = str(value).lower() == "true"

    operators = {
        "=": lambda left, right: left == right,
        "!=": lambda left, right: left != right,
        ">": lambda left, right: left > right,
        "<": lambda left, right: left < right,
        ">=": lambda left, right: left >= right,
        "<=": lambda left, right: left <= right,
    }

    if operator not in operators:
        raise ValueError(f"Оператор '{operator}' не поддерживается.")

    remaining = [
        record
        for record in records
        if not operators[operator](record[column_name], value)
    ]

    deleted = len(records) - len(remaining)
    return remaining, deleted