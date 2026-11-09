
"""Командный интерфейс базы данных."""

import json
import shlex

from prettytable import PrettyTable
from prompt import string

from primitive_db.constants import DB_META_FILE
from primitive_db.core import (
    create_table,
    delete_records,
    drop_table,
    insert_record,
    select_records,
    update_record,
)
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

cache_result = create_cacher()


@confirm_action("delete")
def confirm_delete():
    """Подтвердить удаление записей."""
    return True


@confirm_action("drop_table")
def confirm_drop_table():
    """Подтвердить удаление таблицы."""
    return True


def welcome():
    """Показать приветствие."""
    print("Добро пожаловать в Primitive DB!")
    print("Введите help для просмотра доступных команд.")


def show_help():
    """Показать список доступных команд."""
    print(
        """
Доступные команды:

create_table <table> <column:type> ... — создать таблицу
drop_table <table>                       — удалить таблицу
list_tables                              — показать таблицы
insert into <table> values ...           — добавить запись
select from <table>                      — показать записи
update <table> set ... where ...         — обновить запись
delete from <table> where ...            — удалить запись
info <table>                             — информация о таблице
help                                     — помощь
exit                                     — выход

Пример:
create_table users name:str age:int active:bool
"""
    )


@log_time
def timed_select(metadata, table_name, records, condition):
    """Выполнить выборку с замером времени."""
    return select_records(metadata, table_name, records, condition)


@log_time
def timed_insert(metadata, table_name, values, records):
    """Добавить запись с замером времени."""
    return insert_record(metadata, table_name, values, records)


@handle_db_errors
def run():
    """Запустить командный интерфейс базы данных."""
    welcome()

    while True:
        try:
            command = string("db > ").strip()

            if not command:
                continue

            parts = shlex.split(command)
            action = parts[0]

            metadata = load_metadata(DB_META_FILE)

            if action == "exit":
                print("До свидания!")
                break

            elif action == "help":
                show_help()

            elif action == "list_tables":
                if metadata:
                    print("Таблицы:", ", ".join(metadata))
                else:
                    print("Таблиц пока нет.")

            elif action == "create_table":
                if len(parts) < 2:
                    raise ValueError("Укажите название таблицы.")

                table_name = parts[1]
                columns = []

                for column in parts[2:]:
                    if ":" not in column:
                        raise ValueError(
                            f"Некорректное значение: {column}"
                        )

                    column_name, column_type = column.split(":", 1)
                    columns.append((column_name, column_type))

                create_table(metadata, table_name, columns)
                save_metadata(DB_META_FILE, metadata)
                print(f"Таблица '{table_name}' успешно создана.")

            elif action == "drop_table":
                if len(parts) != 2:
                    raise ValueError("Укажите название одной таблицы.")

                table_name = parts[1]

                if confirm_drop_table():
                    drop_table(metadata, table_name)
                    save_metadata(DB_META_FILE, metadata)
                    print(f"Таблица '{table_name}' успешно удалена.")
                else:
                    print("Удаление отменено.")

            elif action == "insert":
                if (
                    len(parts) < 5
                    or parts[1] != "into"
                    or parts[3] != "values"
                ):
                    raise ValueError(
                        'Формат: insert into users values Sergei 28 true'
                    )

                table_name = parts[2]
                values = parts[4:]

                if values[0].startswith("("):
                    values[0] = values[0][1:]
                if values[-1].endswith(")"):
                    values[-1] = values[-1][:-1]

                values = [value.rstrip(",") for value in values]

                records = load_table_data(table_name)
                record = timed_insert(
                    metadata, table_name, values, records
                )
                records.append(record)
                save_table_data(table_name, records)

                print("Запись успешно добавлена.")

            elif action == "select":
                if len(parts) < 3 or parts[1] != "from":
                    raise ValueError(
                        "Формат: select from users [where age = 28]"
                    )

                table_name = parts[2]
                condition = None

                if len(parts) > 3:
                    if len(parts) != 7 or parts[3] != "where":
                        raise ValueError("Формат условия: where age = 28")

                    condition = (parts[4], parts[5], parts[6])

                records = load_table_data(table_name)
                result = cache_result(
                    (table_name, str(records), str(condition)),
                    lambda: timed_select(
                        metadata, table_name, records, condition
                    ),
                )

                if result:
                    table = PrettyTable()
                    table.field_names = list(metadata[table_name])

                    for record in result:
                        table.add_row(
                            [record[column] for column in table.field_names]
                        )

                    print(table)
                else:
                    print("Записи не найдены.")

            elif action == "update":
                if (
                    len(parts) != 10
                    or parts[2] != "set"
                    or parts[4] != "="
                    or parts[6] != "where"
                    or parts[8] != "="
                ):
                    raise ValueError(
                        "Формат: update users set age = 29 where name = Sergei"
                    )

                table_name = parts[1]
                column_name = parts[3]
                value = parts[5]
                condition = (parts[7], parts[8], parts[9])

                records = load_table_data(table_name)
                records, updated = update_record(
                    metadata,
                    table_name,
                    records,
                    column_name,
                    value,
                    condition,
                )
                save_table_data(table_name, records)

                print(f"Обновлено записей: {updated}")

            elif action == "delete":
                if (
                    len(parts) != 7
                    or parts[1] != "from"
                    or parts[3] != "where"
                    or parts[5] != "="
                ):
                    raise ValueError(
                        "Формат: delete from users where ID = 1"
                    )

                table_name = parts[2]
                condition = (parts[4], parts[5], parts[6])

                records = load_table_data(table_name)
                remaining, deleted = delete_records(
                    metadata,
                    table_name,
                    records,
                    condition,
                )

                if deleted:
                    if confirm_delete():
                        save_table_data(table_name, remaining)
                        print(f"Удалено записей: {deleted}")
                    else:
                        print("Удаление отменено.")
                else:
                    print("Записи не найдены.")

            elif action == "info":
                if len(parts) != 2:
                    raise ValueError("Формат: info users")

                table_name = parts[1]

                if table_name not in metadata:
                    raise KeyError(
                        f"Таблица '{table_name}' не существует."
                    )

                print(f"Таблица: {table_name}")
                print("Колонки:")

                for column_name, column_type in metadata[table_name].items():
                    print(f"  {column_name}: {column_type}")

                records = load_table_data(table_name)
                print(f"Количество записей: {len(records)}")

            else:
                print(f"Функции {action} нет. Попробуйте снова.")

        except (ValueError, KeyError) as error:
            print(f"Ошибка: {error}")
        except (FileNotFoundError, json.JSONDecodeError) as error:
            print(f"Ошибка чтения базы данных: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break
