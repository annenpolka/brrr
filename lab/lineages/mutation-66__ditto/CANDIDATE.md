# mutation-66 — ditto

## Primitive

Two trees in; emit covering predicates that distinguish them as ready-to-run `held`/`berth` lines. Same blob still present on A and also born on B is **COPY**, not FOLLOW.

Path existence is not identity. `git mv a.rs b.rs` is one follow (A name gone). `cp a.rs b.rs` is one copy (both names exist; B is a new holder of the same blob). ditto does not walk history. `ditto A B | sh` may run held/berth.

## Why this might not exist

`glyph --follow` treats a same-blob path change as one identity. That is correct for a rename. It is wrong when the blob remains on A: exclusive-side SHA pairing will call `twin.rs` → `b.rs` a follow even though `a.rs` still holds the blob. `sheaf` treats the dest as a birth (`exists b.rs`). `git diff --name-status -C` prints `C100`. `berth --follow` already refuses to treat a copy as identity — but it answers occupancy, it does not emit the covering question.

The recurring annoyance: you are staring at two trees, one of them a `cp`, and occupancy tools either ask you for a follow of a path that never died or a birth that does not name the source.

Discarded as too conventional: wrapping `git diff -C --name-status`, always emitting two exists, merging ditto into berth so the emitter walks history.

## How to run

```bash
./ditto --help
./demo.sh
./ditto -C /path/to/repo HEAD~1 HEAD
./ditto -C /path/to/repo --held 14b1d6e^ 14b1d6e
./ditto -C /path/to/repo --berth --walks 14b1d6e HEAD
./ditto -C /path/to/repo --no-copy HEAD~1 HEAD
./ditto -C /path/to/repo --no-follow HEAD~1 HEAD
./ditto HEAD :worktree
```

## Empirical transcript

### Before the improvement

v1 pairs exact-SHA copies (dest born, blob still on a shared path) and refuses exclusive-side follow when that blob remains. Clean `git mv` is still one follow. Sitbone cover stayed `grep FocusRiverView`.

**Exact `cp a.rs b.rs` (both exist):**

```
# C   11  copy a.rs → b.rs                                  1 path
held -C repo --rev B --limit 12 exists b.rs
# walks do not carry --follow
```

