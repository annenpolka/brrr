# brrr × HDD Loop — Overnight Developer Tool Evolution Lab, HDD Edition

## Experiment Window

**2026-09-01 22:00 JST → 2026-09-02 09:00 JST**

This is the second overnight developer-tool evolution experiment in the existing `brrr` repository.

The first brrr experiment already explored the conventional path:

> invent → implement → dogfood → select → mutate → destroy

Do not rerun that experiment.

This run uses a different generator:

> dream → pressure → strip magic → ground → implement → evolve

The previous brrr run is the historical baseline.

The new run is HDD-native.

---

# 1. Mission

Search for developer-tool primitives that do not meaningfully exist yet.

We are interested in things such as:

- a Unix verb nobody has quite invented;
- a debugging question that existing debuggers do not expose directly;
- a new testing primitive;
- a repository query with a genuinely different object of inquiry;
- a new way to observe causality, history, execution, state, or change;
- an operation that collapses a recurring investigation into one explicit question;
- something that produces:

> Why isn't this already a first-class operation?

The goal is not to produce strange fictional software.

The goal is to temporarily remove feasibility gravity, discover unfamiliar interactions, then see which of them survive reality.

---

# 2. Governing Model

The experiment has four distinct responsibilities.

## HDD Dreamer

Explores an artifact as if it already exists.

The Dreamer:

- uses;
- inspects;
- fails;
- retries;
- discovers commands and workflows;
- does not design a proposal from outside the world.

Dreamer output is fictional design material.

It is never execution evidence.

## Red Pen

Applies pressure without replacing the artifact with a sensible conventional design.

It attacks:

- contradictions;
- unexplained magic;
- invented semantic knowledge;
- provenance confusion;
- unsupported precision;
- familiar tools with renamed nouns;
- affordances that collapse to existing workflows.

It also decides when another expensive R1 turn is actually justified.

## Grounder

Receives the surviving affordance after Dreaming.

It independently asks:

> What is the smallest present-day implementation that preserves this interaction?

The Grounder does not reproduce fictional APIs merely because the Dreamer invented them.

## brrr evolutionary loop

Once a real implementation exists, normal evolutionary pressure takes over:

- dogfood;
- selection;
- mutation;
- hybridization;
- clean-room reimplementation;
- destroyers;
- final jury.

HDD gets permission to dream.

brrr decides whether the organism lives.

---

# 3. Preserve the Previous Experiment

Treat the previous experiment as read-only historical material.

Do not overwrite:

- `EVOLUTION_REPORT.md`
- `lab/`
- existing lineages
- existing judge reports
- the previous master prompt

Create new coordinator state under:

```text
lab-hdd/
```

Create HDD trial state under:

```text
.hdd/
```

Create the final report as:

```text
HDD_EVOLUTION_REPORT.md
```

Candidate implementation occurs in isolated git worktrees.

Do not merge candidate product code into `main`.

The parent working tree remains coordinator/reporting-only.

---

# 4. Previous-brrr Contamination Rule

The first brrr experiment already contains strong ideas.

Those ideas must not steer initial invention.

Until First Selection is complete, do not expose the contents of:

- `EVOLUTION_REPORT.md`
- `lab/EMERGING.md`
- previous `lab/lineages/`
- previous candidate descriptions
- previous judge reports

to:

- HDD Dreamers;
- Red Pens evaluating initial novelty;
- initial Grounders;
- First Selection judges.

Do not indirectly contaminate seeds by saying things such as:

> invent something unlike invert, zanei, held, when...

The previous experiment becomes prior art **only after First Selection**.

Independent rediscovery across the two experiments is valuable evidence.

---

# 5. R1 Budget Governor

DeepSeek R1 is the expensive speculative operator.

Use it deliberately, but do not starve good lineages.

## Hard budget

```text
OpenRouter R1 hard cap: $50
```

This is a ceiling, not a spending target.

The experiment does not become better merely by spending the full amount.

## Internal budget envelopes

Use approximately:

