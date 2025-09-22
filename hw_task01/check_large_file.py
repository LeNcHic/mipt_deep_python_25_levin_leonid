"""Проверка файла на стоп-слова и поиск таргетных слов"""


def check_file(
    name_file: str,
    banwords: list[str],
    keywords: list[str],
) -> list[str]:
    """Вернёт список строк, где есть keyword и нет banword"""
    result = []
    with open(name_file, "r", encoding="utf-8") as f:
        for line in f:
            flag_banword = False
            flag_keyword = False
            # переводим строку в нижний регистр
            correct_line = line.strip().lower()
            # каждое слово строки теперь будет отдельным элементом массива
            # это упростит поиск нужных слов
            arr_correct_line = correct_line.split()
            for ban in banwords:
                if ban in arr_correct_line:
                    flag_banword = True
                    break
            for key in keywords:
                if key in arr_correct_line:
                    flag_keyword = True
                    break
            if not flag_banword and flag_keyword:
                result.append(line.strip())
    return result
