"""Разбор команд пользовательского интерфейса."""

import shlex


def parse_command(command):
    """Разобрать команду на отдельные элементы."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars="(),")
    lexer.whitespace_split = True

    try:
        parts = list(lexer)
    except ValueError as error:
        raise ValueError("Некорректный формат команды.") from error

    return [part for part in parts if part not in ("(", ")", ",")]