```text
$20 — Cambrian generation and replacement trials
$15 — deepening strong HDD lineages
$10 — Generation-2 HDD jump mutations
 $5 — contingency / retries / exceptional late exploration
```

These are allocation guides, not mandatory spends.

Unused budget may flow to stronger categories.

## R1 budget checkpoints

- **00:00** — review Cambrian spend and prune aggressively if weak trials are consuming budget.
- **02:00** — preserve substantial budget for Generation-2 HDD jumps.
- **05:00** — broad speculative R1 exploration ends; use remaining R1 only for exceptional targeted jumps.
- **Hard cap: $50**

## Guardrails

Before **05:00 JST**, avoid spending more than approximately **$40** unless there is unusually strong evidence that further Dreaming is valuable.

Try to retain roughly **$10** of optional capacity for:

- late jump mutations;
- retries;
- unexpectedly strong lineages;
- targeted final exploration.

At **$45**, stop casual new HDD exploration.

At **$50**, stop new R1 calls completely.

Grounding, implementation, testing, judging, and preservation continue without R1.

## Cost accounting

If OpenRouter usage/cost metadata is available, record actual request cost.

Maintain:

```text
lab-hdd/R1_BUDGET.md
```

containing at least:

- total R1 calls;
- estimated or observed cost;
- calls by trial;
- calls by experiment phase;
- remaining hard budget.

If exact cost is unavailable, record input/output token counts where available and use a conservative estimate.

Do not silently ignore budget uncertainty.

---

# 6. R1 Turn Allocation

Do not treat every HDD trial equally.

## Initial trial

Give every fresh HDD lineage **one exploratory Dream**.

## Standard lineage

A lineage showing something nontrivial should normally receive approximately:

```text
3 Dreamer turns total
```

Typical structure:

```text
Turn 1 — free exploration
Red Pen

Turn 2 — remove the first crutch
Red Pen

Turn 3 — observe how the artifact mutates
Reality assessment
```

Turn 3 is particularly valuable.

Many weak hallucinations survive one criticism.

A useful abstraction often becomes visible only after the second pressure.

## Strong lineage

A genuinely productive lineage may receive:

```text
5–7 Dreamer turns
```

provided each additional turn is justified by a concrete unanswered pressure.

## Kill early

Do not spend five turns on:

- renamed tar/git/grep/debuggers;
- obvious thin wrappers;
- lore that survives only because new magic keeps appearing;
- repeated feasibility essays;
- lineages where Red Pen has already exposed the entire surviving operation.

## Fundamental scheduling rule

A Red Pen turn does **not** imply another R1 turn.

After every critique choose:

```text
CONTINUE_DREAMING
HARVEST_NOW
KILL
PARK_WEIRD
```

R1 is invoked again only for `CONTINUE_DREAMING`.

---

# 7. Worker Model

Target roughly **12–16 simultaneously useful workers** when the environment supports it.

R1 is not the only worker type.

Use cheaper or already-available models for:

- Red Pen;
- grounding;
- coding;
- dogfood;
- research;
- judges;
- destroyers.

R1 should primarily occupy the Dreamer role.

Worker slots move dynamically between stages.

Example early allocation:

```text
8 HDD Dreamers
4 Red Pen / Harvest
2 Grounders
2 Coordinator / exploration
```

Example later allocation:

```text
3 HDD Dreamers
3 Red Pen / Reality Gate
5 Grounder / Implementation
3 Dogfood
2 Coordinator / selection
```

Example Generation 2:

```text
2 HDD Jump
4 Ordinary Mutation
3 Clean-room Reimplementation
2 Hybrid
5 Dogfood / Evaluation
```

Do not synchronize all lineages into lockstep generations.

A weak lineage can die while another is already implemented and another new seed is being born.

The scheduling unit is the **lineage stage**, not the candidate number.

---

# 8. Schedule

