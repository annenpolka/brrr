# Emerging Generation-1 primitives

Snapshot: 2026-08-20 00:09 JST. Independent inventors; names harvested from worktrees only.

| ID | tool | primitive | status |
| --- | --- | --- | --- |
| candidate-01 | akin | Files that once shared a git blob — copy kinship, the merge-base git never recorded | demo.sh + 566-line CLI |
| candidate-02 | aka | Wire tokens living under several inflections (`has_more` / `hasMore`) and one-sided edits | demo.sh + 1253-line CLI |
| candidate-03 | wisp | Code that lived between two refs and vanished, plus remnants still in the tree | 985-line CLI |
| candidate-04 | reverb | Treat the preimage of a diff as a search query; find lingering copies | 741-line CLI |
| candidate-05 | haunt | Inverse dead-code: names that died in history but still speak in the living tree | haunt present |
| candidate-06 | deja | Diff vs history: RELAPSE / UNDOFIX / RESURRECT | demo.sh + 921-line CLI |
| candidate-07 | zanei | Leftover claims a diff just made false (comments/docs/tests still asserting old facts) | demo.sh + fixtures |
| candidate-08 | unfmt | Inverse printf: runtime string → source templates that could have produced it | demo.sh + 1096-line CLI |
| candidate-09 | held | Intervals of history where a predicate holds (eras, not a single bisect cut) | demo.sh + 944-line CLI |
| candidate-10 | also | Birth cohort of a line: siblings born in the same introducing commit, then drifted | CANDIDATE.md present |
| candidate-11 | rift | Identifier-level conflicts a clean git merge would accept | CANDIDATE.md present |
| candidate-12 | wraith | Names whose definitions died but mentions remain (docs, configs, strings) | 1470-line CLI |
| candidate-13 | unfmt | Same inverse-printf primitive as candidate-08 (independent convergent evolution) | 765-line CLI + fixtures |
| candidate-14 | unseen | The definition-diff a use-site has never seen | 962-line CLI |
| candidate-15 | winnow | Partition uncommitted changes by whether they affect a command (bisect the dirty tree) | 598-line CLI |
| candidate-16 | slip | Relocate stale `file:line` by fingerprint, not VCS identity | demo.sh + 865-line CLI |

## Clusters (not yet judged)

- **Ghosts of deleted code:** wisp, reverb, deja, wraith, zanei, haunt?
- **Identity across names/locations:** aka, akin, slip
- **Inverse lookup:** unfmt × 2 (convergent)
- **Time as intervals:** held
- **Use-site vs definition:** unseen
- **Minimal dirty subset:** winnow

## Independent parent demo re-runs (2026-08-20 00:23 JST)

| tool | result |
| --- | --- |
| aka (02) | PASS (dogfood tenaoshi/kizu/sitbone/skills) |
| unfmt (08) | PASS 28/28 including real repos |
| held (09) | PASS 33/33 including sitbone/skills/kizu/voidtrace |
| slip (16) | PASS including kizu `app.rs` split 529→layout.rs:17 |

## Notes for later judges

`unfmt` appearing twice from isolated workers is convergent evolution, not plagiarism. Keep both long enough to compare algorithms.

`also` and `rift` look like the strongest *non-ghost* primitives so far.
