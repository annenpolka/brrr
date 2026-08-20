#!/usr/bin/env python3
"""Leave a descendant running after this process exits."""

from __future__ import annotations

import subprocess
import sys
import time

print("test leak::spawn ... ok", flush=True)
subprocess.Popen(
    [sys.executable, "-c", "import signal,time\nsignal.signal(signal.SIGHUP, signal.SIG_IGN)\ntime.sleep(45)\n"],
    start_new_session=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
)
time.sleep(0.08)
print("test leak::still-running ... ok", flush=True)
