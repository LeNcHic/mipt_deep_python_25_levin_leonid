"""Тесты для дескрипторов: Integer, String,
   PositiveInteger и дата-класс Data."""


from __future__ import annotations
import pytest
from descriptors import Data, Integer, String, PositiveInteger
# pylint: disable=too-few-public-methods, missing-class-docstring


def test_data_valid():
    """Data корректно инициализируется валидными значениями."""
    d = Data(1, "Apple", 10)
    assert d.num == 1
    assert d.name == "Apple"
    assert d.price == 10


@pytest.mark.parametrize("bad", [1.0, "1", True])
def test_integer_type_check(bad):
    """Integer отклоняет значения не типа int (включая bool)."""
    field = Integer()

    class C:
        iv = field

    c = C()
    with pytest.raises(TypeError):
        c.iv = bad


@pytest.mark.parametrize("val, ok", [("", False), ("A", True), ("AB", True)])
def test_string_len(val, ok):
    """String проверяет длину по min_len/max_len."""
    field = String(min_len=1, max_len=2)

    class C:
        s = field

    c = C()
    if ok:
        c.s = val
        assert c.s == val
    else:
        with pytest.raises(ValueError):
            c.s = val


@pytest.mark.parametrize("bad", [0, -1, -10])
def test_positive_integer_range(bad):
    """PositiveInteger отклоняет нули и отрицательные числа."""
    field = PositiveInteger()

    class C:
        p = field

    c = C()
    with pytest.raises(ValueError):
        c.p = bad


def test_storage_is_per_instance():
    """Хранение значений идёт отдельно для каждого экземпляра."""
    class C:
        a = Integer()

    c1, c2 = C(), C()
    c1.a = 1
    c2.a = 2
    assert c1.a == 1 and c2.a == 2


def test_string_type_check():
    """String отклоняет значения не типа str."""
    field = String(min_len=1, max_len=5)

    class C:
        s = field

    c = C()
    with pytest.raises(TypeError):
        c.s = 123  # не str


@pytest.mark.parametrize("val", ["ABC"])
def test_string_too_long(val):
    """String отклоняет строки длиннее max_len."""
    field = String(min_len=1, max_len=2)

    class C:
        s = field

    c = C()
    with pytest.raises(ValueError):
        c.s = val


def test_positive_integer_bool_rejected():
    """PositiveInteger отклоняет bool как недопустимый тип."""
    field = PositiveInteger()

    class C:
        p = field

    c = C()
    with pytest.raises(TypeError):
        c.p = True


def test_unset_returns_none():
    """Неприсвоенный дескриптор возвращает None при чтении."""
    class C:
        a = Integer()

    c = C()
    assert c.a is None


def test_data_invalid_in_init():
    """Data валидирует типы/значения в __init__ и выбрасывает исключения."""
    with pytest.raises(TypeError):
        Data("1", "Apple", 10)
    with pytest.raises(ValueError):
        Data(1, "", 10)
    with pytest.raises(ValueError):
        Data(1, "Apple", 0)


def test_descriptor_access_via_class():
    """Обращение к дескриптору через класс возвращает сам объект-дескриптор."""
    class C:
        a = Integer()

    assert isinstance(C.a, Integer)
