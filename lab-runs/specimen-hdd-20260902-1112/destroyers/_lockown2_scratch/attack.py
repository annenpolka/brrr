#!/usr/bin/env python3
"""lockown second-pass attacks. Does not import lockown for replica."""
from __future__ import annotations

import importlib.machinery
import importlib.util
import inspect
import io
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-lockown")
CLI = ROOT / "lockown"
SCR = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_lockown2_scratch")


def load_mod():
    loader = importlib.machinery.SourceFileLoader("lockown_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


LO = load_mod()


def run_cli(args, stdin=None, extra_env=None):
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
        input=stdin,
    )


def banner(s):
    print(f"\n===== {s} =====")


banner("1. caller-labeled names: run_scene reprints argv names")
for owner, waiter, lock in [
    ("holder", "blocked", "L"),
    ("alice", "bob", "M"),
    ("", "blocked", "L"),
    ("x", "x", "L"),
    ("holder", "holder", "L"),
    ("A" * 200, "B" * 200, "LOCK" * 10),
    ("holder\twith tab", "blocked\nwith nl", "L"),
    ("  spaces  ", " waiter ", " L "),
]:
    try:
        snap = LO.run_scene(owner_name=owner, waiter_name=waiter, lock_name=lock, release_after=True)
        print(repr(snap), "match_owner", snap["owner"] == owner, "match_waiter", snap["waiter"] == waiter, "held", snap["held"])
    except Exception as e:
        print("ERR", type(e).__name__, e, "for", repr(owner), repr(waiter), repr(lock))


banner("2. replica of format_rows without lock")
def replica_rows(owner="holder", waiter="blocked", lock="L", held="true"):
    return {"lock": lock, "owner": owner, "waiter": waiter, "held": held}

def format_rows_replica(rows):
    return "\n".join(f"{k}  {rows[k]}" for k in ("lock", "owner", "waiter", "held"))

snap = LO.run_scene()
rep = replica_rows()
print("scene", snap)
print("replica", rep)
print("equal", snap == rep)
print("format equal", LO.format_rows(snap) == format_rows_replica(rep))


banner("3. extra waiters: only first printed")
lock = LO.OwnedLock("L")
entered = []
go = threading.Event()
held = threading.Event()
released = threading.Event()

def owner():
    lock.acquire()
    held.set()
    go.wait(3)
    lock.release()
    released.set()

def waiter(name):
    held.wait(2)
    lock.acquire()
    entered.append(name)
    if lock.snapshot()["owner"] == name:
        lock.release()

t0 = threading.Thread(target=owner, name="O", daemon=True)
waiters = [threading.Thread(target=waiter, args=(n,), name=n, daemon=True) for n in ("W1", "W2", "W3")]
t0.start()
held.wait(2)
for t in waiters:
    t.start()
# wait until 3 waiters recorded
t_end = time.monotonic() + 2
while time.monotonic() < t_end:
    with lock._meta:
        n = len(lock._waiters)
    if n >= 3:
        break
    time.sleep(0.01)
snap = lock.snapshot()
with lock._meta:
    waiters_list = list(lock._waiters)
print("internal_waiters", waiters_list)
print("snapshot", snap)
print("only_first", snap["waiter"] == waiters_list[0] if waiters_list else None)
go.set()
t0.join(2)
for t in waiters:
    t.join(2)


banner("4. waiter labeled BEFORE Lock.acquire blocks")
lock = LO.OwnedLock("L")
stage = []
held = threading.Event()
proceed_acquire = threading.Event()
let_go = threading.Event()

orig_acquire = lock._lock.acquire

def instrumented_acquire(*a, **k):
    stage.append(("before_real_acquire", list(lock._waiters), lock._owner, lock.waiter_entered.is_set()))
    proceed_acquire.wait(2)
    ok = orig_acquire(*a, **k)
    stage.append(("after_real_acquire", ok))
    return ok

lock._lock.acquire = instrumented_acquire  # type: ignore

def owner():
    # owner uses uninstrumented path? we instrumented _lock.acquire so owner also hits it.
    # Use a different approach: only instrument after owner holds.
    pass

# reset: do owner first with real acquire, then instrument
lock = LO.OwnedLock("L")
held = threading.Event()
let_go = threading.Event()

def owner2():
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

t = threading.Thread(target=owner2, name="holder", daemon=True)
t.start()
held.wait(2)
orig_acquire = lock._lock.acquire
gate = threading.Event()
saw = []

def inst(*a, **k):
    saw.append(("at_real_acquire_entry", list(lock._waiters), lock._owner, lock.waiter_entered.is_set()))
    gate.wait(2)
    return orig_acquire(*a, **k)

lock._lock.acquire = inst  # type: ignore

def waiter2():
    lock.acquire()

