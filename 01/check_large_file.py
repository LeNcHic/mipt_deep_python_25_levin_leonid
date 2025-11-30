"""Проверка файла на стоп-слова и поиск таргетных слов."""


from pathlib import Path
from typing import Iterable, Iterator, TextIO, Union

FileOrName = Union[str, Path, TextIO]


def _iter_lines(file_or_name: FileOrName) -> Iterator[str]:
    """Итерируемся по строкам, поддерживая и путь, и файловый объект."""
    if isinstance(file_or_name, (str, Path)):
        with open(file_or_name, encoding="utf-8") as f:
            for line in f:
                yield line.rstrip("\n")
    else:
        for line in file_or_name:
            yield line.rstrip("\n")


def check_file(
    file_or_name: FileOrName,
    banwords: Iterable[str],
    keywords: Iterable[str],
) -> Iterator[str]:
    """Генератор строк, где есть хотя бы одно keyword
       и нет ни одного banword"""
    ban_set = {w.lower() for w in banwords}
    key_set = {w.lower() for w in keywords}

    for raw_line in _iter_lines(file_or_name):
        words = raw_line.split()
        if not words:
            continue

        lowered = [w.lower() for w in words]

        if any(word in ban_set for word in lowered):
            continue

        if any(word in key_set for word in lowered):
            yield raw_line
