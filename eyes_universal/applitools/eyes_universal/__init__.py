from __future__ import absolute_import

__version__ = "0.2.0"


def get_instance():
    from . import instance

    return instance.instance
