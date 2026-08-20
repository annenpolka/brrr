#!/usr/bin/env python3
"""Leave a descendant running after this process exits."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ready = Path(sys.argv[1]) if len(sys.argv) > 1 else None
subprocess.Popen(
    [
        sys.executable,
        "-c",
        "import signal,time\nsignal.signal(signal.SIGHUP, signal.SIG_IGN)\nsignal.signal(signal.SIGINT, signal.SIG_IGN)\ntime.sleep(45)\n",
    ],
    start_new_session=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
)
if ready is not None:
    ready.parent.mkdir(parents=True, exist_ok=True)
    ready.write_text(f"{os.getpid()}\n", encoding="utf-8")
time.sleep(float(os.environ.get("CLING_HOLD", "0.55")))
