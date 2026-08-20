#!/usr/bin/env python3
"""Long-lived subject for SIGINT / snapshot. Does not die on SIGHUP or SIGINT."""

from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path

signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGINT, signal.SIG_IGN)

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fixtures/work/linger")
out.mkdir(parents=True, exist_ok=True)
beat = out / "heartbeat.txt"
ready = out / "ready"
ready.write_text(f"{os.getpid()} {os.getpgrp()}\n", encoding="utf-8")
fh = open(beat, "w", encoding="utf-8")
n = 0
while n < 80:
    n += 1
    fh.write(f"{n}\n")
    fh.flush()
    os.fsync(fh.fileno())
    time.sleep(0.25)
fh.close()
