# Overnight lab — live board (2026-08-20 03:35 JST)

Hard end: **09:00 JST**. Phase: Gen-2 breeding + early adversarial. First selection already filed.

Parent workspace is coordinator-only. Tools live in isolated worktrees under `~/.grok/worktrees/annenpolka-brrr/`. Reports copied to `lab/lineages/`.

## What happened

16 independent inventors shipped in ~35 minutes. The first cluster was leftover-names (haunt/wraith/wisp). Independent judges **killed haunt**, kept **wraith** as the only leftover-*name* lineage, and treated **zanei** as a different object (leftover *claims*).

Then the search escaped that cluster. Strong primitives were independently reimplemented (`dwelt` matches `held`; `nagori` matches `zanei` gold; `stencil` rebuilt inverse-printf without reading source and beat the original on nested Swift). A bakeoff elected **invert** (then **stump**) as the inverse-printf vehicle. A destroyer found real conceptual holes; v0.3 pin and stump closed the first list; a second destroyer found overcorrection.

## Tomorrow-test shortlist (install these first)

| Tool | Primitive | Worktree / lineage |
| --- | --- | --- |
| **invert / stump** | Inverse printf: paste a log line, bind named holes | `lab/lineages/mutation-15__invert`, `mutation-23__stump` |
| **pin** (v0.3) | Mint a durable `file:line` token; resolve later with no locator | `lab/lineages/mutation-22__pin` |
| **when** | Path-condition stack at a locus (`given` fallthrough) | `lab/lineages/candidate-20__when` |
| **held / perch** | History eras a predicate holds; perch splits when holders change | `candidate-09__held`, `mutation-17__perch` |
| **zanei** | Leftover claims a diff just made false | `candidate-07__zanei_` |
| **erst** | Birth cohort of a *change*; natal keys inflect | `mutation-19__erst` |
| **cinch / hasp** | 1-minimal production hunks new tests lock | `hybrid-03__cinch`, `hybrid-06__hasp` |
| **sate / lodge** | Patch/review occupancy, not `git apply --check` | `candidate-34__sate`, `hybrid-08__lodge` |

## Do not install as products

haunt (killed). folk (0 real orphans). nigh (use `kerf`/`cusp`). unfmt-08/13 walkers (invert is the vehicle). pinch/hitch (use `knot`). kiln/clutch (use `sinter`).

## Pointers

- Constitution: `Overnight Developer Tool Evolution Lab — Master Prompt.md`
- Selection: `lab/FIRST_SELECTION.md`, `lab/judges/FIRST_*.md`
- Bakeoff: `lab/judges/UNFMT_BAKEOFF.md`
- Destroyers: `lab/judges/DESTROYER_*.md`
- Lineage reports: `lab/lineages/*/`

The lab keeps evolving until 09:00 JST.
