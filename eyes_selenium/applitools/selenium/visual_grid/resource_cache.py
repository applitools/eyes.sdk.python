import sys
import threading
import typing
from concurrent.futures import Future, ThreadPoolExecutor

from applitools.common import VGResource, logger


class ResourceCache(typing.Mapping[typing.Text, VGResource]):
    def __init__(self):
        self.cache_map = {}
        kwargs = {}
        if sys.version_info >= (3, 6):
            kwargs["thread_name_prefix"] = "ResourceCache-Executor"
        self.executor = ThreadPoolExecutor(**kwargs)
        self.lock = threading.RLock()

    def __str__(self):
        return str(self.cache_map)[:25]

    def _process_future(self, url, val):
        if isinstance(val, Future):
            try:
                val = val.result()
            except Exception as e:
                logger.debug(
                    "We got an exception for following URL: {}"
                    "\n  See details below: \n{}".format(url, str(e))
                )
                val = None
            finally:
                self.cache_map[url] = val
        return val

    def __getitem__(self, item):
        with self.lock:
            val = self.cache_map[item]
            self._process_future(item, val)
        return val

    def __setitem__(self, key, value):
        with self.lock:
            self.cache_map[key] = value

    def __len__(self):
        with self.lock:
            return len(self.cache_map)

    def __del__(self):
        with self.lock:
            self.executor.shutdown()

    def __iter__(self):
        return iter(self.cache_map)

    def fetch_and_store(self, url, func_to_run):
        if url in self:
            return self[url]
        if func_to_run:
            self[url] = self.executor.submit(func_to_run, url)
            return True
        return False

    def process_all(self):
        with self.lock:
            return [self[r_url] for r_url in self]
