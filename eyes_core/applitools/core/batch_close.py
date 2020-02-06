from typing import Text, List, Union

import attr
import requests

from applitools.common import EyesError
from applitools.common.config import DEFAULT_SERVER_URL
from applitools.common.utils import urljoin
from applitools.common.utils.general_utils import get_env_with_prefix


@attr.s
class _EnabledBatchClose(object):
    _ids = attr.ib()
    _server_url = attr.ib()
    _api_key = attr.ib()

    def close(self):
        if get_env_with_prefix("APPLITOOLS_DONT_CLOSE_BATCHES") in [
            "1",
            "true",
            "True",
        ]:
            print("APPLITOOLS_DONT_CLOSE_BATCHES environment variable set to true.")
            return
        for batch_id in self._ids:
            print("close batch called with {}".format(batch_id))
            url = urljoin(
                self._server_url,
                "api/sessions/batches/{}/close/bypointerid".format(batch_id),
            )
            res = requests.delete(url, params={"apiKey": self._api_key}, verify=False)
            print("delete batch is done with {} status".format(res.status_code))


@attr.s
class BatchClose(object):
    api_key = attr.ib(factory=lambda: get_env_with_prefix("APPLITOOLS_API_KEY", None))
    server_url = attr.ib(default=DEFAULT_SERVER_URL)

    def set_url(self, url):
        self.server_url = url
        return self

    def set_api_key(self, api_key):
        self.api_key = api_key
        return self

    def set_batch_ids(self, *ids):
        # type: (Union[*Text, List[Text]]) -> _EnabledBatchClose
        if isinstance(ids[0], list):
            ids = ids[0]
        if self.api_key is None:
            raise EyesError(
                "API key not set! Log in to https://applitools.com to obtain your"
                " API Key and use 'api_key' to set it."
            )
        return _EnabledBatchClose(ids, self.server_url, self.api_key)
