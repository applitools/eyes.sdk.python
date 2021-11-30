from __future__ import absolute_import

import atexit

from .server import SDKServer

instance = SDKServer(singleton=False)
atexit.register(instance.close)  # python2 destructs objects in non-specified manner
