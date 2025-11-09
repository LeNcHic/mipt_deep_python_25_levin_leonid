"""Декоратор обработки исключений"""


from __future__ import annotations
from functools import wraps
from typing import Any, Callable, Iterable


def retry_deco(
    basic_func: Callable | None = None,
    retries: int = 1,
    expected_exceptions: Iterable[type[BaseException]] | None = None
):
    """Декоратор для исключений"""
    if basic_func and not callable(basic_func):
        first = basic_func
        basic_func = None
        if not expected_exceptions and not isinstance(retries, int):
            expected_exceptions = retries
        retries = int(first)

    if expected_exceptions:
        expected = tuple(expected_exceptions)
    else:
        expected = tuple()

    def decorator(func: Callable):
        """Создаем декоратор """
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            """Пробуем запустить функцию N раз"""
            name = func.__name__
            for attempt in range(1, retries + 1):
                try:
                    result = func(*args, **kwargs)
                # pylint: disable-next=broad-exception-caught
                except Exception as exc:
                    parts = [f'run "{name}"']
                    if args:
                        parts.append(f"with positional args = {args}")
                    if kwargs:
                        parts.append(f"keyword kwargs = {kwargs}")
                    parts.append(f"attempt = {attempt}")
                    parts.append(f"exception = {type(exc).__name__}")
                    print(", ".join(parts))

                    if isinstance(exc, expected):
                        raise

                    if attempt == retries:
                        raise
                    continue

                parts = [f'run "{name}"']
                if args:
                    parts.append(f"with positional args = {args}")
                if kwargs:
                    parts.append(f"keyword kwargs = {kwargs}")
                parts.append(f"attempt = {attempt}")
                parts.append(f"result = {result!r}")
                print(", ".join(parts))
                return result

        return wrapper

    if basic_func and callable(basic_func):
        return decorator(basic_func)
    return decorator
