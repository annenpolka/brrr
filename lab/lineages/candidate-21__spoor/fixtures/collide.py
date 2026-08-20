#!/usr/bin/env python3
"""Two sequential tests write the same temp path — an isolation failure."""

from __future__ import annotations

import os
import time
from pathlib import Path

tmp = Path(os.environ.get("TMPDIR") or "/tmp")
shared = tmp / "spoor-collide-shared.txt"

shared.write_text("from-a\n", encoding="utf-8")
print("test collide::alpha ... ok", flush=True)
# Real runners leave a gap after the completion line; give the parent a
# chance to snapshot before the next test mutates the same path.
time.sleep(0.20)

shared.write_text("from-b\n", encoding="utf-8")
print("test collide::beta ... ok", flush=True)
time.sleep(0.15)
