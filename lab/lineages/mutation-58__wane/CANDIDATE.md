# mutation-58 — wane

## Primitive

Two git trees in. Emit the **exclusive-A path-condition stacks** that died (true on A, false on B), then **occupy those stacks through history**. Invert the trees to ask what was born.

A mixed covering set is not this. `thatch` reserved 1–2 exclusive-A slots and spent the rest on exclusive-B births and leftover AB `else`. wane's default cover is deaths only.

## Why this might not exist

`thatch A B` answers "which stacks cover this delta?" Developers who want the island's own question still get HEAD camera births and a copied `guard totalTime>0` move under `--limit`. `sheaf | tenure` greps the if-text. `tell --cover` occupancy-greedies B-side module names. Tenure cannot invent the stack from two trees, and cannot occupy a pin whose file is gone at `--rev`.

The recurring annoyance is: *this file is gone, `git log -- path` is empty, I want the stacks that died, not a mixed budget of what replaced them.*

Discarded as concatenation: `thatch --limit` plus a filter; covering with `exists *FocusRiverView*` and occupying the first witness line; printing two sections.

## How to run

```bash
chmod +x ./wane
./wane --selftest
./demo.sh
./wane -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --limit 6 14b1d6e HEAD
./wane -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone 70ec7df^ 70ec7df
./wane HEAD :worktree
```

Python 3.10+, stdlib, git. Vendored `whenline` from thatch/tenure. Exit 0 if the trees differ, 1 if identical, 2 on error. `--no-occupy` is covering only. `--walks` prints `tenure FILE:LINE` lines (pin from the true-side snapshot). Invert A/B to name births as deaths.

## Empirical transcript

### Before the improvement

Ancestor thatch on sitbone island `14b1d6e` vs HEAD `--limit 6` reserved one exclusive-A slot then filled with exclusive-B:

```
A   exclusive_a  given ¬(app.flowScore>0.2) | given ¬(app.flowScore<-0.2)
B   exclusive_b  guard let frame = await frameProvider.captureFrame()
B   exclusive_b  try makeTempDir() defer
B   exclusive_b  guard let self | given ¬(fresh) | if isFirst | …
# git log -- FocusRiverView.swift is empty. Five of six slots are births.
```

wane v1 flipped the pool: exclusive-A only, prefer the `if app.flowScore>0.2` true-arm, no exclusive-B, no AB else. Sitbone island `--limit 6` then spent leftover on vanished stacks inside *surviving* files, and walked them `--full --rev 14b1d6e` because tree A is off first-parent:

```
A   exclusive_a  if app.flowScore>0.2
                 holders A: FocusRiverView.swift
A   exclusive_a  given ¬(app.flowScore>0.2) | given ¬(app.flowScore<-0.2)
A   exclusive_a  elif app.flowScore<-0.2
A   exclusive_a  switch current | case .flow | … | if idle<thresholds.flowRecovery
                 holders A: SitboneCore.swift:tick
A   exclusive_a  switch current | case .flow | …          # sibling arm
A   exclusive_a  switch current | case .flow | …          # sibling arm
walk  tenure --full --rev 14b1d6e FocusRiverView.swift:121
walk  tenure --full --rev 14b1d6e SitboneCore.swift:138   # file lives on HEAD
```