| Time            | Phase                     | Main goal                                                                                               |
| --------------- | ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **22:00–00:00** | HDD Cambrian Explosion    | Independent HDD trials, early Red Pen, kill weak lineages, deepen promising ones                        |
| **00:00–01:15** | Reality Gate + Embodiment | Harvest stable affordances, Reality-Stripped assessment, start fresh Grounders and real implementations |
| **01:15–02:00** | First Selection           | Judge real embodiments, select several survivors, then unlock previous brrr as prior art                |
| **02:00–05:00** | Generation 2              | Ordinary mutations, clean-room reimplementations, hybrids, targeted HDD Jump mutations                  |
| **05:00–06:15** | Destroyer Phase           | Empirical attacks on both implementation and primitive; FIX / MUTATE / KILL                             |
| **06:15–07:40** | Generation 3              | Concentrate compute on strongest real lineages; simplify, harden, benchmark, refine                     |
| **07:40–08:20** | Final Jury                | Unix / Toolsmith / Heretic / Skeptic / Reality-Stripped judges                                          |
| **08:20–09:00** | Preservation + Comparison | Tomorrow Test, lineage preservation, R1 budget report, previous-brrr comparison, `HDD_EVOLUTION_REPORT.md` |

## 22:00–00:00 — HDD Cambrian Explosion

Primary goal:

> create a broad population of unfamiliar developer-tool interactions before implementation pressure narrows the space.

Start approximately **12–16 independent HDD trials**.

Use intentionally weak seeds.

Canonical form:

```text
An unfamiliar developer CLI is already installed in this environment.

Discover it by using it on a recurring software-development problem.

Operate what is present rather than proposing a product.
```

Small domain variation is acceptable.

Do not prescribe an affordance.

### During this phase

Continuously:

- spawn new trials;
- run Red Pen;
- kill obvious collapses;
- deepen interesting lineages;
- replace dead slots;
- begin early Harvest when a primitive stabilizes.

Do not wait until 00:00 to process all results.

By the end of this phase, some lineages should already be grounding.

---

# 9. Reality-Stripped Affordance Gate

Every lineage must pass this gate before receiving serious implementation compute.

Strip away:

- artifact-specific naming;
- fictional implementation;
- imaginary APIs;
- lore;
- magic;
- convenience guarantees.

Ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability is lost if that workflow replaces this artifact?
4. Is the novelty in the operation itself, or mainly syntax, metaphor, metadata, or convenience?

Classify:

```text
NOVEL_AFFORDANCE
USEFUL_COMPOSITION
THIN_WRAPPER
NO_SURVIVOR
```

Produce:

```text
Core Affordance
Affordance Classification
Nearest Existing Operation
Observable Delta
Surviving Abstractions
Removed Magic
Research Boundary
Smallest Useful Artifact
```

## Important

`THIN_WRAPPER` is legitimate evidence.

Do not send it back to R1 with:

> make this more novel.

Continue only if a specific observable difference remains genuinely unresolved.

Otherwise kill it or preserve it as an interesting conceptual fossil.

---

# 10. 00:00–01:15 — Reality Gate + Embodiment

Promote strong Harvests to fresh Grounders.

The Grounder normally receives:

- original weak seed;
- Harvest;
- affordance assessment;
- research boundary.

Do not initially provide the complete fictional transcript.

The Grounder's question is:

> What is the smallest real system that preserves the surviving interaction?

Partial implementations are acceptable when they honestly preserve the interesting core.

Fake completeness is not.

## Candidate contract

Every embodied candidate must eventually contain:

1. runnable tool, CLI preferred;
2. `README.md`;
3. `CANDIDATE.md`;
4. runnable demo;
5. fixtures/tests;
6. at least one working commit;
7. actual execution transcript;
8. at least one dogfood-driven improvement.

Use isolated git worktrees.

Record origin:

```yaml
origin:
  method: hdd
  trial: hdd-07
```

Also preserve the pre-implementation Reality assessment.

---

# 11. Evidence Boundary

Never collapse these categories.

## Dreamer output

Fictional design material.

## Red Pen

Design criticism.

## Harvest

Grounding hypothesis.

## Grounded prototype execution

Real evidence.

## Independent dogfood

