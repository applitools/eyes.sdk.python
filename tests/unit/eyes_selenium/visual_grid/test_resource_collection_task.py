import mock

from applitools.common import logger
from applitools.selenium.visual_grid import ResourceCache, ResourceCollectionTask
from applitools.selenium.visual_grid.resource_collection_task import is_cookie_for_url
from tests.unit.eyes_core.test_server_connector import MockResponse


def test_cached_child_resources_get_into_render_request():
    def mock_css(content=b"", type="text/css", code=200):
        return MockResponse(None, content, code, {"Content-Type": type})

    internet = {
        "https://a.com/1.css": mock_css(b'@import url(2.css);@import "3.css"'),
        "https://a.com/2.css": mock_css(b'@import "4.css"'),
        "https://a.com/3.css": mock_css(code=404),
        "https://a.com/4.css": mock_css(b""),
    }

    class ConnectorMock:
        @staticmethod
        def download_resource(url, cookies):
            return internet[url]

    capture_result = {
        "cdt": [],
        "url": "https://a.com/a",
        "resourceUrls": ["https://a.com/1.css"],
    }
    cache = ResourceCache()
    task = ResourceCollectionTask("A", logger, "", cache, None, ConnectorMock, None)

    vg_dom1 = task.parse_frame_dom_resources(capture_result)
    assert set(vg_dom1.resources) == {
        "https://a.com/1.css",
        "https://a.com/2.css",
        "https://a.com/3.css",
        "https://a.com/4.css",
    }
    assert "https://a.com/1.css" in cache
    assert "https://a.com/2.css" in cache
    assert "https://a.com/3.css" in cache
    assert "https://a.com/4.css" in cache

    vg_dom2 = task.parse_frame_dom_resources(capture_result)
    assert set(vg_dom2.resources) == {
        "https://a.com/1.css",
        "https://a.com/2.css",
        "https://a.com/3.css",
        "https://a.com/4.css",
    }


def test_recursive_resources_downloaded_once():
    def mock_css(content=b"", type="text/css", code=200):
        return MockResponse(None, content, code, {"Content-Type": type})

    internet = {
        "https://a.com/1.css": mock_css(b"@import url(2.css);"),
        "https://a.com/2.css": mock_css(b"@import url(1.css);"),
    }

    class ConnectorMock:
        call_count = 0

        @staticmethod
        def download_resource(url, cookies):
            ConnectorMock.call_count += 1
            return internet[url]

    capture_result = {
        "cdt": [],
        "url": "https://a.com/a",
        "resourceUrls": ["https://a.com/1.css"],
    }
    cache = ResourceCache()
    task = ResourceCollectionTask("A", logger, "", cache, None, ConnectorMock, None)

    vg_dom1 = task.parse_frame_dom_resources(capture_result)
    assert ConnectorMock.call_count == 2
    assert set(vg_dom1.resources) == {
        "https://a.com/1.css",
        "https://a.com/2.css",
    }
    assert "https://a.com/1.css" in cache
    assert "https://a.com/2.css" in cache


def test_cookies_passed_to_server_connector():
    connector_mock = mock.MagicMock()
    connector_mock.download_resource.return_value = MockResponse(None, b"", 200, {})

    capture_result = {
        "cdt": [],
        "url": "a.com",
        "srcAttr": None,
        "resourceUrls": ["http://a.com/root.res"],
        "cookies": [
            {
                "domain": "a.com",
                "path": "/",
                "secure": False,
                "name": "insecure",
                "value": "1",
            },
            {
                "domain": ".a.com",
                "path": "/",
                "secure": True,
                "name": "secure",
                "value": "1",
            },
        ],
        "frames": [
            {
                "cdt": [],
                "url": "a.com/frame1.html",
                "srcAttr": "./frame1.html",
                "cookies": [],
                "frames": [
                    {
                        "cdt": [],
                        "url": "a.com/subdir/frame2.html",
                        "srcAttr": "./subdir/frame2.html",
                        "resourceUrls": [
                            "https://a.com/root.res",
                            "http://a.com/subdir/res",
                        ],
                        "cookies": [
                            {
                                "domain": "a.com",
                                "path": "/",
                                "secure": False,
                                "name": "insecure",
                                "value": "1",
                            },
                            {
                                "domain": ".a.com",
                                "path": "/",
                                "secure": True,
                                "name": "secure",
                                "value": "1",
                            },
                            {
                                "domain": ".a.com",
                                "path": "/subdir",
                                "secure": False,
                                "name": "subdir",
                                "value": "1",
                            },
                        ],
                        "frames": [],
                    }
                ],
            }
        ],
    }
    cache = ResourceCache()
    task = ResourceCollectionTask("A", logger, "", cache, None, connector_mock, None)

    task.parse_frame_dom_resources(capture_result)

    connector_mock.download_resource.call_args_list.sort(
        key=lambda a: (a.args[0], len(a.args[1]))
    )
    assert connector_mock.download_resource.call_args_list == [
        mock.call(
            "http://a.com/root.res",
            [
                {
                    "path": "/",
                    "domain": "a.com",
                    "secure": False,
                    "value": "1",
                    "name": "insecure",
                }
            ],
        ),
        mock.call(
            "http://a.com/subdir/res",
            [
                {
                    "path": "/",
                    "domain": "a.com",
                    "secure": False,
                    "value": "1",
                    "name": "insecure",
                },
                {
                    "path": "/subdir",
                    "domain": ".a.com",
                    "secure": False,
                    "value": "1",
                    "name": "subdir",
                },
            ],
        ),
        mock.call(
            "https://a.com/root.res",
            [
                {
                    "path": "/",
                    "domain": "a.com",
                    "secure": False,
                    "value": "1",
                    "name": "insecure",
                },
                {
                    "path": "/",
                    "domain": ".a.com",
                    "secure": True,
                    "value": "1",
                    "name": "secure",
                },
            ],
        ),
    ]


def test_is_cookie_for_url_with_dotted_correct_domain():
    assert is_cookie_for_url(
        {
            "domain": ".a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://a.com/",
    )


def test_is_cookie_for_url_with_dotted_correct_subdomain():
    assert is_cookie_for_url(
        {
            "domain": ".a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://b.a.com/",
    )


def test_is_cookie_for_url_with_not_dotted_correct_domain():
    assert is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://a.com/",
    )


def test_is_cookie_for_url_with_not_dotted_correct_subdomain():
    assert is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://b.a.com/",
    )


def test_is_cookie_for_url_with_dotted_incorrect_domain():
    assert not is_cookie_for_url(
        {
            "domain": ".a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://b.com/",
    )


def test_is_cookie_for_url_with_not_dotted_incorrect_domain():
    assert not is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://b.com/",
    )


def test_is_cookie_for_url_with_not_dotted_incorrect_suffixed_domain():
    assert not is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://ba.com/",
    )


def test_is_cookie_for_url_with_secure_cookie_non_secure_url():
    assert not is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/",
            "secure": True,
            "name": "subdir",
            "value": "1",
        },
        "http://a.com/subdir",
    )


def test_is_cookie_for_url_with_path_cookie_incorrect_url():
    assert not is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/b",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://a.com/",
    )


def test_is_cookie_for_url_with_path_cookie_correct_subdir_url():
    assert is_cookie_for_url(
        {
            "domain": "a.com",
            "path": "/b",
            "secure": False,
            "name": "subdir",
            "value": "1",
        },
        "http://a.com/b/c",
    )
