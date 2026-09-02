#!/usr/bin/env python3
from __future__ import annotations

import importlib.machinery
import importlib.util
import inspect
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-lockown")
CLI = ROOT / "lockown"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("lockown_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


LO = load_mod()


def run_cli(args, stdin=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=os.environ.copy(),
        input=stdin,
    )


def banner(s):
    print(f"\n===== {s} =====")


banner("4. waiter labeled before real lock wait — wrap OwnedLock.acquire body order")
# Source-order proof + Event: snapshot after waiter_entered, while acquire still blocking.
# Additionally: insert a gate BETWEEN label and _lock.acquire by wrapping the method.
lock = LO.OwnedLock("L")
held = threading.Event()
let_go = threading.Event()
labeled = []

orig = lock.acquire

def wrapped_acquire(blocking=True, timeout=-1):
    me = LO._label()
    with lock._meta:
        if lock._owner is not None and lock._owner != me:
            if me not in lock._waiters:
                lock._waiters.append(me)
            lock.waiter_entered.set()
            labeled.append(("labeled_pre_wait", me, list(lock._waiters), lock._owner))
    # do not call orig (which would re-label); call _lock.acquire after a pause
    # pause so snapshot can observe labeled waiter while not yet on OS lock
    time.sleep(0.15)
    ok = lock._lock.acquire(blocking, timeout)
    with lock._meta:
        if me in lock._waiters:
            lock._waiters.remove(me)
        if ok:
            lock._owner = me
    return ok

lock.acquire = wrapped_acquire  # instance bind ok for python function? need MethodType
# simpler: don't rebind; use a custom subclass

class GatedLock(LO.OwnedLock):
    def acquire(self, blocking=True, timeout=-1):
        me = LO._label()
        with self._meta:
            if self._owner is not None and self._owner != me:
                if me not in self._waiters:
                    self._waiters.append(me)
                self.waiter_entered.set()
                labeled.append(("labeled_pre_wait", me, list(self._waiters), self._owner))
        time.sleep(0.2)
        ok = self._lock.acquire(blocking, timeout)
        with self._meta:
            if me in self._waiters:
                self._waiters.remove(me)
            if ok:
                self._owner = me
        return ok

lock = GatedLock("L")
labeled.clear()
held = threading.Event()
let_go = threading.Event()

def owner():
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

def waiter():
    held.wait(2)
    lock.acquire()
    if lock.snapshot()["owner"] == "blocked":
        lock.release()

t = threading.Thread(target=owner, name="holder", daemon=True)
tw = threading.Thread(target=waiter, name="blocked", daemon=True)
t.start()
held.wait(2)
tw.start()
assert lock.waiter_entered.wait(2)
# during the 0.2s sleep, waiter is labeled but not on OS lock
snap = lock.snapshot()
print("labeled_events", labeled)
print("snapshot_during_pre_wait_sleep", snap)
print("owner_thread_alive", t.is_alive(), "waiter_alive", tw.is_alive())
# frames: waiter should be in time.sleep not lock.acquire of stdlib
import sys as _sys
frames = _sys._current_frames()
w_frame = frames.get(tw.ident)
names = []
f = w_frame
while f:
    names.append(f.f_code.co_name)
    f = f.f_back
print("waiter_stack_names", names)
let_go.set()
t.join(2)
tw.join(2)


banner("5. held is owner is not None, not lock.locked()")
lock = LO.OwnedLock("L")
lock.acquire()
print("after_acquire", lock.snapshot(), "locked()", lock._lock.locked())
with lock._meta:
    lock._owner = None
print("owner_cleared", lock.snapshot(), "locked()", lock._lock.locked())
with lock._meta:
    lock._owner = threading.current_thread().name
lock.release()
print("after_release", lock.snapshot(), "locked()", lock._lock.locked())
with lock._meta:
    lock._owner = "sticker"
print("sticker_owner_no_acquire", lock.snapshot(), "locked()", lock._lock.locked())
with lock._meta:
    lock._owner = None


banner("6. timeout removes waiter")
lock = LO.OwnedLock("L")
held = threading.Event()
let_go = threading.Event()
result = {}

def owner3():
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

def waiter3():
    held.wait(2)
    ok = lock.acquire(timeout=0.25)
    result["ok"] = ok
    result["snap"] = lock.snapshot()

t = threading.Thread(target=owner3, name="holder", daemon=True)
t.start()
held.wait(2)
tw = threading.Thread(target=waiter3, name="blocked", daemon=True)
tw.start()
assert lock.waiter_entered.wait(2)
snap_during = lock.snapshot()
tw.join(2)
print("during_wait", snap_during)
print("after_timeout", result)
let_go.set()
t.join(2)


banner("6b. run_scene after timeout (release_after False waiter_timeout 0.2)")
# snapshot is taken WHILE waiter blocked, before timeout completes
snap = LO.run_scene(release_after=False, waiter_timeout=0.2)
print("run_scene_timeout_still_pair", snap)


banner("7. inspect co_names")
print("acquire.co_names", LO.OwnedLock.acquire.__code__.co_names)
print("acquire.co_varnames", LO.OwnedLock.acquire.__code__.co_varnames)
print("snapshot.co_names", LO.OwnedLock.snapshot.__code__.co_names)
print("snapshot.co_varnames", LO.OwnedLock.snapshot.__code__.co_varnames)
print("_label.co_names", LO._label.__code__.co_names)
print("run_scene.co_names", LO.run_scene.__code__.co_names)
print("timeout_probe.co_names", LO.timeout_probe.__code__.co_names)
src = Path(CLI).read_text()
for needle in ["jstack", "gradle", "native_id", "ident", "sys._current_frames", "locked(", "RLock", "ident"]:
    print(f"contains {needle!r}", needle in src)


banner("8. CLI argv / stdin / unknown")
cases = [
    [],
    ["--contrast"],
    ["--contrast", "--contrast"],
    ["--help"],
    ["--owner", "alice"],
    ["--waiter", "bob"],
    ["holder", "blocked"],
    ["--lock", "L"],
    ["-"],
    ["/dev/null"],
]
for args in cases:
    p = run_cli(args)
    print("args", args, "rc", p.returncode, "out", repr(p.stdout[:140].replace("\n", "|")), "err", repr(p.stderr[:180].replace("\n", "|")))

p = run_cli([], stdin="owner  holder\nwaiter  blocked\n")
print("stdin_ignored rc", p.returncode, "stdout", repr(p.stdout))

p = run_cli(["--contrast"], stdin="x")
print("contrast_stdin rc", p.returncode, "out", repr(p.stdout.replace("\n", "|")))


banner("10. rename thread after start, before acquire")
lock = LO.OwnedLock("L")
held = threading.Event()
let_go = threading.Event()

def owner4():
    threading.current_thread().name = "renamed-owner"
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

def waiter4():
    held.wait(2)
    threading.current_thread().name = "renamed-waiter"
    lock.acquire()
    if lock.snapshot()["owner"] == "renamed-waiter":
        lock.release()

t = threading.Thread(target=owner4, name="orig-owner", daemon=True)
tw = threading.Thread(target=waiter4, name="orig-waiter", daemon=True)
t.start()
held.wait(2)
tw.start()
lock.waiter_entered.wait(2)
print("snapshot_renamed", lock.snapshot())
let_go.set()
t.join(2)
tw.join(2)


banner("12. timeout_probe hardcoded unnamed")
print(LO.timeout_probe(0.05))


banner("13. hand-join meta: snapshot reprints caller fields")
lock = LO.OwnedLock("L")
with lock._meta:
    lock._owner = "alice"
    lock._waiters = ["alice", "bob"]
print("hand_join_meta", lock.snapshot())
with lock._meta:
    lock._owner = "holder"
    lock._waiters = ["blocked"]
print("sticker_pair", lock.snapshot())
print("format", LO.format_rows(lock.snapshot()))
print("locked?", lock._lock.locked())


banner("14. same-name: waiter never entered because _owner != me is name eq")
try:
    print(LO.run_scene(owner_name="same", waiter_name="same"))
except Exception as e:
    print(type(e).__name__, e)

# prove the predicate is name, not thread identity
lock = LO.OwnedLock("L")
held = threading.Event()
let_go = threading.Event()
err = {}

def o():
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

def w():
    held.wait(2)
    # same name as owner
    threading.current_thread().name = "holder"
    try:
        # nonblocking so we don't deadlock forever
        ok = lock.acquire(blocking=False)
        err["ok"] = ok
        err["snap"] = lock.snapshot()
        err["waiters"] = list(lock._waiters)
    except Exception as e:
        err["e"] = repr(e)

t = threading.Thread(target=o, name="holder", daemon=True)
t.start()
held.wait(2)
tw = threading.Thread(target=w, name="blocked", daemon=True)
tw.start()
tw.join(2)
print("same_name_nonblocking", err, "waiter_entered", lock.waiter_entered.is_set())
let_go.set()
t.join(2)


banner("15. CLI --contrast is canned unnamed rows")
p = run_cli(["--contrast"])
print(p.stdout)
# replica
rep = "ok  false\nheld  true\nowner  unnamed\nwaiter  unnamed\nreason  timeout does not name the owner\n"
print("contrast_eq_replica", p.stdout == rep)


banner("16. launcher vs python3")
p1 = subprocess.run([str(CLI)], capture_output=True, text=True, cwd=str(ROOT))
p2 = subprocess.run([sys.executable, str(CLI)], capture_output=True, text=True, cwd=str(ROOT))
print("launcher_rc", p1.returncode, "py_rc", p2.returncode, "eq", p1.stdout == p2.stdout)


banner("17. empty owner name Thread-N")
try:
    snap = LO.run_scene(owner_name="", waiter_name="blocked")
    print("empty_owner", snap)
except Exception as e:
    print("empty_owner_err", e)


banner("18. snapshot does not read threading.Lock")
print("snapshot source:\n", inspect.getsource(LO.OwnedLock.snapshot))
print("acquire source:\n", inspect.getsource(LO.OwnedLock.acquire))


banner("done")