Stronger evidence.

## Destroyer reproduction

Strong adversarial evidence.

A number generated by R1 does not become real because several later documents repeat it.

---

# 12. 01:15–02:00 — First Selection

At this point, judge real embodiments.

Use independent judges.

No creator grades its own lineage.

Axes:

- Novelty
- Utility
- Primitive strength
- Composability
- Empirical credibility
- Evolution potential
- Reality-Stripped Strength

Require actual execution evidence for strong empirical scores.

Do not rank primarily by:

- code volume;
- UI polish;
- README size;
- architectural sophistication.

Preserve strange strong primitives even when implementation is ugly.

Kill polished clones.

Select multiple survivors.

Do not collapse to one winner.

---

# 13. 02:00 — Unlock Previous brrr Prior Art

After First Selection, unlock the previous brrr results.

Now compare current survivors against the historical experiment.

Write:

```text
lab-hdd/PRIOR_RUN_COMPARISON.md
```

Classify relationships as:

## Cross-method convergence

HDD independently discovered substantially the same primitive as previous brrr.

This is strong evidence.

## Adjacent convergence

Both methods reached the same problem boundary but exposed different first-class questions.

## New design region

No meaningful previous analogue.

## Regression to prior art

The HDD result is weaker than something previous brrr already produced.

Do not protect HDD-origin ideas from this conclusion.

Never rewrite the original HDD transcript after discovering prior art.

---

# 14. 02:00–05:00 — Generation 2

Use four mutation mechanisms.

## Ordinary Mutation

Reality-first improvements:

- simplify interface;
- remove unnecessary LLM use;
- improve stdout/JSON;
- specialize;
- generalize;
- eliminate global state;
- replace algorithm;
- improve honesty;
- improve composability.

## Clean-room Reimplementation

Give another worker:

- surviving primitive;
- observed interaction;
- tests;
- known failures.

Have it independently reconstruct the tool.

Do not provide the original implementation unless later needed.

Independent recovery of the same interaction is evidence that the primitive is stronger than the original code.

## Hybrid

Combine underlying primitives, not feature lists.

Kill forced mashups quickly.

## HDD Jump Mutation

Take an already-grounded survivor and temporarily remove feasibility gravity again.

Do not say:

> improve this tool.

Instead remove one fundamental assumption.

Examples:

```text
Stable path identity does not exist.
```

```text
There is no total event ordering.
```

```text
There is no explicit baseline.
```

```text
There is no stable semantic entity identity.
```

```text
There is no AST model.
```

```text
Global persistent state is unavailable.
```

```text
Execution is nondeterministic.
```

Then require continued use of the same artifact.

Typical jump budget:

```text
2–3 R1 turns
```

A jump must again pass:

```text
Red Pen
→ Reality Gate
→ fresh Grounder
→ real competing implementation
```

Do not allow HDD Jump to become an endless fictional branch.

---

# 15. Convergent Evolution Tracking

Continuously record independent convergence.

Create:

```text
lab-hdd/CONVERGENCE.md
```

Track separately:

```text
HDD trial ∥ HDD trial
HDD lineage ∥ previous brrr lineage
Grounder ∥ clean-room Grounder
Mutation ∥ independent reimplementation
```

Name collisions are not convergence.

Feature similarity alone is not convergence.

The underlying user-visible operation must substantially match.

---

# 16. 05:00–06:15 — Destroyer Phase

From this point onward, dramatically reduce speculative work.

Claims must be empirical.

Attack survivors with:

- large repositories;
- monorepos;
- generated code;
- malformed inputs;
- strange histories;
- pathological filenames;
- nondeterminism;
- concurrency;
- empty result sets;
- partial failures;
- ambiguity;
- pipes;
- automation;
- performance;
- misleading successful exits;
- stale evidence;
- user misuse.

Destroy the primitive, not only the implementation.

Each serious finding should produce:

```text
FIX
MUTATE
KILL
```

Do not preserve a weak artifact because its Dreamer transcript was entertaining.

---

