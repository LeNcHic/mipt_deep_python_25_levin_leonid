"""LRU-кэш с логированием операций."""


# pylint: disable=duplicate-code
from __future__ import annotations

import logging

LOGGER = logging.getLogger("cache")


class _Node:   # pylint: disable=too-few-public-methods
    """Узел двухсвязного списка."""
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """LRU-кэш"""
    def __init__(self, limit=42):
        if limit <= 0:
            raise ValueError("limit must be positive")

        self.limit = limit
        self._nodes: dict[object, _Node] = {}
        self._head: _Node | None = None
        self._tail: _Node | None = None

        LOGGER.debug("создан LRUCache с лимитом %s", limit)

    def get(self, key):
        """Возвращает значение по ключу или None."""
        node = self._nodes.get(key)
        if node is None:
            LOGGER.warning("get промах по ключу %r", key)
            return None

        self._move_to_head(node)
        LOGGER.info("get успех для ключа %r со значением %r", key, node.value)
        LOGGER.debug("после get состояние кэша: %s", self._debug_state())
        return node.value

    def set(self, key, value):
        """Сохраняет значение по ключу с учётом LRU."""
        node = self._nodes.get(key)

        if node is not None:
            node.value = value
            self._move_to_head(node)
            LOGGER.info("set обновление ключа %r", key)
            LOGGER.debug("после обновления состояние кэша: %s",
                         self._debug_state())
            return

        node = _Node(key, value)
        self._nodes[key] = node
        self._add_to_head(node)
        LOGGER.info("set новый ключ %r со значением %r", key, value)

        if len(self._nodes) > self.limit:
            self._evict_tail()

        LOGGER.debug("после вставки состояние кэша: %s", self._debug_state())

    def _add_to_head(self, node: _Node) -> None:
        node.prev = None
        node.next = self._head

        if self._head is not None:
            self._head.prev = node
        self._head = node

        if self._tail is None:
            self._tail = node

    def _remove_node(self, node: _Node) -> None:
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self._head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self._tail = node.prev

        node.prev = None
        node.next = None

    def _move_to_head(self, node: _Node) -> None:
        if node is self._head:
            return
        self._remove_node(node)
        self._add_to_head(node)

    def _evict_tail(self) -> None:
        """Удаляет самый старый элемент при переполнении."""
        if self._tail is None:
            return

        old = self._tail
        self._remove_node(old)
        self._nodes.pop(old.key, None)
        LOGGER.info(
            "set вытеснение: удалён ключ %r со значением %r",
            old.key,
            old.value,
        )

    def _debug_state(self):
        """Получаем состояние кэша от самого свежего к самому старому."""
        result = []
        current = self._head
        while current is not None:
            result.append((current.key, current.value))
            current = current.next
        return result

    def __repr__(self):
        return f"LRUCache(limit={self.limit}, state={self._debug_state()})"
