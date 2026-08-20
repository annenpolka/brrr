#!/usr/bin/env python3
"""Wrapper sleeps on a child. The wait-source is the child, not this parent."""
from __future__ import annotations

import subprocess
import sys

delay = sys.argv[1] if len(sys.argv) > 1 else "0.35"
subprocess.check_call(["sleep", delay])
