from __future__ import absolute_import

from .server import SDKServer, executable_path

instance = SDKServer(executable_path)
