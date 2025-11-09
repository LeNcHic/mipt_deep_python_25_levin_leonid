"""
Тесты
"""

import os
import socket
import subprocess
import sys
import threading
import time
from contextlib import closing
from http.server import HTTPServer, BaseHTTPRequestHandler
from collections import Counter
from pathlib import Path
import contextlib
import json
import re
import ast
from client import load_urls
import pytest


# pylint: disable=redefined-outer-name
def _find_free_port() -> int:
    """Находит свободный порт"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def parse_client_output(text: str):
    """Парсит вывод клиента 'url: {json}'"""
    results = []
    for line in text.strip().splitlines():
        if not line.strip():
            continue
        url, js = line.split(": ", 1)
        results.append((url.strip(), ast.literal_eval(js.strip())))
    return results


def expected_top3(text: str):
    """Счетчик слов"""
    words = re.findall(r"[a-zа-я0-9_]+", text.lower())
    return dict(Counter(words).most_common(3))


class _TestHandler(BaseHTTPRequestHandler):
    """Пример страницы"""
    PAGES = {
        "/a": "spam spam spam eggs eggs bacon",
        "/b": "bacon bacon spam sausage sausage sausage",
        "/c": "lorem ipsum ipsum dolor dolor dolor",
    }

    def do_GET(self):  # pylint: disable=invalid-name
        """Даем текст страницы"""
        body = self.PAGES.get(self.path, "notfound").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args, **_kwargs):
        return


@pytest.fixture(scope="session")
def http_srv():
    """Поднимаем сервер"""
    port = _find_free_port()
    httpd = HTTPServer(("127.0.0.1", port), _TestHandler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()
    t.join(timeout=2)


@pytest.fixture(scope="session")
def tcp_srv(tmp_path_factory):
    """Запускаем TCP"""
    port = _find_free_port()
    logdir = tmp_path_factory.mktemp("logs")
    logf = logdir / "server.log"

    cmd = [sys.executable, "server.py", "-w", "4", "-k", "3", "-p", str(port)]

    SERVER_PATH = Path(__file__).with_name("server.py")
    log_file = open(logf, "w", encoding="utf-8")  # pylint: disable=consider-using-with
    cmd = [sys.executable, str(SERVER_PATH), "-w", "4", "-k", "3", "-p", str(port)]
    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        env=os.environ.copy(),
    )

    deadline = time.time() + 5
    ok = False
    while time.time() < deadline:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.settimeout(0.2)
                s.connect(("127.0.0.1", port))
                ok = True
                break
            except OSError:
                time.sleep(0.1)

    if not ok:
        proc.kill()
        raise RuntimeError("server.py не запустился")

    yield {"port": port, "proc": proc, "log": logf}
    try:
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:  # pylint: disable=broad-exception-caught
        proc.kill()


@pytest.fixture()
def urls_file(http_srv, tmp_path):
    """Готовит файл c URL"""
    p = tmp_path / "urls.txt"
    lines = [
        f"{http_srv}/a",
        f"{http_srv}/b",
        f"{http_srv}/c",
        f"{http_srv}/a",
        f"{http_srv}/b",
        f"{http_srv}/c",
    ]
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def run_client(urls_txt, tcp_srv, threads=3):
    """Запуск клиента"""
    cmd = [
        sys.executable,
        "client.py",
        str(threads),
        str(urls_txt),
        "--host",
        "127.0.0.1",
        "--port",
        str(tcp_srv["port"]),
    ]
    out = subprocess.check_output(cmd, text=True)
    return parse_client_output(out)


def reference_payloads(http_srv):
    """Проверка счетчика"""
    pages = {
        f"{http_srv}/a": "spam spam spam eggs eggs bacon",
        f"{http_srv}/b": "bacon bacon spam sausage sausage sausage",
        f"{http_srv}/c": "lorem ipsum ipsum dolor dolor dolor",
    }
    return {u: expected_top3(t) for u, t in pages.items()}


def assert_payload_eq(got: dict, want: dict):
    """Вспомогательный assert"""
    assert got == want, f"\nОжидали: {want}\nПолучили: {got}"


def test_one_url(tcp_srv, http_srv, tmp_path):
    """Тест: один URL - один ответ"""
    urls = tmp_path / "one.txt"
    urls.write_text(f"{http_srv}/a\n", encoding="utf-8")
    res = run_client(urls, tcp_srv, threads=1)
    assert len(res) == 1
    url, payload = res[0]
    want = reference_payloads(http_srv)[url]
    assert_payload_eq(payload, want)


def test_parallel_many(tcp_srv, http_srv, urls_file):
    """Тест несколько URL"""
    res = run_client(urls_file, tcp_srv, threads=5)
    assert len(res) == 6
    ref = reference_payloads(http_srv)
    for url, payload in res:
        assert url in ref
        assert_payload_eq(payload, ref[url])


def test_large_batch(tcp_srv, http_srv, tmp_path):
    """Тест на большое количество запросов"""
    urls = tmp_path / "urls_120.txt"
    base = [f"{http_srv}/a", f"{http_srv}/b", f"{http_srv}/c"]
    lines = base * 40
    urls.write_text("\n".join(lines), encoding="utf-8")
    res = run_client(urls, tcp_srv, threads=10)
    assert len(res) == 120
    ref = reference_payloads(http_srv)
    ok = sum(payload == ref[url] for url, payload in res)
    assert ok == 120


def test_parse_output_many_colons():
    """Тест парсера на корректную обрезку при наличии множества двоеточий"""
    sample = ('http://127.0.0.1:9999/a: '
              '{"a": 1, "b": {"c": 2, "d": [3, 4]}, "e:f": 5}\n')
    res = parse_client_output(sample)
    assert len(res) == 1
    url, payload = res[0]
    assert url == "http://127.0.0.1:9999/a"
    assert payload["a"] == 1 and payload["b"]["c"] == 2 and payload["e:f"] == 5


@pytest.mark.parametrize(
    "text, want",
    [
        ("SPAM spam eggs_2 eggs_2 123", {"spam": 2, "eggs_2": 2, "123": 1}),
        ("Привет, мир! spam SPAM", {"spam": 2, "привет": 1, "мир": 1}),
        ("a-b c.d e,f g;h", {"a": 1, "b": 1, "c": 1}),
    ],
)
def test_expected_top3_tokenization(text, want):
    """Тест на совпадение частот"""
    got = expected_top3(text)
    assert all(got.get(k) == v for k, v in want.items())


def test_client_load_urls_skips_blanks(tmp_path):
    """Тест на пропуск пустых строк и пробелов"""
    p = tmp_path / "u.txt"
    p.write_text("\n  \nhttp://a\n\nhttp://b  \n", encoding="utf-8")
    urls = load_urls(str(p))
    assert urls == ["http://a", "http://b"]


def test_server_error_response_on_invalid_url(tcp_srv):
    """Тест на корректную работу даже с неверным URL"""
    bad = "http://bad.invalid\n"
    with socket.create_connection(("127.0.0.1", tcp_srv["port"]),
                                  timeout=5) as s:
        s.sendall(bad.encode("utf-8"))
        s.shutdown(socket.SHUT_WR)
        data = s.makefile("r", encoding="utf-8").readline()
    resp = json.loads(data)
    assert "error" in resp and isinstance(resp["error"], str)


def test_end_to_end_duplicates_preserved_count(tcp_srv, http_srv, tmp_path):
    """Тест на проверку, того что при
       повторах URL число ответов равно числу входных"""
    urls = tmp_path / "dups.txt"
    lines = ([f"{http_srv}/a"] * 25 + [f"{http_srv}/b"] * 35 +
             [f"{http_srv}/c"] * 40)
    urls.write_text("\n".join(lines), encoding="utf-8")
    res = run_client(urls, tcp_srv, threads=8)
    assert len(res) == 100
    cnt = Counter(url for url, _ in res)
    assert cnt[f"{http_srv}/a"] == 25
    assert cnt[f"{http_srv}/b"] == 35
    assert cnt[f"{http_srv}/c"] == 40
    ref = reference_payloads(http_srv)
    assert all(payload == ref[url] for url, payload in res)


def test_server_handles_empty_line_gracefully(tcp_srv):
    """Тест на пустую строку как URL"""
    with socket.create_connection(("127.0.0.1", tcp_srv["port"]),
                                  timeout=5) as s:
        s.sendall(b"\n")
        s.shutdown(socket.SHUT_WR)
        data = s.makefile("r", encoding="utf-8").readline()
    resp = json.loads(data)
    assert resp == {"error": "Empty URL"}
