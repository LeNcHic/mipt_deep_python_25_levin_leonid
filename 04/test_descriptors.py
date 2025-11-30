"""Тесты для дескрипторов:
   Integer, String, PositiveInteger и дата-класс Data."""


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


def test_integer_can_change_to_another_valid_value():
    """Integer можно менять значение на другое валидное."""
    class C:
        iv = Integer()

    c = C()
    c.iv = 1
    c.iv = 10
    assert c.iv == 10


def test_integer_invalid_value_does_not_override_previous():
    """Integer невалидное значение не перезаписывает старое."""
    class C:
        iv = Integer()

    c = C()
    c.iv = 5

    with pytest.raises(TypeError):
        c.iv = "oops"

    assert c.iv == 5


@pytest.mark.parametrize("val, ok", [("", False), ("A", True), ("AB", True)])
def test_string_len(val, ok):
    """String проверяет длину по min_len или max_len."""
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


def test_string_type_check():
    """String отклоняет значения не типа str."""
    field = String(min_len=1, max_len=5)

    class C:
        s = field

    c = C()
    with pytest.raises(TypeError):
        c.s = 123


@pytest.mark.parametrize("val", ["ABC"])
def test_string_too_long(val):
    """String отклоняет строки длиннее max_len."""
    field = String(min_len=1, max_len=2)

    class C:
        s = field

    c = C()
    with pytest.raises(ValueError):
        c.s = val


def test_string_can_change_to_another_valid_value():
    """String: можно менять значение на другое валидное."""
    field = String(min_len=1, max_len=5)

    class C:
        s = field

    c = C()
    c.s = "Hi"
    c.s = "World"
    assert c.s == "World"


def test_string_invalid_value_does_not_override_previous():
    """String: невалидное значение не перезаписывает старое."""
    field = String(min_len=1, max_len=3)

    class C:
        s = field

    c = C()
    c.s = "ok"

    with pytest.raises(TypeError):
        c.s = 123
    assert c.s == "ok"

    with pytest.raises(ValueError):
        c.s = ""
    assert c.s == "ok"

    with pytest.raises(ValueError):
        c.s = "long"
    assert c.s == "ok"


@pytest.mark.parametrize("bad", [0, -1, -10])
def test_positive_integer_range(bad):
    """PositiveInteger отклоняет нули и отрицательные числа."""
    field = PositiveInteger()

    class C:
        p = field

    c = C()
    with pytest.raises(ValueError):
        c.p = bad


def test_positive_integer_bool_rejected():
    """PositiveInteger отклоняет bool как недопустимый тип."""
    field = PositiveInteger()

    class C:
        p = field

    c = C()
    with pytest.raises(TypeError):
        c.p = True


def test_positive_integer_can_change_to_another_valid_value():
    """PositiveInteger: можно менять значение на другое валидное."""
    class C:
        p = PositiveInteger()

    c = C()
    c.p = 1
    c.p = 100
    assert c.p == 100


def test_positive_integer_invalid_value_does_not_override_previous():
    """PositiveInteger: невалидное значение не перезаписывает старое."""
    class C:
        p = PositiveInteger()

    c = C()
    c.p = 10

    with pytest.raises(ValueError):
        c.p = 0
    assert c.p == 10

    with pytest.raises(ValueError):
        c.p = -5
    assert c.p == 10

    with pytest.raises(TypeError):
        c.p = "oops"
    assert c.p == 10


def test_storage_is_per_instance():
    """Хранение значений идёт отдельно для каждого экземпляра."""
    class C:
        a = Integer()

    c1, c2 = C(), C()
    c1.a = 1
    c2.a = 2
    assert c1.a == 1 and c2.a == 2


def test_unset_returns_none():
    """Неприсвоенный дескриптор возвращает None при чтении."""
    class C:
        a = Integer()

    c = C()
    assert c.a is None


def test_data_fields_can_change_to_valid_values():
    """Поля Data можно менять на другие валидные значения."""
    d = Data(1, "Apple", 10)

    d.num = 2
    d.name = "Banana"
    d.price = 20

    assert d.num == 2
    assert d.name == "Banana"
    assert d.price == 20


def test_data_invalid_assignment_does_not_change_value():
    """Попытка записать невалидное значение не меняет фактическое."""
    d = Data(1, "Apple", 10)

    with pytest.raises(TypeError):
        d.num = "not-int"
    assert d.num == 1

    with pytest.raises(ValueError):
        d.name = ""
    assert d.name == "Apple"

    with pytest.raises(ValueError):
        d.price = 0
    assert d.price == 10


@pytest.mark.parametrize(
    "num, name, price, exc_type",
    [
        pytest.param("1", "Apple", 10, TypeError, id="num"),
        pytest.param(1, "", 10, ValueError, id="name"),
        pytest.param(1, "Apple", 0, ValueError, id="price"),
    ],
)
def test_data_invalid_in_init(num, name, price, exc_type):
    """Data валидирует типы и выбрасывает исключения."""
    with pytest.raises(exc_type):
        Data(num, name, price)


def test_descriptor_access_via_class():
    """Обращение к дескриптору через класс."""
    class C:
        a = Integer()

    assert isinstance(C.a, Integer)
