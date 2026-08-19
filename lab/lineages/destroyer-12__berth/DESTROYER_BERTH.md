# DESTROYER — berth

Adversarial pass on **file-identity occupancy**. No rewrites. Failures are conceptual except where git's own R/D+A records already refuse the `git mv`. Not leftover-name search. Not a clone of DESTROYER_OCCUPANCY (timeout / `-I` / empty-repo / glob cost stay there).

- **berth** (mutation-52) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6b-7144-7812-8fcb-cbf1c493bd9a` @ `2c5fe99`
- Transcript: `/tmp/destroy-berth/transcript.txt`
- Follow-up: `/tmp/destroy-berth/followup.txt`
- Fixtures: `/tmp/destroy-berth/fixtures/`
- Drivers: `/tmp/destroy-berth/attack.py`, `/tmp/destroy-berth/followup.py`
- `./demo.sh 0` → `PASS=79 FAIL=0` after the attacks. Victim not edited.

Related (cite, do not absorb): **rove** already resolved identity from all-reachable R so first-parent `grep -- PATH` on a dead name still occupies dest. **ditto** / **pup** / **crib** already distinguished C056 leftover-blob COPY from R100 FOLLOW. This pass asks whether berth's *exists* roost is the file that moved.

Attacks: copies vs renames, kizu C056 leftover blob, first-parent vs all-reachable R, binary dests, NFD paths, merge-of-merges, `git mv` then edit, two files swapping names.

Verdict: **mutate, do not kill.** `--full` still stitches kizu `R100 deep-research-ai-agent-hooks.md → docs/…` as one 187-commit roost from either name. A leftover-blob copy is still not a follow. Sitbone FocusRiverView island and skills `preact-zero-mock` ghost still hold. The claim “query the old name or the new name; occupancy stays TRUE” is **false on the default first-parent walk**, and default `exists PATH` at a living leftover name occupies the *other* file.

---

## Primitive restated

`berth --follow` (default exact `exists`) occupies a **file identity**. A recorded rename is one roost, not a path death plus a birth. Query the old name or the new name; occupancy stays TRUE and holders still split.

`--no-follow` is ancestor path occupancy. `--boolean` is ancestor `held`. Identity is walked from `git log --find-renames --name-status` on **the same spec as the occupancy walk** (`follow_names` in `berth`). Copies (`C`) are ignored. A later file at a dead path is supposed to be a different identity.

---

## 1. Copies vs renames — copy stays copy (survived)

Exact `cp alpha.txt beta.txt` (source remains). Git, with or without `--find-copies`, records `A beta.txt`. Berth's walker never asks for `C`.

```
$ git log --find-renames --name-status --oneline
R100	old name.txt	new name.txt     # later, clean git mv
A	beta.txt                      # the copy

$ ./berth exists alpha.txt
TRUE   4 commits  holders: alpha.txt
aka=alpha.txt
# rc=0  — copy dest is not this roost

$ ./berth exists beta.txt
FALSE  1 / TRUE 3
holders: beta.txt
aka=beta.txt
# dest is a unique birth

$ ./berth exists 'old name.txt'
       identity: old name.txt → new name.txt
TRUE   1  holders: old name.txt
TRUE   1  holders: new name.txt
       + new name.txt
       - old name.txt
# kinds birth/move. Same roost from 'new name.txt'.
```

`--no-follow` on the old name is still TF path death. Demo gold (copy is not beta; 3-hop CJK rename is one roost) is this object working.

**Copy then later delete the source** is not a delayed `git mv`:

```
$ git log --find-renames --find-copies --name-status
A	beta.txt
D	alpha.txt          # next commit; not R

$ ./berth exists alpha.txt    # TF, dies at the delete, aka=alpha.txt
$ ./berth exists beta.txt     # FT, own birth, aka=beta.txt
```

That is the distinguisher ditto/crib/pup exist for. Berth already refuses to treat a remaining-holder copy as identity. Not a kill.

---

## 2. C056 leftover blob — dest is a silent unique birth (survived + cite)

kizu `5671a72` is git's recorded copy, source still held:

```
$ git -C kizu show -C --name-status --oneline 5671a72
5671a72 refactor: split init installers
M	src/init.rs
C056	src/init.rs	src/init/install.rs
```

Berth never looks at `C`. `--find-renames` on that commit is `A src/init/install.rs` plus `M src/init.rs`.

```
$ ./berth --full exists src/init.rs
TRUE  165 commits  holders: src/init.rs
aka=src/init.rs
# leftover source is its own roost. dest is not picked up.

