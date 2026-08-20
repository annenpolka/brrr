#!/usr/bin/env python3
"""Write SIZE bytes to stdout as fast as possible."""
import os
import signal
import sys

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 8 * 1024 * 1024
CHUNK = 65536
blob = b"P" * CHUNK
left = SIZE
while left > 0:
    n = min(CHUNK, left)
    os.write(1, blob[:n])
    left -= n
