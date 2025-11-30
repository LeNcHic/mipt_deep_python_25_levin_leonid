"""Классификатор оценки строки."""


from typing import Final


class SomeModel:  # pylint: disable=R0903
    """Класс - предсказатель оценки."""

    def predict(self, message: str) -> float:
        """Примитивный порог оценки строки."""
        return 0.9 if len(message) >= 10 else 0.2


def predict_message_mood(
    message: str,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> str:
    """Возвращаем неуд/норм/отл в зависимости от предсказания модели."""
    model: Final[SomeModel] = SomeModel()
    score = model.predict(message)

    if score < bad_thresholds:
        return "неуд"
    if score > good_thresholds:
        return "отл"
    return "норм"

