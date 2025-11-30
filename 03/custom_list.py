"""Расширенный список с арифметическими операциями и сравнением по сумме."""


from __future__ import annotations
from typing import Callable, Iterable, List
import operator


def _elementwise(
    left: Iterable[int],
    right: Iterable[int],
    op: Callable[[int, int], int],
) -> List[int]:
    """Применим операцию or к двум последовательностям поэлементно."""
    left_list = list(left)
    right_list = list(right)

    max_len = max(len(left_list), len(right_list))
    result: List[int] = []

    for index in range(max_len):
        lhs = left_list[index] if index < len(left_list) else 0
        rhs = right_list[index] if index < len(right_list) else 0
        result.append(op(lhs, rhs))

    return result


class CustomList(list[int]):
    """Список целых чисел с расширенной арифметикой и сравнением по сумме."""
    @staticmethod
    def _as_sequence(value: object, length: int) -> List[int] | None:
        """Преобразуем value в последовательность целых чисел."""
        if isinstance(value, CustomList):
            return list(value)
        if isinstance(value, list):
            return list(value)
        if isinstance(value, int):
            return [value] * length
        return None

    def _binary_operation(
        self,
        other: object,
        op: Callable[[int, int], int],
        *,
        reverse: bool = False,
    ) -> CustomList | NotImplemented:
        """Общая реализация для операций сложения и вычитания."""
        if reverse:
            left_values = self._as_sequence(other, len(self))
            right_values: List[int] = list(self)
        else:
            left_values = list(self)
            right_values = self._as_sequence(other, len(self))

        if left_values is None or right_values is None:
            return NotImplemented

        return CustomList(_elementwise(left_values, right_values, op))

    def __add__(self, other: object) -> CustomList | NotImplemented:
        return self._binary_operation(other, operator.add)

    def __radd__(self, other: object) -> CustomList | NotImplemented:
        return self._binary_operation(other, operator.add, reverse=True)

    def __sub__(self, other: object) -> CustomList | NotImplemented:
        return self._binary_operation(other, operator.sub)

    def __rsub__(self, other: object) -> CustomList | NotImplemented:
        return self._binary_operation(other, operator.sub, reverse=True)

    @staticmethod
    def _coerce_other_for_compare(other: object) -> CustomList | None:
        """Возвращает other, если CustomList."""
        if isinstance(other, CustomList):
            return other
        return None

    def _sum(self) -> int:
        """Возвращает сумму элементов списка как int."""
        return int(sum(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomList):
            return NotImplemented
        return self._sum() == other._sum()

    def __ne__(self, other: object) -> bool:
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

    def __lt__(self, other: object) -> bool:
        other_list = self._coerce_other_for_compare(other)
        if other_list is None:
            return NotImplemented
        return self._sum() < other_list._sum()

    def __le__(self, other: object) -> bool:
        other_list = self._coerce_other_for_compare(other)
        if other_list is None:
            return NotImplemented
        return self._sum() <= other_list._sum()

    def __gt__(self, other: object) -> bool:
        other_list = self._coerce_other_for_compare(other)
        if other_list is None:
            return NotImplemented
        return self._sum() > other_list._sum()

    def __ge__(self, other: object) -> bool:
        other_list = self._coerce_other_for_compare(other)
        if other_list is None:
            return NotImplemented
        return self._sum() >= other_list._sum()

    def __str__(self) -> str:
        return f"CustomList({list(self)}), sum: {self._sum()}"

    def __repr__(self) -> str:
        return f"CustomList({list(self)!r})"
