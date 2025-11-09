"""
Многопоточный клиент для отправки URL‑ов серверу. Запуск через команду:
python client.py 10 urls.txt --host localhost --port 8000
Клиент загружает список URL‑ов из файла и распределяет их между M потоками.
"""

import argparse
import queue
import socket
import threading
from typing import List


class ClientWorker(threading.Thread):
    """Поток, отправляющий URL серверу"""
    def __init__(self, url_queue: queue.Queue,
                 host: str, port: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.url_queue = url_queue
        self.host = host
        self.port = port
        self.daemon = True

    def run(self) -> None:
        while True:
            try:
                url = self.url_queue.get_nowait()
            except queue.Empty:
                break
            try:
                self.process_url(url)
            finally:
                self.url_queue.task_done()

    def process_url(self, url: str) -> None:
        """Отправляет URL серверу и выводит ответ"""
        try:
            with socket.create_connection((self.host, self.port),
                                          timeout=10) as sock:
                sock.sendall((url + "\n").encode())
                f = sock.makefile('r', encoding='utf-8', newline='\n')

                line = f.readline()
                if not line:
                    raise RuntimeError("empty response from server")

                data = line.rstrip('\r\n')
                print(f"{url}: {data}", flush=True)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"{url}: Ошибка: {exc}")


def parse_args() -> argparse.Namespace:
    """Парсим команды"""
    parser = argparse.ArgumentParser(
             description="Многопоточный клиент для отправки URL серверу")
    parser.add_argument("threads", type=int,
                        help="Количество клиентских потоков")
    parser.add_argument("file", type=str,
                        help="Файл с URL‑ами (по одному в строке)")
    parser.add_argument("--host", type=str,
                        default="localhost", help="Адрес сервера")
    parser.add_argument("--port", type=int,
                        default=8000, help="Порт сервера")
    return parser.parse_args()


def load_urls(file_path: str) -> List[str]:
    """Считывает URL из файла"""
    urls: List[str] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                urls.append(line)
    return urls


def main() -> None:
    """Основной вызов"""
    args = parse_args()
    urls = load_urls(args.file)
    if not urls:
        print("Файл с URL пуст")
        return
    url_queue: queue.Queue = queue.Queue()
    for url in urls:
        url_queue.put(url)

    workers = [ClientWorker(url_queue, args.host, args.port)
               for _ in range(args.threads)]
    for worker in workers:
        worker.start()

    url_queue.join()


if __name__ == "__main__":
    main()
