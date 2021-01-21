import typing
import uuid

import attr

from applitools.common import TestResults, logger

if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Text

    from structlog import BoundLogger


@attr.s(hash=True)
class VGTask(object):
    name = attr.ib()  # type: Text
    func_to_run = attr.ib(hash=False, repr=False)  # type: Callable
    logger = attr.ib(hash=False, repr=False)  # type: BoundLogger
    uuid = attr.ib(init=False, repr=False, factory=lambda: str(uuid.uuid4()))

    callback = None
    error_callback = None
    complete_callback = None

    def __attrs_post_init__(self):
        self.logger = self.logger.bind(task_name=self.name)

    def on_task_succeeded(self, code):
        # type: (Callable) -> VGTask
        self.callback = code
        return self

    def on_task_error(self, code):
        # type: (Callable) -> VGTask
        self.error_callback = code
        return self

    def on_task_completed(self, code):
        # type: (Callable) -> VGTask
        self.complete_callback = code
        return self

    def __call__(self):
        # type: () -> Optional[TestResults]
        self.logger.debug("Executing " + self.__class__.__name__)
        res = None
        try:
            if callable(self.func_to_run):
                self.logger.debug(
                    "VGTask().func_to_run", func_to_run=self.func_to_run.__name__
                )
                res = self.func_to_run()
            if callable(self.callback):
                self.logger.debug("VGTask().callback", callback=self.callback.__name__)
                self.callback(res)
        except Exception as e:
            self.logger.error("Failed to execute task!", exc_info=e)
            if callable(self.error_callback):
                self.logger.debug(
                    "VGTask().error_callback",
                    error_callback=self.error_callback.__name__,
                )
                self.error_callback(e)
        finally:
            if callable(self.complete_callback):
                self.logger.debug(
                    "VGTask().complete_callback",
                    complete_callback=self.complete_callback.__name__,
                )
                self.complete_callback()
        return res
