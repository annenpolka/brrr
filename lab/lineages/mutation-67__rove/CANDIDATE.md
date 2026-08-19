# mutation-67 — rove

## Primitive

`rove grep --follow -- PATH` occupies a **token along a file identity**. A path-limited grep survives `git mv`. Query the old name or the new name; occupancy of the token stays TRUE and holders still split.

Default exact path-limited grep follows. `--no-follow` is ancestor path-limited grep (dies with the old name). Tree-wide `grep PATTERN` is unchanged. `--boolean` is ancestor `held`.

## Why this might not exist

`git log -G PATTERN -- PATH` and `git grep PATTERN $(git rev-list HEAD) -- PATH` are both **current-path** queries. After `git mv old new`, grepping the old name is a death even though the token never left the file. `git log --follow` / `git log -G --follow` walk *changes*, backward, from a name that exists at HEAD — they do not occupy every commit, they do not follow forward from a dead name, and they do not split holders. berth `--follow` occupies the file, but `--follow` was exists-only: `grep -- PATH` still did not follow the pathspec.

Discarded as too conventional: wrapping `git log -G --follow`, leftover-name search (find mentions of the old path), tenure's split (`git.rs` → `parse.rs`).

## How to run

```bash
./rove --help
./demo.sh 0
./demo.sh
./rove -C /path/to/repo grep ghost -- 'old name.txt'
./rove -C /path/to/repo --no-follow grep ghost -- 'old name.txt'
./rove -C /path/to/repo --full grep -F '10 の AI' -- docs/deep-research-ai-agent-hooks.md
./rove -C /path/to/repo --full grep -F '10 の AI' -- deep-research-ai-agent-hooks.md
./rove -C /path/to/repo --full --no-follow grep -F '10 の AI' -- deep-research-ai-agent-hooks.md
./rove -C /path/to/repo --full grep parse_diff_git_header -- src/git.rs
./rove -C /path/to/repo grep preact-zero-mock
```

Python 3.9+, stdlib only, `git`. Exit 0 iff the predicate holds at the last sample.

## Empirical transcript

### Before the improvement (same-walk R records)

Synthetic fixture: `--no-follow grep TOKEN_G -- 'old name.txt'` is TF (dies at the rename) and hints `--follow`. `--follow` on either name is one identity (`old name.txt → new name.txt`), TRUE through the rename, FALSE when the token is dropped from dest, kinds `birth/move/death`. A copy (`alpha.txt` → `beta.txt`) is not a follow: `grep TOKEN_B -- alpha.txt` stays on alpha. Oscillate delete+revive is path occupancy FTFT and identity occupancy FTF (reincarnation is a different file). 3-hop `old.txt → new name.txt → 最終.md` with `計画TOKEN` is the same roost from any name.

kizu `--full --follow grep -F '10 の AI'` on either name: TRUE 187, holders old then `docs/`, kinds `birth/move`. `--full --no-follow` on the old name: TRUE 13 then FALSE 174, hint `died at rename 4e37f16 → docs/…`. Tenure split is refused: `grep parse_diff_git_header -- src/git.rs` dies at `3b3e0a9` (`aka=src/git.rs`), does not jump into `parse.rs`.

Then first-parent **lies**:

```
$ ./rove grep -F '10 の AI' -- docs/deep-research-ai-agent-hooks.md
identity: docs/deep-research-ai-agent-hooks.md
FALSE  3 / TRUE 21
       origin: 321a830  as deep-research-ai-agent-hooks.md
       holders: docs/deep-research-ai-agent-hooks.md

$ ./rove grep -F '10 の AI' -- deep-research-ai-agent-hooks.md
FALSE  24 commits
warning: pathspec 'deep-research-ai-agent-hooks.md' matched no file identity
now=FALSE  true=0/24
```

Same token, same identity, two names. Dest works because dest exists after the merge. The old name never appears on first-parent (the merge added dest as **A**, not R), so same-walk follow found no identity. `--full` from the old name already knew the roost. First-parent should too.

skills `grep preact-zero-mock` still README-only ghost. sitbone `grep FocusRiverView` still `boolean=3` kinds `birth/spread/shrink`. Those must not change.

### After the improvement

