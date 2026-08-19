# candidate-23 — hitch

## Primitive

A wait-for graph of a process tree: join OS sleep state to pipe / socket / fifo / child-wait peers and attribute blocked time to those edges.

## Four primitives considered

1. **gaplog** — timestamp a command's stdout and highlight silences. Conventional (`moreutils ts`, `annotate-output`). **Discarded.**
2. **openset** — treat the file-open set of a command as coverage. Conventional (`strace -e open`, testmon, bear). **Discarded.**
3. **coda** — time and leftover children between last useful output and process death. Unusual, but a metric more than a verb.
4. **hitch** — the wait-for graph. Unusual as a Unix verb, answers "on what is this hung?" without ptrace. **Implemented.** (Coda survives as a derived field: time after the last descendant vanished.)

## Why this might not exist

Every developer has a hung `cargo test` / `vitest` / `make`. The ritual is `pstree`, then `lsof -p` on a guessed child, then trying to match `PIPE 0xabc → 0xdef` by eye. `strace -p` is too loud. `spindump` is a novel. There is no `waitgraph` that samples the tree and prints waiter → blocker with seconds.

## How to run

From the worktree root:

```bash
./hitch selftest
./hitch -- python3 fixtures/pipe_block.py 0.8
./demo.sh
```

## Empirical transcript

### Before the improvement

Pipe fixture already found `pipe-read`. TCP found `tcp`. Then dogfood on kizu:

```
cargo test --lib watcher::tests::writes_inside_git_dir_do_not_emit_worktree_event
wall 4.4s  samples 31  idle 4.0s
snags: sleep cargo, sleep kizu-fe28…
graph: sleep only
```

lsof *did* capture PIPE fds, but cargo and the test binary **share inherited stdout** (same local hex address). Joining that would have invented a fake pipe-read. The real wait was cargo in `waitpid` on the test, and the test asleep in the watcher. hitch called both `sleep`.

FIFO fixture was also "just sleep": Unix `open(fifo, O_RDONLY)` blocks *before* the fd exists, so lsof saw nothing.

`hitch -p` on a sleeper swallowed the whole login/pgid, including the grok wrapper zsh and hitch's own `ps`.

### After

1. **child-wait** — a sleeping parent with live children is waiting on them, not on a kernel timer.
2. **Same-side pipes** (identical `0x` local addr) are not wait edges.
3. **FIFO** fixture holds `O_RDWR` so `read()` blocks on a visible FIFO; `u`+`r` pair as `fifo`.
4. **Snag ranking** uses time-per-kind, not last sample; `child-wait` is down-weighted so the leaf hitch wins.
5. **Pgid walk** only when the root is session leader (`pgid == pid`), i.e. `hitch -- cmd` with `start_new_session`.

kizu after:

```
wall 2.98s  idle 2.81s  coda 0.0
snags: sleep kizu-fe28… ; child-wait cargo
graph: cargo --child-wait--> kizu-fe28… --sleep--> kernel
```

voidtrace `pnpm exec vitest run` two contract files:

```
wall 0.66s  kinds: child-wait
node pnpm --child-wait--> node vitest
```

Pipe human report (v0.2):

```
SNAGS
  pid …  Python  blocked 0.54s  pipe-read   ← python3 fixtures/pipe_block.py
  pid …  Python  blocked 0.54s  child-wait  ← python3 fixtures/pipe_block.py
GRAPH
  child-wait  parent → child
  pipe-read   child  → parent
```

That cycle *is* the fixture: parent sleeps then writes; child is blocked on the pipe until then.

## Dogfood targets

- fixtures: `pipe_block.py`, `tcp_block.py`, `fifo_block.py`, `sleep_block.py`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `cargo test --lib watcher::tests::…`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — `pnpm exec vitest run packages/contracts/src/*.test.ts`

## Surprises

- macOS `lsof` omits r/w on anonymous pipes. Direction has to be inferred (prefer child as waiter when parent created the pipe).
- macOS `WCHAN` is almost always `-`. The graph has to come from fds and the parent/child relation, not wait channels.
- A process can be in `S` for its entire "work" (kizu's watcher test). CPU profilers would say the suite is idle; hitch says it is waiting.
- `open(fifo)` vs `read(fifo)` are different hitches; only the second has an fd.

## Failures

- No stacks, so "sleep" on a leaf is still opaque (`kevent` vs `nanosleep` vs blocked `open`). Linux `wchan` helps; macOS does not.
- Very short commands (8ms vitest) may only show the parent `child-wait` / startup, not a test-worker graph.
- Sampling + `lsof` adds overhead; fine for hung tests, not for microbenchmarks.
- Direction of mode-less pipes is a heuristic.

## Suggested mutations

- Attach `sample`/`thread_apply_all bt` when a leaf snag is `sleep` for >N seconds (stack-enriched hitch).
- Stream JSONL idle-window events *during* the run so a timeout killer can print the graph.
- Invert: given a graph, kill the blocker (not the waiter).
- Join file-lock waiters (`F_SETLKW`) the same way.

## Kill / keep

**Keep.** Small verb, composes (`--samples` / `fold` / `-p` / `--json`), empirically different on kizu than `time` or `ps`.
