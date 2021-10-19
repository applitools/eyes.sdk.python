from typing import List, Optional, Text, Union

import attr
import requests

from applitools.common import EyesError, ProxySettings
from applitools.common.config import DEFAULT_SERVER_URL
from applitools.common.utils import ABC, argument_guard, quote_plus, urljoin
from applitools.common.utils.converters import str2bool
from applitools.common.utils.general_utils import get_env_with_prefix
from applitools.core import state


class _BatchCloseBase(ABC):
    def __init__(
        self,
        api_key=None,  # type: Optional[Text]
        server_url=DEFAULT_SERVER_URL,  # type: Text
        proxy=None,  # type: Optional[ProxySettings]
    ):
        if api_key is None:
            api_key = get_env_with_prefix("APPLITOOLS_API_KEY", None)
        if api_key is None:
            raise EyesError(
                "API key not set! Log in to https://applitools.com to obtain your"
                " API Key and use 'api_key' to set it."
            )
        self.api_key = api_key
        self.server_url = server_url
        self.proxy = proxy

    def set_url(self, url):
        # type: (Text) -> BatchClose
        self.server_url = url
        return self

    def set_api_key(self, api_key):
        # type: (Text) -> BatchClose
        self.api_key = api_key
        return self

    def set_proxy(self, proxy):
        # type: (ProxySettings) -> BatchClose
        argument_guard.is_a(proxy, ProxySettings)
        self.proxy = proxy
        return self


class BatchClose(_BatchCloseBase):
    def set_batch_ids(self, *ids):
        # type: (Union[Text, List[Text]]) -> _EnabledBatchClose
        if isinstance(ids[0], list):
            ids = ids[0]
        return _EnabledBatchClose(ids, self.server_url, self.api_key, self.proxy)


class _EnabledBatchClose(_BatchCloseBase):
    def __init__(
        self,
        ids,  # type: List[Text]
        api_key,  # type: Text
        server_url,  # type: Text
        proxy=None,  # type: Optional[ProxySettings]
    ):
        super(_EnabledBatchClose, self).__init__(api_key, server_url, proxy)
        self._ids = ids

    def close(self):
        if state.get("dont_close_batches") or str2bool(
            get_env_with_prefix("APPLITOOLS_DONT_CLOSE_BATCHES")
        ):
            print("APPLITOOLS_DONT_CLOSE_BATCHES environment variable set to true.")
            return
        for batch_id in self._ids:
            print("close batch called with {}".format(batch_id))
            url = urljoin(
                self.server_url.rstrip("/"),
                "api/sessions/batches/{}/close/bypointerid".format(
                    quote_plus(batch_id)
                ),
            )
            if self.proxy:
                proxies = {"http": self.proxy.url, "https": self.proxy.url}
            else:
                proxies = None
            res = requests.delete(
                url, params={"apiKey": self.api_key}, verify=False, proxies=proxies
            )
            print("delete batch is done with {} status".format(res.status_code))
