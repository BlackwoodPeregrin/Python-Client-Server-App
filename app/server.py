import argparse
import socket
import json
from queue import Queue
from threading import Thread
from urllib.error import URLError
from urllib.request import urlopen
from parser import MyHTMLParser


class Master:
    def __init__(self):
        self.exit_program = False

    def start(self, queue):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', 50000))
        sock.listen()

        while not self.exit_program:
            client, addr = sock.accept()
            queue.put(client)

        sock.close()

    def stop(self):
        self.exit_program = True


class Worker:
    def __init__(self, w: int, k: int):
        self.exit_program = False
        self.w = w
        self.k = k
        self.statistics_buffer = []
        for i in range(self.w):
            self.statistics_buffer.append(0)

    def start(self, queue):
        threads = []

        while not self.exit_program:
            if not queue.empty() and len(threads) < self.w:
                t = Thread(target=self.worker_process, args=(queue.get(),))
                t.start()
                threads.append(t)
            else:
                for i in range(len(threads)):
                    threads[i].join()
                    self.statistics_buffer[i] += 1
                    self.print_statistics()

                threads = []

    def stop(self):
        self.exit_program = True

    def worker_process(self, client: socket):
        try:
            recv = client.recv(1024)
            content = urlopen(recv.decode('utf-8'))
            text_content = content.read().decode('utf-8')
            parser = MyHTMLParser()
            parser.feed(text_content)
            json_object = json.dumps(self.get_top_n_words(parser.result_data()))

            client.send(json_object.encode())
            client.close()
        except (ConnectionResetError, URLError) as e:
            error = f"Error sending request to {recv.decode('utf-8')} : {str(e)}"
            client.send(error.encode())
            client.close()

    def get_top_n_words(self, text: str):
        tokens = text.split()
        quantities = {}
        for token in tokens:
            if token not in quantities:
                quantities[token] = 1
            else:
                quantities[token] += 1
        sorted_quantities = sorted(quantities.items(), key=lambda x: x[1], reverse=True)[:self.k]
        return {word: freq for word, freq in sorted_quantities}

    def print_statistics(self):
        view_statistics = "statistics: "
        for i in range(len(self.statistics_buffer)):
            view_statistics += f"worker{str(i + 1)}={str(self.statistics_buffer[i])} "
        print(view_statistics)


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("w", nargs='?', type=int, default=5, help="number of workers")
    parser.add_argument("k", nargs='?', type=int, default=5, help="top key words")
    args = parser.parse_args()

    queue = Queue()

    while True:
        try:
            master = Master()
            worker = Worker(args.w, args.k)
            th1 = Thread(target=master.start, args=(queue,))
            th2 = Thread(target=worker.start, args=(queue,))
            th1.start()
            th2.start()
            while th1.is_alive():
                th1.join(1)
            while th1.is_alive():
                th2.join(1)
        except KeyboardInterrupt:
            print("Server interrupted")
            master.stop()
            worker.stop()
            break


if __name__ == "__main__":
    main()
