#!/usr/bin/env python3
"""Write SIZE bytes slowly so the consumer starves."""
import os
import sys
import time

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 512 * 1024
CHUNK = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
DELAY = float(sys.argv[3]) if len(sys.argv) > 3 else 0.003
blob = b"S" * CHUNK
left = SIZE
while left > 0:
    n = min(CHUNK, left)
    os.write(1, blob[:n])
    left -= n
    time.sleep(DELAY)
