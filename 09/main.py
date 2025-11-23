"""Проверка LRU-кэщ с логированием."""

from __future__ import annotations

import argparse

from lru_cache import LRUCache, LOGGER
from logging_setup import configure_logging


def parse_args(argv=None):
    """Парсим аргументы команды"""
    parser = argparse.ArgumentParser(
        description="Проверка LRU-кэша с логированием.",
    )
    parser.add_argument(
        "-s",
        "--stdout",
        action="store_true",
        help="дополнительно писать логи в stdout",
    )
    parser.add_argument(
        "-f",
        "--filter",
        action="store_true",
        help="включить фильтр, который отбрасывает"
             " записи с чётным числом слов",
    )
    return parser.parse_args(argv)


def run_demo() -> None:
    """Минимальный набор операций."""
    cache = LRUCache(limit=2)

    LOGGER.info("Старт")

    # set отсутствующего ключа
    cache.set("k1", "val1")

    # set другого отсутствующего ключа
    cache.set("k2", "val2")

    # get отсутствующего ключа
    _ = cache.get("k3")

    # get существующего ключа
    _ = cache.get("k2")

    # get другого существующего ключа
    _ = cache.get("k1")

    # set существующего ключа
    cache.set("k1", "val1-upd")

    # set отсутствующего ключа при полной ёмкости
    cache.set("k3", "val3")

    # get ключа, который мог быть вытеснён
    _ = cache.get("k2")

    LOGGER.debug("финальное состояние кэша: %r", cache)
    LOGGER.info("Завершено")


def main(argv=None) -> None:
    """Запуск"""
    args = parse_args(argv)
    configure_logging(to_stdout=args.stdout, use_filter=args.filter)
    run_demo()


if __name__ == "__main__":
    main()