# 17. 06:15–07:40 — Generation 3

By 06:15, new large speculative lineages should be rare.

Park ungrounded grand ideas unless they are exceptional.

Concentrate compute on strong real objects.

Run competing attempts at:

- minimal command grammar;
- correct uncertainty semantics;
- strong structured output;
- performance;
- portability;
- alternate algorithms;
- better names;
- removal of dependencies;
- adjacent high-value use cases.

A final targeted HDD Jump is allowed only when:

1. a strong real survivor has a clearly identified conceptual ceiling;
2. the R1 budget allows it;
3. one capability-removal experiment could plausibly change the primitive.

Do not start broad Cambrian exploration after this point.

---

# 18. 07:40–08:20 — Final Jury

Create independent judges.

## Unix Judge

Values tiny orthogonal primitives and composition.

## Toolsmith Judge

Asks what a real developer would use repeatedly.

## Heretic Judge

Values genuinely unfamiliar interactions.

## Skeptic

Assumes the tool should not exist until evidence demonstrates otherwise.

## Reality-Stripped Judge

Ignores branding and implementation.

For each survivor asks:

```text
What operation remains?

What ordinary workflow is nearest?

What observable capability is lost by replacing this tool with it?
```

Do not average all judges into one synthetic score.

Disagreement is useful evidence.

Hide HDD-origin details from final judges where practical until after they evaluate the real artifact.

---

# 19. Tomorrow Test

Produce a deliberately small list.

Ask:

> Which binaries should a human actually install and try tomorrow?

A primitive can be worth remembering without deserving a PATH entry.

Do not reward abundance.

Empty slots are allowed.

---

# 20. 08:20–09:00 — Preservation + Comparison

Stop broad experimentation.

Use remaining compute to preserve evidence.

Save:

- raw HDD trials;
- ledgers;
- Dreamer transcripts;
- Red Pen evolution;
- Reality assessments;
- extinct weird ideas;
- Grounder reports;
- real implementations;
- fixtures/tests;
- empirical transcripts;
- mutations;
- hybrids;
- clean-room reimplementations;
- HDD jumps;
- destroyer reports;
- judge reports;
- convergence;
- prior-run comparison;
- R1 budget accounting.

Suggested coordinator tree:

```text
lab-hdd/
├── SCHEDULE.md
├── STATE.md
├── STATUS.md
├── R1_BUDGET.md
├── CONVERGENCE.md
├── PRIOR_RUN_COMPARISON.md
├── FIRST_SELECTION.md
├── hdd-origins/
├── judges/
├── destroyers/
└── lineages/
```

Keep `.hdd/<trial>/` as canonical raw HDD state.

Do not copy every transcript into `lab-hdd/`.

---

# 21. Final Report

Create:

```text
HDD_EVOLUTION_REPORT.md
```

Include:

## 1. Executive Summary

What happened.

## 2. Final Survivors

Real tools and one-sentence primitives.

## 3. Tomorrow Test

What should actually be installed.

## 4. Weirdest HDD Discoveries

Including extinct but memorable operations.

## 5. Reality-Gate Extinctions

Especially:

- THIN_WRAPPER;
- NO_SURVIVOR;
- magic-dependent concepts.

## 6. Embodiment Failures

Ideas that looked good while fictional but collapsed under current technology.

## 7. Destroyer Extinctions

Ideas that grounded successfully but failed empirical attack.

## 8. Convergent Evolution

Within HDD and across the previous brrr experiment.

## 9. HDD Jump Mutations

Which real tools changed meaningfully after a fundamental assumption was removed.

## 10. New Primitives

One sentence each.

Write them so they still make sense if all implementation code is deleted.

## 11. Judge Disagreement

Do not collapse disagreement.

## 12. R1 Budget

Report:

- calls;
- observed/estimated cost;
- expensive lineages;
- whether more R1 spend appeared useful;
- whether budget or wall-clock time was the actual limiting factor.

## 13. Comparison with Previous brrr

Compare descriptively.

Where available:

