from __future__ import absolute_import

__version__ = "0.15"


def get_instance():
    from . import instance

    return instance.instance
