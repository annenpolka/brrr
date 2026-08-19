# hybrid-02 — knot

## Primitive

A command line is both a pipeline and a process tree: one wait-for conversation spanning pipe meters and child-wait / sleep / fifo, naming the wait-source of the whole tree.

## Why this might not exist

`pinch` answers "who waited on this `|`?" `hitch` answers "what is this process tree blocked on?" Developers type command lines that are both at once: `cargo metadata | jq`, `swift build 2>&1 | tee`, `just spec-check` (a hidden pipeline). Concatenating the two tools still produces two reports. The object is one graph and one walk: jq waited on cargo, cargo waited on rustc — **the knot is rustc**.

Discarded as concatenation: run pinch then hitch, or print `pinch.stage` next to `hitch.snags`. That is two scores, never a joint.

## How to run

From the worktree root:

```bash
chmod +x ./knot
./knot selftest
./demo.sh
./knot -- python3 fixtures/hidden_producer.py + python3 fixtures/fast_consumer.py
./knot --json --report out.json --sh 'cargo metadata --format-version 1 | jq ".packages | length"'
./knot -- cargo test --lib -- --list
```

`--` ends options. A lone `+` separates stages. `--sh` splits a quoted pipeline on `|`.

## Empirical transcript

### Before the improvement

`./demo.sh` 0. Fixture shapes (still hold):

| command line | knot | via |
|---|---|---|
| pipe_block (child read, parent sleeps) | writer | pipe-read + child-wait cycle |
| fast_producer \| slow_consumer | slow_consumer | pipe-full |
| slow_producer \| fast_consumer | slow_producer | pipe-empty |
| producer \| cpu \| consumer | cpu_stage (compute) | neighbors wait on it |
| hidden_child.py → sleep | sleep | child-wait |
| hidden_producer \| fast_consumer | inner writer pid, not the stage parent | pipe-empty retargeted through child-wait |
| fifo_block | fifo reader | fifo |

Joint fixture already proved the synthesis: stage 0 pid ≠ knot pid, conversation has both `pipe-empty` and `child-wait`. Pinch would have named the parent stage. Hitch without meters would not have quantified the pipe.

Dogfood, first pass:

- **kizu** `cargo metadata --offline | jq '.packages | length'`: jq `pipe-empty` 0.336s on cargo, 1.32MB, 290 packages. Knot is cargo. Correct, but reason also blamed a nameless `Python` wrap, and bash was marked instrument because `--wrap` appeared *inside* `bash -c`.
- **kizu** `cargo test --offline --lib watcher::tests::writes_inside_git_dir_do_not_emit_worktree_event`: wall 3.67s. Knot is `kizu-fe283ed0a064d8be` (wait), via `child-wait`. Hitch's answer. The waiter was named `<defunct>` — cargo's last sample after exit wiped the argv.
- **voidtrace** `node tools/spec-check/src/main.ts`: wall 0.30s. Conversation `node --child-wait--> pkl`, pkl ran, but the walk stopped at node because node also had run samples. Pinch's inner-pkl hole, unfixed.
- **voidtrace** `pnpm exec vitest run` two contract files: wall 0.77s. Walk `pnpm → vitest → node worker`. Knot is the inner worker (compute). This is the joint object working: a single command that is a hidden pipeline.
- **python** `cat knot | gzip-oneliner | len`: gzip stage is the knot (pipe-full from cat, pipe-empty from wc). Named `Python` — macOS ps dropped argv.

### After the improvement

One change, driven by the transcript: **keep names, and walk through inner wrappers**.

1. Prefer the longest real argv over later `<defunct>` / `Python`.
2. Recover stage names from wrap argv; label forked children of a stage.
3. `bash -c` that *embeds* `--wrap` is not instrument; wrap/meter pids are recorded in their logs and marked.
4. Collapse absolute args to basename so the knot is `python3 hidden_producer.py`, not a truncated worktree path that lost the script.
5. Walk `child-wait` into a running descendant when the parent is an inner wrapper (`node`/`cargo`/`python`/`pnpm`/…) or the child did comparable work. That is pinch's inner pinch joined to hitch's edge.

