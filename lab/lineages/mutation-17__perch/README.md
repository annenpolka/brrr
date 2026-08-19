# perch

Occupancy eras that also split when **who is holding** changes.

`held` compresses a boolean: as long as the predicate stays TRUE, that is one era, even if the files (or lines) that make it true are a different set. `perch` walks the same predicates (`exists`, `grep`, `exec`) and splits a still-TRUE run the moment the witness set changes. Occupancy + who is holding.

`--boolean` recovers ancestor `held`.

## Install / run

```bash
# from this directory
./perch --help
./demo.sh
```

Requires Python 3.9+ and `git`. No other dependencies. Copy `perch` onto your `PATH` if you want.

Exit codes: `0` predicate holds at the last sample (HEAD, or the working tree with `--now`), `1` it does not, `2` tool error.

## Examples

**1. A name that never left the tree, but changed hands.** (`held` reports one TRUE era.)

```bash
perch grep TOKEN_B
perch --boolean grep TOKEN_B
```

```
TRUE   2 commits   alpha.txt
TRUE   2 commits   alpha.txt, beta.txt
       + beta.txt
TRUE   3 commits   beta.txt
       - alpha.txt
now=TRUE  eras=3  boolean=1  holder_splits=2
```

**2. A deleted plugin that `grep` still says is TRUE — because README mentions it.**

```bash
perch -C skills grep preact-zero-mock
```

```
TRUE  21 commits  holders: preact-zero-mock/SKILL.md
TRUE  10 commits  holders: README.md, preact-zero-mock/SKILL.md
       + README.md
TRUE  16 commits  holders: README.md
       - preact-zero-mock/SKILL.md
       ghost: definition left; name still perches in documentation
now=TRUE  true=47/49  boolean=2  holder_splits=2
hint: now=TRUE only as a documentation mention (README.md); definition preact-zero-mock/SKILL.md is gone
```

`held` collapses this to FALSE 2 / TRUE 47. The last sixteen commits are occupancy without a definition. perch names that **ghost**.

**3. A type that lived on a side branch `git log -- PATH` cannot see, and that gained then lost a second holder while it lived.**

```bash
perch --full grep FocusRiverView
```

```
FALSE  11 commits
TRUE    1 commit   FocusRiverView.swift
TRUE    5 commits  FocusRiverView.swift, NotchOverlay.swift
       + NotchOverlay.swift
TRUE    5 commits  FocusRiverView.swift
       - NotchOverlay.swift
FALSE  78 commits
```

Grain: `--grain files` (default, matching paths), `--grain loci` (path + matching line text; ignores line-number drift), `--grain lines` (`path:lineno`, noisy).
