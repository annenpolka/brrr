# dreg

Occupancy is not a report. `dreg` occupies a patch stream against a tree, then **stdout is a unified diff of the picked cores**.

Default pick is **SUPERSEDED** — the dregs: hunks HEAD no longer occupies. `--pick PENDING` is the leftover apply.

| fate | meaning |
| --- | --- |
| **APPLIED** | after-image is in the tree; before-image is gone |
| **PENDING** | before-image is in the tree; after-image is absent |
| **MIXED** | both change-cores are tangled in the same region |
| **DUPLEX** | both images exist as independent blocks |
| **SUPERSEDED** | neither image; the world moved on |

sate names those fates. lodge occupies mixed streams with the same vocabulary. Both stop at the report. The daily next step is always *give me the hunks that left HEAD, as a patch*.

Sandwich: against C, SUPERSEDED of `C^..C` is empty. Against a later rewrite, the old cores come out as a patch.

Not `git apply --check` (boolean). Not `git-format-patch` of those commits. Not GitHub outdated (line-identity).

## Install / run

Python 3.10+, `git` for `--git` / `--log` / `--against`. Stdlib only.

```bash
chmod +x ./dreg
./dreg --help
./dreg --selftest
./demo.sh
```

Exit: `0` empty pick (no dregs), `1` emitted a patch, `2` `--report` occupancy split, `3` error.

## Examples

### 1. What died after a version ratchet

kizu `release: v0.6.0` vs HEAD (now 0.7.0): sate said `PENDING=1 SUPERSEDED=1`. dreg emits the dead core.

```bash
./dreg --git 88362116 -C ~/src/kizu --against HEAD
```

```
dreg  pick=SUPERSEDED  unanimous=SPLIT  against=HEAD  git:88362116  PENDING=1 SUPERSEDED=1
  PENDING     Cargo.lock  #1  core-minus  88362116
* SUPERSEDED  Cargo.toml  #1  neither  88362116
diff --git a/Cargo.toml b/Cargo.toml
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -2,3 +2,3 @@ SUPERSEDED 88362116
 name = "kizu"
-version = "0.5.1"
+version = "0.6.0"
 edition = "2024"
```

That patch applies onto the v0.5.1 tree (`88362116^`). It does not apply onto HEAD — occupancy already said SUPERSEDED. `git apply --check` against HEAD is the boolean lie you are not wrapping.

`--pick PENDING` on the same commit is the leftover Cargo.lock hunk. Occupancy found `version = "0.5.1"` still in the lockfile (other packages). `git apply --check` of that leftover against HEAD fails. Same lie, other side.

### 2. Sandwich, and leftover apply

```bash
./dreg --git HEAD --against HEAD          # SUPERSEDED empty, exit 0
./dreg --git HEAD --against HEAD^ --pick PENDING   # leftover apply
./dreg --git HEAD --against HEAD^ --pick PENDING | git apply
```

A commit occupies itself. Its dregs against itself are empty. Against its parent, `--pick PENDING` is the patch you would still apply.

### 3. `--log`: every hunk HEAD no longer occupies

```bash
./dreg --log 8 -C ~/src/kizu --stat
```

```
6 hunks  SUPERSEDED=6
SUPERSEDED  88362116  Cargo.toml  -1/+1  neither  release: v0.6.0
SUPERSEDED  54cdccfc  plans/performance-benchmark-suite.md  -0/+305  add-neither  …
SUPERSEDED  f9fba257  src/hook/tests.rs  -0/+583  add-neither  refactor: split hook responsibilities
```

Drop `--stat` to emit those cores as one patch stream (not `git format-patch` of the commits — occupancy-filtered hunks).

```bash
git show some-stash | ./dreg
./dreg main...HEAD --pick PENDING
./dreg --log HEAD~20..HEAD --pick SUPERSEDED
```

## Flags

| flag | what |
| --- | --- |
| `-C DIR` | tree root |
| `--against REF` | read files from git REF (default **HEAD** in a repo) |
| `--worktree` | read the dirty worktree instead of HEAD |
| `--git REV` | occupy `git show REV`, or `A..B` as `git diff` |
| `--log [N\|RANGE]` | each non-merge commit occupied against `--against` |
| `--pick FATE[,FATE]` | default SUPERSEDED |
| `--core` | minus/plus only (0-context; `git apply --unidiff-zero`) |
| `--full` | original hunks (default for `--pick PENDING`) |
| `--stat` / `--report` / `--json` / `--tsv` | listing / occupancy, not a patch |
| `--quiet` | patch only (no stderr legend) |

SUPERSEDED default emit is the change-core plus **one** original context line so vanilla `git apply` works on the preimage. `--core` drops that margin.

Prefix rule (sate v2): a pure addition whose before-image is a prefix of the after-image is APPLIED, not DUPLEX. Do not regress.

## Why this might not exist

`sate --log` tells you v0.6.0's Cargo.toml is SUPERSEDED. The next keystroke is still *show me that hunk*. Concatenating `sate --json | jq …` with `git format-patch` is two tools and the wrong object (the commit, not the unoccupied cores). GitHub "outdated" is line-identity. `git apply --check` is a boolean.

dreg's object is occupancy. Its stdout is the patch of the cores that fate names.
