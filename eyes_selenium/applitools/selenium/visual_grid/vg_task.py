import typing
import uuid

import attr

from applitools.common import TestResults, logger

if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Text


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
                logger.debug(
                    "VGTask().func_to_run: {}".format(self.func_to_run.__name__)
                )
                res = self.func_to_run()
            if callable(self.callback):
                logger.debug("VGTask().callback: {}".format(self.callback.__name__))
                self.callback(res)
        except Exception as e:
            logger.error("Failed to execute task! \n\t %s" % self.name)
            logger.exception(e)
            if callable(self.error_callback):
                logger.debug(
                    "VGTask().error_callback: {}".format(self.error_callback.__name__)
                )
                self.error_callback(e)
        finally:
            if callable(self.complete_callback):
                logger.debug(
                    "VGTask().complete_callback: {}".format(
                        self.complete_callback.__name__
                    )
                )
                self.complete_callback()
        return res
