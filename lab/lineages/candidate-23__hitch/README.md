# hitch

Wait-for graph of a process tree.

`ps` lists processes. `lsof` lists files. Nobody joins them into **who is waiting on whom** — a pipe peer, a silent TCP socket, a fifo, a child that has not exited. `hitch` samples the tree while a command runs (or snapshots a pid) and prints that graph, with time attributed to each edge.

## Primitive

**A wait-for graph**: sleep state joined to pipe / socket / fifo / child-wait peers, folded across samples into snags and idle windows.

## Run

```bash
chmod +x hitch
./hitch -- cargo test
./hitch --json -o report.json -- python3 fixtures/pipe_block.py 1
./hitch -p PID                 # snapshot a live tree
./hitch fold samples.jsonl     # re-fold a JSONL recording
./hitch -- python3 fixtures/pipe_block.py 0.8   # human report on stderr
```

Python 3.9+, plus `ps` and `lsof` (macOS) or `/proc` (Linux). No pip packages.

## Three examples

**1. Where did this pipeline wedge?**

```bash
./hitch --expect-kind pipe-read -- python3 fixtures/pipe_block.py 1
```

Child is `pipe-read` on the parent; parent is `child-wait` on the child — a deadlock-shaped wait until the parent writes.

**2. The test runner is "running" but the CPU is idle.**

```bash
./hitch --json -o /tmp/kizu.json -- cargo test --lib
```

On kizu this reports `cargo -- child-wait --> kizu-fe28… -- sleep --> kernel` for a watcher test that spends its wall-clock in `kevent`/timer, not rustc.

**3. Compose: record then fold.**

```bash
./hitch --samples run.jsonl --ignore-exit -- make test
./hitch --json fold run.jsonl
```

JSONL samples on disk, report on stdout. `hitch` never steals the child's stdout.

`./demo.sh` exercises fixtures plus kizu and voidtrace.
