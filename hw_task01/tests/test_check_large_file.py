"""Тесты для проверки файла"""


from hw_task01.check_large_file import check_file

BANWORDS = ["unlike", "dislike", "skip", "spam"]
KEYWORDS = ["like", "listen", "favorite"]


def test_check_file():
    """Поиск бан-слов и key-слов"""
    result = check_file("hw_task01/tests/check_file.txt", BANWORDS, KEYWORDS)

    assert result == [
        "I really like this song",
        "I listen to this music often",
        "This is my favorite album",
        "I would like to listen more",
    ]
