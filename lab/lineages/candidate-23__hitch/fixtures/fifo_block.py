#!/usr/bin/env python3
"""Reader blocks on a FIFO; writer appears after a delay."""
from __future__ import annotations

import os
import sys
import tempfile
import time

delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8
path = tempfile.mktemp(prefix="hitch-fifo-")
os.mkfifo(path)
# Hold both ends open so read() blocks on an empty fifo (open() itself
# would block *before* the fd exists, and lsof would see nothing).
keeper = os.open(path, os.O_RDWR)
reader = os.fork()
if reader == 0:
    os.close(keeper)
    with open(path, "rb") as f:
        f.read(1)
    os._exit(0)
time.sleep(delay)
os.write(keeper, b"x")
os.waitpid(reader, 0)
os.close(keeper)
os.unlink(path)
