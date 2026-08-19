# cling

**You did not start this command.** cling latches onto a pid (or process group) that is already running and waits until that world goes still — or until you hit SIGINT. Then it reports the same wake `spoor` would have if it had spawned the process: late writes, leaked children, leftover paths, plus the files the process still had open.

waitpid is still a lie. cling just does not get to be the parent.

Python 3.10+, stdlib only. Optional: `fswatch`, `lsof` (present on macOS).

```bash
chmod +x ./cling
./cling 12345
./cling --group 12345
./cling snapshot 12345
./demo.sh
```

JSON is the composable form (`--out report.json` or `--json`). Human report goes to stderr. SIGINT does **not** kill the subject; a second SIGINT abandons the report.

## Examples

### 1. A process that writes *after* it exits

Start the fixture yourself, then attach:

```bash
python3 fixtures/afterexit.py /tmp/out &
./cling --watch /tmp/out $!
```

The pid reaps in ~500ms. cling stays until the world is still:

```
end: exited
quiesce: 740ms after end  LATE ACTIVITY
late writes (1):
  +0.22s  source    /tmp/out/late.txt
```

### 2. Same-pgid child vs `--group`

`fixtures/groupkid.py` forks a child in the **same** process group, then the parent exits. The child writes after that.

```bash
python3 fixtures/groupkid.py /tmp/g &
./cling --watch /tmp/g $!            # late write + leaked group-mate
./cling --group --watch /tmp/g $!    # waits until the group is empty
```

That is the attach-shaped aftershock: a shell script died, its pipeline did not.

### 3. SIGINT as a mid-run wake

```bash
python3 fixtures/linger.py /tmp/l &
./cling --watch /tmp/l $!
# Ctrl-C
```

```
end: interrupted  TARGET STILL ALIVE
```

The linger process is still running. cling dumps open files and residue so far. Use `cling snapshot PID` when you do not want to wait at all.

## Flags (attach)

| flag | what |
| --- | --- |
| `--group` / `--pgid N` | wait until that process group is empty |
| `--watch PATH` | extra tree to snapshot/watch |
| `--watch-cwd` | poll subject cwd even when the tree is large |
| `--settle-ms` | stillness window after the last FS event (default 350) |
| `--kill-leaked` | SIGTERM descendants that outlived the subject (never the subject) |
| `--timeout SEC` | stop waiting; do not kill the subject |
| `--json` / `--out FILE` | machine report |

Exit: 0 after a clean end, 130 on SIGINT, 124 on `--timeout`, 2 if the pid is already gone. There is usually no child exit code — you were not the parent.
