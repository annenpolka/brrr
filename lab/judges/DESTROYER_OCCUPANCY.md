# DESTROYER — occupancy (held × perch × tenure)

Adversarial pass on the occupancy family. No rewrites: the failures are conceptual, not one-line bugs.

- **held** (boolean occupancy eras) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-796f-76d0-988f-5c2c16399eaa`
- **perch** (occupancy + who is holding) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bd-7c52-b01b-c771008e6951`
- **tenure** (occupancy of a path-condition stack) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-05-tenure`
- Transcript: `/tmp/destroy-occupancy/transcript.txt`
- Fixtures: `/tmp/destroy-occupancy/{empty,empty-dirty,bare.git,huge,huge-flip,diamond,rename,binary,always,timeout,exec-chain,kizu-shallow,sitbone-shallow}`
- `tenure --selftest` still exits 0 after the attacks.

Verdict: **mutate, do not kill.** Occupancy is still a real verb. The attacks show where each tool pretends a walk of `git log --reverse` is the lattice, a timeout is a FALSE, a binary is empty air, and a broken regex is “never held.”

---

## held

Primitive restated: walk commits, compress a predicate into contiguous TRUE/FALSE eras. Exit 0 iff it holds at the last sample.

## perch

Primitive restated: the same walk, then split a still-TRUE run when the witness set changes. `--boolean` is ancestor `held`.

## tenure

Primitive restated: pin `FILE:LINE`, reconstruct the nested stack (`when`), walk git, emit eras of *this stack held* plus who sat in it. `--boolean` is ancestor `held`. Echoes are mentions that are not occupants.

---

## 1. Empty repo — `--now` cannot see a dirty tree (conceptual)

All three refuse a repo with no commits. Dedicated message, exit 2. Honest.

```
$ ./held -C $EMPTY exists README.md
held: no commits at HEAD (empty repository?)
# rc=2  elapsed=0.045s

$ ./perch -C $EMPTY exists README.md
perch: no commits at HEAD (empty repository?)
# rc=2

$ ./tenure -C $EMPTY README.md:1
tenure: no commits at HEAD (empty repository?)
# rc=2
```

Same on `stratal` (known empty). Same if the empty repo already has a dirty `README.md` and you pass `--now`:

```
$ ./held -C $EMPTY_DIRTY --now exists README.md
held: no commits at HEAD (empty repository?)
# rc=2  — README.md is sitting on disk

$ ./perch -C $EMPTY_DIRTY --now exists README.md
perch: no commits at HEAD (empty repository?)

$ ./tenure -C $EMPTY_DIRTY --now README.md:1
tenure: no commits at HEAD (empty repository?)
```

`--now` is documented as “append the working tree as a final sample.” `rev-parse HEAD` runs first and aborts. Occupancy of a tree that does not yet have a first commit is unaskable. `git add` without `git commit` is the same hole (`--index` never runs).

`--range HEAD` skips the dedicated empty check and leaks git’s fatal:

```
$ ./held -C $EMPTY --range HEAD exists README.md
held: fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree.
Use '--' to separate paths from revisions, like this:
'git <command> [<revision>...] -- [<file>...]'
# rc=2
```

A **bare** repo is not “empty”; it is a git directory with no work tree. `rev-parse --show-toplevel` fails, so occupancy of a mirror is “not a git repository”:

```
$ git -C $BARE rev-parse --is-bare-repository
true

$ ./held -C $BARE exists x
held: not a git repository: /tmp/destroy-occupancy/bare.git
# rc=2
```

No one-line fix: `--now` on a commit-less repo is a different object (the filesystem), and a bare clone is a different object (no checkout). The current errors are closed; they are also the wrong closed.

---

## 2. Huge history — exists/grep live; glob and exec are a different cost class (conceptual)

1500-commit chain, identical tree (`keep.txt` / `TOKEN_STABLE`). Generation 7.1s.

| query | tool | elapsed | probes | eras |
| --- | --- | --- | --- | --- |
| `exists keep.txt` | held | 0.189s | 1 | 1 TRUE |
| `exists keep.txt` | perch | 0.184s | 1 | 1 TRUE |
| `grep TOKEN_STABLE` | held | 0.369s | 19 | 1 TRUE |
| `grep TOKEN_STABLE` | perch | 0.364s | 19 | 1 TRUE |
| `exists *` (glob) | held | **6.451s** | **1500** | 1 TRUE |
| `exec -- true` (20 commits) | held | 0.226s | 20 | 1 TRUE |

Exact `exists` is one `cat-file --batch-check`. Glob `exists *` is one `ls-tree -r` **per commit**. Same answer (`TRUE 1500`, witness `keep.txt`). Thirty-fold slower because `*?[]` is a different algorithm pretending to be the same verb.

Oscillating 360-commit flip (`TOKEN_FLIP` in the middle third) is the occupancy the primitive exists for, and it is fast:

```
$ ./held -C $HUGE_FLIP grep TOKEN_FLIP
FALSE  120 commits  00f6887..ed2d036
TRUE   120 commits  88af8dd..f5c71c8
       witnesses: flip.txt
