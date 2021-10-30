import json
from os import environ, path

import pytest

samples_dir = path.join(path.dirname(__file__), "resources")


@pytest.fixture
def sauce_driver_url():
    return "https://{}:{}@ondemand.saucelabs.com:443/wd/hub".format(
        environ["SAUCE_USERNAME"], environ["SAUCE_ACCESS_KEY"]
    )


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
