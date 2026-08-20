#!/usr/bin/env python3
"""Pipeline stage whose slow work is a child writing to inherited stdout.

Pinch would name this parent (the stage). Hitch would see child-wait.
The knot of the whole tree is the child — the wait-source of the pipe.
"""
from __future__ import annotations

import os
import sys
import time

chunks = int(sys.argv[1]) if len(sys.argv) > 1 else 24
delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
pid = os.fork()
if pid == 0:
    time.sleep(0.05)
    blob = b"H" * 4096
    for _ in range(chunks):
        os.write(1, blob)
        time.sleep(delay)
    os._exit(0)
os.waitpid(pid, 0)
