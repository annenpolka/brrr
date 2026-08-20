#!/usr/bin/env python3
"""Age quickly, then freeze: worldline should switch # to ~."""
import sys
import time

busy = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
block = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
end = time.perf_counter() + busy
n = 0
while time.perf_counter() < end:
    n += 1
time.sleep(block)
print(n)
