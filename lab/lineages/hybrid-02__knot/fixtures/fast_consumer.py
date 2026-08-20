#!/usr/bin/env python3
"""Drain stdin as fast as possible."""
import os
import sys

total = 0
while True:
    data = os.read(0, 65536)
    if not data:
        break
    total += len(data)
sys.stderr.write(f"fast_consumer drained {total} bytes\n")
