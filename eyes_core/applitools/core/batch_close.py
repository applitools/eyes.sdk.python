from typing import List, Optional, Text, Union

import attr
import requests

from applitools.common.config import DEFAULT_SERVER_URL
from applitools.common.utils import quote_plus, urljoin
from applitools.common.utils.converters import str2bool
from applitools.common.utils.general_utils import get_env_with_prefix


@attr.s
class _EnabledBatchClose(object):
    _ids = attr.ib()  # type: List[Text]
    server_url = attr.ib()  # type: Text
    api_key = attr.ib()  # type: Text

    def set_url(self, url):
        # type: (Text) -> _EnabledBatchClose
        self.server_url = url
        return self

    def set_api_key(self, api_key):
        # type: (Text) -> _EnabledBatchClose
        self.api_key = api_key
        return self

    def close(self):
        if self.api_key is None:
            print("WARNING: BatchClose wont be done cause no APPLITOOLS_API_KEY is set")
            return
        if str2bool(get_env_with_prefix("APPLITOOLS_DONT_CLOSE_BATCHES")):
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
            res = requests.delete(url, params={"apiKey": self.api_key}, verify=False)
            print("delete batch is done with {} status".format(res.status_code))


@attr.s
class BatchClose(object):
    api_key = attr.ib(
        factory=lambda: get_env_with_prefix("APPLITOOLS_API_KEY", None)
    )  # type: Optional[Text]
    server_url = attr.ib(default=DEFAULT_SERVER_URL)  # type: Text

    def set_url(self, url):
        # type: (Text) -> BatchClose
        self.server_url = url
        return self

    def set_api_key(self, api_key):
        # type: (Text) -> BatchClose
        self.api_key = api_key
        return self

    def set_batch_ids(self, *ids):
        # type: (Union[Text, List[Text]]) -> _EnabledBatchClose
        if isinstance(ids[0], list):
            ids = ids[0]
        return _EnabledBatchClose(ids, self.server_url, self.api_key)
