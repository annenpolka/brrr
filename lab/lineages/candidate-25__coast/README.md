# coast

A command's `waitpid` is not the end of the machine.

`coast` runs a process, keeps watching its process group and a file tree after the leader exits, and reports the **coast**: late writes, straggler children, and every generation of a path rewritten during the run.

```
waitpid() returned.
the machine was not still.
```

## Primitive

The interval between `waitpid` returning and the machine (child PIDs + file contents) becoming still, treated as a first-class diagnostic object.

## Install / run

Python 3.9+, stdlib only.

```bash
./coast run -- <command>
./coast wait -- <command>     # exit 124 if the machine does not settle
./coast show [path]           # last run, or the layer stack of one path
```

## Examples

### 1. A test that writes after it "finished"

```bash
mkdir -p /tmp/c/tree
./coast run --root /tmp/c/tree --no-passthrough -- \
  bash fixtures/late_write.sh /tmp/c/tree
```

```
exit 0 in 0.028s  COAST 0.367s  settled
HAZARD late artifacts:
  +0.367s        6b  create  late.txt
```

The parent printed `parent-done` and exited. A child wrote `late.txt` 367ms later. That is the flake where a later test, or you, inspect the tree and see a file the exiting process had not yet produced.

### 2. A bundler that overwrites the same path

```bash
./coast run --root /tmp/c/tree --no-passthrough -- \
  bash fixtures/rewrite.sh /tmp/c/tree
./coast show bundle.js
```

```
rewritten during watch:
  bundle.js  3 layers [r,r,r]

bundle.js  3 layers
    1  t=0.050s  run    create  artifact   3a1f3e32526c
    2  t=0.099s  run    write   artifact   e333ef2be9c7
    3  t=0.195s  run    write   artifact   4b664bca8270
```

After a failed test you usually see generation 3. The assertion may have read generation 2.

### 3. Hidden `/tmp` leftovers, and a composable gate

Commands stash state in `TMPDIR`. `--isolate-tmp` gives the command a private temp tree and watches it.

```bash
./coast run --root /tmp/c/tree --isolate-tmp --no-passthrough -- \
  python3 fixtures/tmp_late.py
```

```
HAZARD late artifacts:
  +0.368s        5b  write   tmp:secret.bin
```

`coast wait` is `wait(1)` for the side-effect cloud: it exits `124` if stragglers are still alive at `--max-coast-ms`.

```bash
./coast wait --max-coast-ms 400 -- bash fixtures/straggler.sh /tmp/c/tree
# -> 124, leftover sleep still running, cwd and open files from lsof
```

## Flags worth knowing

| flag | why |
| --- | --- |
| `--root DIR` | tree to watch (default: cwd) |
| `--also DIR` | extra tree (repeatable) |
| `--isolate-tmp` | private `TMPDIR` + watch it |
| `--kill-stragglers` | SIGTERM/KILL leftovers after the observation window |
| `--json` / `--json-out FILE` | machine-readable report |
| `--quiet-ms` / `--max-coast-ms` | stillness vs give-up |

Do not `communicate()` a pipe until EOF after the leader exits. Children inherit stdout; holding that pipe **is** coast.
