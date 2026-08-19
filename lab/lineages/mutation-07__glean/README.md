# glean

Find the **1-minimal set of dirty and untracked files** that reproduces a command's current behavior (wheat). Everything else is chaff: restore or delete it and the command still behaves the same.

The unit is a **whole file**, never a hunk. Untracked files are first-class. This is `git bisect` for the dirty tree, stopping at file grain.

## Install / run

Needs Python 3.9+ and `git`. No other dependencies.

```bash
chmod +x glean
./glean -- pytest tests/test_foo.py
python3 ./glean --format paths -- python3 test.py
./demo.sh
```

The working tree is restored after the run (including on SIGINT). The git index is never touched.

## Examples

**1. Which file actually broke the test?**

Mixed WIP: a bug in `app.py`, a README tweak, and an untracked `notes.txt`.

```bash
./glean -- python3 test.py
```

```
HEAD: exit=0 pass
WIP:  exit=1 AssertionError
trials: 6  fingerprint: all  unit: file

wheat (1 files):
  modify    app.py
chaff (2 files):
  modify    README.md
  untracked notes.txt
```

**2. Paths only, for pipelines**

```bash
./glean --format paths -- python3 test.py
# app.py
```

**3. Drop the files that do not matter**

File grain means chaff is actually discardable. On a 108-file tenaoshi WIP, wheat was one path; this is the rest:

```bash
./glean --format drop -- python3 -c "from pathlib import Path; assert 'GLEAN_PROBE_MARKER' in Path('tools/e2e/verify-log.ts').read_text()"
```

```
git restore --worktree --source=HEAD -- AGENTS.md justfile src/config.rs
rm -f -- Engine/Sources/TenaoshiEngine/EditPlan.swift notes.txt
```

`--drop` applies that and leaves only wheat dirty. Hunk tools cannot emit `git restore`.

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` | git repo (and command cwd) |
| `--cwd DIR` | command cwd only |
| `--base REF` | baseline (default `HEAD`) |
| `--format text\|paths\|json\|patch\|drop` | output (`drop` is `git restore`/`rm` for chaff) |
| `--drop` | leave only wheat in the worktree |
| `--fingerprint all\|strict\|stderr\|exit\|raw` | what "same behavior" means |
| `--max-files N` | abort if the dirty set is larger (default 400) |
| `-v` | print each trial |
| `-q` | hide the chaff list in text mode |

Exit 0 on a successful partition (including "WIP does not affect this command"). Exit 2 for usage/tool errors. Exit 3 if the command is flaky.
