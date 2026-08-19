# dirge

A Unix command the parent did not invert: **which HEAD path-conditions would die if this unapplied patch landed — as one obituary per sibling-arm fork, not N rows?**

`neap` overlays a unified diff in memory and emits the exclusive-A stacks that would die. Sibling arms (`if flowScore>0.2` / `elif` / given-else / sequential `if`) print N obituaries. `dirge` is the mutation: same overlay-deaths, **clustered**. Not `git apply && wane`. Not overlay-births. The worktree is never written.

A move is silent. Leftover stays on deleted files (`--also-changed` names vanished stacks inside surviving files). Independent if-chains stay separate obituaries.

This is not a third `ambit`/`amid` clone. It does not walk cwd. It does not hunt leftover names.

## Install / run

Python 3.9+, stdlib only. `git` to load a revision other than `:wt`.

```bash
chmod +x ./dirge ./demo.sh
./dirge --help
./dirge --selftest
./demo.sh
```

Exit: `0` named overlay-deaths, `1` overlay ok but nothing died (move, births-only), `2` usage / unplaced.

## Examples

### 1. Island delete — one obituary for if/elif, not two rows

```bash
./dirge --base :wt --diff fixtures/island.diff
```

`if flow_score > 0.2` and `elif flow_score < -0.2` die as **one** covering member (`dirge=1`, `arms=2`). The added `unique_mod_*` stacks are births. `fixtures/mod0.py` is never created.

### 2. Sitbone island, before you reset HEAD

```bash
git -C sitbone diff 14b1d6e HEAD | ./dirge -C sitbone --base 14b1d6e --limit 6
```

`git log -- FocusRiverView.swift` from HEAD is empty. Overlay onto `14b1d6e` names the flowScore fork that would die — `if` / `elif` / sequential `if` / given-else as one obituary. Camera / Presence births stay off the covering. Porcelain unchanged.

### 3. kizu split is a move

```bash
git -C kizu diff 3b3e0a9^ 3b3e0a9 | ./dirge -C kizu --base 3b3e0a9^
```

`git.rs` → `parse.rs` is silent. A move is not a death. `parse.rs` is never written.

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` / `--repo` | repo root (git `-C`). Pre-image only; not a walk |
| `--base REV` | pre-image revision (default `HEAD`). `:wt` = working tree |
| `--diff FILE` | unified diff (`-` = stdin) |
| `--limit N` | max obituaries (clustered forks) to name (default 8) |
| `--also-changed` | vanished stacks inside surviving files |
| `--json` / `--tsv` / `--oneline` | machine output |
| `--selftest` | in-process checks |

stdin = unified diff. Without a diff, `dirge` refuses (exit 2). See `CANDIDATE.md`.
