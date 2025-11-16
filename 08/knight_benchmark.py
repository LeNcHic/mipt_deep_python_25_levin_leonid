"""Профилирование по времени и памяти"""


import time
import weakref
import cProfile
import pstats
import tracemalloc
import gc


class KnightPlain:  # pylint: disable=too-few-public-methods
    """Обычный класс: атрибуты хранятся в __dict__."""
    def __init__(self, hp: int, damage: int, speed: int) -> None:
        self.hp = hp
        self.damage = damage
        self.speed = speed


class KnightSlots:  # pylint: disable=too-few-public-methods
    """Класс с __slots__."""
    __slots__ = ("hp", "damage", "speed")

    def __init__(self, hp: int, damage: int, speed: int) -> None:
        self.hp = hp
        self.damage = damage
        self.speed = speed


class KnightSlotsWeak:  # pylint: disable=too-few-public-methods
    """Класс с __slots__ + weakref."""
    __slots__ = ("hp", "damage", "speed", "__weakref__")

    def __init__(self, hp: int, damage: int, speed: int) -> None:
        self.hp = hp
        self.damage = damage
        self.speed = speed


def measure(func, *args, **kwargs):
    """Измеряем время работы функции и возвращаем результат"""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    t1 = time.perf_counter()
    return t1 - t0, result


def spawn_knights(cls, count: int):
    """Создаем список из рыцарей."""
    knights = []
    for i in range(count):
        knights.append(
            cls(
                hp=100 + i,
                damage=10 + (i % 5),
                speed=5 + (i % 3),
            )
        )
    return knights


def work_with_knights(knights):
    """Работаем с рыцарями."""
    total = 0
    for k in knights:
        total += k.hp + k.damage + k.speed
        k.hp -= 1
        k.speed += 1
    return total


def bench_class(label: str, cls, count: int) -> None:
    """Замер создания и работы с атрибутами для одного класса."""
    print(f"\n {label} (n={count}) ")

    t_create, knights = measure(spawn_knights, cls, count)
    print(f"Создание объектов: {t_create:.6f} с")

    t_touch, _ = measure(work_with_knights, knights)
    print(f"Чтение/изменение: {t_touch:.6f}")

    return knights


def bench_weakrefs(knights) -> None:
    """Замер создания слабых ссылок на рыцарей."""
    def build_refs():
        return [weakref.ref(k) for k in knights]

    t, refs = measure(build_refs)
    alive = sum(1 for r in refs if r() is not None)
    print(f"Слабые ссылки: {t:.6f} с (объектов: {alive})")


def bench_all_classes(count: int = 100_000) -> None:
    """Простой бенчмарк: время создания и
       доступа к атрибутам для всех классов."""
    classes = [
        ("KnightPlain", KnightPlain),
        ("KnightSlots", KnightSlots),
        ("KnightSlotsWeak", KnightSlotsWeak),
    ]

    for label, cls in classes:
        knights = bench_class(label, cls, count)
        if cls is KnightSlotsWeak:
            bench_weakrefs(knights)


def profile_calls_for_class(label: str, cls, count: int = 100_000) -> None:
    """Профилирование времени для одного варианта рыцаря."""
    print(f"\n=== Профилирование вызовов: {label} (n={count}) ===")

    gc.collect()
    profiler = cProfile.Profile()
    profiler.enable()

    knights = spawn_knights(cls, count)
    work_with_knights(knights)

    # для варианта с weakref можно заодно прогнать создание слабых ссылок
    if cls is KnightSlotsWeak:
        _ = [weakref.ref(k) for k in knights]

    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats(15)  # top-15 самых "тяжёлых" мест


def profile_calls_per_class(count: int = 100_000) -> None:
    """Сравнение профилей времени для всех классов по отдельности."""
    classes = [
        ("KnightPlain", KnightPlain),
        ("KnightSlots", KnightSlots),
        ("KnightSlotsWeak", KnightSlotsWeak),
    ]

    for label, cls in classes:
        profile_calls_for_class(label, cls, count)


def profile_memory_per_class(count: int = 500_000) -> None:
    """Сравнение памяти для каждого варианта рыцаря отдельно."""
    classes = [
        ("KnightPlain", KnightPlain),
        ("KnightSlots", KnightSlots),
        ("KnightSlotsWeak", KnightSlotsWeak),
    ]

    for label, cls in classes:
        gc.collect()
        tracemalloc.start()

        knights = spawn_knights(cls, count)
        work_with_knights(knights)

        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"\n=== Память: {label} (n={count}) ===")
        print(f"Пиковая память: {peak / 1024 / 1024:.2f} MiB")


if __name__ == "__main__":
    bench_all_classes(count=1_000_000)
    profile_calls_per_class(count=1_000_000)
    profile_memory_per_class(count=1_000_000)
