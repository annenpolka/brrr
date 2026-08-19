# mutation-42 — glyph

## Primitive

Two trees in; emit the shortest covering **set** of predicates that distinguish them as ready-to-run `held`/`perch` lines, with **`--follow` so a rename is one identity**.

Path existence is not identity. `git mv a.rs b.rs` is one glyph, not `exists a.rs` plus `exists b.rs`. glyph does not walk history. `glyph A B | sh` may run held.

## Why this might not exist

`tell` lists unary questions. `sheaf` prints a covering set plus walks — and still treats a rename as two exists (old dies, new is born). `held exists PATH` then reports a death. `git log --follow` is a path walk you already have to name. `git diff --name-status` prints `R100`. None of those emit the *question* you would paste into occupancy: `held --follow exists old`.

The recurring annoyance: you are staring at two trees, one of them a `git mv`, and occupancy tools ask you for a path that just died.

Discarded as too conventional: wrapping `git diff --name-status`, leftover-name n-grams, merging tell and perch into one binary that walks history by default.

## How to run

```bash
./glyph --help
./demo.sh
./glyph -C /path/to/repo HEAD~1 HEAD
./glyph -C /path/to/repo --held 14b1d6e^ 14b1d6e
./glyph -C /path/to/repo --perch --walks 14b1d6e HEAD
./glyph -C /path/to/repo --no-follow HEAD~1 HEAD
./glyph HEAD :worktree
```

## Empirical transcript

### Before the improvement

