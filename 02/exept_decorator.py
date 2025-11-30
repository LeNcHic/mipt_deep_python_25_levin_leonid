"""Декоратор обработки исключений"""


from __future__ import annotations
from functools import wraps
from typing import Any, Callable, Iterable


def _build_log_message(
    name: str,
    attempt: int,
    details: dict[str, Any],
) -> str:
    """Собираем строку лога в одном месте."""
    parts: list[str] = [f'run "{name}"']

    args = details.get("args")
    kwargs = details.get("kwargs")
    if args:
        parts.append(f"with positional args = {args}")
    if kwargs:
        parts.append(f"keyword kwargs = {kwargs}")

    parts.append(f"attempt = {attempt}")

    exc = details.get("exception")
    if exc is not None:
        parts.append(f"exception = {type(exc).__name__}")
    else:
        parts.append(f"result = {details.get('result')!r}")

    return ", ".join(parts)


def retry_deco(
    retries: int = 1,
    expected_exceptions: Iterable[type[BaseException]] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор, повторяющий вызов функции при исключениях."""
    if retries < 1:
        raise ValueError("retries must be >= 1")
    allowed_exceptions: tuple[type[BaseException], ...] = (
        tuple(expected_exceptions) if expected_exceptions is not None else ()
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            name = func.__name__
            # pylint: disable=broad-exception-caught
            for attempt in range(1, retries + 1):
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    if isinstance(exc, allowed_exceptions):
                        print(
                            _build_log_message(
                                name,
                                attempt,
                                {
                                    "args": args,
                                    "kwargs": kwargs,
                                    "exception": exc,
                                },
                            )
                        )
                        raise exc

                    print(
                        _build_log_message(
                            name,
                            attempt,
                            {
                                "args": args,
                                "kwargs": kwargs,
                                "exception": exc,
                            },
                        )
                    )
                    if attempt == retries:
                        raise exc
                    continue

                print(
                    _build_log_message(
                        name,
                        attempt,
                        {
                            "args": args,
                            "kwargs": kwargs,
                            "result": result,
                        },
                    )
                )
                return result

        return wrapper

    return decorator
