from __future__ import absolute_import

__version__ = "2.5.17"


def get_instance():
    from . import instance

    return instance.instance
