# snag

A unified diff is a superposition of syntactic classes. **snag** is the one-class tripwire: `--forbid CLASS` exits 1 if that ply moved.

weft asked *did anything except CLASS leak?* snag asks *did CLASS leak at all?* Path does not free a hit. stdin is a unified diff. No TSV unless `--emit`.

## Install / run

Python 3.9+, stdlib. No `git` required (stdin filter).

```bash
./demo.sh
./snag --selftest
./snag --help
git diff | ./snag --forbid number
git diff | ./snag --forbid number --emit
git diff origin/main...HEAD | ./snag --forbid number
```

Exit 0 = CLEAR, 1 = TRIP, 2 = usage.

## Examples

Comment rewrite, timeout stayed:

```bash
$ git diff | ./snag --forbid number
snag CLEAR  forbid=number  stdin  files=1  hits=0
```

Same line, timeout moved with the comment:

```bash
$ git diff | ./snag --forbid number
snag TRIP  forbid=number  stdin  files=1  hits=1  number=1
  src.rs:2  number  chg  30 → 60
```

Docs PR that also bumped a number — weft `--only docs` can pass markdown; snag does not:

```bash
$ git diff | weft --only docs     # OK on a date-only markdown add
$ git diff | ./snag --forbid number   # TRIP: 2026, run ids, 30→60
```

A number that hid inside a comment or a string (weft's named miss) is still a number ply:

```bash
$ git diff   # let timeout = 30; // timeout 30  →  // timeout 60
$ git diff | weft --only docs          # OK — class comment
$ git diff | ./snag --forbid number    # TRIP 30 → 60
```
