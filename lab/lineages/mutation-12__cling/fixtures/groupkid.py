#!/usr/bin/env python3
"""Parent stays attachable, then forks a same-pgid child and exits.

The child writes AFTER the parent dies. cling on the parent pid should
see a late write and a leaked group-mate. cling --group should wait the
child out and report no leak.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

out = Path(sys.argv[1] if len(sys.argv) > 1 else "fixtures/work/groupkid")
out.mkdir(parents=True, exist_ok=True)
(out / "ready").write_text(f"{os.getpid()} {os.getpgrp()}\n", encoding="utf-8")
time.sleep(float(os.environ.get("CLING_HOLD", "0.55")))
child_pid = os.fork()
if child_pid == 0:
    time.sleep(0.26)
    (out / "child-late.txt").write_text("from-child\n", encoding="utf-8")
    # Stay alive so a pid-wait clinger can still see us after settle.
    # --group demos keep the default short so the group can empty.
    time.sleep(float(os.environ.get("CLING_CHILD_STAY", "0.05")))
    os._exit(0)
(out / "parent.txt").write_text(
    f"parent {os.getpid()} child {child_pid} pgid {os.getpgrp()}\n",
    encoding="utf-8",
)
