#!/usr/bin/env python3
"""Keep a regular file open, then exit without unlinking it."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fixtures/work/openleft")
out.mkdir(parents=True, exist_ok=True)
held = out / "held.txt"
ready = out / "ready"
fh = open(held, "w", encoding="utf-8")
fh.write("held-open\n")
fh.flush()
ready.write_text(f"{os.getpid()}\n", encoding="utf-8")
time.sleep(float(os.environ.get("CLING_HOLD", "0.70")))
fh.write("closed-on-exit\n")
fh.close()
