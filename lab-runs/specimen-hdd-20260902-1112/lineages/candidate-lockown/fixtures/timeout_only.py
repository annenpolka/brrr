#!/usr/bin/env python3
"""Nearest existing operation: Lock.acquire timeout does not name the owner."""

from __future__ import annotations

import threading

lock = threading.Lock()
held = threading.Event()
let_go = threading.Event()


def owner() -> None:
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()


t = threading.Thread(target=owner, name="holder")
t.start()
held.wait(2)
ok = lock.acquire(timeout=0.2)
print(f"acquire_ok  {str(ok).lower()}")
print(f"locked  {str(lock.locked()).lower()}")
print("(timeout does not name the owner)")
if ok:
    lock.release()
let_go.set()
t.join(2)