FALSE  120 commits  449661c..a68296c
now=FALSE  true=120/360  eras=3  probes=5
# elapsed=0.138s
```

perch matches. Compression works at hundreds of commits.

`exec` is not that walk. It `git worktree add` then **checkout every SHA**. 20× `true` is 0.23s; 20× `sleep 2 --timeout 0.05` is 1.41s of timeouts. Linear in history. The CLI presents `exists` / `grep` / `exec` as peer subcommands. They are not the same cost.

tenure on kizu `src/git/parse.rs:60`:

```
# first-parent (24 of 244)
now=TRUE  true=22/24  eras=3  probes=46   elapsed=1.001s

# --full (244)
now=TRUE  true=213/244  eras=3  probes=457  elapsed=9.060s
```

No `--timeout`. `--full` is 10× probes because every sample greps seeds and parses every candidate. Fine on kizu. The knob that would bound it is `--limit`, which silently drops the prefix of history — occupancy of a tail, reported as occupancy of the repo.

**Shallow clone is a confident lie** (`git clone --depth 1 file://kizu`):

```
$ git -C kizu-shallow rev-list --count HEAD
1

$ ./held -C kizu-shallow exists CLAUDE.md
TRUE   1 commit   9349dc5
now=TRUE  true=1/1  eras=1
```

Full kizu first-parent is `FALSE 1 / TRUE 23` (birth at the merge). `--full` is `FALSE 1 / TRUE 243` (birth at `e1098c8`). Depth-1 occupancy is “always, from the beginning of the world.” No hint. sitbone depth-1 `exists FocusRiverView.swift` is `FALSE 1/1` with **no** `--full` hint; the 11-commit island the full clone reports is not reachable, so diagnose has nothing to say.

---

## 3. First-parent vs full — `--full` is not the lattice (conceptual, load-bearing)

Synthetic diamond (dates force `git log --reverse` to emit `A C D B M`):

```
A(no) -- B(no) -- M(yes, merge)
     \           /
      C(yes) -- D(yes)
```

First-parent `exists src/app.py` (held) and `src/app.py:3` (tenure) agree: occupancy begins at the merge.

```
$ ./held -C $DIAMOND exists src/app.py
# exists src/app.py  (diamond, 3 of 5 commits, first-parent)
FALSE  2 commits  70b4d04..0286af3  2022-01-01 → 2022-01-04
TRUE   1 commit   3042f3b  2022-01-05
       M merge topic
now=TRUE  true=1/3  eras=2
```

`--full` does **not** say “born on topic at C, joined main at M.” It serializes the DAG into a list and compresses the list:

```
$ ./held -C $DIAMOND --full exists src/app.py
FALSE  1 commit   70b4d04          A
TRUE   2 commits  3bd51b6..1455a54 C..D
FALSE  1 commit   0286af3          B main no occupancy
TRUE   1 commit   3042f3b          M
now=TRUE  true=3/5  eras=4
```

The file never died. `B` is a mainline commit that never had it; it is **adjacent in `git log --reverse`**, so occupancy reports a death and a rebirth. tenure `--full` is the same `FTFT` on `if x > 0`. CANDIDATE already named this (“eras follow `git log --reverse`, not a merge diamond”). Confirmed. `--full` is not “the truth of history”; it is “first-parent, but more rows, still a list.”

Real repos match the documented story:

```
$ ./held -C kizu exists CLAUDE.md
FALSE  1 / TRUE 23
       TRUE starts at 0ea3916  Merge pull request #1 …   # the merge

$ ./held -C kizu --full exists CLAUDE.md
FALSE  1 / TRUE 243
       TRUE starts at e1098c8  chore: bootstrap CLAUDE.md…  # the topic birth
```

