#!/usr/bin/env python3
"""Throughput-limited CPU middle stage: burn CPU on each chunk before forwarding."""
import hashlib
import os
import sys

ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
total = 0
while True:
    data = os.read(0, 65536)
    if not data:
        break
    h = data
    for _ in range(ROUNDS):
        h = hashlib.sha256(h).digest()
    os.write(1, data)
    total += len(data)
sys.stderr.write(f"cpu_stage forwarded {total} bytes\n")
