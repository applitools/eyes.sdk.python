from applitools.common import RectangleSize
from applitools.core import EyesBase


class TestEyes(EyesBase):
    def _get_screenshot(self):
        return None

    def _get_viewport_size(self):
        return RectangleSize(100, 100)

    def _inferred_environment(self):
        return "TestEyes"

    def _set_viewport_size(self, size):
        return None

    def _title(self):
        return "TestEyes_Title"

    def _try_capture_dom(self):
        return None

    def base_agent_id(self):
        return None