$ ./berth --full exists src/init/install.rs
FALSE 232 / TRUE 12
TRUE starts at 5671a72
holders: src/init/install.rs
aka=src/init/install.rs
# dest is a unique birth. No copy annotation. No hint.

$ ./berth exists src/init/install.rs          # first-parent
FALSE 19 / TRUE 5   starts at merge 243c46e
       origin: 5671a72  as src/init/install.rs
```

Synthetic extract-and-edit (C077 leftover) is the same shape: `exists src/init.rs` stays on source; `exists src/init/install.rs` is dest birth.

kizu `src/git.rs` → `src/git/parse.rs` (split, leftover source) is the same refusal: `git.rs` true=244/244, `parse.rs` is its own birth at `3b3e0a9`. Tenure's stack follow is a different object. CANDIDATE already said so.

**Do not mutate this into leftover-name search.** The dest *name* is occupied as a birth. The missing verb is crib's (`copy SRC` / extra holder of this blob), which ditto already emits and pup already walks. Identity occupancy that started treating C056 as `init.rs → install.rs` would lie: the source still berths.

---

## 3. First-parent vs all-reachable R — default walk breaks “either name” (conceptual, load-bearing)

The first real-repo rename is `4e37f16` `R100 deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md`. The merge that first-parent sees (`ca0577a`) adds dest as **A**, not R.

`--full` is the roost CANDIDATE sold:

```
$ ./berth --full exists docs/deep-research-ai-agent-hooks.md
       identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
FALSE  57 / TRUE 13 (old) / TRUE 174 (docs/)
now=TRUE  true=187/244  boolean=2  holder_splits=1
# kinds birth/move. Same command on the dead name is the same roost.
```

Default (first-parent) dest works as dest occupancy with an origin footnote:

```
$ ./berth exists docs/deep-research-ai-agent-hooks.md
FALSE   3 / TRUE 21
       origin: 321a830  feat(ui,watcher): …  (55 commits before this merge)
                as deep-research-ai-agent-hooks.md
       holders: docs/deep-research-ai-agent-hooks.md
aka=docs/deep-research-ai-agent-hooks.md
# identity chain is dest-only. The old name is not in aka.
```

Default (first-parent) **dead name** is never-held. The dest is sitting on the same walk after the merge:

```
$ ./berth exists deep-research-ai-agent-hooks.md
FALSE  24 commits
now=FALSE  true=0/24  never=1
hint: never held on first-parent, but existed in 13 reachable
      commits off the mainline (321a830..b826f98). rerun with --full
```

`git log --follow -- deep-research-ai-agent-hooks.md` still names `4e37f16` then `321a830`. `git log --first-parent --` on the old name is empty. Berth's never-held diagnosis re-probes **path** existence on full history (`probe_exists`, not follow), so the hint is `--full`, not “same roost as dest, already TRUE on this walk.” `--follow` and `--no-follow` on the dead name produce the same first-parent lie.

Synthetic non-ff merge (topic `old.txt`→`dest.txt`, main extras, merge adds dest as A) is the same object:

```
$ git log --first-parent --name-status
M: merge topic (dest as A)
A	dest.txt

$ ./berth exists dest.txt
FALSE 3 / TRUE 1
       origin: 834166a  T0: birth old.txt  as old.txt
aka=dest.txt

$ ./berth exists old.txt
FALSE 4/4  never=1
hint: existed in 1 reachable commit off the mainline. rerun with --full
```

`--full` on that fixture **invents deaths**. `git log --reverse` emits `A, T0, B, T1, C, M`. The identity never died; B and C are mainline commits that never had it, adjacent in the list:

```
$ ./berth --full exists dest.txt
       identity: old.txt → dest.txt
FTFTFT   true=3/6  kinds=absent,birth,death,birth,death,birth
```

CANDIDATE already named “eras follow `git log --reverse`, not a merge diamond.” Confirmed on identity, not just path occupancy. DESTROYER_OCCUPANCY §3 is the same lattice lie; this is that lie **after** a successful R stitch.

**Rove already mutated this.** mutation-67: resolve identity from all reachable R, occupy the requested walk. First-parent `grep -F '10 の AI' -- deep-research-ai-agent-hooks.md` became the dest roost. Berth's `exists` still uses the walk's own name-status.

`--limit` is the same hole in miniature. Rename at t1, then five noise commits:

```
$ ./berth --limit 3 exists old.txt
FALSE 3/3  never=1
hint: existed in 1 reachable commit off the mainline. rerun with --full
# the R is just outside the window; dest is in the window and is the same identity