sitbone `FocusRiverView.swift`: first-parent never held **and** hints `--full`; `--full` recovers the 11-commit island `git log -- PATH` cannot see. perch `--full grep FocusRiverView` further splits that island when NotchOverlay gained then lost the name (`eras=5 boolean=3 holder_splits=2`). That is the occupancy primitive working.

The hole is the other direction: `--full` on a diamond **invents a FALSE gap**. Anyone who takes “eras” as intervals on a timeline is reading a topo-ish list as time.

---

## 4. Renamed paths — three tools, three objects (conceptual)

Fixture: `old.txt` → `new name.txt` → `計画.md`, then `src/app.py` → `src/lib.py` with the same `if x > 0` body.

`exists` is path identity. A rename is death plus birth. Spaces and CJK paths resolve:

```
$ ./held exists old.txt
TRUE 1 / FALSE 4     now=FALSE

$ ./held exists 'new name.txt'
FALSE / TRUE 1 / FALSE 3

$ ./held exists 計画.md
FALSE 2 / TRUE 3     now=TRUE

$ ./held exists src/app.py     # after git mv to lib.py
TRUE 1 then FALSE at the rename

$ ./held exists src/lib.py
FALSE 4 / TRUE 1     now=TRUE
```

`grep TOKEN_RENAME` is content occupancy: one TRUE era across all five commits. perch splits the still-TRUE run when the holder path changes (`boolean=1 holder_splits=2`). That is the pitch.

The holder **string** is not a path. git grep default-quotes non-ASCII; held/perch copy the quoted bytes:

```
$ ./held grep TOKEN_RENAME
TRUE   5 commits
       witnesses: old.txt, "\350\250\210\347\224\273.md"

$ ./perch grep TOKEN_RENAME
TRUE 1  holders: old.txt
TRUE 1  holders: new name.txt
TRUE 3  holders: "\350\250\210\347\224\273.md"

$ git grep -l TOKEN_RENAME HEAD
HEAD:"\350\250\210\347\224\273.md"

$ git -c core.quotepath=false grep -l TOKEN_RENAME HEAD
HEAD:計画.md
```

`exists 計画.md` talks to `cat-file` with a real path. `grep` occupancy talks to `git grep` and then claims the quoted spelling is who is holding. A later `exists` of that witness misses.

tenure on the moved stack does the thing `exists` will not: occupancy stays TRUE, holders move.

```
$ ./tenure -C $RENAME src/lib.py:3
# if x > 0
FALSE  3 commits
TRUE   1 commit   holders: src/app.py:process
TRUE   1 commit   holders: src/lib.py:process
       + src/lib.py:process
       - src/app.py:process
now=TRUE  true=2/5  eras=3  boolean=2  holder_splits=1
```

`--follow` is still listed as a mutation on held/perch. tenure already follows the **stack**, not the path. Asking `exists src/app.py` after a move is a different question than asking `tenure src/lib.py:3`. The family does not say so at the prompt.

---

## 5. Binary files — `-I` occupancy death; NUL source is an empty stack (conceptual)

`visible.txt` and `secret.bin` / `src/evil.py` all contain `TOKEN_BIN`. The binaries include a NUL. git grep:

```
# git grep -I TOKEN_BIN HEAD   → (no hits)
# git grep    TOKEN_BIN HEAD   → HEAD:secret.bin  HEAD:src/evil.py
```

held/perch grep always pass `-I`. After the text copy is deleted, occupancy is FALSE even though the token still lives in two tracked blobs:

```
$ ./held -C $BINARY grep TOKEN_BIN
TRUE   1 commit   witnesses: visible.txt
FALSE  1 commit   remove text TOKEN_BIN, binary still has it
now=FALSE  true=1/2

$ ./perch -C $BINARY grep TOKEN_BIN
# same eras, holders: visible.txt then death
```

`exists secret.bin` stays TRUE. Path occupancy sees the binary; content occupancy pretends it is not a holder. That is git’s binary skip, promoted to a historical fact.

tenure pinning the clean sibling `src/app.py:3` survives and names `src/evil.py` as a **mention echo** (seed hit, stack not occupied — the parser will not sit in a NUL-tainted file):

