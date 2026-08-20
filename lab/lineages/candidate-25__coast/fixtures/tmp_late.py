#!/usr/bin/env python3
"""Write a tempfile, then mutate it from a child after the parent exits."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

tmpdir = Path(os.environ["TMPDIR"])
path = tmpdir / "secret.bin"
path.write_text("early\n")
subprocess.Popen(
    [
        sys.executable,
        "-c",
        "import time, pathlib; time.sleep(0.35); pathlib.Path(%r).write_text('late\\n')"
        % str(path),
    ]
)
print("parent-done", flush=True)
