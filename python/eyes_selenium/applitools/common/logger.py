"""
Stub module that that supported original log handling.
"""
from applitools.common import deprecated

__all__ = ("StdoutLogger", "FileLogger")


def StdoutLogger(*args, **kwargs):
    """Stub function to avoid breaking existing code"""
    pass


def FileLogger(*args, **kwargs):
    """Stub function to avoid breaking existing code"""
    pass


@deprecated.attribute("logging configuration is not supported anymore")
def set_logger(logger=None):
    """Stub function to avoid breaking existing code"""
    pass
