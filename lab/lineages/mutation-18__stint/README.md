# stint

Interval occupancy of files and symbols that lived between two git refs and vanished.

`git diff A B` is the net. `git log A..B` is the commits. **stint** is the forgotten middle as *occupancy*: how many commits a path or definition held the tree, the last blob it left, and `--pick` to restore that blob. No leftover-name search.

## Install / run

```bash
chmod +x stint
./stint --help
```

Requires Python 3.10+ and `git`. No other dependencies.

```bash
./stint                  # auto range: this branch vs main, else a history window
./stint main HEAD        # explicit range
./stint --root           # empty tree → HEAD
./stint --pick PATH      # last blob of an ephemeral path, on stdout
./stint --pick PATH --write
./stint --check -q       # exit 1 if any ephemeral file occupied the interval
```

Exit codes: `0` ok, `1` `--check` found files or `--pick` missed, `2` usage/git error.

## Examples

**1. What occupied this branch and is gone from the net diff?**

```bash
./stint main HEAD
```

Each row is a path (or symbol) born after the base and dead at HEAD, with how many commits it occupied and the last blob.

**2. Restore the last body of a deleted experiment**

```bash
./stint --root --pick FocusRiverView.swift
./stint --root --pick circuit-breaker/ --to /tmp/out
```

`--pick` accepts a unique suffix or basename. A prefix matching several ephemeral paths is a deleted tree: `--to DIR` or `--write` restores every last blob. One path defaults to stdout.

**3. CI: fail if this interval abandoned a file**

```bash
./stint origin/main HEAD --check --quiet
```

`--root --check` on a long-lived repo is archaeology, not a gate.

See `./demo.sh` for an ugly fixture (spaces, Unicode, two occupancy spans, nested git) plus skills `circuit-breaker` and sitbone `FocusRiverView`.
