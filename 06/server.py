"""
Многопоточный master‑worker сервер для обработки URL‑ов.
Запускается через команду: python server.py -w 10 -k 7 -p 8000
Параметры:
    -w (количество воркеров)
    -k (топ частотных слов)
    -p (порт)
"""

import argparse
import json
import queue
import re
import socket
import threading
from collections import Counter
from typing import Dict

import requests
from bs4 import BeautifulSoup


def fetch_top_words(url: str, top_k: int) -> Dict[str, int]:
    """Скачивает страницу по URL и возвращает топ‑K
       частотных слов в виде словаря: {слово: частота}"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ")

        words = re.findall(r"\b\w+\b", text.lower())
        if not words:
            return {}
        counter = Counter(words)
        most_common = counter.most_common(top_k)
        return dict(most_common)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return {"error": str(exc)}


class Worker(threading.Thread):
    """Поток, который обрабатывает соединения из очереди"""
    def __init__(self, task_queue: queue.Queue, top_k: int,
                 stats: Dict[str, int],
                 stats_lock: threading.Lock, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.task_queue = task_queue
        self.top_k = top_k
        self.stats = stats
        self.stats_lock = stats_lock
        self.daemon = True

    # pylint: disable=broad-exception-caught
    def run(self) -> None:
        while True:
            try:
                conn, _ = self.task_queue.get()
            except Exception:
                continue
            try:
                self.handle_connection(conn)
            finally:
                self.task_queue.task_done()

    def handle_connection(self, conn: socket.socket) -> None:
        """Читает URL обрабатывает его и отправляет ответ"""
        try:
            conn.settimeout(10)
            data = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break
            url = data.decode().strip()
            if not url:
                result = {"error": "Empty URL"}
            else:
                result = fetch_top_words(url, self.top_k)
            response = json.dumps(result, ensure_ascii=False).encode() + b"\n"
            conn.sendall(response)
            try:
                conn.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        except Exception as exc:
            try:
                err_response = json.dumps({"error": str(exc)},
                                          ensure_ascii=False).encode() + b"\n"
                conn.sendall(err_response)
            except Exception:
                pass
        finally:
            conn.close()
            with self.stats_lock:
                self.stats["processed"] += 1
                count = self.stats["processed"]
            print(f"[Worker {self.name}] Обработано URL: {count}")
    # pylint: disable=broad-exception-caught


# pylint: disable=too-many-instance-attributes, too-few-public-methods
class Master:
    """Поток, принимающий входящие соединения
       и распределяющий их между воркерами."""
    def __init__(self, host: str, port: int,
                 num_workers: int, top_k: int) -> None:
        self.host = host
        self.port = port
        self.num_workers = num_workers
        self.top_k = top_k
        self.task_queue: queue.Queue = queue.Queue()
        self.stats = {"processed": 0}
        self.stats_lock = threading.Lock()
        self.workers = [Worker(self.task_queue, self.top_k,
                               self.stats, self.stats_lock)
                        for _ in range(self.num_workers)]

    def start(self) -> None:
        """Запускаем воркеры"""
        for worker in self.workers:
            worker.start()

        with socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            print(f"Сервер запущен на {self.host}:{self.port}" +
                  f"Воркеров: {self.num_workers}, top_k: {self.top_k}")
            try:
                while True:
                    conn, addr = server_socket.accept()
                    self.task_queue.put((conn, addr))
            except KeyboardInterrupt:
                print("\nСервер завершает работу...")
            finally:
                pass


def parse_args() -> argparse.Namespace:
    """Парсим команды"""
    parser = argparse.ArgumentParser(
        description="Master‑worker сервер для обработки URL")
    parser.add_argument("-w", "--workers", type=int, default=4,
                        help="Количество рабочих потоков")
    parser.add_argument("-k", "--top", type=int, default=5,
                        help="Сколько самых частых слов отправлять клиенту")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Порт для прослушивания")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Адрес для привязки")
    return parser.parse_args()


def main() -> None:
    """Основной запуск"""
    args = parse_args()
    master = Master(args.host, args.port, args.workers, args.top)
    master.start()


if __name__ == "__main__":
    main()
