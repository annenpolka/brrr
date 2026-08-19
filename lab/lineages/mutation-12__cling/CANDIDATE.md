# mutation-12 — cling

## Primitive

Attach to a pid / process group you did **not** spawn. The command's true end is still filesystem+process quiescence; SIGINT is a first-class end that reports the same wake (late writes, leaked children, leftover paths, open-file heap) **without killing the subject**.

## Four primitives considered

1. Keep `spoor run` and add `--pid` as a flag. *Discarded: that keeps the spawn assumption at the centre.*
2. Invert: `spoor replay` CI gate. *Ancestor's suggested mutation; not this flip.*
3. **cling / attach-to-running** — implemented. The missing verb is "latch on", not "wrap".
4. Pipe-hang autopsy. *Still a later mutation.*

## Why this might not exist

`wait $pid` and FreeBSD `pwait` only reap. `strace -p` / `fs_usage -p` stream syscalls, not a queryable residue object. `spoor` (candidate-21) records the wake but **insists on being the parent**, so it cannot attach to a cargo test you already started, a daemon, or a pipeline whose shell has not died yet. Nobody treats **the heap of a process you walked in on** as something you can wait on, interrupt, and diff.

## How to run

From this worktree:

```bash
./cling --help
./cling snapshot $PID
./cling --watch /tmp/out $PID
./cling --group $PID
./demo.sh
```

## Empirical transcript

*(filled after the first demo + dogfood)*

## Dogfood targets

- fixtures: `afterexit.py`, `leak.py`, `groupkid.py`, `linger.py`, `openleft.py`, `hold.py`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (`cargo test --lib` via `hold.py` exec)
- live `snapshot` of a process we did not start

## Surprises

## Failures

## Suggested mutations

- Per-test TMPDIR still wants spawn (cannot inject env). Pair cling with a wrapper that *does* exec after setting env.
- `pgrep -f cargo | cling` already works via stdin; a `--follow-exec` kevent NOTE_EXEC breadcrumb would show the hold→cargo handoff.
- Pipe-hang autopsy (ancestor primitive 4) attaches naturally: the pids already exist.

## Kill / keep

Pending demo.
