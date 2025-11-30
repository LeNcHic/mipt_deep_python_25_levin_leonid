"""Тесты для проверки файла и генератора."""

from io import StringIO
from check_large_file import check_file

BANWORDS = ["unlike", "dislike", "skip", "spam"]
KEYWORDS = ["like", "listen", "favorite"]


def test_check_file_from_path():
    """Поиск бан-слов и key-слов по имени файла."""
    result = list(check_file("01/check_file.txt", BANWORDS, KEYWORDS))

    assert result == [
        "I really like this song",
        "I listen to this music often",
        "This is my favorite album",
        "I would like to listen more",
    ]


def test_check_file_from_file_object():
    """Проверка, что генератор умеет работать с файловым объектом."""
    data = "\n".join(
        [
            "I really like this song",
            "Please skip this track",
            "Spam message here",
        ]
    )
    file_obj = StringIO(data)
    result = list(check_file(file_obj, BANWORDS, KEYWORDS))
    assert result == ["I really like this song"]


def test_case_insensitive_and_full_word_match():
    """Проверка, что поиск не зависит от регистра
       и только по полному слову."""
    data = "\n".join(
        [
            "A LiKe song",
            "This is UNLIKE it",
            "favorite",
        ]
    )
    file_obj = StringIO(data)
    result = list(check_file(file_obj, BANWORDS, KEYWORDS))
    assert result == ["A LiKe song", "favorite"]


def test_line_with_ban_and_keyword_is_skipped():
    """Если в строке есть и keyword, и banword, то строка игнорируется."""
    data = "I really like spam\n"
    file_obj = StringIO(data)
    result = list(check_file(file_obj, BANWORDS, KEYWORDS))
    assert not result
