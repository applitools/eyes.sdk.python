import json
import os
from itertools import cycle

import pytest
import requests

_fixutres2vm_types = {}


def vm(func):
    _fixutres2vm_types[func.__name__] = "vm"
    return func


def mac_vm(func):
    _fixutres2vm_types[func.__name__] = "mac_vm"
    return func


def rd(func):
    _fixutres2vm_types[func.__name__] = "rd"
    return func


@pytest.fixture(scope="function")
def sauce_url():
    name, access_key = _sauce_credentials()
    return "https://{}:{}@ondemand.saucelabs.com/wd/hub".format(name, access_key)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    sauce_fixtures = _fixutres2vm_types.keys()
    limits = _SAUCE_LIMITS.items()
    # use up to half of the allowed VMs of each kind
    thread_counters = {k: iter(cycle(range(n // 2))) for k, n in limits if n > 0}
    for test in items:
        sauce_fixture = set(test.fixturenames) & sauce_fixtures
        if sauce_fixture:
            assert len(sauce_fixture) == 1
            sauce_fixture = sauce_fixture.pop()
            vm_type = _fixutres2vm_types[sauce_fixture]
            thread_number = next(thread_counters[vm_type + "s"])
            xdist_group = "sauce_{}_{}".format(vm_type, thread_number)
            test.add_marker(pytest.mark.xdist_group(xdist_group))


def _sauce_credentials():
    return os.environ["SAUCE_USERNAME"], os.environ["SAUCE_ACCESS_KEY"]


def _fetch_sauce_limits():
    # Use environment variable to cache limits to avoid sending same request multiple
    # times when xdist workers start
    if "SAUCE_LIMITS" not in os.environ:
        url_template = (
            "https://{username}:{key}@api.us-west-1.saucelabs.com/"
            "rest/v1.2/users/{username}/concurrency"
        )
        username, key = _sauce_credentials()
        url = url_template.format(username=username, key=key)
        response = requests.get(url).json()
        allowed = response["concurrency"]["team"]["allowed"]
        os.environ["SAUCE_LIMITS"] = json.dumps(allowed)
    return json.loads(os.environ["SAUCE_LIMITS"])


_SAUCE_LIMITS = _fetch_sauce_limits()
