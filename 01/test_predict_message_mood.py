"""Тесты для predict_message_mood"""


import predict_message_mood as pm


class DummyModel:
    """Простейшая модель для подмены SomeModel в тестах."""
    def __init__(self, return_value: float):
        self._return_value = return_value
        self.seen_messages: list[str] = []

    def predict(self, message: str) -> float:
        self.seen_messages.append(message)
        return self._return_value


def _patch_model(monkeypatch, return_value: float) -> DummyModel:
    """Подменяем SomeModel в модуле predict_message_mood на DummyModel."""
    dummy = DummyModel(return_value)

    def factory() -> DummyModel:
        return dummy

    monkeypatch.setattr(pm, "SomeModel", factory)
    return dummy


def test_returns_bad_when_below_bad_threshold(monkeypatch):
    dummy = _patch_model(monkeypatch, return_value=0.1)
    msg = "short"
    result = pm.predict_message_mood(msg, bad_thresholds=0.3, good_thresholds=0.8)
    assert result == "неуд"
    assert dummy.seen_messages == [msg]


def test_returns_best_when_above_good_threshold(monkeypatch):
    dummy = _patch_model(monkeypatch, return_value=0.95)
    msg = "some message"
    result = pm.predict_message_mood(msg, bad_thresholds=0.3, good_thresholds=0.8)
    assert result == "отл"
    assert dummy.seen_messages == [msg]


def test_returns_norm_between_thresholds(monkeypatch):
    dummy = _patch_model(monkeypatch, return_value=0.5)
    result = pm.predict_message_mood("msg", bad_thresholds=0.3, good_thresholds=0.8)
    assert result == "норм"
    assert dummy.seen_messages == ["msg"]


def test_equal_to_bad_threshold_is_norm(monkeypatch):
    _patch_model(monkeypatch, return_value=0.3)
    result = pm.predict_message_mood("msg", bad_thresholds=0.3, good_thresholds=0.8)
    assert result == "норм"


def test_equal_to_good_threshold_is_norm(monkeypatch):
    _patch_model(monkeypatch, return_value=0.8)
    result = pm.predict_message_mood("msg", bad_thresholds=0.3, good_thresholds=0.8)
    assert result == "норм"


def test_custom_thresholds(monkeypatch):
    """Проверяем вызов с другими порогами."""
    _patch_model(monkeypatch, return_value=0.9)

    result = pm.predict_message_mood(
        "Чапаев и пустота",
        bad_thresholds=0.8,
        good_thresholds=0.99,
    )
    assert result == "норм"
