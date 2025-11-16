"""Тесты для fetcher.py"""

from pathlib import Path
import asyncio
import pytest
import fetcher


def test_parse_args_ok() -> None:
    """Проверяем корректные аргументы: число и существующий файл."""
    concurrency, path = fetcher.parse_args(["5", "urls.txt"])
    assert concurrency == 5
    assert path.name == "urls.txt"


def test_parse_args_bad_len() -> None:
    """Падаем, если передано не два аргумента."""
    with pytest.raises(SystemExit):
        fetcher.parse_args(["10"])


def test_parse_args_not_int_existing_file() -> None:
    """Падаем, если concurrency не число."""
    with pytest.raises(SystemExit):
        fetcher.parse_args(["abc", "urls.txt"])


def test_parse_args_file_not_found() -> None:
    """Падаем, если файла с urls не существует."""
    with pytest.raises(SystemExit):
        fetcher.parse_args(["5", "no_file.txt"])


def test_parse_args_non_positive_concurrency() -> None:
    """Заменяем неположительное concurrency на 1."""
    concurrency, _ = fetcher.parse_args(["0", "urls.txt"])
    assert concurrency == 1


def test_fetch_real_network_basic(capsys) -> None:
    """Делаем реальные запросы к паре сайтов и проверяем,
       что они попали в вывод."""
    urls = [
        "https://www.google.com",
        "https://www.python.org",
    ]
    asyncio.run(fetcher.fetch_all(urls, concurrency=2))
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) >= len(urls)

    for url in urls:
        assert any(url in line for line in lines)


def test_fetch_on_full_urls_txt(capsys) -> None:
    """Работаем со всеми url из urls.txt."""
    urls_path = Path("urls.txt")

    urls = fetcher.read_urls(urls_path)
    asyncio.run(fetcher.fetch_all(urls, concurrency=5))
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) >= len(urls)

    for url in urls:
        assert any(url in line for line in lines)


def test_fetch_all_handles_empty_list(capsys) -> None:
    """Проверяем поведение на пустом списке urls."""
    asyncio.run(fetcher.fetch_all([], concurrency=3))
    out = capsys.readouterr().out
    assert "Больше url нет" in out