$ ./berth --limit 3 exists new.txt
TRUE 3/3  aka=new.txt     # dest-only; no stitch
```

CANDIDATE listed “`--follow` with `--limit` can miss a rename outside the window.” Confirmed. The hint still talks like a side-branch path.

---

## 4. Binary dests — exact R is identity; rewrite is D+A; `-I` is grep (mixed)

Exact `git mv secret.bin hidden.bin` (NUL payload, no edit):

```
R100	secret.bin	hidden.bin

$ ./berth exists secret.bin
       identity: secret.bin → hidden.bin
TRUE 1 holders: secret.bin
TRUE 4 holders: hidden.bin
# same roost from hidden.bin. Binary dest is a first-class identity.
```

Binary copy leftover (`clone.bin`, source remains) is a unique birth. Same distinguisher as text.

`git mv payload.bin payload2.bin` **and rewrite** in one commit: git records `D`/`A` even with `--find-renames=20`. Berth follows the letters:

```
$ ./berth exists payload.bin     # FTF, dies at the "rename", aka=payload.bin
$ ./berth exists payload2.bin    # FT, unique birth, aka=payload2.bin
```

`grep TOKEN_BIN` always passes `-I`. After the text sibling is the only non-binary holder, occupancy is `visible.txt` forever; the binary that still contains the token is not a holder. That is DESTROYER_OCCUPANCY §5, not an identity bug. `exists` of the binary path still works.

Identity of a binary is “exact R, or death.” `git mv` intent plus a rewrite is not a roost. Same as §7.

---

## 5. NFD paths — spelling is the identity; the FS is not (conceptual)

APFS treats NFC `café.txt` (`c3 a9`) and NFD `café.txt` (`65 cc 81`) as one directory entry (`lexists` both True). Git `cat-file` does not.

```
$ git -c core.precomposeunicode=false add   # stored NFD bytes
$ git ls-files -z | xxd
00000000: 6361 6665 cc81 2e74 7874 00        # cafe + combining acute

$ git cat-file --batch-check
HEAD:café.txt        → missing          # NFC
HEAD:café.txt        → <blob>           # NFD

$ ./berth exists café.txt                 # NFC query of NFD blob
FALSE 1/1  never=1  ident=[]

$ ./berth exists $'cafe\xcc\x81.txt'      # NFD query
TRUE 1/1   aka=café.txt
```

Inverse if `core.precomposeunicode=true` stores NFC: NFD query is never-held.

When a recorded R chain *contains* both spellings (`NFC → moved-cafe.txt → NFD`), querying either stitches. That is follow working on git's bytes, not Unicode identity. A user who types the composed name of an NFD-only blob gets “never held,” while the worktree path they are looking at exists.

Not leftover-name search. The roost's name is a byte string. `--now` uses `os.path.lexists` and would say TRUE for both spellings of a dirty tree; history seed uses `cat-file` and disagrees.

---

## 6. Merge-of-merges — one file, two dests; first R wins (conceptual, load-bearing)

Rename/rename: `file.txt` → `left.txt` on left, → `right.txt` on right, then merge the merges. Git:

```
CONFLICT (rename/rename): file.txt renamed to left.txt in HEAD
                          and to right.txt in right.
# resolved by keeping both dests

$ git log --first-parent --find-renames --name-status
M1  R060	file.txt	left.txt
M2  A	right.txt
```

```
$ ./berth exists file.txt
       identity: file.txt → left.txt
TRUE always, holders file.txt then left.txt
# first-parent first R is left. right is not this roost.

$ ./berth exists left.txt     # same roost as file.txt

$ ./berth exists right.txt
FALSE 3 / TRUE 1 (M2)
       origin: b48ad44  A: birth file.txt  as file.txt
aka=right.txt
# dest-only identity. Origin claims the same birth file.txt already
# gave to left.
```

`--full exists file.txt` is `TTFT`: death across `B: main extra` and the right-side rename, rebirth at M1. `--full exists right.txt` is `TFTTFT` (dies when left renamed it, rebirths on main where `file.txt` still sat, moves to right, dies at M1, rebirths at M2). The file never flickered like that. First-parent picked a side. Full history listed both sides as a timeline.

Two dests of one identity both origin-name the birth. Querying the birth name occupies only left. That is a **split**. CANDIDATE said `--follow` of a split is tenure's object. Confirmed: berth will not occupy both roosts, and will not say it split.

---

## 7. `git mv` then edit — identity is similarity, not the mv (conceptual)

Tiny edit in the same commit as `git mv src.rs mid.rs`: `R098`. Identity holds (`src.rs → mid.rs`).

Rewrite ~0% similar in the same commit as `git mv mid.rs dst.rs`:

```
$ git log --find-renames --name-status
A	dst.rs
D	mid.rs
# --find-renames=20 is still D+A

