# mutation-63 — mint

## Primitive

A **visa-birth** is the occupancy onset of clearance: a production argument world that was OPEN/SPEC (or absent) at the parent and BOUND at the child. Default stdout is that birth (commit, world, machine). `--check` fails if this range minted a visa the parent did not have.

## Why this might not exist

`stain` asks whether HEAD currently leaks a machine. CI empty stdout is green even if *this PR* is the commit that bound Alice — and red forever after, including README-only follow-ups. `held` occupies a path/string predicate, not clearance polarity. `erst`/`brood` occupy leftover *names*. Concatenation is `stain | git log -S /Users/alice`: a string pickaxe, not OPEN→BOUND of a world.

Discarded as a flag on stain: `--since` on a snapshot linter is still "is it stained now?" The object changed. The verb is *when the visa was minted*.

Discarded as stain|erst: leftover natal keys (`t1`↔`driftDelay`) are not a machine. Discarded as `--emit`: tests are admit's default, stain's opt-in, and mint's non-object.

## How to run

```bash
chmod +x ./mint
./mint --self-test
./demo.sh
./mint -C /path/to/repo
./mint -C /path/to/repo --walk --max 20
./mint --check origin/main..HEAD
./mint --spread HEAD
```

Python 3.10+, stdlib, `git`. Exit 0 if the range minted no visa. Exit 1 if a production world became BOUND to a machine the parent did not have. Exit 2 on usage / not a repo root. No test file.

## Empirical transcript

### v0.1 — occupancy of clearance; sitbone empty; kizu walk crashes

`./mint --self-test` ok. `./demo.sh` → **passed=42 failed=0**.

Synthetic history (OPEN `/tmp/cache` → Alice HOME, Brave stays OPEN, textbook `/home/user`, then SPREAD into Swift, then GitHub titles):

```
./mint -C $FIX <alice-sha>
# mint  births=1  worlds=1  commit=…  parent=…
#   pin Alice home
#   BIRTH  OPEN→BOUND  HOME=/Users/alice USER=alice platform=Darwin
#     load_profile  load_profile("/Users/alice")  src/profile.py
#     was  SPEC  load_profile("/tmp/cache")  src/profile.py
# exit 1
```

HEAD (titles only) empty exit 0. SPREAD of the same visa into `loadHome` is hidden by default (`--check` 0); `--spread` names it. Brave, `/home/user`, `annenpolka/sitbone` titles are not births. No pytest, no XCTest, no leftover `t1`.

sitbone (read-only, 2026-08-20): HEAD empty exit 0. `--walk` 31 first-parent commits, 22 scanned, **births=0**. Production never acquired a visa.

kizu HEAD (no source hunk) empty exit 0. `--walk` **crashed**: `tarfile.AbsoluteLinkError: 'AGENTS.md' is a link to an absolute path`. Python 3.14's tar data filter refuses git-archive of that blob. HEAD vs parent happened to skip materialize (no source diff) so demo stayed green.

v0.1 also printed `OPEN→BOUND` with `was SPEC` for `/tmp/cache` — payload tmp is SPEC, not OPEN.

### v0.2 — source-only extract; SPEC→BOUND; -C is a repo root

After: `git archive` extracts only source files and skips symlinks. Occupancy kind follows parent polarity (`SPEC→BOUND` vs `OPEN→BOUND`). `-C` must be a worktree root so a nested `fixtures/ugly` is not silently the parent lab.

kizu `--walk` 24 first-parent, 14 scanned, **births=0**, 7.8s, no traceback. `/home/user` and `John Doe` stay SPEC. sitbone still 0.

`nick("desktop")` → `nick("/Users/bob")` is the real **OPEN→BOUND**. `/tmp/cache` → `/Users/alice` is **SPEC→BOUND**. Absolute-symlink fixture walks without crash.

stain `fixtures/ugly` as a folder: exit 2 (`not a git repository`). The same tree `git init`'d as a root commit: `ABSENT→BOUND` Alice, worlds=3 (load_profile ×2 + loadHome), Brave absent. stain's snapshot linter vs mint's birth.

`./demo.sh` → **passed=53 failed=0**.

```
./mint -C $FIX <alice-sha>
# BIRTH  SPEC→BOUND  HOME=/Users/alice USER=alice platform=Darwin
#   load_profile  load_profile("/Users/alice")  src/profile.py
#   was  SPEC  load_profile("/tmp/cache")  src/profile.py
```

## Dogfood targets

- Synthetic git history in `./demo.sh` / `--self-test` (Alice, Bob OPEN→BOUND, Brave, textbook, GitHub title, absolute symlink)
- `fixtures/ugly` — stain's tree; needs `git init` to become a birth
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` full first-parent (31, births=0)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` full first-parent (24, births=0; v0.1 crash)

## Surprises

- `/tmp/cache` visad as SPEC (payload tmp), not OPEN. v0.1 named the kind OPEN anyway. v0.2 split SPEC→BOUND / OPEN→BOUND; `was` was already honest.
- SPREAD is not a mint. stain would still fail after the second Alice call; mint `--check` 0 because the parent already had that machine. That is the flip.
- sitbone 31 commits, zero births. kizu 24, zero births. Real trees in this dogfood pair never minted a visa on first-parent. The empty report is the product — and it is why synthetic history is required.
- kizu HEAD can be green while `--walk` dies: no-source commits skip materialize. Occupancy tools that only probe HEAD vs parent hide archive bugs.
- `git -C fixtures/ugly` is *inside* this worktree. v0.1 would have archived the lab. `-C` must be the toplevel.

## Failures

- sitbone/kizu first-parent have no visa-birth to show a real SHA. Ugly imported as a root commit is ABSENT→BOUND, not a lived OPEN→BOUND on those repos.
- `runAppleScript`-class instance methods are still not constructed (hatch/stain leftover; mint does not emit tests).
- File rename of a BOUND world looks like ABSENT→BOUND (path is in the slot key).
- JS/TS options-bag worlds stay coarse (hatch's).

## Suggested mutations

- `--follow` slot identity across renames.
- Join with held: eras of BOUND for one named world, not only onset.
- `--allow HOME=/Users/alice` documented exceptions so a recording fixture can exist on purpose.
- Full-history (`--full`) when first-parent never held the world (held's side-branch hint).

## Kill / keep

**Keep.** The object is not stain-with-`--since`. sitbone/kizu never-minted is a different green from stain's currently-clean. `--check` on a range is the PR gate stain cannot speak: this commit minted Alice; the next README commit does not. Kill only if `git log -S /Users/` plus stain recovers OPEN→BOUND of a world — it does not, because Brave and Alice share a file and `/tmp`→Alice is a value change, not a pickaxe hit on a constant string.
