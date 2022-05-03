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
    thread_counters = None
    for test in items:
        sauce_fixture = set(test.fixturenames) & sauce_fixtures
        if sauce_fixture:
            if not thread_counters:
                limits = _sauce_limits().items()
                # use up to half of the allowed VMs of each kind
                thread_counters = {k: iter(cycle(range(n // 2))) for k, n in limits}
            assert len(sauce_fixture) == 1
            sauce_fixture = sauce_fixture.pop()
            vm_type = _fixutres2vm_types[sauce_fixture]
            thread_number = next(thread_counters[vm_type + "s"])
            xdist_group = "sauce_{}_{}".format(vm_type, thread_number)
            test.add_marker(pytest.mark.xdist_group(xdist_group))


def _sauce_credentials():
    return os.environ["SAUCE_USERNAME"], os.environ["SAUCE_ACCESS_KEY"]


def _sauce_limits():
    urlt = "https://{u}:{k}@api.us-west-1.saucelabs.com/rest/v1.2/users/{u}/concurrency"
    username, key = _sauce_credentials()
    url = urlt.format(u=username, k=key)
    response = requests.get(url).json()
    return response["concurrency"]["team"]["allowed"]
