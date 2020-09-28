import os

import pytest

__all__ = ("image",)

from applitools.common import (
    MatchResult,
    RenderingInfo,
    RenderStatusResults,
    RunningRender,
    RunningSession,
    TestResults,
)
from applitools.core import ServerConnector


@pytest.fixture
def image():
    from PIL import Image

    img = Image.new("RGB", (800, 600), "black")
    pixels = img.load()  # create the pixel map

    for i in range(img.size[0]):  # for every col:
        for j in range(img.size[1]):  # For every row
            pixels[i, j] = (i, j, 100)  # set the colour accordingly
    return img


def pytest_generate_tests(metafunc):
    import uuid

    # setup environment variables once per test run if not settled up
    # needed for multi thread run

    os.environ["APPLITOOLS_BATCH_ID"] = os.getenv(
        "APPLITOOLS_BATCH_ID", str(uuid.uuid4())
    )


@pytest.fixture
def fake_connector_class():
    return FakeServerConnector


class FakeServerConnector(ServerConnector):
    def __init__(self):
        super(FakeServerConnector, self).__init__()
        self.calls = {}

    def start_session(self, session_start_info):
        self.calls["start_session"] = session_start_info
        return RunningSession(
            **{
                "id": "MDAwMDANzk~",
                "session_id": "000002518",
                "batch_id": "000002518010",
                "baseline_id": "5411539b-558a-44c6-8a93-d95ddf909552",
                "is_new_session": True,
                "url": "https://eyes.applitools.com/app/batches/2124/04235423?accountId=asfd1124~~",
            }
        )

    def stop_session(self, running_session, is_aborted, save):
        self.calls["stop_session"] = (running_session, is_aborted, save)
        return TestResults()

    def match_window(self, running_session, match_data):
        self.calls["match_window"] = (running_session, match_data)
        return MatchResult(as_expected=True)

    def render(self, *render_requests):
        self.calls["render"] = render_requests
        return [
            RunningRender(
                **{
                    "render_id": "d226bfd0-e6e0-4c5e-9651-3a844a3e9b45",
                    "job_id": "33305ec6-c03e-4fdf-8a11-bae62f3900a8",
                    "render_status": "rendering",
                }
            )
        ]

    def render_status_by_id(self, *render_ids):
        self.calls["render_status_by_id"] = render_ids
        return [
            RenderStatusResults(
                **{
                    "image_location": "https://eyesapi.applitools.com/api/images/sti/se%-4e8e-9fd7-c01b33e47dcc?accessKey=None",
                    "status": "rendered",
                    "os": "linux",
                    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/85.0.4183.83 Safari/537.36",
                    "visual_viewport": {"width": 800, "height": 600},
                    "device_size": {"width": 800, "height": 600},
                    "retry_count": 0,
                    "dom_location": "https://eyespublicw0.blob.core/a255-se/40b1-bf12df29cd5?sv=2017-04-17&sr=c&sig=1smaTPYU27cwPZuGx9pEooNNc%3D&se=2015%3A11%3A50Z&sp=w&accessKey=None",
                    "render_id": "d226bfd0-e6e0-4c5e-9651-3a844a3e9b45",
                }
            )
        ]

    def render_put_resource(self, running_render, resource):
        self.calls["render_put_resource"] = running_render, resource
        return resource.hash

    def render_info(self):
        self.calls["render_info"] = True
        return RenderingInfo(
            **{
                "service_url": "https://render.applitools.com",
                "stitching_service_url": "https://eyesapi.applitools.com/api/images/s?accessKey=None",
                "access_token": "NYNyBxWppb1a0NvMrZXmMHqrUrdYUM",
                "results_url": "https://eyespublicwi0.blob.core/a-se/__random__?sv=2&sr=c&sig=wrasda%3D&se=09-29T10%3A12%3A13Z&sp=w&accessKey=None",
                "max_image_height": 15000,
                "max_image_area": 37500000,
            }
        )
