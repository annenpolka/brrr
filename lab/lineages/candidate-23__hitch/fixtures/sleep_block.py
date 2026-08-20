#!/usr/bin/env python3
"""A 'test' whose only work is sleeping."""
from __future__ import annotations

import sys
import time

delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
time.sleep(delay)