tw = threading.Thread(target=waiter2, name="blocked", daemon=True)
tw.start()
ok_event = lock.waiter_entered.wait(2)
# at this point waiter_entered is set but we have not let real acquire proceed
snap = lock.snapshot()
print("waiter_entered_before_real_acquire", ok_event)
print("snapshot_before_real_acquire", snap)
print("saw_at_real_entry", saw)
print("thread_is_alive", tw.is_alive())
# inspect stack-ish: waiter is waiting on gate, not on the lock
gate.set()
let_go.set()
t.join(2)
# waiter may still be blocked on lock; release already happened so it may acquire
tw.join(2)
print("snapshot_after", lock.snapshot())


banner("5. held is owner is not None, not lock.locked()")
lock = LO.OwnedLock("L")
lock.acquire()
print("after_acquire", lock.snapshot(), "locked()", lock._lock.locked())
# lie: clear owner without release
with lock._meta:
    lock._owner = None
print("owner_cleared", lock.snapshot(), "locked()", lock._lock.locked())
# restore and release
with lock._meta:
    lock._owner = threading.current_thread().name
lock.release()
print("after_release", lock.snapshot(), "locked()", lock._lock.locked())
# lie: set owner without acquire
with lock._meta:
    lock._owner = "sticker"
print("sticker_owner_no_acquire", lock.snapshot(), "locked()", lock._lock.locked())
with lock._meta:
    lock._owner = None


banner("6. timeout removes waiter (nearest op unnamed again)")
lock = LO.OwnedLock("L")
held = threading.Event()
let_go = threading.Event()
timed = threading.Event()
result = {}

def owner3():
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

def waiter3():
    held.wait(2)
    lock.waiter_entered.wait(2)
    # wait until snapshot-able then timeout
    ok = lock.acquire(timeout=0.2)
    result["ok"] = ok
    result["snap"] = lock.snapshot()
    timed.set()

t = threading.Thread(target=owner3, name="holder", daemon=True)
t.start()
held.wait(2)
# start waiter with timeout only after we snapshot while blocked
# Actually waiter3 calls acquire(timeout=0.2) which will label then timeout
tw = threading.Thread(target=waiter3, name="blocked", daemon=True)
# Better: label-then-timeout via run_scene release_after False
tw.start()
lock.waiter_entered.wait(2)
snap_during = lock.snapshot()
timed.wait(2)
print("during_wait", snap_during)
print("after_timeout", result)
let_go.set()
t.join(2)
tw.join(2)


banner("7. inspect acquire/snapshot co_names")
print("acquire.co_names", LO.OwnedLock.acquire.__code__.co_names)
print("acquire.co_varnames", LO.OwnedLock.acquire.__code__.co_varnames)
print("snapshot.co_names", LO.OwnedLock.snapshot.__code__.co_names)
print("snapshot.co_varnames", LO.OwnedLock.snapshot.__code__.co_varnames)
print("_label.co_names", LO._label.__code__.co_names)
src = Path(CLI).read_text()
for needle in ["jstack", "gradle", "ident", "native_id", "ident", "sys._current_frames", "locked(", "RLock"]:
    print(f"contains {needle!r}", needle in src)
print("source has threading.Lock", "threading.Lock" in src)


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
    print("args", args, "rc", p.returncode, "stdout", repr(p.stdout[:120]), "stderr", repr(p.stderr[:160]))

p = run_cli([], stdin="owner  holder\nwaiter  blocked\n")
print("stdin_ignored rc", p.returncode, "stdout_eq_replica", p.stdout == format_rows_replica(replica_rows()) + "\n")

p = run_cli(["--contrast"], stdin="x")
print("contrast_stdin rc", p.returncode, "stdout", repr(p.stdout))


banner("9. same-name two threads: owner==waiter")
snap = LO.run_scene(owner_name="same", waiter_name="same")
print(snap, "owner==waiter", snap["owner"] == snap["waiter"])


banner("10. rename thread after start, before acquire")
lock = LO.OwnedLock("L")
held = threading.Event()
renamed = threading.Event()
let_go = threading.Event()
got = {}

def owner4():
    threading.current_thread().name = "renamed-owner"
    lock.acquire()
    held.set()
    let_go.wait(3)
    lock.release()

def waiter4():
    held.wait(2)
    threading.current_thread().name = "renamed-waiter"
    renamed.set()
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


banner("11. CLI cannot take names; always holder/blocked")
# already shown replica
print("main defaults", inspect.signature(LO.run_scene))
print("main() argv only --contrast")


banner("12. timeout_probe owner/waiter hardcoded unnamed")
print(LO.timeout_probe(0.05))


banner("13. snapshot waiter is waiters[0] even if owner is that name")
lock = LO.OwnedLock("L")
with lock._meta:
    lock._owner = "alice"
    lock._waiters = ["alice", "bob"]
print("hand_join_meta", lock.snapshot())


banner("14. native_id not used")
print("native_id in source", "native_id" in src, "ident" in src)


banner("done")
