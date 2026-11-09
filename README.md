# Primitive DB

Примитивная база данных на Python с консольным интерфейсом и хранением данных в JSON-файлах.

## Возможности

- Создание и удаление таблиц.
- Просмотр списка таблиц.
- Добавление записей.
- Выборка записей с условиями.
- Обновление и удаление записей.
- Просмотр информации о таблице.
- Автоматическая генерация ID.
- Поддержка типов `int`, `str`, `bool`.
- Подтверждение удаления.
- Измерение времени выполнения операций.
- Кэширование результатов выборки.

## Установка

```bash
git clone https://github.com/mzxnbc/project2_emelianov_m26-555.git
cd project2_emelianov_m26-555
uv sync
```

## Запуск

```bash
uv run database
```

## Примеры команд

Создать таблицу:

```text
create_table users name:str age:int active:bool
```

Добавить запись:

```text
insert into users values Sergei 28 true
```

Показать все записи:

```text
select from users
```

Выбрать записи по условию:

```text
select from users where age = 28
```

Обновить запись:

```text
update users set age = 29 where name = Sergei
```

Удалить запись:

```text
delete from users where ID = 1
```

Посмотреть информацию о таблице:

```text
info users
```

Показать список команд:

```text
help
```

Выйти из программы:

```text
exit
```

## Проверка качества кода

```bash
uv run ruff check .
```

## Сборка проекта

```bash
uv build
```