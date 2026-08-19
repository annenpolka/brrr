# candidate-25 — coast

## Primitive

The interval between `waitpid` returning and the machine (process group + file contents under watched trees) becoming still — late writes, straggler children, and intra-run path generations as one object.

## Four primitives considered

1. **coast** (implemented) — post-`waitpid` settling of processes and files. Tests, builds, leftover servers, torn writes, "sleep 2 after the test".
2. **clot** — infer streaming vs batch from byte-arrival timing between pipeline stages. Pipes, processes, time.
3. **kiln** (discarded, conventional) — artifacts that should have rebuilt but did not. `ninja -d explain`, Bazel, `make -d`.
4. **witness** (discarded, conventional) — undeclared inputs from observed reads. Sandboxes, tup, Bazel, `strace` + Makefile.

`clot` remains a strong mutation. `coast` was chosen because `wait(1)` does not cover the side-effect cloud, and developers already write `sleep 1` after commands without measuring why.

## Why this might not exist

Unix gives you `waitpid` for a PID, `wait` for a known child, `sync` for disks, and `docker wait` for a container. None of those answers:

> the test printed "ok" and exited 0; which files still changed, which children still lived, and for how long?

Flakes from pytest-xdist, esbuild workers, Django's live_server, and `make -j` are often **coast bugs**: a later assertion reads a non-final generation, or a later test binds a port the previous test's child still holds. The workaround is cargo-cult `sleep`. The missing verb is to *name and measure the coast*.

## How to run

From the worktree root:

```bash
./demo.sh
python3 tests/test_coast.py
./coast run --root DIR -- -- bash fixtures/late_write.sh DIR
./coast wait --max-coast-ms 400 -- -- bash fixtures/straggler.sh DIR
```

## Empirical transcript

### Before the improvement

`python3 -m py_compile coast.py` under `--root .`:

```
exit 0 in 0.066s  COAST 0.000s  settled
run events: __pycache__/coast.cpython-314.pyc   (bytecode, during run)
late writes: (none)
```

Honest: `py_compile` waits for the write. Then the own test suite:

```
./coast run --root . -- python3 tests/test_coast.py
exit 0 in 3.475s  COAST 0.000s  settled
late writes: (none)
stragglers: pid (Python) died +37ms
```

**Surprise:** every interesting write (`late.txt`, `bundle.js` layers, tempfile goldens) landed in `/var/folders/.../T/tmp*` — outside `--root .`. Coast of the *source tree* was zero while the *machine* was busy. Process names from `ps` collapsed to `(Python)`.

Also, an earlier implementation called `Popen.communicate()` after `waitpid`. Children inherit the stdout pipe; `communicate` blocked until they closed it — swallowing the coast into a silent wait. That bug *is* the primitive.

### After `--isolate-tmp` + `lsof`

Private `TMPDIR`, extra watch root, leftover `lsof` (cwd + open files), late artifact **HAZARD** vs cache notes.

Own tests with `--isolate-tmp`:

```
exit 0 in 4.993s  COAST 0.000s  settled
rewritten during watch:
  tmp:tmpflo3j3yr/tree/bundle.js  4 layers [r,r,r,r]
  tmp:tmpsuqo1nsl/store/isolated-tmp/secret.bin  3 layers [r,r,r]
run events included tmp:…/late.txt, tmp:…/out.txt (create then delete)
```

Nested coasts become visible as layers under the outer isolated tmp. No *late* writes from the outer view — inner `coast` already waited — which is the correct happens-before.

Direct fixture after the fix:

```
./coast run --isolate-tmp -- python3 fixtures/tmp_late.py
exit 0 in 0.029s  COAST 0.368s  settled
HAZARD late artifacts:
  +0.368s  write  tmp:secret.bin
straggler: Python -c '…Path(isolated-tmp/secret.bin).write_text("late")'
           (full argv via lsof, not "(Python)")

./coast wait --max-coast-ms 400 -- bash fixtures/straggler.sh
exit 124
straggler pid sleep 30  alive
           cwd  <repo>
           open /bin/sleep
           open /dev/null
```

Layer stack on a bundler-like rewrite (no coast, all during run):

```
bundle.js  3 layers
    1  t=0.050s  run  create  3a1f3e32526c
    2  t=0.099s  run  write   e333ef2be9c7
    3  t=0.195s  run  write   4b664bca8270
```

## Dogfood targets

- `fixtures/clean.sh`, `late_write.sh`, `rewrite.sh`, `straggler.sh`, `tmp_late.py`
- `python3 -m py_compile coast.py` (bytecode during run, zero coast)
- `python3 tests/test_coast.py` as the command under coast, with and without `--isolate-tmp`
- `./demo.sh`

## Surprises

- `communicate()` after `waitpid` *is* an accidental coast-hider. Drain pipes on a thread; do not wait for EOF from inherited stdout.
- Background `sleep` in a non-interactive bash script stays in the session; `ps` still sometimes labels Python children `(Python)` until `lsof -c`.
- Watching the repo root is the wrong default for test tools. They live in `TMPDIR`.
- Deletes originally lost their `watch` label because the post-image lacked the file (fixed: take the label from the pre-image).
- Outer coast of an inner coast-run test suite has *layers* and *deletes* but not *late* writes: the inner tool already waited. Coast does not always nest as "more coast".

## Failures

- Polling (~15ms) can miss two rewrites of the same path inside one interval. Demo fixtures sleep; a real esbuild burst may collapse generations.
- `setsid` daemons leave the watched group and become invisible. Documented, not solved.
- Whole-machine FSEvents is not used; without `--root` / `--isolate-tmp` / `--also`, writes elsewhere are silent.
- macOS `lsof` on a dying PID is racy; inspect is best-effort.
- `coast wait` with a leaked `sleep 30` will leak unless the caller uses `--kill-stragglers` or kills leftover PIDs from JSON.

## Suggested mutations

- **clot** as a subcommand: timestamp byte chunks between `|` stages; report which stage buffered the pipeline.
- Read-hazard: if a path has ≥2 layers, flag reads (via `lsof` sampling) that happened before the final layer.
- `coast gate --max-artifact-coast-ms 50` for CI: fail only on HAZARD late artifacts, ignore bytecode.
- Overlay / FSEvents backend so generations are not poll-sampled.
- Attribute each layer to a PID (sample `lsof` on the path at the moment of the write).
- Compress clock: rerun with `libfaketime` and see whether coast duration is wall-clock waits or CPU work.

## Kill / keep

**Keep.** The verb is small (`wait` for the side-effect cloud), the dogfood surprise (`TMPDIR` is where tests actually write) changed the tool, and `coast wait` is composable in scripts that today say `sleep 2`.
