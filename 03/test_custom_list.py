"""Тесты для класса CustomList с проверкой арифметики и сравнений."""


from __future__ import annotations
from typing import Any
import pytest
from custom_list import CustomList


def test_list_inheritance() -> None:
    """CustomList должен наследоваться от list."""
    assert isinstance(CustomList(), list)


def test_not_implemented() -> None:
    """Операции с неподдерживаемыми типами должны давать TypeError."""
    foreign: Any = object()

    with pytest.raises(TypeError):
        _ = CustomList() + foreign
    with pytest.raises(TypeError):
        _ = foreign + CustomList()
    with pytest.raises(TypeError):
        _ = CustomList() - foreign
    with pytest.raises(TypeError):
        _ = foreign - CustomList()
    with pytest.raises(TypeError):
        _ = CustomList() < foreign
    with pytest.raises(TypeError):
        _ = CustomList() <= foreign
    with pytest.raises(TypeError):
        _ = CustomList() > foreign
    with pytest.raises(TypeError):
        _ = CustomList() >= foreign


def test_operands_immutability() -> None:
    """Арифметические операции не должны изменять операнды."""
    operands: list[Any] = [
        CustomList([9, 8, 7, 6]),
        [100, -5],
        42,
    ]

    for left_index, left in enumerate(operands):
        for right_index, right in enumerate(operands):
            if not isinstance(left, CustomList) and not isinstance(
                right,
                CustomList,
            ):
                continue

            first_before = list(operands[0])
            second_before = list(operands[1])
            third_before = operands[2]

            try:
                _ = left + right
            except TypeError:
                pass

            assert list(operands[0]) == first_before
            assert list(operands[1]) == second_before
            assert operands[2] == third_before

            try:
                _ = left - right
            except TypeError:
                pass

            assert list(operands[0]) == first_before
            assert list(operands[1]) == second_before
            assert operands[2] == third_before
            assert left_index in (0, 1, 2)
            assert right_index in (0, 1, 2)


@pytest.mark.parametrize(
    ("lhs", "rhs", "res"),
    [
        # CustomList + CustomList, одинаковая длина
        (CustomList([2, 3]), CustomList([4, 1]), CustomList([6, 4])),
        # CustomList + CustomList, левый длиннее
        (CustomList([5, 0, -2]), CustomList([7]), CustomList([12, 0, -2])),
        # CustomList + CustomList, правый длиннее
        (CustomList([9]), CustomList([1, -1, 3]), CustomList([10, -1, 3])),
        # CustomList + CustomList, работа с пустым
        (CustomList([]), CustomList([4, -1]), CustomList([4, -1])),
        (CustomList([4, -1]), CustomList([]), CustomList([4, -1])),
        # CustomList + list
        (CustomList([3, 3]), [10, -2], CustomList([13, 1])),
        (CustomList([-1, 4, 5]), [2], CustomList([1, 4, 5])),
        (CustomList([7]), [1, 1, 1], CustomList([8, 1, 1])),
        # CustomList + int
        (CustomList([2, -3]), 5, CustomList([7, 2])),
        (CustomList([10, 0, -10]), -2, CustomList([8, -2, -12])),
        (CustomList([]), 7, CustomList([])),
        # list + CustomList
        ([5, 5], CustomList([1]), CustomList([6, 5])),
        ([0], CustomList([2, 2, 2]), CustomList([2, 2, 2])),
        # int + CustomList
        (100, CustomList([1, -1]), CustomList([101, 99])),
    ],
)
def test_add(lhs: object, rhs: object, res: CustomList) -> None:
    """Проверяет поэлементное сложение для разных комбинаций типов."""
    lhs_copy = list(lhs) if isinstance(lhs, (list, CustomList)) else lhs
    rhs_copy = list(rhs) if isinstance(rhs, (list, CustomList)) else rhs

    result = lhs + rhs

    assert isinstance(result, CustomList)
    assert list(result) == list(res)

    if isinstance(lhs, (list, CustomList)):
        assert list(lhs) == list(lhs_copy)
    if isinstance(rhs, (list, CustomList)):
        assert list(rhs) == list(rhs_copy)


