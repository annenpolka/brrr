# DESTROYER — ford

Occupancy of a merge is a join of parent *trees*, not a boolean sample
on the merge SHA. This pass attacks the lattice (not the occupancy walk
DESTROYER occupancy already broke).

Full report: [`lab/judges/DESTROYER_FORD.md`](lab/judges/DESTROYER_FORD.md).

## Primitive

At a two-parent commit, occupancy is `meet`/`join` of the incoming
**snapshots**. Default meet: TRUE iff every parent TRUE (preserve).
`--any`: TRUE if any parent TRUE (introduce via a side). A merge-parent
that is itself a merge still contributes its *tree*, so kizu PR #2
(`21ae074`) is `T⊓T` preserve after the introducing ford at `0ea3916`.

## How to run

Victim (do not rewrite):

```bash
FORD=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb2e776f004a/ford
"$FORD" --help
"$FORD" lattice
"$FORD" -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
```

Peel (recursive join, already shipped):

```bash
WEIR=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-109aeaf41ba5/weir
"$WEIR" -C /Users/annenpolka/ghq/github.com/annenpolka/kizu exists CLAUDE.md
```

Replay this battery:

```bash
python3 /tmp/destroy-ford/attack.py
# transcript: /tmp/destroy-ford/transcript.txt
# fixtures:   /tmp/destroy-ford/fixtures/
```

Python 3.9+, stdlib, git. Victim `./demo.sh` still **PASS=88 FAIL=0**.

## Examples

**1. kizu gold — introducing ford is honest; TRUE still spans PR #2.**

```bash
$ ford -C kizu exists CLAUDE.md
FALSE     1 commit    0ea3916
       ford  FALSE ⊓ TRUE = FALSE
       origin: e1098c8
TRUE     22 commits   21ae074..9349dc5
       preserve after ford 0ea3916; not birth
```

`--boolean` recovers held's birth at `0ea3916`. weir makes `21ae074`
itself `FALSE ⊓ TRUE` (parent occupancy, not tree).

**2. Diamond — `now=FALSE` while HEAD's tree has the file.**

```bash
$ ford exists src/app.py          # rc=1  now=FALSE  tree_now=TRUE  never_held=True
$ ford --any exists src/app.py    # rc=0  introduce via topic
$ ford --tree exists src/app.py   # held FT birth at M
```

**3. `--boolean` skips the lattice and the SHALLOW horizon.**

```bash
$ ford --timeout 0.2 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
# UNKNOWN rc=3 — then --boolean → FALSE rc=1 (weir refuses)

$ git clone --depth 1 kizu && ford --boolean exists CLAUDE.md
# TRUE 1/1 at 9349dc5, no warning — occupancy DESTROYER's shallow birth
```

## Dogfood

| target | asked | observed |
| --- | --- | --- |
| kizu `exists CLAUDE.md` | not birth at `0ea3916`; span of TRUE | ford at `0ea3916`, origin `e1098c8`; TRUE `21ae074..9349dc5` |
| sitbone `FocusRiverView.swift` | first-parent never; `--full` island | never_held + `--full` hint; 11 commits; 0 fords |
| skills `grep preact-zero-mock` | still TRUE at HEAD | TRUE 47/49 |
| octopus 1-of-3 vs 2-of-3 | arity | both `⊓` FALSE, same `never_held` |
| merge-of-merges | tree vs occupancy | ford `T⊓T` preserve at M2; weir recursive FALSE |

## Kill / keep

**Mutate, do not kill.** The two-parent introducing join is real.
weir is the recursive peel. `--boolean` / `21ae074` span / octopus
fold / rename-as-death are mutations, not a reason to throw away the
lattice.
