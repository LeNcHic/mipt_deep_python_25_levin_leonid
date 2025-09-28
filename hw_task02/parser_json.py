"""Распарсить json строку"""


import json
from typing import Callable


def process_json(
    json_str: str,
    required_keys: list[str] | None = None,
    tokens: list[str] | None = None,
    callback: Callable[[str, str], None] | None = None,
) -> None:
    """ Функция поиск токенов по ключам в json строке"""
    if required_keys is None or tokens is None or callback is None:
        return

    data = json.loads(json_str)
    for key in required_keys:
        if key in data:
            words = data[key].lower().split()
            for token in tokens:
                if token.lower() in words:
                    callback(key, token)
