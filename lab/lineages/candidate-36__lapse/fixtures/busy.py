#!/usr/bin/env python3
"""Burn CPU so proper time tracks the awake clock."""
import sys
import time

dur = float(sys.argv[1]) if len(sys.argv) > 1 else 0.3
end = time.perf_counter() + dur
n = 0
while time.perf_counter() < end:
    n += 1
print(n)
