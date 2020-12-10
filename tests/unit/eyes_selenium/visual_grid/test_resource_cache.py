from collections import namedtuple

from mock import MagicMock, call

from applitools.selenium.visual_grid import PutCache

DummyResource = namedtuple("DummyResource", "url, hash, hash_format, content")
DummyResource.clear = lambda _: None


def test_put_cache_uploads_provided_url_once():
    resources = [DummyResource("http://1", "hash1", "sha1", "a")]
    put_cache = PutCache()
    eyes_connector_mock = MagicMock()
    eyes_connector_mock.check_resource_status.side_effect = [[False], [True]]

    put_cache.put(resources, eyes_connector_mock)
    put_cache.put(resources, eyes_connector_mock)
    put_cache.shutdown()
    put_mock = eyes_connector_mock.render_put_resource

    assert put_mock.call_args_list == [
        call(DummyResource("http://1", "hash1", "sha1", "a"))
    ]


def test_put_cache_uploads_same_url_with_different_hashes():
    resources1 = [DummyResource("http://1", "hash1", "sha1", "a")]
    resources2 = [DummyResource("http://1", "hash2", "sha1", "b")]
    put_cache = PutCache()
    eyes_connector_mock = MagicMock()
    eyes_connector_mock.check_resource_status.return_value = [False]

    put_cache.put(resources1, eyes_connector_mock)
    put_cache.put(resources2, eyes_connector_mock)
    put_cache.shutdown()
    put_mock = eyes_connector_mock.render_put_resource

    assert put_mock.call_args_list == [
        call(DummyResource("http://1", "hash1", "sha1", "a")),
        call(DummyResource("http://1", "hash2", "sha1", "b")),
    ]


def test_put_cache_skips_already_cleared_resource():
    resources = [DummyResource("http://1", "hash1", "sha1", None)]
    put_cache = PutCache()
    eyes_connector_mock = MagicMock()
    eyes_connector_mock.check_resource_status.return_value = [False]

    put_cache.put(resources, eyes_connector_mock)
    put_cache.shutdown()
    put_mock = eyes_connector_mock.render_put_resource

    assert put_mock.call_args_list == []
