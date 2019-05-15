import sys
import threading
import typing
from concurrent.futures import Future, ThreadPoolExecutor

from applitools.common import VGResource, logger


def _process_future(val):
    if isinstance(val, Future):
        try:
            val = val.result()
        except Exception:
            logger.exception("Resource haven't been downloaded.")
    return val


lock = threading.RLock()


class ResourceCache(typing.Mapping[typing.Text, VGResource]):
    def __init__(self):
        self.cache_map = {}
        kwargs = {}
        if sys.version_info >= (3, 6):
            kwargs["thread_name_prefix"] = "ResourceCache-Executor"
        self.executor = ThreadPoolExecutor(**kwargs)

    def __str__(self):
        return str(self.cache_map)[:25]

    def get(self, k, default=None):
        with lock:
            val = self.cache_map.get(k, default)
            val = _process_future(val)
            self[k] = val
        return val

    def __getitem__(self, item):
        with lock:
            val = self.cache_map[item]
            val = _process_future(val)
            self[item] = val
        return val

    def __setitem__(self, key, value):
        with lock:
            self.cache_map[key] = value

    def __len__(self):
        with lock:
            return len(self.cache_map)

    def __iter__(self):
        return iter(self.cache_map)

    def fetch_and_store(self, url, func_to_run):
        if url in self:
            return self[url]
        if func_to_run:
            self[url] = self.executor.submit(func_to_run, url)
            return True
        return False
