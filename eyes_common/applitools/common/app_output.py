import attr

from .utils.json_utils import JsonInclude

__all__ = ("AppOutput",)


@attr.s
class AppOutput(object):
    title = attr.ib(metadata={JsonInclude.THIS: True})
    screenshot64 = attr.ib(repr=False, metadata={JsonInclude.NON_NONE: True})
    screenshot_url = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
    dom_url = attr.ib(default=None, metadata={JsonInclude.NON_NONE: True})
