#!/usr/bin/env python3
"""Child blocks on a pipe; parent sleeps, then writes one byte."""
from __future__ import annotations

import os
import sys
import time

delay = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
r, w = os.pipe()
pid = os.fork()
if pid == 0:
    os.close(w)
    os.read(r, 1)
    os._exit(0)
os.close(r)
time.sleep(delay)
os.write(w, b"x")
os.close(w)
os.waitpid(pid, 0)
