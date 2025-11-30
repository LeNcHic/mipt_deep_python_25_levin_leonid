"""Тесты декоратора ошибок"""


import pytest
from exept_decorator import retry_deco


def test_success_no_retry(capsys):
    """Функция отрабатывает с первой попытки, без исключений."""
    @retry_deco(3)
    def add(a, b):
        return a + b

    assert add(4, 2) == 6
    out_lines = capsys.readouterr().out.splitlines()
    assert out_lines == [
        'run "add", with positional args = (4, 2), attempt = 1, result = 6',
    ]


def test_retry_then_success(capsys):
    """Функция падает первые две попытки и успешно завершается с третьей."""
    calls = {"n": 0}

    @retry_deco(3)
    def sometimes_fail():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("error")
        return 42

    assert sometimes_fail() == 42
    out_lines = capsys.readouterr().out.splitlines()
    assert out_lines == [
        'run "sometimes_fail", attempt = 1, exception = RuntimeError',
        'run "sometimes_fail", attempt = 2, exception = RuntimeError',
        'run "sometimes_fail", attempt = 3, result = 42',
    ]
    assert calls["n"] == 3


def test_positional_and_keyword_args_logged(capsys):
    """Проверяем корректный вывод позиционных и именованных аргументов."""
    @retry_deco(1)
    def add(a, b):
        return a + b

    assert add(4, b=3) == 7
    out_lines = capsys.readouterr().out.splitlines()
    assert out_lines == [
        'run "add", with positional args = (4,), '
        "keyword kwargs = {'b': 3}, attempt = 1, result = 7",
    ]


def test_expected_exception_no_retry(capsys):
    """Исключение из expected_exceptions не приводит к повторным попыткам."""
    @retry_deco(5, [ValueError])
    def f():
        raise ValueError("ok")

    with pytest.raises(ValueError):
        f()
    out_lines = capsys.readouterr().out.splitlines()
    assert out_lines == [
        'run "f", attempt = 1, exception = ValueError',
    ]


def test_all_retries_failed(capsys):
    """После всех попыток исключение всё равно пробрасывается наружу."""
    @retry_deco(3)
    def always_fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        always_fail()
    out_lines = capsys.readouterr().out.splitlines()
    assert out_lines == [
        'run "always_fail", attempt = 1, exception = RuntimeError',
        'run "always_fail", attempt = 2, exception = RuntimeError',
        'run "always_fail", attempt = 3, exception = RuntimeError',
    ]
