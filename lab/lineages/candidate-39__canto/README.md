# canto

The plot of a mixed commit: name-closed acts in required reading order.

A mixed commit is an epic dumped as one blob. `git add -p` clusters. canto
emits the story: a name is a plot point if this diff defines it; an act is a
name-closed set of hunks; later acts may use earlier defs, never the reverse.

```
$ ./canto -C sitbone e9b0f75
canto 3 acts  2 tracks  spoil=0 tangle=0  grain=hunk  e9b0f75^..e9b0f75
TRACK 1  presentThreshold
  #1  PRELUDE  Sources/SitboneCore/PresenceArbiter.swift
           defs  presentThreshold, absentThreshold, applyHysteresis
  #3  PAYOFF   Tests/SitboneCoreTests/PresenceHysteresisTests.swift
           via   PresenceArbiter
TRACK 2  (aside)
  #2  ASIDE    Tests/SitboneCoreTests/PresenceArbiterTests.swift
```

Kinds: **PRELUDE** (defs later acts use) · **PAYOFF** (uses earlier defs) ·
**SOLO** (closed) · **ASIDE** (no plot names) · **CYCLE** (mutual defs) ·
**SPOIL** (prod + test in one strongly-connected piece). Independent name
sets are **tracks**. `--check` exits 1 on SPOIL/TANGLE.

## Run

Python 3.9+, `git`, stdlib. From this directory:

```bash
chmod +x ./canto ./demo.sh
./canto --help
./canto --selftest
./demo.sh 0
./canto -C /path/to/repo HEAD
./canto -C /path/to/repo --grain file --check COMMIT
git diff A B | ./canto --stdin
```

Default range: dirty worktree vs HEAD, else `HEAD^ HEAD`.

## Examples

**1. Reading order of a squash (the fixture `./demo.sh` builds)**

```bash
./canto -C "$FIX" --grain file $C0 $HEAD
# Lexer PRELUDE → Parser PRELUDE → tests PAYOFF
# util is a second track; README is ASIDE
```

**2. Recover the commits that should have been (`--against`)**

```bash
./canto -C "$FIX" --grain file --against $C0 $C3
# against commits=3 acts=3 mean_jaccard=1.0
```

**3. Unsquash into patches (`--split --verify`)**

```bash
./canto -C repo --grain file --split /tmp/story --verify FROM TO
# APPLY.txt: start at FROM, apply 01-prelude.patch, 02-payoff.patch, …
# --verify checks the reconstituted tree equals TO
```

`--format json|tsv` for composition. `--grain hunk` is the kernel (in-file
`#[test]` vs prod); `--grain file` is what `--split` writes.
