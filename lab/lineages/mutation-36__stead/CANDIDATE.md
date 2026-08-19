# mutation-36 — stead

## Primitive

`stead` emits contiguous occupancy eras whose sample is not a boolean.
Statuses are TRUE / FALSE / UNKNOWN / SHALLOW / EMPTY. A failed probe is
not FALSE. `--now` on a commit-less dirty tree answers the filesystem. A
depth-1 clone prints SHALLOW and does not claim birth. `--full` compresses
along parent edges; `git log --reverse` is `--list`. `--boolean` recovers
ancestor `held` for TRUE/FALSE-only probes.

## Why this might not exist

DESTROYER_OCCUPANCY kept the occupancy verb and listed the lies:

1. `--now` on a repo with no commits cannot see a dirty README.
2. Timeout / failed exec is reported as FALSE.
3. Binary blobs are empty air (`git grep -I`).
4. A shallow clone reports TRUE from the beginning of the world.
5. `--full` is not the merge lattice; list order invents a FALSE gap.
6. Glob `exists *` pretends to be the same cost class as `exists`.

held, perch, and tenure share the assumption **a probe that does not
return TRUE is FALSE**. Occupancy of an unmeasurable tree is a different
object. `stead` is that object. It does not invent leftover-name search,
does not walk ignore policy, and does not become `git log --name-only -S`.

## How to run

```bash
chmod +x ./stead
./stead --help
./demo.sh
./stead --now -C /tmp/destroy-occupancy/empty-dirty exists README.md
./stead -C /tmp/destroy-occupancy/kizu-shallow exists CLAUDE.md
./stead -C /tmp/destroy-occupancy/timeout --timeout 0.25 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
./stead -C /Users/annenpolka/ghq/github.com/annenpolka/kizu --full exists CLAUDE.md
./stead -C /Users/annenpolka/ghq/github.com/annenpolka/skills grep preact-zero-mock
```

Python 3.10+, stdlib only, git. TSV on a pipe, human on a tty, `--json`
for asserts. Exit 0 iff last sample is TRUE, 1 if FALSE, 3 if
UNKNOWN/SHALLOW/EMPTY dominates, 2 error.

## Empirical transcript

### Before the improvement

v1 already had five statuses, lattice compression, glob as its own verb,
and `--timeout 0` refused. DESTROYER fixtures were the first attack.

`--now` on a commit-less tree *without* README crashed inside diagnose:
`never_held` looked TRUE, so diagnose ran `git log HEAD` and leaked

```
stead: fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree.
# rc=2
```

The filesystem sample never ran. Same hole held had, just moved later.

Invalid regex was UNKNOWN (good) but `never_held` was still true — a
failed probe compressed into “never occupied.” Human `--now` on
empty-dirty said `walk=first-parent` and `true=0/0` while `now=TRUE`.

### After the improvement

Diagnose does not walk HEAD when there are no commit samples. `never_held`
requires no SHALLOW/UNKNOWN/EMPTY. A commit-less walk is `filesystem` or
`unborn`, not first-parent.

```
$ ./stead -C empty --human exists README.md
EMPTY     1 sample   UNBORN
now=EMPTY  true=0/1 samples  walk=unborn
# rc=3

$ ./stead -C empty --now --human exists README.md
FALSE     1 sample   WORKTREE
now=FALSE  walk=filesystem
# rc=1   — filesystem occupancy of a missing path

$ ./stead -C empty-dirty --now --human exists README.md
TRUE      1 sample   WORKTREE
       witnesses: README.md
now=TRUE  true=1/1 samples  walk=filesystem
# rc=0   — held aborted here
```

Timeout is a hole, not a death. Witness `(timeout)` prints on the UNKNOWN era:

```
$ ./stead -C timeout --timeout 0.25 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
TRUE      1 commit   fast only
UNKNOWN   1 commit   slow present
       witnesses: (timeout)
TRUE      1 commit   slow gone
now=TRUE  unknown=1
# rc=0
```