kizu `3b3e0a9^` vs `3b3e0a9` is a holder move (thatch's money shot). v1 correctly refused `role=move`, then filled `--limit` with `arm |` stacks that died inside surviving `git.rs`. That is exclusive-A, but it is not what died as a file.

Birth `14b1d6e^` vs `14b1d6e` is empty (nothing died). Invert names the born stack. Fixture island vs 8-module flood is one `if flow_score > 0.2` occupying `src/river.py:bar_color`. TOKEN_A silent. `計画.md` unexplained.

### After the improvement

Forced by sitbone island leftover, not polish.

1. **Deleted files first, leftover stays there.** Default cover is exclusive-A stacks whose holders sit on only-A paths (the file died). Vanished stacks inside surviving files are `--also-changed`. kizu's `arm |` flood and SitboneCore tick siblings drop out unless asked.
2. **`--full` is a property of this stack's file.** v1 treated "tree A is off first-parent" as a walk flag for every exclusive-A member. Surviving files walk first-parent of HEAD. Island files still `--full --rev` the true-side snapshot.

Same island command:

```
A   exclusive_a  if app.flowScore>0.2
                 holders A: FocusRiverView.swift
A   exclusive_a  given ¬(app.flowScore>0.2) | given ¬(app.flowScore<-0.2)
A   exclusive_a  elif app.flowScore<-0.2
walk  tenure --full --rev 14b1d6e FocusRiverView.swift:121
# no SitboneCore tick. no CameraDetector birth. no else.
```

`git log -- FocusRiverView.swift` is empty. wane named the dead stacks and occupied them from HEAD with a pin reconstructed from tree A.

kizu default is empty (nothing died as a file; the split is a move). `--also-changed` would name `git.rs` exclusive-A arms; thatch still names the move.

Fixture island and sitbone death `70ec7df` unchanged.

## Dogfood targets

| target | what we asked |
| --- | --- |
| synthetic fixture | birth silent; invert names it; move silent; sibling silent; island vs 8-module flood; TOKEN_A; `計画.md`; `:worktree` invert |
| `kizu 3b3e0a9^..3b3e0a9` | default empty (move is AB); not claimed as a death |
| sitbone `14b1d6e^..14b1d6e` | birth empty |
| sitbone `70ec7df^..70ec7df` | FocusRiverView death, `if app.flowScore>0.2` |
| sitbone `14b1d6e` vs HEAD `--limit 6` | island; `git log -- path` empty; exclusive-A only |
| sitbone PresenceArbiter vs its birth parent | `isEnabled` is a birth; silent |

Read-only on the real repos.

## Surprises

- Exclusive-A of a *changed* file is a real death of a stack identity (`given ready | if x>0` dies when production grows `enabled`). It is the wrong covering member for a deleted-file island under a size budget.
- thatch's island reservation already named one FocusRiverView stack. The flip is occupying the whole `--limit` with deaths, then refusing to spend leftover on surviving-file internals.
- Invert (`wane B A`) is the birth verb. A `--born` flag would have been mixed cover in disguise.
- `if app.flowScore>0.2` (true-arm) ranks above `given ¬(flowScore)` else. thatch's pin was the midpoint of the default color arm.

## Failures

1. **Match-arm / `if let` / Swift `guard-else` pairing** inherited from `when`. kizu `--also-changed` still emits `arm |` test stacks.
2. **Non-source delta** (計画.md, lockfiles, binaries) stays unexplained. That is the object, not a bug.
3. **Walk lines** name `tenure` on PATH. Demo rewrites the token to a worktree binary.
4. **Full-tree stack discovery** parses every source blob on both sides.
5. **A copied stack** (`guard totalTime>0` now in SiteObserver) is AB, so a deleted file whose every stack was copied is unexplained. Honest: the stack did not die.

## Suggested mutations

- Cluster sibling arms (`if flowScore>0.2` / `elif flowScore<-0.2` / given-else) as one obituary.
- `--echo no|mention|related` to quiet kizu `app.rs` when `--also-changed`.
- Pipe `wane A B | tenure --stdin`.
- Cache probes `(sha, cond_key, grain)`.

## Flipped assumption: bought and lost

thatch assumed the covering members are the mixed set that distinguishes two trees (exclusive sides reserved, AB leftovers). Tenure assumed the user already has `FILE:LINE`. Concatenation assumes token occupancy *is* stack occupancy.

**Bought**

- The output is the stacks that died. You do not re-rank a mixed catalog, then ignore the births.
- Invert is the birth question. One verb.
- Occupancy detaches identity from the walk end. The island file is gone at HEAD; the stack still gets eras.

**Lost**

- kizu `git.rs → parse.rs` is a move, not a death. thatch's money shot is silent here.
- Birth covering of FocusRiverView is empty. Invert to name `guard totalTime>0`.
- Surviving-file stack deaths are behind `--also-changed`.

## Kill / keep

**Keep.** It is not `thatch | awk '$1=="A"'`. On the first real deleted-file island it spent `--limit` on `if app.flowScore>0.2` (and the sibling color arms), occupied them `--full` without being told the name, the pin, or `--full`, and refused HEAD `else` / camera births. On the first real Rust split it stayed silent, which is the object: a move is not a death.

Kill only if a later generation proves that filtering thatch's exclusive-A column recovers the island pin *and* does not inherit `--full` onto surviving-file leftovers — v1 did inherit it; the improvement is the object.
