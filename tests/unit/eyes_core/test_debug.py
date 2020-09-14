import os

from mock import patch

from applitools.core.debug import FileDebugScreenshotsProvider


@patch.dict(
    os.environ, {"DEBUG_SCREENSHOT_PREFIX": "prefix", "DEBUG_SCREENSHOT_PATH": "path"}
)
def test_debug_screenshots_env():
    provider = FileDebugScreenshotsProvider()
    assert provider.prefix == "prefix"
    assert provider.path == "path"


def test_debug_screenshot_save(image, tmpdir):
    provider = FileDebugScreenshotsProvider(path=tmpdir, prefix="some")
    provider.save(image, "test")
    img1 = tmpdir.listdir()[0].basename
    assert img1.startswith("some") and img1.endswith("0-test.png")
    provider.save(image, "test2")
    img2 = tmpdir.listdir(sort=True)[1].basename
    assert img2.startswith("some") and img2.endswith("1-test2.png")
