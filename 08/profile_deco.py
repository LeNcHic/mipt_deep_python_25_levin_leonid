"""Декоратор для удобного профилирования"""


import cProfile
import pstats
import functools
from typing import Callable, Any


def profile_deco(func: Callable) -> Callable:
    """
    Декоратор, который копит статистику cProfile
    по всем вызовам одной и той же функции.
    """
    profiler = cProfile.Profile()

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        profiler.enable()
        try:
            return func(*args, **kwargs)
        finally:
            profiler.disable()

    def print_stat(sort_by: str = "tottime", lines: int = 20) -> None:
        stats = pstats.Stats(profiler).sort_stats(sort_by)
        stats.print_stats(lines)

    wrapper.print_stat = print_stat
    return wrapper


@profile_deco
def add(a, b):
    """Сумма"""
    return a + b


@profile_deco
def sub(a, b):
    """Разность"""
    return a - b


if __name__ == "__main__":
    add(1, 2)
    add(4, 5)
    sub(4, 5)

    print("\n=== Профиль add ===")
    add.print_stat()

    print("\n=== Профиль sub ===")
    sub.print_stat()
