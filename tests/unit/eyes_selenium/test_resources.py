from applitools.selenium.resource import get_resource


def test_open_resource_no_error():
    get_resource("processPageAndSerializePoll.js")