Re-runs:

- **kizu cargo test**: `cargo test --offline --lib watcher::… --child-wait 2.93s--> kizu-fe283ed0a064d8be --sleep--> kernel`. Knot is the test binary. **Cargo kept its name.** Reason: "cargo test waited here".
- **kizu metadata \| jq**: jq `pipe-empty` on cargo; knot cargo (compute). Path `jq .packages | length --pipe-empty--> cargo`.
- **voidtrace vitest**: `node pnpm --child-wait--> vitest --child-wait--> node worker`. Knot is the worker.
- **voidtrace spec-check** (warm, 0.38s, 4 samples): pkl gone; knot `node tools/spec-check/src/main.ts`. First-pass 0.30s with a visible pkl remains the colder evidence that the walk *should* descend — selftest now covers `node S/R + pkl R → knot pkl`.
- **joint fixture**: knot pid ≠ stage-0 pid, cmd `python3 hidden_producer.py 24 0.03`.

Human report after:

```
KNOT  cpu_stage
      compute · incoming 0.21s
      python3 fast_producer.py --pipe-full--> python3 cpu_stage.py
CONVERSATION
  pipe-empty  python3 fast_consumer.py → cpu_stage  [meter]
  pipe-full   python3 fast_producer.py → cpu_stage  [meter]
```

## Dogfood targets

- fixtures: pipe_block, fifo, hidden_child, hidden_producer \| consumer, cpu middle
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `cargo metadata \| jq`, `cargo test` watcher
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — `node tools/spec-check`, `pnpm exec vitest`
- python `cat \| gzip \| wc` of `./knot`

## Surprises

- A pipeline stage is often a waitpid parent. Meter blame on the stage pid is correct *as a pipe*, wrong as a wait-source. Retargeting the meter dst through child-wait is the synthesis, not a display trick.
- macOS `ps` loses argv on forked Python and on exiting cargo (`<defunct>`). Without wrap-argv / prefer-longest-cmd, the knot of a real command line is unreadable.
- `bash -c '… --wrap …'` contains `--wrap` as text. Treating that as instrument swallows the session leader and, worse, can swallow user wrappers.
- Warm `node spec-check` is 300ms; 50ms sampling still misses `pkl`. The walk cannot name a child it never saw.
- `tee` / `cat` / `jq` on cached cargo metadata are free. People still profile the wrong stage.

## Failures

- Sub-200ms pipelines (gzip of this file) are near the stall noise floor; kind (wait vs compute) flickers.
- 80ms sampling + lsof every 280ms will miss short rustc / pkl children.
- macOS WCHAN is `-`. Leaf `sleep` is still opaque (kevent vs nanosleep vs blocked open).
- Direction of mode-less anonymous pipes remains a heuristic (inherit hitch's: prefer the child as waiter).
- `--sh` wraps a stage in `bash -lc` when the snippet contains `;`, so a `python3 -c 'a; b'` gzip is named `bash -lc`.

## Suggested mutations

- Stream the conversation as JSONL *during* the run so a timeout killer can print the knot.
- Treat `tee`/`pv` as declared taps and drop them from stage wait-sources automatically.
- Attach a stack (`sample bt`) when the knot is a leaf `sleep` for >N seconds.
- `--replay` a previous JSON against a new run ("gzip used to be the knot").
- Invert: given the graph, SIGTERM the knot, not the waiter.

## Kill / keep

**Keep.** The object (one wait-for conversation over pipe meters ∩ process tree, walked to a wait-source) is smaller than either parent report and answers a question developers already ask ("where's this wedged?"). First real use immediately found argv-wipe, wrap-false-instrument, and a node→pkl walk that concatenation would have split across two tools.
