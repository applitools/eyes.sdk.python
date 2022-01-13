from __future__ import absolute_import

import subprocess
import sys

from .server import executable_path

try:
    exit(subprocess.call([executable_path] + sys.argv[1:]))
except KeyboardInterrupt:
    exit(1)
