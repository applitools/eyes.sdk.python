from applitools.selenium.visual_grid import RenderTask, ResourceCache
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
        def download_resource(url):
            return internet[url]

    capture_result = {
        "cdt": [],
        "url": "https://a.com/a",
        "resourceUrls": ["https://a.com/1.css"],
    }
    cache = ResourceCache()
    task = RenderTask("A", {}, cache, None, ConnectorMock, None)

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
        def download_resource(url):
            ConnectorMock.call_count += 1
            return internet[url]

    capture_result = {
        "cdt": [],
        "url": "https://a.com/a",
        "resourceUrls": ["https://a.com/1.css"],
    }
    cache = ResourceCache()
    task = RenderTask("A", {}, cache, None, ConnectorMock, None)

    vg_dom1 = task.parse_frame_dom_resources(capture_result)
    assert ConnectorMock.call_count == 2
    assert set(vg_dom1.resources) == {
        "https://a.com/1.css",
        "https://a.com/2.css",
    }
    assert "https://a.com/1.css" in cache
    assert "https://a.com/2.css" in cache
