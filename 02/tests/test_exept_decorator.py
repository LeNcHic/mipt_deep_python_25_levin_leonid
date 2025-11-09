"""Тесты декоратора ошибок"""


import pytest
from hw_task02.exept_decorator import retry_deco


def test_success_no_retry(capsys):
    """Тест без исключений"""
    @retry_deco(3)
    def add(a, b):
        return a + b

    assert add(4, 2) == 6
    out = capsys.readouterr().out
    assert 'run "add"' in out
    assert "attempt = 1" in out
    assert "result = 6" in out


def test_retry_then_success(capsys):
    """Тест на успех с 3 попытки"""
    calls = {"n": 0}

    @retry_deco(3)
    def sometimes_fail():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("error")
        return 42

    assert sometimes_fail() == 42
    out = capsys.readouterr().out
    assert out.count("exception = RuntimeError") == 2
    assert "attempt = 3" in out and "result = 42" in out
    assert calls["n"] == 3


def test_positional(capsys):
    """Тест на позиционные параметры в декораторе"""
    @retry_deco(1)
    def add(a, b):
        return a + b

    assert add(4, b=3) == 7
    out = capsys.readouterr().out
    assert 'positional args = (4,)' in out
    assert "keyword kwargs = {'b': 3}" in out
    assert "result = 7" in out


def test_decorator(capsys):
    """Тест на отсутствие параметры в декораторе"""
    @retry_deco
    def echo(x):
        return x

    assert echo("hi") == "hi"
    out = capsys.readouterr().out
    assert 'run "echo"' in out
    assert "attempt = 1" in out
    assert "result = 'hi'" in out


def test_expected_exception(capsys):
    """Исключение из expected_exceptions"""
    @retry_deco(5, [ValueError])
    def f():
        raise ValueError("ok")

    with pytest.raises(ValueError):
        f()
    out = capsys.readouterr().out
    assert out.count("exception = ValueError") == 1
    assert "attempt = 1" in out
    assert "attempt = 2" not in out
