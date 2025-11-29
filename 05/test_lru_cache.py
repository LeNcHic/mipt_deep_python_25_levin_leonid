"""Тесты для реализации LRUCache"""

import pytest
from lru_cache import LRUCache


def test_basic_example_from_task() -> None:
    """Пример из условия"""
    cache = LRUCache(2)

    cache.set("k1", "val1")
    cache.set("k2", "val2")

    assert cache.get("k3") is None
    assert cache.get("k2") == "val2"
    assert cache.get("k1") == "val1"

    cache.set("k3", "val3")

    assert cache.get("k3") == "val3"
    assert cache.get("k2") is None
    assert cache.get("k1") == "val1"


def test_get_returns_none_for_missing_key() -> None:
    """Проверка, что при отсутствии ключа get возвращает None."""
    cache = LRUCache(3)

    assert cache.get("missing") is None

    cache.set("a", 1)
    assert cache.get("other") is None


def test_update_existing_key_does_not_increase_size() -> None:
    """Проверяем, что обновление ключа не должно вести к вытеснению."""
    cache = LRUCache(2)

    cache.set("k1", "v1")
    cache.set("k2", "v2")

    cache.set("k1", "v1-upd")

    cache.set("k3", "v3")

    assert cache.get("k1") == "v1-upd"
    assert cache.get("k2") is None
    assert cache.get("k3") == "v3"


def test_lru_eviction_order_depends_on_recent_get() -> None:
    """Проверка, что новых не выкидываем при следующем set."""
    cache = LRUCache(2)

    cache.set("a", 1)
    cache.set("b", 2)

    assert cache.get("a") == 1
    cache.set("c", 3)

    assert cache.get("a") == 1
    assert cache.get("b") is None
    assert cache.get("c") == 3


def test_limit_must_be_positive() -> None:
    """Проверка, что лимит не может быть нулевым или отрицательным."""
    with pytest.raises(ValueError):
        LRUCache(0)

    with pytest.raises(ValueError):
        LRUCache(-1)


def test_limit_one_eviction() -> None:
    """Проверка, что при лимите 1 каждый новый ключ вытесняет предыдущий."""
    cache = LRUCache(1)

    cache.set("a", "va")
    assert cache.get("a") == "va"

    cache.set("b", "vb")
    assert cache.get("a") is None
    assert cache.get("b") == "vb"

    cache.set("b", "vb-new")
    assert cache.get("b") == "vb-new"


def test_many_inserts_more_than_limit() -> None:
    """Проверка, что после множества вставок остаются
       только последние limit ключей."""
    limit = 3
    cache = LRUCache(limit)

    for i in range(10):
        cache.set(f"k{i}", i)

    for i in range(7):
        assert cache.get(f"k{i}") is None

    assert cache.get("k7") == 7
    assert cache.get("k8") == 8
    assert cache.get("k9") == 9


def test_get_does_not_create_key() -> None:
    """Проверка на то, что промах по get не создаёт новые записи в кэше"""
    cache = LRUCache(2)

    assert cache.get("missing") is None
    cache.set("a", 1)
    cache.set("b", 2)

    assert cache.get("missing") is None
    assert cache.get("a") == 1
    assert cache.get("b") == 2