`--timeout 0` is exit 2 (`a timeout is UNKNOWN; 0 is not a probe`). 20×
`sleep 2` × `--timeout 0.05` is `UNKNOWN 20`, exit 3, no leftover sleep
processes (killed as a process group).

Binary-only TOKEN_BIN is EMPTY, not FALSE. Path occupancy still sees the blob:

```
$ ./stead -C binary grep TOKEN_BIN
TRUE      1 commit   witnesses: visible.txt
EMPTY     1 commit   witnesses: secret.bin, src/evil.py
       binary/NUL occupancy, not text FALSE
now=EMPTY  empty=1
# rc=3

$ ./stead -C binary exists secret.bin
TRUE
```

Invalid regex is one probe, not twenty FALSE:

```
$ ./stead grep '['
UNKNOWN   (invalid regex: brackets not balanced)
never_held=false  probes=1  rc=3
```

Diamond `--full` is two lattice components, not FTFT. `--list` recovers
the lie for comparison:

```
$ ./stead -C diamond --full exists src/app.py
FALSE     2 commits  70b4d04, 0286af3     A, B
TRUE      3 commits  3bd51b6, 1455a54, 3042f3b   C, D, M
       lattice component (not adjacent in git log --reverse)
now=TRUE  true=3/5  walk=lattice

$ ./stead -C diamond --full --list exists src/app.py
FTFT     # held's git log --reverse order
```

Shallow clone does not claim birth or never-held. `--limit 1` is the same
horizon. `--boolean` downcasts SHALLOW-from-TRUE back to held:

```
$ ./stead -C kizu-shallow exists CLAUDE.md
SHALLOW   1 commit   9349dc5
# rc=3   — held: TRUE 1/1 from the beginning of the world

$ ./stead -C sitbone-shallow exists Sources/SitboneUI/FocusRiverView.swift
SHALLOW   1 commit   094769d
# rc=3   — held: FALSE 1/1 never-held, no --full hint (island unreachable)

$ ./stead -C kizu-shallow --boolean exists CLAUDE.md
TRUE      1 commit   9349dc5
# rc=0   — lossy held recovery
```

`exists *` is refused (`stead glob PATTERN`). Glob on the 1500-commit
identical-tree fixture is **1 probe** (per unique tree), not 1500
ls-tree, and still labelled `cost=per-tree`. Exact `exists keep.txt` is
`cost=batch`, 0.35s. huge-flip TOKEN_FLIP is FTF in 0.14s.

Bare clone of diamond walks commits (held said “not a git repository”).
`--now` on bare is exit 2, no work tree. CJK `exists 計画.md` and `grep
TOKEN_RENAME` witnesses are unquoted (`core.quotepath=false`).

`./demo.sh` — 61 assertions, exit 0.

## Dogfood targets

| target | what we asked |
| --- | --- |
| `/tmp/destroy-occupancy/{empty,empty-dirty,binary,timeout,diamond,kizu-shallow,sitbone-shallow,huge,huge-flip,rename,bare.git,always,exec-chain}` | DESTROYER occupancy cases, reproduced |
| kizu `exists CLAUDE.md` | first-parent birth `0ea3916` (merge); `--full` lattice birth `e1098c8`; depth-1 is SHALLOW |
| sitbone `exists Sources/SitboneUI/FocusRiverView.swift` | `git log -- PATH` empty; `--full` island 11; depth-1 is SHALLOW not never-held |
| skills `grep preact-zero-mock` | perch gold: boolean occupancy still TRUE at HEAD; witnesses include README.md after `127df9c` deleted the plugin; `exists preact-zero-mock/SKILL.md` is FALSE |
| synthetic demo fixture | TFTF path, glob cost class, `--boolean` TFTF |

Read-only on the real repos. Shallow clones were throwaway `git clone --depth 1 file://…`.

## Surprises

