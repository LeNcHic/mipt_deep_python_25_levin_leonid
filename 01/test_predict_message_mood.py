"""Тесты для predict_message_mood"""


from predict_message_mood import predict_message_mood


def test_returns_best():
    """Тест на отл"""
    assert predict_message_mood("Чапаев и пустота") == "отл"


def test_returns_norm():
    """Тест на норм"""
    assert predict_message_mood(
        "Чапаев и пустота",
        bad_thresholds=0.8,
        good_thresholds=0.99,
    ) == "норм"


def test_returns_bad():
    """Тест на неуд"""
    assert predict_message_mood("Вулкан") == "неуд"
