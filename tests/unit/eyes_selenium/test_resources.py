from typing import Text

from applitools.selenium.resource import get_resource


def test_open_resource_is_unicode():
    assert type(get_resource("pollResult.js")) is Text
