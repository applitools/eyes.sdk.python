import typing
import uuid

import attr

from applitools.common import TestResults, logger

if typing.TYPE_CHECKING:
    from typing import Callable, Text, Optional


@attr.s(hash=True)
class VGTask(object):
    name = attr.ib()  # type: Text
    func_to_run = attr.ib(hash=False, repr=False)  # type: Callable
    uuid = attr.ib(init=False, repr=False, factory=lambda: str(uuid.uuid4()))

    callback = None
    error_callback = None
    complete_callback = None

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
        logger.debug("%s called %s" % (self.__class__.__name__, self.name))
        res = None
        try:
            if callable(self.func_to_run):
                res = self.func_to_run()
            if callable(self.callback):
                self.callback(res)
        except Exception as e:
            logger.error("Failed to execute task! \n\t %s" % self.name)
            logger.exception(e)
            if callable(self.error_callback):
                self.error_callback(e)
        finally:
            if callable(self.complete_callback):
                self.complete_callback()
        return res
