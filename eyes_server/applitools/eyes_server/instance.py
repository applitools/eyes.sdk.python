from __future__ import absolute_import

import atexit

from .server import SDKServer, executable_path

instance = SDKServer(executable_path)
atexit.register(instance.close)  # python2 destructs objects in non-specified manner