- The occupancy verb survived every DESTROYER hole once FALSE was no longer the dump status. The interesting output is the **status letter**, not a new query language.
- `--full` on kizu is still FALSE 1 / TRUE 243. The diamond is the case where list order lies; real GitHub-flow history of a file that never died looks the same as held. Lattice matters when a FALSE commit is *adjacent in the list* but not on the occupied lineage.
- Tree-hash memo turns DESTROYER's “glob is 30× slower” into “glob is per unique tree.” The 1500-commit identical-tree fixture is one ls-tree. The cost class is still not `exists`.
- skills README-only `grep preact-zero-mock` is still one TRUE era. That is held. perch's gold (ghost tenure) is a different mutation. `stead` footnotes both witnesses (`SKILL.md, README.md`) and does not split holders.
- `--limit` and shallow clone are the same horizon. Occupancy of a tail is SHALLOW, not occupancy of the repo.

## Failures

1. **`--boolean` reintroduces every DESTROYER lie** by design. It is labelled lossy. Scripts that want held exit 0/1 can have it; the default will not.
2. **Holder splits are not occupancy status.** skills README-only tenure still looks like one TRUE island. Use perch.
3. **Lattice display of a disjoint component uses comma-separated shorts**, not `a..b`. `a..b` would include the FALSE commits in the date range. TSV `start`/`end` are oldest/newest, `chain=0`.
4. **`glob '*SKILL.md'` on skills is 49 probes** (each commit a new tree as plugins accrue). Honest. Loud if you wanted `exists`.
5. **Rename is still path death for `exists`.** Content occupancy (`grep TOKEN_RENAME`) stays TRUE across `old.txt` → `計画.md`. `--follow` is a different mutation.
6. **`true_commits` is commit samples only.** A `--now`-only TRUE is `true=1/1 samples` in human output; JSON `true_commits` stays 0.
7. Empty `--range HEAD` is still exit 2 (no commits), not an EMPTY era. Range asked for a revision that does not exist.

## Suggested mutations

- Pipe from perch: `perch grep X | stead --status` to re-label FALSE holes as UNKNOWN when the probe was a timeout.
- Cache `(tree, predicate) → status` in `.git/stead-cache/`.
- `--follow` so a rename is one TRUE component on the path-identity lattice.
- `stead count PATTERN` — integer occupancy, UNKNOWN when the probe fails.
- Occupancy of a merge commit as a join of parent statuses (TRUE if any parent TRUE? TRUE iff all?) — a real lattice algebra, not connected components of a boolean.
- Refuse `--boolean` when any raw status is not T/F, instead of downcasting.

## Flipped assumption: bought and lost

Parents assumed **a failed probe is FALSE**.

**Bought**

- `--now` on empty-dirty README is filesystem TRUE.
- Timeout, invalid regex, checkout failure are UNKNOWN and do not found a never-held era.
- Depth-1 kizu CLAUDE.md is SHALLOW, not birth. Depth-1 sitbone FocusRiverView is SHALLOW, not never-held.
- Binary TOKEN_BIN after the text copy dies is EMPTY, and `exists secret.bin` stays TRUE.
- Diamond `--full` is FALSE {A,B} / TRUE {C,D,M}. The file never died.
- `exists` vs `glob` is a cost-class split. `--timeout 0` is not a probe.

**Lost**

- Exit 3 is a new contract. Scripts that treated any non-zero as “does not hold” now need to distinguish 1 and 3.
- `--boolean` is the only way back to held, and it lies on purpose.
- Eras on `--full` are DAG components, so `start..end` is not a git rev-range when `chain=0`.
- TRUE is no longer the only “something is here”: EMPTY is occupancy you cannot read as text; SHALLOW is occupancy you cannot date.

## Kill / keep

**Keep.** The occupancy verb was already real. DESTROYER's verdict was mutate, do not kill; this mutation is the status algebra the attacks asked for. The v1→v2 change was forced by `--now` on a commit-less tree (diagnose walked HEAD) and by `never_held` treating UNKNOWN as absence — the same lie, inside the new tool. Not polish.
