#!/usr/bin/env python3
"""Sleep without aging (blocked proper-time ≈ 0)."""
import sys
import time

time.sleep(float(sys.argv[1]) if len(sys.argv) > 1 else 0.4)
