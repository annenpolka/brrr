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

Python 3.10+, stdlib only. Optional `fswatch`. `lsof` is used to discover cwd and the open-file heap.

## Empirical transcript

### Before the first real-use improvement (v0.1)

`./demo.sh` eventually passed after two attach-specific traps:

- `--kill-leaked` harvested every pid in the subject's **pgid**. Non-interactive `cmd &` shares the demo script's process group, so cling SIGTERM'd the grok zsh wrapper (`snap=$(command cat <&3)…`).
- `--group` waited forever because `fswatch` (a child of cling) sat in that same pgid.

Once those were fenced (track only descendants / same-pgid orphans; `fswatch` in its own session; never wait for cling's lineage), the fixtures worked:

```
afterexit   late_writes 1  backend fswatch+poll  settle 750  waitpid 398
leak        leaked 1 python -c 'sleep 45' + kill-leaked
groupkid    pid-wait: late child-late.txt + leaked mate
            --group: end=group-empty leaked=0
SIGINT      end=interrupted target_alive=true  linger still running
kizu        end=exited leaked=0 late=0 git+=0   empty wake
```

Two misses on that same run:

1. **kizu via `hold.py` exec.** The pid became `cargo test`, but the report's `command` was still `python3 fixtures/hold.py …`. After waitpid, `ps` is gone, so we printed the attach-time image.
2. **`openleft` leftovers: [].** Last `lsof` sample ran *after* the pid died and was empty, so the file we had watched being held vanished from the heap object. The demo only passed because it also accepted `open_at_attach`.

`cling snapshot` on live processes we did not start:

- **tmux 803** — cwd `/Users/annenpolka`, 36 children, 11 held files (`~/.grok/logs/unified.jsonl`, session transcripts, mcp stderr logs). The heap of a multiplexer.
- **hermes gateway 1377** — `state.db` + four log files open. A daemon's residue while it is still alive.
- **codex mcp-server** — cwd voidtrace, one lockfile, one vendor child.
- **login -flp … tmux** — `cwd: None`, `open: 0` (cannot lsof a setuid login).

### After (v0.2)

Sample command and `lsof` **only while the pid is visible**. Record `execs` (same pid, new image). Last non-empty live `lsof` is the leftover heap.

`./demo.sh` — still exit 0, and the two misses are now hits:

```
openleft  open leftovers 1  held.txt fd=4w
kizu      command='…/bin/cargo test --manifest-path …/kizu/Cargo.toml --lib scan_scars_finds_ask'
          execs=3
            t=0.000  python3 fixtures/hold.py …
            t=0.368  cargo test --manifest-path …/kizu …
          leaked=0 late=0 git+=0 tmp=0
```

kizu's last-live heap is cargo's expected caches (`~/.cargo/.global-cache`, `.package-cache`, a `.crate` file) — persistent, not test residue. An empty *wake* with a non-empty *last-live heap* is the attach-shaped negative result.

## Dogfood targets

- fixtures: `afterexit.py`, `leak.py`, `groupkid.py`, `linger.py`, `openleft.py`, `hold.py`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (`cargo test --lib scan_scars_finds_ask` via `hold.py` exec)
- live `snapshot`: tmux 803, hermes gateway 1377, `codex mcp-server` (cwd voidtrace)

## Surprises

- The hard part of attach is **not** kqueue `NOTE_EXIT` (it works on a non-child). It is **process-group identity** in a non-interactive shell: the subject, the demo, cling, and the agent wrapper share a pgid. "Wait for the group" without subtracting your own lineage is a self-deadlock; `--kill-leaked` is suicide.
- macOS `NOTE_EXIT` `data` is 0 even when the process `exit(7)`. You do not get a wait status for a pid you do not parent. `exit_code` stays `null`. That is the cost of the flip.
- `hold.py` → `os.execvp(cargo)` is the realistic attach: you latched onto a wrapper. Following the image is the only way the report names the command that actually ran.
- tmux's open-file heap is a session log multiplex. `snapshot` on a pid you did not start is already useful without waiting.

## Failures

- No child exit status (kqueue `data` always 0 here).
- No stdio, so no test-boundary collisions (`collide.py` is spawn-shaped; dropped).
- Cannot inject `TMPDIR` / `--sandbox-tmp`.
- `ps` can report `(Python)` in the last sample as the interpreter exits.
- mtime slop (20ms) can tag a write at waitpid as `t_after_exit: -0.002`.
- Last-live `lsof` of cargo includes `~/.cargo` caches that are *supposed* to persist.
- `lsof` of setuid/`login` yields `cwd: None`.
- Commands that hardcode `/tmp` are still invisible unless that dir is `--watch`ed.
- Pipe-hang autopsy was not implemented (primitive 4).

## Suggested mutations

- `NOTE_FORK` / `NOTE_CHILD` breadcrumb so a setsid leak spawned in the last 10ms cannot hide between samples.
- Pair with a tiny wrapper that *does* exec after setting env (`cling-hold TMPDIR=… -- cargo test`) — spawn is then a one-line exec, attach stays the verb.
- `pgrep -f cargo | cling` already works via stdin; a `--follow-new` that re-latches onto the first child would cover "I attached to the shell, the work is the grandchild."
- Pipe-hang autopsy attaches naturally: the pids already exist.

## What the flipped assumption bought

- Attach to a cargo test / daemon / tmux that is **already running**.
- SIGINT is a mid-run wake that does not murder the subject.
- `--group` vs pid: same-pgid child writes after the parent dies (a shell script's pipeline) without needing `setsid`.
- Open-file heap + `snapshot` — objects `spoor run` never had, because it started from an empty child.

## What it lost

- Sandbox TMPDIR and guaranteed stdio (so test collisions).
- A reliable exit code.
- The ability to say "I know I saw the first byte" — you can attach late.

## Kill / keep

**Keep.** The verb is different from `spoor` (`cling 12345`, not `spoor run -- cmd`). Demo is green, kizu exec is named, SIGINT leaves the subject up, and snapshot of tmux/hermes produced a heap we did not allocate. Not a flag on `spoor`.
