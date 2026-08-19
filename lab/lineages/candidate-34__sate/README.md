# sate

A patch is not a boolean. `git apply --check` says *does not apply*. `sate` says **how the tree occupies each hunk**.

| fate | meaning |
| --- | --- |
| **APPLIED** | after-image is in the tree; before-image is gone |
| **PENDING** | before-image is in the tree; after-image is absent (would apply) |
| **MIXED** | both change-cores are tangled in the same region |
| **DUPLEX** | both images exist as blocks (copied, not replaced) |
| **SUPERSEDED** | neither image; the world moved on |

The object is a **hunk occupancy vector**. A review `suggestion` fence is the same object: a one-hunk patch.

## Install / run

Python 3.10+, `git` for `--git` / `--log` / `--against`. Stdlib only.

```bash
chmod +x ./sate
./sate --help
./sate --selftest
./demo.sh
```

## Examples

### 1. Why `git apply` failed

```bash
git show some-stash | ./sate
./sate fix.patch
./sate --git HEAD           # last commit vs the worktree
./sate --git main...HEAD    # the PR diff vs the worktree
```

```
sate  git:HEAD  unanimous=PENDING  PENDING=3
PENDING     src/app.rs  #1  exact-before  @@ -40,6 +40,7 @@
PENDING     src/app.rs  #2  exact-before  @@ -88,3 +89,10 @@
```

Exit `0` if every hunk is APPLIED, `1` if every hunk is PENDING, `2` if the fates split (or MIXED / DUPLEX / SUPERSEDED). `--json` / `--tsv` compose.

### 2. Which recent patches still occupy HEAD

```bash
./sate --log 8 -C ~/src/kizu
```

```
sate log  n=8  against=HEAD
APPLIED       2h  9349dc50  release: v0.7.0
APPLIED      74h  04adde1f  feat: add complete jsx tsx support
SPLIT         2h  88362116  release: v0.6.0
            PENDING=1 SUPERSEDED=1
APPLIED       8h  c0d963ff  perf: speed up stream file rebuilds
SPLIT        44h  54cdccfc  perf: add operation benchmarks and cache hot paths
            APPLIED=43 SUPERSEDED=1
```

A commit whose after-image is still in HEAD is APPLIED. A later rewrite SUPERSEDES it. That is not `git log -S` (when a string changed) and not `git bisect` (one cut).

The occupancy sandwich: `sate --git C --against C` is APPLIED; `--against C^` is PENDING.

### 3. Review suggestions as patches

```bash
./sate --suggest fixtures/suggest.jsonl -C .
./sate --suggest gh-review-comments.json   # GitHub API array with ```suggestion
```

```
APPLIED     mod.py  #1  exact-after     @@ suggestion r1 @@
PENDING     mod.py  #2  exact-before    @@ suggestion r2 @@
SUPERSEDED  gone.py #1  missing-file    @@ suggestion r3 @@
```

APPLIED = the author took the suggestion. PENDING = the quoted code is still there. SUPERSEDED = they did something else (or deleted the file). GitHub's "outdated" is line-identity; this is image occupancy.

## Flags

| flag | what |
| --- | --- |
| `-C DIR` | tree root |
| `--against REF` | read files from a git ref, not the worktree |
| `--git REV` | `git show REV`, or `A..B` as `git diff` |
| `--log [N]` | last N non-merge commits vs `--against` (HEAD) |
| `--first-parent` | with `--log`, GitHub merge-mainline walk |
| `--suggest FILE` | JSON / JSONL review comments |
| `--ignore-space` | collapse horizontal whitespace |
| `--fuzz` | accept a window with ≥0.85 line overlap |
| `--json` / `--tsv` / `--quiet` | machine output |
| `--report-only` | always exit 0 |

## Why this might not exist

`git apply --reverse --check` is the folk test for "already applied", and it is a boolean per patch. It fails when context drifted even though the *change* is in the tree, and it cannot say MIXED or DUPLEX. `sate` classifies the **change-core** (the `+`/`-` lines), then the full before/after blocks, then (opt-in) a fuzzy window.

Compose: `git stash show -p \| sate --tsv \| awk -F'\\t' '$1=="PENDING"'`
