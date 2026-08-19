# wisp

Show the code that lived between two git refs and vanished, plus the remnants it left behind.

`git diff A B` is the net. `git log A..B` is the commits. **wisp** is the forgotten middle: files and symbols that were born and killed in the interval, and names from that dead code that still linger at HEAD.

## Install / run

```bash
chmod +x wisp
./wisp --help
```

Requires Python 3.10+ and `git`. No other dependencies.

```bash
./wisp                  # auto range: this branch vs main, else a history window
./wisp main HEAD        # explicit range
./wisp --root           # empty tree → HEAD (whole-repo ghosts)
./wisp --check -q       # CI: exit 1 if remnants exist
```

Exit codes: `0` ok, `1` remnants found with `--check`, `2` usage/git error.

## Examples

**1. What died on this branch that the net diff hides?**

```bash
./wisp main HEAD
```

Ephemeral files and symbols were added in some commit in `main..HEAD` and are gone at HEAD. They never appear in `git diff main HEAD`.

**2. Did a deleted experiment leave residue?**

```bash
./wisp --root --remnants --json | jq '.remnants[] | select(.role=="comment" or .role=="code")'
```

A comment that still says `LegacyParser` after the class was deleted is a remnant.

**3. CI: fail if this branch left ghosts in the source**

```bash
./wisp origin/main HEAD --check --quiet
```

See `./demo.sh` for an ugly-fixture run (spaces, Unicode paths, nested git, leftover comments).
