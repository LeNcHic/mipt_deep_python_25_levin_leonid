"""LRU-кэш"""


class _Node:  # pylint: disable=too-few-public-methods
    """Узел двусвязного списка."""
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
        self._nodes = {}
        self._head = None
        self._tail = None

    def get(self, key):
        """Возвращает значение по ключу или None."""
        node = self._nodes.get(key)
        if node is None:
            return None

        self._move_to_head(node)
        return node.value

    def set(self, key, value):
        """Сохраняет значение по ключу с учётом LRU."""
        node = self._nodes.get(key)

        if node is not None:
            node.value = value
            self._move_to_head(node)
            return

        node = _Node(key, value)
        self._nodes[key] = node
        self._add_to_head(node)

        if len(self._nodes) > self.limit:
            self._evict_tail()

    def _add_to_head(self, node):
        node.prev = None
        node.next = self._head

        if self._head is not None:
            self._head.prev = node
        self._head = node

        if self._tail is None:
            self._tail = node

    def _remove_node(self, node):
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

    def _move_to_head(self, node):
        if node is self._head:
            return
        self._remove_node(node)
        self._add_to_head(node)

    def _evict_tail(self):
        """Удаляет самый старый элемент при переполнении."""
        if self._tail is None:
            return
        old = self._tail
        self._remove_node(old)
        self._nodes.pop(old.key, None)
