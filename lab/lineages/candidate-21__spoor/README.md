# spoor

**Waitpid is a lie.** A command is not done when its pid reaps. It is done when descendants, temp files, and the watched tree go still. spoor records that wake.

The filesystem is a shared heap that commands and tests allocate into. spoor is a leak detector for that heap: late writes after exit, leaked children, leftover paths, tests that collided on the same file, and generated artifacts whose sources have moved on.

## Install / run

Python 3.10+, stdlib only. Optional: `fswatch` for live FS events (poll + git bookend always work).

```bash
chmod +x ./spoor
./spoor run -- cargo test
./spoor inspect .
./demo.sh
```

JSON is the composable form (`--out report.json` or `--json`). Human report goes to stderr.

## Examples

### 1. A process that writes *after* it exits

```bash
./spoor run --watch /tmp/out -- python3 fixtures/afterexit.py /tmp/out
```

waitpid returns in ~180ms. spoor stays until the world is still, then reports:

```
quiesce: 739ms after waitpid  LATE ACTIVITY
late writes (1):
  +0.215s  source    /tmp/out/late.txt
```

### 2. Tests sharing one temp path (isolation failure)

```bash
./spoor run --sandbox-tmp -- python3 fixtures/collide.py
```

`--sandbox-tmp` gives the command a private `TMPDIR`. Two libtest-shaped tests write the same file; spoor attributes writes at test-completion boundaries:

```
test collisions (1 paths written by >1 test):
  $TMPDIR/spoor-collide-shared.txt
    tests: collide::alpha, collide::beta
```

### 3. Generated artifacts vs their declared sources

```bash
./spoor inspect /Users/annenpolka/ghq/github.com/annenpolka/voidtrace
```

Reads `Generated from specs/main.pkl`, JSON `"source"`, and sibling inheritance. On voidtrace this currently reports **14 FRESH** generated files (spec-gen is up to date) plus mtime write-bursts that reconstruct a `just spec-gen` cluster.

```bash
./spoor inspect /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
# FRESH Engine/Tests/TenaoshiEngineTests/OraclesGenerated.swift
# source specs/tenaoshi.pkl  generator tools/spec-gen.ts
```

Wrap a real test:

```bash
./spoor run --sandbox-tmp --cwd /path/to/kizu -- \
  cargo test --lib scan_scars_finds_ask -- --test-threads=1
# leaked=0 late=0 git residue=none  → the suite cleaned up after itself
```

## Flags (run)

| flag | what |
| --- | --- |
| `--sandbox-tmp` | private `TMPDIR`; all temp residue is then yours |
| `--watch PATH` | extra tree to snapshot/watch (do not default-watch cwd; too slow to arm) |
| `--settle-ms` | stillness window after the last FS event (default 350) |
| `--kill-leaked` | SIGTERM descendants that outlived waitpid |
| `--json` / `--out FILE` | machine report |
| `--quiet` | do not tee child stdio |

Exit: 0 if spoor itself succeeded (child status is in the report). `--forward-exit` to pass the child's code through. Timeout → 124.
