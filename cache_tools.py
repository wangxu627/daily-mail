import os
from collections.abc import Iterable


class CacheCookie(Iterable):
    def __init__(self, file_name):
        self.file_name = file_name
        self.urls = set()
        if os.path.exists(self.file_name):
            self.load()

    def __contains__(self, value):
        return value in self.urls

    def __iter__(self):
        return iter(self.urls)

    def add(self, value):
        self.urls.add(value)

    def update(self, urls):
        self.urls = urls

    def clear(self):
        self.urls.clear()

    def save(self):
        with open(self.file_name, "w") as f:
            for l in self.urls:
                f.write(l + "\n")

    def load(self):
        with open(self.file_name) as f:
            for l in f:
                self.urls.add(l.strip())


if __name__ == "__main__":
    # test
    cache = CacheCookie("tmp")
    cache.add("1111")
    cache.add("2222")
    s = set(cache)
    print("1111" in s)
    print("3333" in s)
