# First Selection — 2026-09-02 01:15–01:26 JST

Independent judges. Scores are **not** averaged. Multiple survivors. Not one winner.
Empirical scores required actual `./demo.sh` and unittest runs (all seven demos exited 0).

Sources:

- `judges/FIRST_UNIX.md`
- `judges/FIRST_TOOLSMITH.md`
- `judges/FIRST_HERETIC.md`
- `judges/FIRST_SKEPTIC.md`
- `judges/FIRST_REALITY.md`

Do not rank by polish or LOC.

## KEEP / KILL by judge (disagreement preserved)

| Candidate | Unix | Toolsmith | Heretic | Skeptic | Reality-Stripped |
| --- | --- | --- | --- | --- | --- |
| whence | KEEP | KEEP | KEEP | KEEP | KEEP |
| envfrom | KEEP | KEEP | KEEP | KEEP | KEEP |
| stated | KILL | KEEP | KEEP | KEEP | KEEP |
| owes | KILL | KEEP | KEEP | KEEP | KEEP |
| capdiff | KILL | KEEP | KILL | KEEP | KEEP |
| same | KEEP | KILL | KEEP | KILL | KEEP |
| hits | KEEP | KILL | KILL | KILL | KILL |

## Coordinator KEEP list (multiple)

These stay in the breeding pool. A single KILL from one judge is disagreement, not a veto, except **hits** (four of five kill; Unix keep is the exit-code hole only).

**KEEP**

1. **whence** — unanimous. Parent-tagged resolve + provenance.
2. **envfrom** — unanimous. Per-variable source including empty file override.
3. **stated** — 4/5. Declaration vs contradicting assignment. Unix calls it grep-plus-status.
4. **owes** — 4/5. Leftover mentions and missing companion files. Unix dislikes the snapshot protocol.
5. **capdiff** — 3/5. Named env+file captures. Heretic/Unix: thin diff/env.
6. **same** — 3/5. Exclusive identity kind. Skeptic/Toolsmith: stat/cmp/jq lecture.

**Park (not PATH, not breeding priority)**

7. **hits** — 1/5. Empty-is-success search. Reality-Stripped RSS 1. Keep as fossil-adjacent composition, not a Gen-2 vehicle.

## Disagreement worth keeping

- Unix KEEP hits; everyone else KILL.
- Unix KILL stated/owes/capdiff; Toolsmith KEEP all three.
- Heretic KILL capdiff/hits; KEEP same; Skeptic inverse on same.

This split is evidence. Do not synthesize a single score.

## Unlock

Previous brrr is now prior art. Write `PRIOR_RUN_COMPARISON.md`. Do not rewrite `.hdd/` transcripts.
