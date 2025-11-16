"""Асинхронное считывание url из файла"""

import asyncio
import sys
from pathlib import Path
from typing import Sequence
import aiohttp


def parse_args(argv: Sequence[str]) -> tuple[int, Path]:
    """Достаем переменные из команды"""
    if len(argv) != 2:
        raise SystemExit("Неправильные аргументы команды: "
                         "python fetcher.py <concurrency> urls.txt")

    conc_str, filename = argv

    if not conc_str.isdigit():
        raise SystemExit("Concurrency должно быть числом.")

    concurrency = int(conc_str)
    if concurrency <= 0:
        concurrency = 1

    urls_path = Path(filename)
    if not urls_path.is_file():
        raise SystemExit(f"Файл не найден: {urls_path}")

    return concurrency, urls_path


def read_urls(path: Path) -> list[str]:
    """Читаем файл с urls"""
    text = path.read_text(encoding="utf-8")
    lines = (line.strip() for line in text.splitlines())
    return [line for line in lines if line]


async def fetch_one(
    session: aiohttp.ClientSession,
    url: str,
    sem: asyncio.Semaphore,
) -> None:
    """Определяем действие одной задачи: обратиться по url"""
    async with sem:
        try:
            async with session.get(url) as resp:
                body = await resp.read()
                print(f"{url} -> {resp.status} ({len(body)} bytes)")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"{url} -> Ошибка: {exc}")


async def fetch_all(urls: list[str], concurrency: int) -> None:
    """Асинхронно работаем с urls"""
    if not urls:
        print("Больше url нет")
        return

    sem = asyncio.Semaphore(concurrency)
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch_one(session, url, sem) for url in urls]
        await asyncio.gather(*tasks)


def main(argv: Sequence[str]) -> None:
    """Запускаем"""
    concurrency, urls_file = parse_args(argv)
    urls = read_urls(urls_file)
    asyncio.run(fetch_all(urls, concurrency))


if __name__ == "__main__":
    main(sys.argv[1:])
