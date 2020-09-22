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


@pytest.fixture
def expected_json_data(request):
    """Loads expected result from json file"""
    mark = request.node.get_closest_marker("expected_json")
    file_name = mark.args[0] if mark else request.node.originalname
    with open(path.join(samples_dir, file_name + ".json"), "rb") as f:
        return f.read()


@pytest.fixture
def expected_json(expected_json_data):
    return json.loads(expected_json_data)