**Remaining blob (glyph's false follow):** `a.rs` and `twin.rs` share a SHA; delete twin, `cp a.rs b.rs`:

```
# C   copy a.rs → b.rs
# A   exists *twin*
# not follow twin.rs → b.rs
```

**kizu R100** still one follow + `grep char_len`. **kizu C056** (`git` recorded `C056 src/init.rs → src/init/install.rs`; init.rs still present, 56% similar, source edited) is a miss — exact SHA only:

```
$ ./ditto -C kizu --limit 6 5671a72^ 5671a72
# B   16  exists *install*                                  1 file
# not copy src/init.rs → src/init/install.rs
# not follow (source still lives — that part is already right)
```

### After the improvement

Forced by kizu `5671a72`, not polish. Dest SHA matches neither side of `src/init.rs` (the source was edited). Compare dest-on-B to source-on-A: line Jaccard 0.551. B-vs-B is 0.04 — extraction emptied the source.

```
$ ./ditto -C kizu --limit 6 5671a72^ 5671a72
# C   26  copy src/init.rs → src/init/install.rs            1 path
held -C kizu --rev 5671a72 --limit 12 exists src/init/install.rs
# not --follow (source still holds)
# not exists *install*
```

Copy+edit leftover-name stays dead: `cp a.rs b.rs` plus `extra_token` is copy + `grep extra_token`, not `grep b.rs`.

Sitbone gold, unchanged:

```
$ ./ditto -C sitbone 14b1d6e^ 14b1d6e
# B   19  grep FocusRiverView      1 file
held -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView

$ ./ditto -C sitbone --limit 6 14b1d6e HEAD
# A   19  grep FocusRiverView
held -C sitbone --full --rev 094769d grep FocusRiverView
```

kizu R100 still one follow, not a copy:

```
$ ./ditto -C kizu 4e37f16^ 4e37f16
# R   follow deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
# B   grep char_len
held -C kizu --follow --rev 4e37f16 --limit 12 exists deep-research-ai-agent-hooks.md
```

`./demo.sh` — 37 assertions. Exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView birth/death/island; cover stays `grep FocusRiverView`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — R100 markdown move `4e37f16` vs recorded copy `5671a72` (`C056 src/init.rs → src/init/install.rs`, blob still at source)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — `第一級` / `MAN-023` vs leftover `向けに調整`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — HEAD~1..HEAD sheaf + held walks
- synthetic fixture: `cp a.rs b.rs` vs `git mv`; remaining-blob twin; directory copy `src/* → lib/*`; oscillate; spaces rename; `計画.md`; nested git; `:worktree`; mv+edit; empty repo

## Surprises

- Exclusive-side same-SHA is not enough to decide follow. If any shared path still holds the blob, the dest is a new holder.
- After a copy, a later `git mv` of one holder while the other remains is also a copy plus a death, not a follow. The blob never uniquely moved.
- Directory copy compresses the same way directory rename does (`copy src/* → lib/*`) but the walk is `exists lib/*` without `--follow`.
- `held --follow exists old` is the wrong paste for a copy: occupancy of the source never died. The distinguisher is dest birth.
- Extract-and-edit copy detection must compare dest-on-B to source-on-A. kizu B-vs-B Jaccard is 0.04; A-vs-B is 0.551. Git's `C056` is the A-vs-B number.

## Failures

- v1 exact-SHA missed kizu `5671a72`. v2 compares dest-on-B to source-on-A; Jaccard 0.551. Cover is copy, not `exists *install*`.
- Copy+edit still spends a sheaf slot on a leftover import (`grep -F 'use anyhow::Result;' -- src/init/install.rs`). Dest *name* leftover is gone; dest *boilerplate* is not.
- Generated `held --follow exists` is still pasteable; current `held` (candidate-09) does not parse `--follow`. Demo runs live berth on follow walks and live held on unary walks. Copy walks are `exists DEST` and run today.
- Unique-basename exclusive pairing can still over-pair a delete+unrelated-add. `--no-follow` recovers.
- Similarity copies can glue two coincidentally similar new files that share an extension. `--no-copy` recovers. Related-path + changed-source scoring is the hedge, not a proof.
- Binary-only dests have no unary grep; an exact-SHA copy still names them.

## Suggested mutations

- Teach `held` / `berth` `--copy exists SRC` so the generated line occupies "new holder of this blob".
- `ditto A B | berth --stdin` so the pipe is predicates-in, eras-out, without `sh`.
- `--code` grain so kizu dest boilerplate (`use anyhow::Result`) does not steal a copy+edit slot.
- Prefer `exists DEST` over a content line when both cover the same copy dest.

## Flipped assumption: bought and lost

Parent glyph (mutation-42) assumed **same-blob exclusive-side pairing is one follow**.

**Bought**

- `cp a.rs b.rs` is one copy member, dest walk without `--follow`.
- Blob still present on a shared path cannot be a follow, even if an exclusive path died with the same SHA.
- Directory copies compress. Mixed commits (kizu R100 + ui.rs) keep a content glyph beside the identity.
- `--no-copy` / `--no-follow` are explicit downcasts, not forks.
- Default walker is held; `--berth` is the identity occupancy consumer. ditto does not walk history.

**Lost**

- Unary TRUE/FALSE of the source does not split a copy: both trees hold the occupant at the old name. The distinguisher is the extra holder.
- A later rename of one of several same-blob holders is reported as copy+death, not `git mv`. Path existence was at least unambiguous.
- Similarity copies need a related-path hedge. Path existence was at least unambiguous.

## Kill / keep

**Keep.** It is not glyph with a copy letter and it is not `git diff -C`. On the first remaining-blob fixture it refused follow; on the first real R100 it still emitted one follow plus `grep char_len`; on the first real recorded copy (`C056`, blob still at `src/init.rs`) v1 named `exists *install*` and v2 was forced to `copy src/init.rs → src/init/install.rs`. Sitbone stayed `grep FocusRiverView`.
