#!/usr/bin/env python3
"""Read stdin slowly so the producer fills the pipe."""
import os
import sys
import time

CHUNK = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
DELAY = float(sys.argv[2]) if len(sys.argv) > 2 else 0.003
total = 0
while True:
    data = os.read(0, CHUNK)
    if not data:
        break
    total += len(data)
    time.sleep(DELAY)
sys.stderr.write(f"slow_consumer read {total} bytes\n")
