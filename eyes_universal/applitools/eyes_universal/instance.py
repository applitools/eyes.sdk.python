from __future__ import absolute_import

import atexit

from .server import SDKServer

instance = SDKServer()
atexit.register(instance.close)  # python2 destructs objects in non-specified manner
