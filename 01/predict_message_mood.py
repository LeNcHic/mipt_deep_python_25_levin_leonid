"""Классификатор оценки строки"""


from typing import Final


class SomeModel:  # pylint: disable=R0903
    """Класс - предсказатель оценки"""

    def predict(self, message: str) -> float:
        """Примитивный порог оценки строки"""
        return 0.9 if len(message) >= 10 else 0.2


def predict_message_mood(
    message: str,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> str:
    """Оценим строку в рамках неуд/норм/отл"""
    model: Final[SomeModel] = SomeModel()
    flag = model.predict(message)
    if bad_thresholds <= flag <= good_thresholds:
        return "норм"
    if flag > good_thresholds:
        return "отл"
    return "неуд"
