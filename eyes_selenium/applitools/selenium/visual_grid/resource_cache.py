import sys
import threading
import typing
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial

from applitools.common import VGResource, logger

if typing.TYPE_CHECKING:
    from typing import Dict, Iterable, Text

    from applitools.selenium.visual_grid import EyesConnector


class ResourceCache(typing.Mapping[typing.Text, VGResource]):
    def __init__(self):
        self.cache_map = {}
        kwargs = {}
        if sys.version_info[:2] >= (3, 6):
            kwargs["thread_name_prefix"] = "ResourceCache-Executor"
        self.executor = ThreadPoolExecutor(**kwargs)
        self.lock = threading.RLock()

    def __str__(self):
        with self.lock:
            return str(self.cache_map)[:25]

    def _process_future(self, url, val):
        if isinstance(val, Future):
            try:
                val = val.result()
            except Exception:
                logger.exception(
                    "We got an exception during processing URL: {}".format(url)
                )
                val = None
            finally:
                self.cache_map[url] = val
        return val

    def __getitem__(self, item):
        with self.lock:
            val = self.cache_map[item]
            return self._process_future(item, val)

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
        with self.lock:
            return iter(list(self.cache_map))

    def fetch_and_store(self, url, fetch_function, force=False):
        # type: (typing.Text, typing.Callable[[typing.Text], VGResource], bool) -> bool
        """
        Schedules fetch of the url using fetch_function.

        :param url: url to fetch resource from
        :param fetch_function: function called to fetch the resource in a worker thread
        :param force: option to force fetch even if the resource is
                      already fetched or fetching

        :return: True if the fetch was just scheduled or already in process
                 False if it's already fetched and in the cache
        """
        with self.lock:
            if force or url not in self.cache_map:
                self.cache_map[url] = self.executor.submit(fetch_function, url)
                return True
            else:
                return isinstance(self.cache_map[url], Future)

    def process_all(self):
        with self.lock:
            return [self[r_url] for r_url in self]


class PutCache(object):
    def __init__(self):
        if sys.version_info[:2] >= (3, 6):
            executor_args = dict(thread_name_prefix=self.__class__.__name__)
        else:
            executor_args = dict()
        self._executor = ThreadPoolExecutor(**executor_args)
        self._lock = threading.Lock()
        self._sent_hashes = set()
        self._currently_uploading = deque()

    def put(
        self,
        urls,  # type: Iterable[Text]
        full_request_resources,  # type: Dict[Text, VGResource]
        render_id,  # type: Text
        eyes_connector,  # type: EyesConnector
        force=False,  # type: bool
    ):
        # type: (...) -> None
        logger.debug(
            "PutCache.put({}, render_id={}) call".format(list(urls), render_id)
        )
        with self._lock:
            all_resources = [full_request_resources.get(url) for url in urls]
            put_resources = [
                r for r in all_resources if force or r.hash not in self._sent_hashes
            ]
            self._sent_hashes.update(r.hash for r in put_resources)
            futures = self._executor.map(
                partial(eyes_connector.render_put_resource, render_id),
                put_resources,
            )
            self._currently_uploading.append(futures)

    def wait_for_all_uploaded(self):
        # type: () -> None
        with self._lock:
            for futures in self._currently_uploading:
                list(futures)
            self._currently_uploading.clear()

    def shutdown(self):
        # type: () -> None
        with self._lock:
            self._executor.shutdown()

    def __del__(self):
        # type: () -> None
        self.shutdown()
