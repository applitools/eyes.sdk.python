import sys
import threading
import typing
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial

from applitools.common import VGResource, logger
from applitools.core import ServerConnector

if typing.TYPE_CHECKING:
    from typing import List


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
        kwargs = {}
        if sys.version_info[:2] >= (3, 6):
            kwargs["thread_name_prefix"] = self.__class__.__name__
        self._executor = ThreadPoolExecutor(**kwargs)
        self._lock = threading.Lock()
        self._sent_hashes = set()

    def put(
        self,
        all_resources,  # type: List[VGResource]
        server_connector,  # type: ServerConnector
        force=False,  # type: bool
    ):
        # type: (...) -> None
        logger.debug("PutCache.put({} call".format(all_resources))
        if not force:
            check_result = server_connector.check_resource_status(
                None,
                *[{"hashFormat": r.hash_format, "hash": r.hash} for r in all_resources]
            )
            resources_to_upload = [
                resource
                for resource, exists in zip(all_resources, check_result)
                if not exists
            ]
        else:
            resources_to_upload = all_resources

        with self._lock:
            put_resources = [r for r in resources_to_upload if force or r.hash]
            results_iterable = self._executor.map(
                partial(server_connector.render_put_resource, None),
                put_resources,
            )
            self._sent_hashes.update(list(results_iterable))

    def shutdown(self):
        # type: () -> None
        with self._lock:
            self._executor.shutdown()

    def __del__(self):
        # type: () -> None
        self.shutdown()
