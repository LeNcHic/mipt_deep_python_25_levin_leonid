"""Метакласс"""


from __future__ import annotations
from typing import Any, Dict

_PREFIX = "custom_"


def _is_magic(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _prefixed(name: str) -> str:
    if _is_magic(name) or name.startswith(_PREFIX):
        return name
    return f"{_PREFIX}{name}"


class CustomMeta(type):
    """Метакласс, который добавляет префикс 'custom_'
       ко всем немагическим атрибутам и методам."""
    def __setattr__(cls, name: str, value: Any) -> None:
        super().__setattr__(_prefixed(name), value)

    def __delattr__(cls, name: str) -> None:
        super().__delattr__(_prefixed(name))

    def __new__(mcs, name: str, bases: tuple[type, ...],
                namespace: Dict[str, Any], **kwargs: Any):
        new_ns: Dict[str, Any] = {}
        for key, val in namespace.items():
            if key in ("__module__", "__qualname__"):
                new_ns[key] = val
                continue
            new_ns[_prefixed(key)] = val

        if "__setattr__" not in namespace:
            def __setattr__(self, key: str, value: Any) -> None:
                object.__setattr__(self, _prefixed(key), value)
            new_ns["__setattr__"] = __setattr__

        if "__delattr__" not in namespace:
            def __delattr__(self, key: str) -> None:
                object.__delattr__(self, _prefixed(key))
            new_ns["__delattr__"] = __delattr__

        if "__getattribute__" not in namespace:
            def __getattribute__(self, key: str) -> Any:
                if _is_magic(key) or key.startswith(_PREFIX):
                    return object.__getattribute__(self, key)
                raise AttributeError(f"{type(self).__name__!s} no {key!r}")
            new_ns["__getattribute__"] = __getattribute__

        return super().__new__(mcs, name, bases, new_ns, **kwargs)