```text
previous brrr
vs
HDD-native brrr

initial explored ideas
embodied candidates
First Selection survivors
destroyer survivors
final survivors
Tomorrow Test entries
cross-method convergence
THIN_WRAPPER count
NO_SURVIVOR count
```

Counts are not a statistically valid benchmark.

More important:

- What kind of question appeared only under HDD?
- What independently appeared in both methods?
- What HDD idea sounded extraordinary but grounded to nothing?
- What HDD-born primitive survived implementation and destroyers?
- Did delayed feasibility produce genuinely different questions?

## 14. Lineage Tree

Example:

```text
hdd-07
  → Dream 1
  → Red Pen
  → Dream 2
  → Red Pen
  → Dream 3
  → NOVEL_AFFORDANCE
  → candidate-04
  → clean-room reimplementation
  → HDD jump
  → mutation-11
  → destroyer survive
  → final survivor
```

---

# 22. Heartbeat

Maintain:

```text
lab-hdd/STATE.md
lab-hdd/heartbeat.md
```

At every heartbeat:

1. inspect active workers;
2. collect finished work;
3. refill empty capacity;
4. kill hopeless lineages;
5. identify R1 turns waiting without good justification;
6. promote stable affordances to Reality Gate;
7. promote strong Harvests to Grounding;
8. ensure implementation work is being independently exercised;
9. check candidate diversity;
10. check previous-brrr contamination before 02:00;
11. update R1 spend;
12. check current JST;
13. continue.

A long Dreamer transcript is not progress.

A large implementation is not a strong primitive.

---

# 23. Failure Modes

## Novelty Theater

A THIN_WRAPPER gets arbitrary exotic features added solely to escape the classification.

Reject this.

## Fiction Laundering

Generated Dreamer output is later cited as real execution evidence.

Reject this.

## Implementation Gravity

Dreamers are forced to explain exact current implementation before the interaction has stabilized.

Avoid this.

## HDD Romanticism

Strange hallucinations receive more protection than empirically strong tools.

Reject this.

## Feasibility Conservatism

A hard but meaningful affordance is killed merely because one Grounder cannot fully automate it.

Try an honest partial embodiment or competing Grounder first.

## Previous-run Contamination

Old brrr primitives leak into initial invention.

Prevent until First Selection.

## R1 Budget Drift

The coordinator keeps calling R1 because another turn is easy.

Every additional Dreamer call must have a specific unresolved pressure.

## Endless Dreaming

A lineage remains fictional long after its central interaction is clear.

Harvest it and put gravity back on.

## Lineage Monopoly

One early attractive idea consumes most worker slots before sufficient diversity exists.

Maintain Cambrian diversity.

---

# 24. Success Criteria

The experiment succeeds if, by 09:00 JST:

1. a broad independent HDD population was explored;
2. weak hallucinations were explicitly killed;
3. good lineages received enough R1 turns to mutate under pressure;
4. several Harvests reached real implementation;
5. implementations were independently dogfooded;
6. destroyers were allowed to kill conceptually weak ideas;
7. fictional and empirical evidence remained clearly separated;
8. cross-method convergence with the old brrr run was recorded where present;
9. new primitives remain worth remembering even if the code is deleted;
10. R1 spending stayed below the $50 hard cap;
11. the final report can answer:

> Did temporarily removing feasibility gravity produce developer-tool questions that the original brrr experiment did not?

The governing principle is:

> Spend R1 on conceptual mutation, not routine work.
>
> Dream until an unfamiliar operation emerges.
>
> Strip away the magic.
>
> Put reality back.
>
> Then let brrr kill whatever does not deserve to exist.

Begin at **22:00 JST**.

First actions:

1. create `lab-hdd/`;
2. locate and validate the current `hdd-loop`;
3. initialize `lab-hdd/R1_BUDGET.md`;
4. establish `.hdd/` as the trial root;
5. write the fixed schedule;
6. confirm that previous brrr candidate material is sealed until First Selection;
7. spawn the first HDD population;
8. keep useful worker capacity saturated until the hard end.