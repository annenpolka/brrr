# tenure

A path-condition is a predicate that **occupies** history. `tenure` emits eras of *this stack held*, plus who sat in it.

`when` answers the snapshot: nested predicates still in force at `FILE:LINE`. `perch` answers occupancy of a user-supplied grep/exists/exec, split when the witness set changes. Piping them greps the if-text. The if-text lives on the guard line. Occupancy of a path-condition is the lines that **run under** the stack.

Same TRUE, different occupants → a new era. `--boolean` is the ancestor `held`. Files that mention a stack token without sitting in it are **echoes**, not holders.

## Install / run

Python 3.10+, stdlib only, `git`.

```bash
chmod +x ./tenure
./tenure --selftest
./demo.sh
./tenure -C /path/to/repo src/git/parse.rs:60
./tenure --boolean Sources/SitboneCore/PresenceArbiter.swift:81
./tenure --grain files src/app.py:12
```

Exit 0 if the stack holds at the last sample, 1 if not, 2 on error.

## Examples

```bash
# kizu: four fallthrough givens occupied src/git.rs, then moved with the function
./tenure -C kizu src/git/parse.rs:60

# sitbone: lines that run after `guard isEnabled` — not every file that mentions isEnabled
./tenure -C sitbone Sources/SitboneCore/PresenceArbiter.swift:81

# tests copied the old guards; production grew a new one. Occupancy stayed TRUE. Holder is a ghost.
./tenure tests/test_app.py:5
```

## Grain

| grain | who is holding |
| --- | --- |
| `functions` (default) | `file:fn` |
| `files` | path |
| `regions` | consecutive line runs `file:start-end` |
| `loci` | `file:line` |