Forced by that first-parent old-name transcript, not polish. Identity is resolved from **all reachable R records**, then occupancy is evaluated on the requested walk. A first-parent merge that added dest as A still knows old→dest.

```
$ ./rove grep -F '10 の AI' -- deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
FALSE   3 commits
TRUE   21 commits
       origin: 321a830  feat(ui,watcher): …  (55 commits before this merge)
                as deep-research-ai-agent-hooks.md
       holders: docs/deep-research-ai-agent-hooks.md
now=TRUE  true=21/24
```

Same command on dest is now the same roost (same identity, same origin, same holders). `--full` is still 187 from either name. `--no-follow` old name is still a path death. Copy is still copy. Oscillate still does not reincarnate. `src/git.rs` still does not follow the split into `parse.rs`.

Synthetic non-ff merge (topic `old.txt`→`dest.txt`, main extra commit, merge): first-parent `--follow grep TOKEN_M -- old.txt` is FT, origin is the topic birth, holders `dest.txt`. `--no-follow` on old.txt is never-held (path never existed on mainline).

## Dogfood targets

- synthetic fixture: spaces rename; 3-hop CJK token; copy vs rename; oscillate reincarnation vs identity; TOKEN_B tree-wide; `--now`; nested git; empty repo; non-ff merge-birth
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — `R100 deep-research-ai-agent-hooks.md → docs/…` (`true=187` follow vs `true=13` path death); first-parent old name = dest after identity stitch; `src/git.rs` split is not a follow
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — FocusRiverView island (ancestor gold; no rename)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — preact-zero-mock README-only ghost; circuit-breaker path death

## Surprises

- `git log --follow -- dest` reports 2 commits. Occupancy is 187. Follow-of-changes is not follow-of-occupancy.
- First-parent never records the R (merge is A). v1 follow from the old name was never-held and warned "no file identity" — a lie `--full` already contradicted.
- `--no-follow` on the old name after a real rename now *says so*: `pathspec died at rename 4e37f16 → docs/…. rerun with --follow`.
- A token can die after the rename (fixture TOKEN_G dropped from dest). exists --follow stays TRUE; grep --follow becomes FALSE. That is the whole point of this mutation.
- kizu `git.rs` still exists after the split. Follow stays on `git.rs` and dies. Tenure's object is the stack that moved into `parse.rs`.

## Failures

- v1 identity used the walk's own name-status. First-parent old-name grep --follow never-held. v2: resolve identity from all reachable R, occupy the requested walk.
- Full-history eras are still `git log --reverse` order, not a merge diamond (topic TRUE / main extra FALSE / merge TRUE can flicker under `--full`).
- `--follow` with a glob is refused. A glob is not an identity.
- `--now` of a dead identity that the worktree recreated under the query path is a new identity; path occupancy still wants `--no-follow`.
- Not `git log -G --follow`. Not leftover-name search.

## Suggested mutations

- `--follow` of a split (kizu `git.rs` → `parse.rs`) is tenure's object, not this one. Honest refuse.
- Cache name-status per spec so first-parent follow does not pay a second full walk.
- `exec --follow -- PATH` so a path-conditioned command survives `git mv`.
- Occupancy on the merge lattice, not `git log --reverse`.

## Flipped assumption: bought and lost

Ancestor berth assumed **`--follow` is exists-only**. `grep -- PATH` was current-path occupancy, so `git mv` killed a path-limited grep.

**Bought**

- Path-limited grep of a token is occupancy along the file identity, from either name, including a dead name `git log -G --follow` will not continue, including first-parent when the merge hid the R.
- `--no-follow` keeps the path death (and now names the dest).
- Copy stays copy. Split stays split. Oscillate reincarnation stays a new file.

**Lost**

- Default exact path-limited grep is no longer path occupancy. Callers who wanted "did this token leave *this path*" must pass `--no-follow`.
- First-parent `--follow` pays a full-history rename walk.

## Kill / keep

**Keep.** The first real-repo path-limited grep (`kizu` `10 の AI` through R100 into `docs/`) is one 187-commit token occupancy from either name, which neither `git log -G` nor berth `grep -- PATH` will say. v1 lied on first-parent from the old name; v2 was forced by that run. Ghost remains correct for skills `grep preact-zero-mock`. Tenure's split remains refused.
