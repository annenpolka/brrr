# neap

A Unix command the parents did not invert: **which HEAD path-conditions would die if this unapplied patch landed?**

`liken` overlays a unified diff in memory and emits the **added** lines that share a stack. `wane` takes two git trees and emits exclusive-A stacks that died. `neap` is the hybrid, not the union: overlay the patch in memory onto `--base` (default HEAD) and emit the stacks that exist on that pre-image and would **die**. Not the stacks the patch births. Not `git apply && wane`. The worktree is never written.

A move is silent. Leftover stays on deleted files (`--also-changed` names vanished stacks inside surviving files).

This is not a third `ambit`/`amid` clone. It does not walk cwd. It does not hunt leftover names.

## Install / run

Python 3.9+, stdlib only. `git` to load a revision other than `:wt`.

```bash
chmod +x ./neap ./demo.sh
./neap --help
./neap --selftest
./demo.sh
```

Exit: `0` named overlay-deaths, `1` overlay ok but nothing died (move, births-only), `2` usage / unplaced.

## Examples

### 1. Island delete — deaths, not the flood of new `if`s

```bash
./neap --base :wt --diff fixtures/island.diff
```

`if flow_score > 0.2` dies with `fixtures/river.py`. The added `unique_mod_*` stacks are births. `fixtures/mod0.py` is never created.

### 2. Sitbone island, before you reset HEAD

```bash
git -C sitbone diff 14b1d6e HEAD | ./neap -C sitbone --base 14b1d6e --limit 6
```

`git log -- FocusRiverView.swift` from HEAD is empty. Overlay onto `14b1d6e` names the stacks that would die. Camera / Presence births stay off the covering. Porcelain unchanged.

### 3. kizu split is a move

```bash
git -C kizu diff 3b3e0a9^ 3b3e0a9 | ./neap -C kizu --base 3b3e0a9^
```

`git.rs` → `parse.rs` is silent. A move is not a death. `parse.rs` is never written.

## Flags

| flag | meaning |
| --- | --- |
| `-C DIR` / `--repo` | repo root (git `-C`). Pre-image only; not a walk |
| `--base REV` | pre-image revision (default `HEAD`). `:wt` = working tree |
| `--diff FILE` | unified diff (`-` = stdin) |
| `--limit N` | max exclusive-A stacks to name (default 8) |
| `--also-changed` | vanished stacks inside surviving files |
| `--json` / `--tsv` / `--oneline` | machine output |
| `--selftest` | in-process checks |

stdin = unified diff. Without a diff, `neap` refuses (exit 2). See `CANDIDATE.md`.
