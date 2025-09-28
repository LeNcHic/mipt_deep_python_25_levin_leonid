"""Тесты для parse_json"""


from hw_task02.parser_json import process_json


def test_basic_example():
    """Тест из примера"""
    results = []
    json_str = '{"key1": "Word1 word2", "key2": "word2 word3"}'
    process_json(json_str, ["key1", "KEY2"], ["WORD1", "word2"],
                 lambda key, token: results.append((key, token)))
    assert results == [("key1", "WORD1"), ("key1", "word2")]


def test_no_matching_keys():
    """Тест без нужного ключа"""
    results = []
    json_str = '{"key1": "hello world"}'
    process_json(json_str, ["word"], ["hello"],
                 lambda key, token: results.append((key, token)))
    assert not results


def test_no_matching_tokens():
    """Тест без нужного токена"""
    results = []
    json_str = '{"key1": "hello world"}'
    process_json(json_str, ["key1"], ["python"],
                 lambda key, token: results.append((key, token)))
    assert not results


def test_multi_required():
    """Тест обширный"""
    results = []
    json_str = '{"a": "one    two", "b": "two    three"}'
    process_json(json_str, ["a", "b"], ["two"],
                 lambda key, token: results.append((key, token)))
    assert results == [("a", "two"), ("b", "two")]
