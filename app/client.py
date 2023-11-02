import socket
from pathlib import Path
from threading import Thread
import argparse


class UrlConverter:
    def load(self, path_to_urls: str):
        urls_file_path = str(Path(__file__).parent / Path(path_to_urls))
        with open(urls_file_path, 'r', encoding="utf-8") as txt_file:
            return txt_file.read().strip().split('\n')


class Client:
    def execute(self, url: str):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 50000))
            sock.send(url.encode())
            data = sock.recv(1024)
            sock.close()
            print(f"{url}: {data.decode('utf-8')}")
        except Exception as e:
            print("Error sending request to", url, ":", str(e))


class ClientThreads:
    def __init__(self, n: int):
        self.n = n

    def execute(self, url_list: list[str]):
        idx_url = 0

        while idx_url < len(url_list):
            threads = []

            while len(threads) < self.n and idx_url < len(url_list):
                client = Client()
                t = Thread(target=client.execute, args=(url_list[idx_url],))
                t.start()
                threads.append(t)
                idx_url += 1

            # if len(threads) == self.n:
            for th in threads:
                th.join()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("n", nargs='?', type=int, default=10, help="number of threads")
    parser.add_argument("f", nargs='?', default="urls.txt", help="file with URLs")
    args = parser.parse_args()

    url_converter = UrlConverter()
    clients_pull = ClientThreads(args.n)

    urls_list = url_converter.load(args.f)
    clients_pull.execute(urls_list)


if __name__ == "__main__":
    main()
