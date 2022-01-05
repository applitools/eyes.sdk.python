from __future__ import absolute_import

__version__ = "1.0.1"


def get_instance():
    from . import instance

    return instance.instance
