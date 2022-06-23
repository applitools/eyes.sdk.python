from typing import List, Optional, Text, Union

import attr

from applitools.common import ProxySettings
from applitools.common.config import DEFAULT_SERVER_URL
from applitools.common.utils import argument_guard
from applitools.common.utils.general_utils import get_env_with_prefix


@attr.s
class _EnabledBatchClose(object):
    _ids = attr.ib()  # type: List[Text]
    server_url = attr.ib()  # type: Text
    api_key = attr.ib()  # type: Text
    proxy = attr.ib(default=None)  # type: Optional[ProxySettings]

    def set_url(self, url):
        # type: (Text) -> _EnabledBatchClose
        self.server_url = url
        return self

    def set_api_key(self, api_key):
        # type: (Text) -> _EnabledBatchClose
        self.api_key = api_key
        return self

    def set_proxy(self, proxy):
        # type: (ProxySettings) -> _EnabledBatchClose
        argument_guard.is_a(proxy, ProxySettings)
        self.proxy = proxy
        return self

    def close(self):
        from applitools.selenium.__version__ import __version__
        from applitools.selenium.command_executor import CommandExecutor
        from applitools.selenium.eyes import EyesRunner
        from applitools.selenium.universal_sdk_types import marshal_enabled_batch_close

        cmd = CommandExecutor.get_instance(EyesRunner.BASE_AGENT_ID, __version__)
        marshaled = marshal_enabled_batch_close(self)
        cmd.core_close_batches(marshaled)


@attr.s
class BatchClose(object):
    api_key = attr.ib(
        factory=lambda: get_env_with_prefix("APPLITOOLS_API_KEY", None)
    )  # type: Optional[Text]
    server_url = attr.ib(default=DEFAULT_SERVER_URL)  # type: Text
    proxy = attr.ib(default=None)  # type: Optional[ProxySettings]

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

    def set_batch_ids(self, *ids):
        # type: (Union[Text, List[Text]]) -> _EnabledBatchClose
        if isinstance(ids[0], list):
            ids = ids[0]
        return _EnabledBatchClose(ids, self.server_url, self.api_key, self.proxy)