$ ./berth exists src.rs
       identity: src.rs → mid.rs
TTF  now=FALSE     # dies at the rewrite. dst.rs is not in aka.

$ ./berth exists dst.rs
FT   aka=dst.rs    # unique birth of the rewritten dest
```

`git mv` happened. The roost died because `--find-renames` default 50% (and 20%) refused the letter R. Occupancy of “the file that moved” is occupancy of git's similarity record. A caller who typed `git mv` and then rewrote the dest cannot ask the old name and land on dest.

Same object as binary mv+rewrite (§4). Not a one-line bug.

---

## 8. Two files swapping names — default exists is the wrong roost (conceptual, load-bearing)

### Same-commit swap (`git mv a tmp; git mv b a; git mv tmp b`)

Git does **not** record R. Both names still exist:

```
$ git show --find-renames --name-status HEAD~1
M	a.txt
M	b.txt
# contents: a.txt is now BBB, b.txt is now AAA
```

```
$ ./berth exists a.txt
TRUE 3/3  aka=a.txt   holders: a.txt     # path occupancy
$ ./berth exists b.txt
TRUE 3/3  aka=b.txt   holders: b.txt

$ ./berth grep AAA-IDENTITY
TRUE 1 holders: a.txt
TRUE 2 holders: b.txt      # kind move. Content roost traded.

$ ./berth --no-follow exists a.txt
TRUE 3/3                   # same answer as --follow
```

`--follow` ran and found no R. The badge says follow; the occupancy is the path. The file that was `a.txt` now lives at `b.txt`. `exists a.txt` will not say so. Grep of a unique token will. That is perch/roost content occupancy, which CANDIDATE said `exists` cannot do because “the holder *is* the path.” After a swap the holder is *not* the path, and there is no R to patch it.

### Serialized swap (three commits, three R100)

```
R100	a.txt	tmp.txt
R100	b.txt	a.txt
R100	tmp.txt	b.txt
# HEAD a.txt = BBB, HEAD b.txt = AAA
```

```
$ ./berth exists a.txt
       identity: a.txt → tmp.txt → b.txt
holders at HEAD: b.txt          # occupies AAA, which is no longer named a

$ ./berth exists b.txt
       identity: b.txt → a.txt
holders at HEAD: a.txt          # occupies BBB

$ ./berth --no-follow exists a.txt
TFT   path a died then reincarnated (the other file)
```

Default `exists a.txt` follows the **first** existence of that path (original AAA) forward through R, and reports the dest. The file the user is looking at (`a.txt` = BBB) is the *other* identity, reachable only by querying `b.txt`. The living name is the wrong handle for its occupant.

### Leftover name recreated (the suggested `--now` mutation, confirmed)

```
t0  old.txt = ORIG
t1  git mv old.txt new.txt          # R100
t2  recreate old.txt = REINCARNATED
```

```
$ ./berth exists old.txt
       identity: old.txt → new.txt
TRUE 1 holders: old.txt
TRUE 2 holders: new.txt      # HEAD holders are new.txt
now=TRUE
# the file sitting at old.txt is invisible

$ ./berth --no-follow exists old.txt
TFT   now=TRUE  holders at HEAD: old.txt    # the leftover occupant
```

`--now` of a leftover that exists only in the worktree is the same lie (CANDIDATE suggested mutation; confirmed):

```
$ git mv old.txt new.txt && echo DIRTY-REINCARNATE > old.txt

$ ./berth --now exists old.txt
       identity: old.txt → new.txt
holders at WORKTREE: new.txt     # ignores the dirty leftover
$ ./berth --now --no-follow exists old.txt
TFT  WORKTREE holders: old.txt   # path occupancy sees it
```

Dirty `git mv` is the **inverse** of the first-parent merge hole:

```
$ git mv 'old name.txt' 'new name.txt'     # uncommitted

$ ./berth --now exists 'old name.txt'
holders: old name.txt then WORKTREE new name.txt    # query dead name, see dest

