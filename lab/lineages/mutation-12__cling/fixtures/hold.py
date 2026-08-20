#!/usr/bin/env python3
"""Stay a stable pid long enough to attach, then exec the rest of argv.

cling attached to this pid follows the exec (same pid, new command).
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

if len(sys.argv) < 3:
    print("usage: hold.py READY_FILE -- COMMAND [ARGS...]", file=sys.stderr)
    raise SystemExit(2)
ready = Path(sys.argv[1])
args = sys.argv[2:]
if args and args[0] == "--":
    args = args[1:]
if not args:
    print("hold.py: missing command", file=sys.stderr)
    raise SystemExit(2)
ready.parent.mkdir(parents=True, exist_ok=True)
ready.write_text(f"{os.getpid()}\n", encoding="utf-8")
time.sleep(float(os.environ.get("CLING_HOLD", "0.40")))
os.execvp(args[0], args)
