"""Настройка логирования для LRU-кэша."""

from __future__ import annotations

import logging
import sys

LOG_FILE = "cache.log"
LOGGER_NAME = "cache"


class OddWordsFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Оставляет только сообщения с нечётным количеством слов."""
    def filter(self, record):
        message = record.getMessage()
        words = message.split()
        return len(words) % 2 == 1


def configure_logging(to_stdout: bool, use_filter: bool) -> None:
    """Настраиваем логирование в файл и в stdout."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    file_handler.setFormatter(file_formatter)

    handlers: list[logging.Handler] = [file_handler]

    if to_stdout:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_formatter = logging.Formatter("%(levelname)s: %(message)s")
        stream_handler.setFormatter(stream_formatter)
        handlers.append(stream_handler)

    if use_filter:
        filt = OddWordsFilter()
        for handler in handlers:
            handler.addFilter(filt)

    for handler in handlers:
        logger.addHandler(handler)