```
$ ./tenure -C $BINARY src/app.py:3
TRUE   2 commits  holders: src/app.py:process
       echo   src/evil.py  mention (token, no occupant)
now=TRUE  probes=4
```

Pinning the binary itself is a closed error, not a decode crash (worktree `read_text(..., errors="replace")` keeps the NUL; Python/brace frames come out empty):

```
$ ./tenure src/evil.py:3
tenure: src/evil.py:3 has an empty stack
# rc=2   file is 88 bytes, one NUL, the `if x > 0` line is still there

$ ./tenure secret.bin:1
tenure: secret.bin:1 has an empty stack
# rc=2
```

The line is visible to `cat -v`. Occupancy of a path-condition refuses it because the object is a parsed stack, and the parser treats a single NUL as “no stack.” Not a crash. Also not “this `if` occupied evil.py.”

---

## 6. Predicates that are always true — `--boolean` is the only brake (conceptual)

`exec -- true` is occupancy of the constant. JSON knows (`always_held: true`). Human output does not say “always”; it is a normal TRUE island.

```
$ ./held -C $ALWAYS exec -- true
TRUE   4 commits
now=TRUE  true=4/4  eras=1  probes=4
```

`exists *` / `grep .` are always TRUE on any nonempty tree. held compresses to one era (witness union truncated). perch treats “who is holding **every path**” as the inventory and emits one era per addition:

```
$ ./perch -C $ALWAYS exists '*'
TRUE 1  holders: a.txt
TRUE 1  holders: a.txt, b.txt       + b.txt
TRUE 1  holders: a.txt, b.txt, c.txt
TRUE 1  holders: a.txt, b.txt, c.txt, src/app.py
now=TRUE  true=4/4  eras=4  boolean=1  holder_splits=3
```

Same split on `grep .`. On skills `--limit 12 grep .`: `true=12/12  eras=5  boolean=1`, holders `(+56)` … `(+65)`. `exists '*SKILL.md'` on skills is the documented catalog (one TRUE occupancy, an era per plugin). Correct for “who is holding a glob.” Loud if you meant “did any file exist.” There is no `--min-era` / `--boolean` default for tautologies.

`grep -v NEVER_THIS_STRING_9f3a` (pattern matches nothing, invert): always TRUE, holder is the placeholder for a negative:

```
$ ./held grep -v NEVER_THIS_STRING_9f3a
TRUE   4 commits
       witnesses: (no match)
now=TRUE  true=4/4

$ ./perch --json grep -v NEVER_THIS_STRING_9f3a
always_held True
holders ['(no match)']  kind birth
```

“Who is holding” a universal negative is `(no match)`. Occupancy of “this string is absent” has no witness file; perch still prints one.

Empty pattern is accepted and matches every blob:

```
$ ./held -C $ALWAYS grep ''
# grep    (always, 4 commits, first-parent)
TRUE   4 commits
       witnesses: a.txt, b.txt, c.txt, src/app.py
now=TRUE  true=4/4
```

**Invalid regex is silent never-held.** `git grep -e '['` is `fatal: brackets ([ ]) not balanced` (rc 128). held/perch treat any grep rc `> 1` as “path absent in this tree → no match,” then diagnose finds no case/`--full` hits either:

```
$ ./held -C $ALWAYS grep '['
FALSE  4 commits
now=FALSE  true=0/4  eras=1  probes=20
# rc=1   hints=[]  warnings=[]

$ ./perch -C $ALWAYS grep '['
# identical FALSE island, probes=20
```

A broken predicate is reported as a historical fact: this never held. 20 probes are the per-commit fallback plus never-held diagnosis, all fatalling the same way, none of it shown. This is the occupancy analogue of pin’s truncated token resolving as `deleted`.

tenure `if True` is not a tautology in the math sense. Occupancy starts when the line appears:

```
$ ./tenure -C $ALWAYS src/app.py:3
# if True
FALSE  3 / TRUE 1
holders: src/app.py:process
always_held False
```

That is the object (the stack in the tree), not `exec true`.

---

## 7. Timeouts — timeout is occupancy death, not unknown (conceptual)

`--timeout 0` (and `--timeout -1`) makes `exec -- true` never-held. Python `subprocess.run(..., timeout=0)` raises `TimeoutExpired` before `true` can finish. held/perch map that to `False, ["(timeout)"]`. Human format prints witnesses **only on TRUE eras**, so the word `(timeout)` is invisible:

```
$ ./held --timeout 0 exec -- true
FALSE  3 commits
now=FALSE  true=0/3  eras=1  probes=3
# rc=1  elapsed=0.100s   no witnesses printed

$ ./held --json --timeout 0 exec -- true
never True  holds False
era False  w_start ['(timeout)']  w_end ['(timeout)']
```

A predicate that is actually TRUE on some trees and slow on others becomes a FALSE gap:

```
$ ./held --timeout 0.25 exec -- bash -c 'if test -f slow; then sleep 8; exit 0; else exit 0; fi'
TRUE   1 commit   fast only
FALSE  1 commit   slow present      # JSON witnesses: (timeout)
TRUE   1 commit   slow gone
now=TRUE  true=2/3  eras=3
```

The slow commit would have exited 0. Occupancy reports it did not hold. JSON still knows; the human report looks like the file `slow` falsified the predicate.

20 commits × `sleep 2` × `--timeout 0.05` → `FALSE 20/20` in 1.41s. Bound is `timeout × N`, not a global budget. tenure has **no** `--timeout` at all (kizu `--full` 9s is luck of repo size).

Process-group leak of `bash -c 'sleep 87'` did **not** reproduce on this macOS run (`pgrep` empty after held and perch). Not cited as a kill. The mapping timeout→FALSE is the conceptual miss either way.

---

## What survived

- Empty repo without `--now` is a clean exit 2, no stacktrace. All three.
- 1500-commit exact `exists` / `grep` stay well under a second. Flip 360 is the right `FTF` in 0.14s.
- sitbone `FocusRiverView` first-parent still hints `--full`; `--full` still beats `git log -- PATH` (empty). perch still splits NotchOverlay on that island.
- kizu `CLAUDE.md` `--full` still names `e1098c8`, not the merge. tenure `parse.rs:60` still splits `git.rs` → `parse.rs` (probes 46 first-parent / 457 `--full`).
- Spaces in `exists 'new name.txt'` and CJK `exists 計画.md` round-trip via `cat-file`.
- tenure follows a **stack** across `app.py` → `lib.py` without a FALSE gap. That is the rename story exists cannot tell.
- Binary pin is fail-closed (`empty stack`), not a `UnicodeDecodeError`.
- `exec -- true` on a tiny repo is honest TRUE. perch `--boolean` still recovers held on huge grep.
- tenure `--selftest` 16/16. CLIs still `--help`.

---

## Kill / keep

**Keep all three. Mutate all three. Do not rewrite in this pass.**

The occupancy object is still the missing partner of bisect. perch’s ghost on `preact-zero-mock` and tenure’s sitbone echo vs `grep isEnabled` were not touched by these attacks and still justify the lineage.

| tool | do not kill because | mutate toward |
| --- | --- | --- |
| held | Exact exists/grep at 1500 commits is cheap. sitbone deleted-path and kizu merge-vs-birth still need this verb. Empty is fail-closed. | Invalid regex must not look like never-held (git rc 128 is not “no match”). Human FALSE eras must show `(timeout)` / refuse `--timeout 0`. `--now` on a commit-less dirty tree is a sample, or a distinct error. `core.quotepath=false` on grep witnesses. Glob `exists` should not pretend to be the batch path. `--full` should not invent a FALSE gap across a merge diamond (or must say “list order, not lattice”). |
| perch | Holder splits and `--boolean` still distinguish TOKEN reincarnation from boolean occupancy. skills glob catalog is the inventory the primitive claims. | Same regex/timeout/quoting/lattice as held. Tautology (`grep .`, `exists *`, `grep -v NEVER`) should default to `--boolean` or cap holder eras — “who holds everything” is a changelog of the tree. `(no match)` is not a holder. |
| tenure | Stack occupancy across kizu’s file split and the synthetic rename is not `when \| grep`. Echoes still unmask sitbone `isEnabled`. Selftest holds. | `--full` needs a budget or cache (`probes=457` / 9s on 244 commits, no `--timeout`). `--now` before first commit. NUL / binary source: refuse as binary, do not “empty stack” a visible `if`. Lattice same as held. `--rev` still pins the worktree file when it exists (named in CANDIDATE; not re-probed here). |

A one-line held/perch change that mapped grep rc 128 to `HeldError` would hide the silent-FALSE and would not touch lattice, `-I`, rename, or timeout-as-death. Not applied.