v1 already paired same-blob renames and reserved exclusive-side slots (sheaf's island fix). Two real queries were wrong.

**Rename + edit leftover-named the dest path.** `git mv a.rs b.rs` plus a new token `delta_token`:

```
sheaf
  follow a.rs → b.rs
  grep -F b.rs          # leftover: the new filename, not the edit
```

**tenaoshi policy commit covered a leftover CJK verb phrase**, not the contract id / slogan tell already learned to keep:

```
$ ./glyph -C tenaoshi 70b450d^ 70b450d
# B   15  grep -F '向けに調整'     4 files
# 第一級 was in the catalog, ranked below a mixed kana crumb that occupied more files.
```

sitbone birth already named FocusRiverView (tokenization inherited from tell/sheaf). The island vs HEAD already reserved the only-A slot. The rename fixture was already one follow. The failures were leftover-name, the same class tell killed with `がるパ`.

### After the improvement

Grep is content occupancy (token must live in a blob). Mixed short CJK is not name-like; all-kanji compounds (`第一級`) and hyphenated contract ids (`MAN-023`) are.

```
$ ./glyph -C tenaoshi 70b450d^ 70b450d
# B   15  grep -F MAN-023          4 files
held -C tenaoshi --rev 70b450d --limit 12 grep -F MAN-023
```

```
$ # mv a.rs b.rs + delta_token
sheaf
  R   follow a.rs → b.rs
  B   grep delta_token
```

`--no-follow` on the spaced rename recovers two exists — the sheaf answer, now an explicit downcast:

```
$ ./glyph --no-follow T2 T3
  exists '*old name*'
  exists '*new name*'
```

Sitbone gold, unchanged by the leftover fix:

```
$ ./glyph -C sitbone 14b1d6e^ 14b1d6e
# B   19  grep FocusRiverView      1 file
held -C sitbone --rev 14b1d6e --limit 12 grep FocusRiverView
# not grep 'がるパ'

$ ./glyph -C sitbone --limit 6 14b1d6e HEAD
# A   19  grep FocusRiverView
held -C sitbone --full --rev 094769d grep FocusRiverView
# git log -- Sources/SitboneUI/FocusRiverView.swift  → empty
```

kizu's real R100 plus an unrelated edit:

```
$ ./glyph -C kizu 4e37f16^ 4e37f16
# R   follow deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
# B   grep char_len                                      1 file   (src/ui.rs)
held -C kizu --follow --rev 4e37f16 --limit 12 exists deep-research-ai-agent-hooks.md
held -C kizu --rev 4e37f16 --limit 12 grep char_len
```

Three files `src/*.rs` → `lib/*.rs` compress to one directory identity:

```
# R   follow src/* → lib/*
held -C repo --follow --rev B --limit 12 exists src/*
```

`./demo.sh` — assertions over the fixture, sitbone, kizu, tenaoshi, skills. Exit 0.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView birth/death/island (`git log -- path` empty); cover is `grep FocusRiverView` not `がるパ`
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — CLAUDE.md birth; jsx/tsx; real `R100` markdown move `4e37f16`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — Japanese policy `第一級` / contract `MAN-023` vs leftover `向けに調整`
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — HEAD~1..HEAD sheaf + held walks
- synthetic fixture: oscillating path, rename with spaces, `計画.md`, nested git, `:worktree`, mv+edit, directory rewrite, empty repo

## Surprises

- Shortest *set* of *identities* is not shortest *path list*. A 3-file `src/ → lib/` rewrite is one glyph (`follow src/* → lib/*`), which `git diff --name-status` would print three times.
- `held --follow exists old` is TRUE on both trees of a pure rename. The distinguisher is the mapping; occupancy of the identity never died. That is the whole point, and it is why glyph must not walk history itself — a unary TRUE/FALSE of the identity does not split the snapshots.
- kizu `4e37f16` is the honest mixed case: one identity move *and* a content glyph on `src/ui.rs`. Swallowing the edit into the rename would have been the other failure mode.
- Default walker is `held` only, so `glyph A B | sh` is occupancy, not perch. sheaf defaulted to both and indented the lines, which cannot be piped.
- `--no-follow` on a pure rename now emits two exists (path identity). v1 emitted two greps of the filenames because grep accepted path-only tokens. Making grep blob-only restored exists as the path verb.

## Failures

- v1 leftover-named `grep b.rs` on mv+edit and `grep '向けに調整'` on tenaoshi. Same family as tell's `がるパ`.
- Generated `held --follow exists` is the intended occupancy line; current `held` (candidate-09) does not parse `--follow`. Demo runs live held only on grep walks. The distinguisher is still pasteable; the walker has not grown the flag.
- Unique-basename pairing will call a delete+unrelated-add of the same filename a rename. `--no-follow` recovers. Similarity pairing of leftover exclusive blobs can glue two coincidentally similar new files.
- Far-apart trees still leave an unexplained tail (island +29 paths). `--limit` is the point.
- Binary-only modifies have no unary grep; they remain unexplained except by "blob differs", which is not a held predicate.
- Directory compression needs a shared basename rewrite (`src/one.rs` → `lib/one.rs`). `a.rs` → `b.rs` of several unrelated files will not glob.

## Suggested mutations

- Teach `held` / `perch` `--follow exists PATH` so the generated line actually occupies identity (blob follow, not path death).
- `glyph A B | held --stdin` so the pipe is predicates-in, eras-out, without `sh`.
- Copy vs rename: same blob still on A and also born on B should be `copy`, not `follow`.
- `--code` grain so kizu `line_number` docs do not steal cover slots from the type.
- Cache tree token sets in `.git/glyph-cache/`.

## Flipped assumption: bought and lost

Parents: tell (mutation-03) assumed **two snapshots in, unary predicates out**. sheaf (mutation-25) assumed **the value is the covering set plus walks**. Both treated **path occupancy as identity**.

**Bought**

- A rename is one member of the sheaf and one `--follow` occupancy command.
- Directory rewrites compress. Mixed commits (kizu R100 + ui.rs) keep a content glyph beside the identity.
- `--no-follow` is an explicit downcast to sheaf, not a fork.
- Default stdout is pipeable (`#` sheaf + unindented held lines). `--held` / `--perch` pick the walker. glyph does not walk history.

**Lost**

- Unary TRUE/FALSE no longer describes a follow member: both trees hold the occupant, under different names. Covering is of identities, not of exclusive paths.
- `held` as it exists today will reject `--follow`. The line is the mutation; the walker has not caught up.
- Unique-basename identity can over-pair. Path existence was at least unambiguous.
- Two snapshots still, not a three-state occupancy interval. TOKEN_A moving keep.txt → other.txt is still two pairwise glyphs.

## Kill / keep

**Keep.** It is not `git diff --name-status` and it is not sheaf with `--follow` echoed on. On the first real R100 it emitted one follow plus the unrelated `grep char_len`, and on sitbone the cover stayed `grep FocusRiverView`. The v1→v2 change was forced by leftover-name on tenaoshi and mv+edit, not polish.
