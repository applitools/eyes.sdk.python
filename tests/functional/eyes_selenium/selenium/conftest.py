import json
from collections import OrderedDict
from os import path

import attr
import pytest

from applitools.common import BatchInfo

samples_dir = path.join(path.dirname(__file__), "resources")


@pytest.fixture
def batch_info():
    return BatchInfo("Python SDK Selenium")


@attr.s
class ExpectedJson(object):
    data = attr.ib()  # type: bytes

    @property
    def parsed(self):
        return json.loads(self.data)

    @property
    def parsed_ordered(self):
        return json.loads(self.data, object_pairs_hook=OrderedDict)


@pytest.fixture
def expected_json(request):
    """Loads expected result from json file"""
    mark = request.node.get_closest_marker("expected_json")
    file_name = mark.args[0] if mark else request.node.originalname
    with open(path.join(samples_dir, file_name + ".json"), "rb") as f:
        return ExpectedJson(f.read())
