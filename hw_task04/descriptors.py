"""Дескрипторы для валидации полей: int/str/positive-int."""


from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class BaseField(ABC):
    """Базовый дескриптор, который хранит значение
       в __dict__ под приватным ключом."""

    def __init__(self) -> None:
        self._storage_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._storage_name = f"_{owner.__name__}__{name}"

    def __get__(self, obj: Any, owner: type | None = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__.get(self._storage_name)

    def __set__(self, obj: Any, value: Any) -> None:
        value = self.validate(value)
        obj.__dict__[self._storage_name] = value

    @abstractmethod
    def validate(self, value: Any) -> Any:
        """Должен либо вернуть нормализованное значение,
           либо бросить исключение."""


class Integer(BaseField):  # pylint: disable=too-few-public-methods
    """Поле: строго int."""
    def validate(self, value: Any) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("field requires int")
        return value


class String(BaseField):  # pylint: disable=too-few-public-methods
    """Поле: str с ограничениями по длине."""
    def __init__(self, *, min_len: int = 0,
                 max_len: int | None = None) -> None:
        super().__init__()
        self.min_len = min_len
        self.max_len = max_len

    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("field requires str")
        if len(value) < self.min_len:
            raise ValueError(f"length must be >= {self.min_len}")
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(f"length must be <= {self.max_len}")
        return value


class PositiveInteger(Integer):  # pylint: disable=too-few-public-methods
    """Поле: положительный int (> 0)."""
    def validate(self, value: Any) -> int:
        ivalue = super().validate(value)
        if ivalue <= 0:
            raise ValueError("must be > 0")
        return ivalue


class Data:  # pylint: disable=too-few-public-methods
    """Обьединение классов"""
    num = Integer()
    name = String(min_len=1)
    price = PositiveInteger()

    def __init__(self, num: int, name: str, price: int) -> None:
        self.num = num
        self.name = name
        self.price = price
