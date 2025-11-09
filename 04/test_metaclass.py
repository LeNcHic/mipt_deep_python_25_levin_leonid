"""Тесты для проверки поведения метакласса CustomMeta"""


from __future__ import annotations
import pytest
from metaclass import CustomMeta
# pylint: disable=no-member


class CustomClass(metaclass=CustomMeta):
    """Пример класса для тестирования работы метакласса."""
    x = 50

    def __init__(self, val=99):
        self.val = val

    def line(self):
        """line"""
        return 100

    def __str__(self):
        return "Custom_by_metaclass"


def test_class_attributes_prefixed():
    """Проверка: атрибуты класса доступны только с префиксом custom_."""
    assert CustomClass.custom_x == 50
    with pytest.raises(AttributeError):
        _ = CustomClass.x


def test_instance_initial_and_methods():
    """Проверка: экземпляр имеет только атрибуты и методы с префиксом."""
    inst = CustomClass()
    assert inst.custom_x == 50
    assert inst.custom_val == 99
    assert inst.custom_line() == 100
    assert str(inst) == "Custom_by_metaclass"


@pytest.mark.parametrize("name", ["x", "val", "line", "yyy"])
def test_instance_forbid_unprefixed(name):
    """Доступ к неперефиксованным именам на экземпляре должен падать."""
    inst = CustomClass()
    with pytest.raises(AttributeError):
        _ = getattr(inst, name) if name != "line" else getattr(inst, name)()


def test_dynamic_attributes_are_prefixed():
    """Проверка: динамически добавленные атрибуты сохраняются с префиксом."""
    inst = CustomClass()
    # pylint: disable=attribute-defined-outside-init
    inst.dynamic = "added later"
    assert inst.custom_dynamic == "added later"
    with pytest.raises(AttributeError):
        _ = inst.dynamic


def test_class_level_setattr_is_prefixed():
    """Проверка: при установке атрибутов на уровне
       класса они тоже получают префикс."""
    # pylint: disable=attribute-defined-outside-init
    CustomClass.new_attr = 123
    assert CustomClass.custom_new_attr == 123
    with pytest.raises(AttributeError):
        _ = CustomClass.new_attr


def test_instance_set_prefixed_keeps_single_prefix():
    """Проверка: если имя уже имеет префикс, новый префикс не добавляется."""
    inst = CustomClass()
    inst.custom_foo = 1  # pylint: disable=attribute-defined-outside-init
    assert inst.custom_foo == 1
    assert not hasattr(inst, "custom_custom_foo")


def test_class_delattr_prefixed():
    """Проверка: удаление по непрефиксованному имени
       удаляет префиксованный атрибут."""
    CustomClass.tmp = 7  # pylint: disable=attribute-defined-outside-init
    assert CustomClass.custom_tmp == 7
    del CustomClass.tmp
    assert not hasattr(CustomClass, "custom_tmp")


def test_instance_delattr_prefixed():
    """Проверка: удаление атрибута экземпляра удаляет
       и его префиксованный вариант."""
    inst = CustomClass()
    # pylint: disable=attribute-defined-outside-init
    inst.aaa = 1
    del inst.aaa
    with pytest.raises(AttributeError):
        _ = inst.custom_aaa