@pytest.mark.parametrize(
    ("lhs", "rhs", "res"),
    [
        # CustomList - CustomList, одинаковая длина
        (CustomList([5, 1]), CustomList([2, -3]), CustomList([3, 4])),
        # CustomList - CustomList, левый длиннее
        (CustomList([4, 4, 4]), CustomList([1]), CustomList([3, 4, 4])),
        # CustomList - CustomList, правый длиннее
        (CustomList([7]), CustomList([2, 2, 2]), CustomList([5, -2, -2])),
        # CustomList - CustomList, работа с пустым
        (CustomList([]), CustomList([3, 3]), CustomList([-3, -3])),
        (CustomList([3, 3]), CustomList([]), CustomList([3, 3])),
        # CustomList - list
        (CustomList([10, 0]), [3, 7], CustomList([7, -7])),
        (CustomList([-2, -2, -2]), [1], CustomList([-3, -2, -2])),
        (CustomList([1]), [1, 2, 3], CustomList([0, -2, -3])),
        # CustomList - int
        (CustomList([2, 3]), 1, CustomList([1, 2])),
        (CustomList([0, 0, 0]), -5, CustomList([5, 5, 5])),
        (CustomList([]), 9, CustomList([])),
        # list - CustomList
        ([8, 1], CustomList([3]), CustomList([5, 1])),
        ([0], CustomList([1, -1, 2]), CustomList([-1, 1, -2])),
        # int - CustomList
        (10, CustomList([3, 4]), CustomList([7, 6])),
    ],
)
def test_sub(lhs: object, rhs: object, res: CustomList) -> None:
    """Проверяет поэлементное вычитание для разных комбинаций типов."""
    lhs_copy = list(lhs) if isinstance(lhs, (list, CustomList)) else lhs
    rhs_copy = list(rhs) if isinstance(rhs, (list, CustomList)) else rhs

    result = lhs - rhs

    assert isinstance(result, CustomList)
    assert list(result) == list(res)

    if isinstance(lhs, (list, CustomList)):
        assert list(lhs) == list(lhs_copy)
    if isinstance(rhs, (list, CustomList)):
        assert list(rhs) == list(rhs_copy)


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CustomList([2, 2]), CustomList([1, 3])),
        (CustomList([10]), CustomList([4, 6])),
        (CustomList([0, 0, 0]), CustomList([])),
        (CustomList([-1, 2]), CustomList([3, -2])),
    ],
)
def test_eq(lhs: CustomList, rhs: CustomList) -> None:
    """Проверяет равенство списков по сумме элементов."""
    assert lhs == rhs
    assert not lhs != rhs


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CustomList([2, 2]), CustomList([1, 2])),
        (CustomList([10]), CustomList([4, 7])),
        (CustomList([1]), CustomList([])),
        (CustomList([-1, 2]), CustomList([3, -1])),
    ],
)
def test_ne(lhs: CustomList, rhs: CustomList) -> None:
    """Проверяет неравенство списков по сумме элементов."""
    assert lhs != rhs
    assert not lhs == rhs


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CustomList([1]), CustomList([2])),
        (CustomList([1, 1]), CustomList([3])),
        (CustomList([-5]), CustomList([0])),
        (CustomList([]), CustomList([1])),
    ],
)
def test_lt(lhs: CustomList, rhs: CustomList) -> None:
    """Проверяет операцию < по сумме элементов."""
    assert lhs < rhs
    assert not lhs >= rhs


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CustomList([1]), CustomList([2])),
        (CustomList([1, 1]), CustomList([2])),
        (CustomList([-5]), CustomList([-5])),
        (CustomList([]), CustomList([])),
    ],
)
def test_le(lhs: CustomList, rhs: CustomList) -> None:
    """Проверяет операцию <= по сумме элементов."""
    assert lhs <= rhs
    assert not lhs > rhs


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CustomList([5]), CustomList([1])),
        (CustomList([1, 2]), CustomList([2])),
        (CustomList([0]), CustomList([-1])),
        (CustomList([1]), CustomList([])),
    ],
)
def test_gt(lhs: CustomList, rhs: CustomList) -> None:
    """Проверяет операцию > по сумме элементов."""
    assert lhs > rhs
    assert not lhs <= rhs


@pytest.mark.parametrize(
    ("lhs", "rhs"),
    [
        (CustomList([5]), CustomList([1])),
        (CustomList([1, 2]), CustomList([3])),
        (CustomList([0]), CustomList([0])),
        (CustomList([]), CustomList([])),
    ],
)
def test_ge(lhs: CustomList, rhs: CustomList) -> None:
    """Проверяет операцию >= по сумме элементов."""
    assert lhs >= rhs
    assert not lhs < rhs


def test_str_representation() -> None:
    """Проверяет формат строкового представления CustomList."""
    value = CustomList([2, 5, 0])
    assert str(value) == "CustomList([2, 5, 0]), sum: 7"