$ ./berth --now exists 'new name.txt'
FALSE  never=1     # query live dest: no commit seed, follow_dirty_name never runs
```

Committed merge (kizu): query dest works, query old name does not. Dirty tree: query old name works, query dest does not. “Either name” is not a symmetry. It depends on whether the R is on the walk you already paid for.

`follow_names` seeds from the **first** `cat-file` hit of the query path, then walks R forward. A leftover occupant at that path after the identity left is never a seed. `--now` only remaps the last historical name through `git diff -M`. It will not start a new identity for a leftover path.

---

## What survived

- `./demo.sh 0` → `PASS=79 FAIL=0`. Victim not touched.
- kizu `--full` dest and dead name: same roost, `true=187/244`, kinds `birth/move`, not ghost.
- kizu first-parent dest origin is still `321a830 as deep-research-ai-agent-hooks.md`.
- kizu `exists CLAUDE.md` origin is still `e1098c8`.
- C056 leftover `src/init.rs` does **not** follow into `install.rs`. `git.rs` does **not** follow into `parse.rs`.
- sitbone first-parent `FocusRiverView.swift` still hints `--full`; `--full` is the 11-commit island; `--full grep FocusRiverView` is still `boolean=3` kinds `birth/spread/shrink`.
- skills `grep preact-zero-mock` is still README-only ghost. circuit-breaker path death is still FTF.
- Spaces rename, 3-hop CJK, directory `src/ → lib/` file-by-file, case-fold `Foo.txt → foo.txt`, exact binary `git mv`, uncommitted `--now` from the *old* name: identity holds.
- Copy (exact, leftover-blob, binary, copy-then-delete-source) is not a follow.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “the file that moved,” which neither `git log --follow` (changes, backward, living name) nor roost `exists PATH` (path death plus birth) will occupy. kizu `--full` 187 from either name, dest first-parent origin `321a830`, leftover-blob refusal, sitbone island, skills ghost — none of that became `git log --follow --name-only` under these attacks. Do not kill because first-parent dead-name is never-held, because a swap is M/M, or because NFD is a different byte string. Those are mutations. Killing them would throw away the R100 roost to hide a same-spec name-status walk.

| do not kill because | mutate toward |
| --- | --- |
| `--full` R100 kizu `true=187` from either name; dest FP origin `321a830 as <old>`; demo 79/79; copy/C056 leftover is not a follow; sitbone island; skills ghost | **Resolve identity from all reachable R, occupy the requested walk** (rove already did this for `grep -- PATH`). First-parent `exists` of the dead name must be the dest roost, not never-held + `--full`. Identity `aka=` on dest FP must name the old path. |
| | **Seed from the occupant at the walk tip.** If the query path exists at HEAD / WORKTREE, that file is the identity (walk incoming R backward). A leftover name is a new roost. A dead name with no tip occupant walks outgoing R forward. Today's first-existence seed makes `exists old.txt` after recreate report `new.txt`. |
| | **`--now exists DEST` of an uncommitted `git mv`** must see dest (today never-held). Dirty follow is already implemented from the old name; the dest query has no seed. |
| | **`--full` must not invent FALSE gaps** across a merge diamond / merge-of-merges (list order ≠ lattice). Same mutation as held/perch/tenure. Say “list order” or occupy the merge lattice. |
| | **Rename/rename split:** if two dests share a birth, say split (or refuse). Do not origin-name `file.txt` on `right.txt` while `exists file.txt` occupies only `left.txt`. Tenure's object stays the stack, not this. |
| | **`git mv` + rewrite below similarity is D+A.** Human report should not look like a unique birth of dest and a death of source without naming the missing R. Do not lower `-M` globally (false follows). |
| | **NFC/NFD:** either normalize the seed (one user-visible name) or print the stored bytes and refuse the other spelling with a hint. `lexists`/`cat-file` disagreement under `--now` is the dirty form. |
| | Same-commit name swap is M/M. `--follow` that found no R is path occupancy; do not print `aka=a.txt` as if identity ran. Grep of a unique token already splits. |

A one-line change that pointed first-parent never-held at dest would hide the kizu dead-name transcript and would not touch leftover-name seed, swap M/M, NFD, or rewrite-as-D+A. Not applied.

Do not grow a rename platform. The next mutation is **rove's all-reachable R for `exists`**, plus tip-occupant seed so a living leftover is its own roost — not leftover-name search, and not crib's leftover-blob copy.
