from collections import namedtuple

from mock import MagicMock, call

from applitools.selenium.visual_grid import PutCache

DummyResource = namedtuple("DummyResource", "url, hash")


def test_put_cache_uploads_only_provided_url():
    resources = {
        "http://1": DummyResource("http://1", "hash1"),
        "http://2": DummyResource("http://2", "hash2"),
    }
    put_cache = PutCache()
    eyes_connector_mock = MagicMock()

    put_cache.put(["http://1"], resources, "a", eyes_connector_mock)
    put_cache.wait_for_all_uploaded()
    put_cache.shutdown()
    put_mock = eyes_connector_mock.render_put_resource

    assert put_mock.call_args_list == [call("a", DummyResource("http://1", "hash1"))]


def test_put_cache_uploads_provided_url_once():
    resources = {
        "http://1": DummyResource("http://1", "hash1"),
        "http://2": DummyResource("http://2", "hash2"),
    }
    put_cache = PutCache()
    eyes_connector_mock = MagicMock()

    put_cache.put(["http://1"], resources, "a", eyes_connector_mock)
    put_cache.put(["http://1"], resources, "b", eyes_connector_mock)
    put_cache.wait_for_all_uploaded()
    put_cache.shutdown()
    put_mock = eyes_connector_mock.render_put_resource

    assert put_mock.call_args_list == [call("a", DummyResource("http://1", "hash1"))]


def test_put_cache_uploads_same_url_with_different_hashes():
    resources1 = {
        "http://1": DummyResource("http://1", "hash1"),
    }
    resources2 = {
        "http://1": DummyResource("http://1", "hash2"),
    }
    put_cache = PutCache()
    eyes_connector_mock = MagicMock()

    put_cache.put(["http://1"], resources1, "a", eyes_connector_mock)
    put_cache.wait_for_all_uploaded()
    put_cache.put(["http://1"], resources2, "b", eyes_connector_mock)
    put_cache.wait_for_all_uploaded()
    put_cache.shutdown()
    put_mock = eyes_connector_mock.render_put_resource

    assert put_mock.call_args_list == [
        call("a", DummyResource("http://1", "hash1")),
        call("b", DummyResource("http://1", "hash2")),
    ]
