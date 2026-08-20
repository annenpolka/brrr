#!/usr/bin/env python3
"""N children burn CPU together: tree proper time can exceed awake time."""
import os
import sys
import time

nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 3
dur = float(sys.argv[2]) if len(sys.argv) > 2 else 0.3
kids = []
for _ in range(nproc):
    pid = os.fork()
    if pid == 0:
        end = time.perf_counter() + dur
        x = 0
        while time.perf_counter() < end:
            x += 1
        os._exit(0)
    kids.append(pid)
for pid in kids:
    os.waitpid(pid, 0)
