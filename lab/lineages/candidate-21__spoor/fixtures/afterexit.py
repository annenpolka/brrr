#!/usr/bin/env python3
"""Write during the process, then spawn a writer that mutates disk AFTER we exit."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fixtures/work/afterexit")
out.mkdir(parents=True, exist_ok=True)
during = out / "during.txt"
late = out / "late.txt"
during.write_text("during\n", encoding="utf-8")
print("test afterexit::during ... ok", flush=True)

late_script = (
    "import signal, time, pathlib\n"
    "signal.signal(signal.SIGHUP, signal.SIG_IGN)\n"
    "signal.signal(signal.SIGINT, signal.SIG_IGN)\n"
    "time.sleep(0.28)\n"
    f"pathlib.Path({str(late)!r}).write_text('late\\n', encoding='utf-8')\n"
)
subprocess.Popen(
    [sys.executable, "-c", late_script],
    start_new_session=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    stdin=subprocess.DEVNULL,
)
time.sleep(0.08)
print("test afterexit::spawned-late-writer ... ok", flush=True)
