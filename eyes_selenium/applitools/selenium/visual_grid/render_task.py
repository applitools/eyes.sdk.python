import typing

import attr

from applitools.common import EyesError, RenderRequest, RenderStatus, logger
from applitools.common.utils import datetime_utils
from applitools.core import ServerConnector

from .vg_task import VGTask

if typing.TYPE_CHECKING:
    from typing import Callable, List

    from applitools.common import RenderStatusResults
    from applitools.selenium.visual_grid import EyesConnector, RunningTest


@attr.s(hash=False)
class RenderTask(VGTask):
    MAX_FAILS_COUNT = 5
    MAX_ITERATIONS = 2400  # poll_render_status for 1 hour

    render_requests = attr.ib(hash=False, repr=False)  # type: List[RenderRequest]
    on_success = attr.ib(hash=False, repr=False)
    on_error = attr.ib(hash=False, repr=False)
    rendering_service = attr.ib(hash=False, repr=False)
    func_to_run = attr.ib(default=None, hash=False, repr=False)  # type: Callable

    def __attrs_post_init__(self):
        # type: () -> None
        self.func_to_run = self.perform  # type: Callable

    def perform(self):  # noqa
        # type: () -> List[RenderStatusResults]
        self.rendering_service.render(self)
