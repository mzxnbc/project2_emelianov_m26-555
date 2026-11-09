"""Декораторы и кэширование."""

import time
from functools import wraps


def handle_db_errors(func):
    """Обработать ошибки базы данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError) as error:
            print(f"Ошибка: {error}")
            return None

    return wrapper


def confirm_action(action_name):
    """Запросить подтверждение действия."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            confirmation = input(
                f"Подтвердите действие '{action_name}' [y/n]: "
            ).strip().lower()

            if confirmation == "y":
                return func(*args, **kwargs)

            return False

        return wrapper

    return decorator


def log_time(func):
    """Измерить время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start

        print(
            f"Функция {func.__name__} выполнилась "
            f"за {elapsed:.3f} секунд"
        )
        return result

    return wrapper


def create_cacher():
    """Создать кэш результатов."""

    cache = {}

    def cache_result(key, value_func):
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    return cache_result