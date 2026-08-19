# FIRST_UNIX — 03:00 JST first selection

Unix judge. Clock window: 2026-08-20 03:00 JST. Values: **tiny orthogonal primitives** and **composition**. Prefer stdin/stdout filters, exit codes, TSV/JSON, no implicit repo walk when a producer already exists. Do not rank by polish, LOC, README length, or UI.

Axes (0–5 integer). A 4+ on Empirical requires execution evidence, not README claims.

| code | axis |
| --- | --- |
| N | Novelty |
| U | Utility |
| P | Primitive strength |
| C | Composability |
| E | Empirical credibility |
| Ev | Evolution potential |

Verdicts: **mutate** = Gen-3 evolution vehicle. **keep** = survive as parent/spare; do not spend a rewrite slot. **park** = object interesting or already absorbed; no Gen-3 slot until a new empirical condition. **kill** = stop.

Mandates honored: **kill haunt**. **park folk**. Several survivors. No single winner.

---

## Stance

The night produced too many *join-history-to-the-living-tree* tools and too many walkers that own ignore policy. The Unix cut is: **one object, one verb, a stream if possible**. Mutations that flipped a buried assumption (walker→stream, `file:line`→token, boolean occupancy→witness set, fingerprint→pass/fail lockset) beat the polished ancestors.

Do not spend Gen-3 inventing another leftover-name search. Do not keep two inverse-printf walkers. Do not keep pinch and hitch next to knot. Do not keep kiln and clutch next to sinter.

---

## Evolution vehicles (several, orthogonal)

Carry these **sixteen** into Gen-3. They are different objects. Pipe them; do not merge them.

| object | vehicle | why Unix |
| --- | --- | --- |
| inverse printf + named holes + span | **invert** | `rg \| invert`; no walker |
| durable locus token | **pin** | mint once; resolve has no `path:line` |
| locator stream rewrite | **flume** | log in, log out, gitless |
| shortest distinguishing predicate | **tell** | two trees in → `held` query out |
| occupancy + holder | **perch** | `held` boolean is `--boolean` |
| hunk occupancy vs a tree | **sate** | `git apply --check` is a boolean lie |
| birth cohort of a change | **erst** | commit/diff in; never `FILE:LINE` |
| exact wire key | **sic** | `git diff \| sic --check` |
| production argument worlds as fixtures | **sow** | JSON/NDJSON, not a tilt sentence |
| leftover *claims* a diff made false | **zanei** | diff in, afterimages out, linter exit |
| env ABI of the load image set | **lode** | `ldd` for getenv names |
| oracle modulo substitution | **lees** | residue, not bool |
| 1-minimal production lockset | **cinch** | tests stay NEW; pass/fail predicate |
| path-condition invert | **under** | name a predicate, print the lines |
| constructed values on a cut | **cusp** | BRINK/OFFBY, not string distance |
| signature-lag gate | **doze** | `--check` exit 1; no ghost ranking |

Also keep (do not evolve this wave unless a vehicle needs them as a backend): **held, when, chime, aka, also, winnow, glean, alibi, rift, zure, wraith, deja, reverb, stencil, once, cleave, cling, orbit, yoke, unseen, veil, moor, knot, slip, sluice, dwelt, skew, sinter, spoor**.

---

## Cluster map

```
inverse printf     unfmt-08, unfmt-13, stencil, sluice, invert, moor
durable address    slip, flume, pin, moor
occupancy          held, dwelt, perch, tell, stint
path-condition     when, under, chime
protocol tokens    aka, sic
copy kinship       akin, once
leftover names     haunt, wraith, wisp          ← one survivor: wraith
leftover claims    zanei                        ← not a ghost
diff-vs-history    deja, reverb
dirty-tree ddmin   winnow, glean, alibi, cinch
semantic merge     rift, zure
use-site lag       unseen, doze, skew
brink values       nigh, cusp
argument worlds    cleave, sow
wait / quiescence  spoor, coast, cling, pinch, hitch, knot
env / guise        due, lode, orbit
generation lots    kiln, clutch, sinter, yoke
oracles            lees, veil, sate
birth cohort       also, owe, erst
folk protocols     folk                         ← parked
```

---

## Verdict ledger

| ID | tool | N | U | P | C | E | Ev | Σ | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| candidate-01 | akin | 3 | 3 | 3 | 4 | 4 | 3 | 20 | mutate (`--port` only) |
| candidate-02 | aka | 4 | 4 | 5 | 5 | 5 | 3 | 26 | keep |
| candidate-03 | wisp | 3 | 3 | 3 | 3 | 3 | 2 | 17 | park |
| candidate-04 | reverb | 4 | 4 | 4 | 4 | 4 | 3 | 23 | keep |
| candidate-05 | haunt | 3 | 2 | 2 | 3 | 4 | 1 | 15 | **kill** |
| candidate-06 | deja | 4 | 4 | 4 | 4 | 4 | 3 | 23 | keep |
| candidate-07 | zanei | 5 | 5 | 5 | 5 | 4 | 4 | 28 | **mutate** |
| candidate-08 | unfmt | 4 | 4 | 5 | 3 | 5 | 2 | 23 | park |
| candidate-09 | held | 5 | 5 | 5 | 5 | 5 | 3 | 28 | keep |
| candidate-10 | also | 5 | 4 | 5 | 4 | 4 | 3 | 25 | keep |
| candidate-11 | rift | 4 | 4 | 4 | 4 | 4 | 3 | 23 | keep |
| candidate-12 | wraith | 4 | 4 | 4 | 4 | 3 | 3 | 22 | keep |
| candidate-13 | unfmt | 4 | 4 | 5 | 3 | 5 | 2 | 23 | park |
| candidate-14 | unseen | 5 | 4 | 4 | 3 | 3 | 3 | 22 | keep |
| candidate-15 | winnow | 4 | 5 | 4 | 4 | 4 | 3 | 24 | keep |
| candidate-16 | slip | 4 | 5 | 5 | 4 | 5 | 3 | 26 | keep |
| candidate-17 | nigh | 3 | 2 | 3 | 3 | 2 | 1 | 14 | park |
| candidate-18 | cleave | 5 | 4 | 5 | 4 | 2 | 3 | 23 | keep |
| candidate-19 | folk | 4 | 2 | 4 | 3 | 2 | 3 | 18 | **park** |
| candidate-20 | when | 5 | 5 | 5 | 5 | 5 | 3 | 28 | keep |
| candidate-21 | spoor | 5 | 4 | 4 | 3 | 2 | 3 | 21 | keep |
| candidate-22 | pinch | 4 | 3 | 4 | 3 | 2 | 2 | 18 | park |
| candidate-23 | hitch | 4 | 3 | 4 | 3 | 2 | 2 | 18 | park |
| candidate-24 | alibi | 5 | 4 | 4 | 3 | 3 | 3 | 22 | keep |
| candidate-25 | coast | 3 | 3 | 3 | 4 | 3 | 2 | 18 | park |
| candidate-26 | kiln | 4 | 4 | 4 | 3 | 3 | 2 | 20 | park |
| candidate-27 | clutch | 4 | 4 | 4 | 3 | 3 | 2 | 20 | park |
| candidate-28 | due | 4 | 4 | 4 | 4 | 3 | 2 | 21 | park |
| candidate-29 | yoke | 4 | 4 | 4 | 3 | 3 | 3 | 21 | keep |
| candidate-30 | orbit | 4 | 4 | 4 | 3 | 3 | 3 | 21 | keep |
| candidate-31 | lees | 5 | 4 | 5 | 5 | 3 | 4 | 26 | **mutate** |
| candidate-32 | veil | 4 | 4 | 4 | 4 | 3 | 3 | 22 | keep |
| candidate-34 | sate | 5 | 5 | 5 | 5 | 3 | 4 | 27 | **mutate** |
| hybrid-01 | moor | 5 | 4 | 4 | 5 | 4 | 3 | 25 | keep |
| hybrid-02 | knot | 4 | 4 | 5 | 4 | 3 | 3 | 23 | keep |
| hybrid-03 | cinch | 5 | 4 | 5 | 4 | 3 | 4 | 25 | **mutate** |
| hybrid-04 | sinter | 4 | 4 | 5 | 4 | 3 | 3 | 23 | keep |
| mutation-01 | sic | 4 | 5 | 5 | 5 | 4 | 4 | 27 | **mutate** |
| mutation-02 | sluice | 4 | 5 | 5 | 5 | 5 | 2 | 26 | keep |
| mutation-03 | tell | 5 | 4 | 5 | 5 | 4 | 5 | 28 | **mutate** |
| mutation-04 | flume | 4 | 5 | 5 | 5 | 2 | 4 | 25 | **mutate** |
| mutation-05 | zure | 4 | 4 | 4 | 4 | 2 | 3 | 21 | keep |
| mutation-06 | owe | 4 | 4 | 4 | 4 | 3 | 2 | 21 | park |
| mutation-07 | glean | 3 | 5 | 4 | 5 | 4 | 3 | 24 | keep |
| mutation-08 | skew | 4 | 3 | 4 | 4 | 2 | 3 | 20 | keep |
| mutation-09 | once | 3 | 4 | 4 | 4 | 2 | 3 | 20 | keep |
| mutation-10 | under | 4 | 5 | 5 | 5 | 3 | 4 | 26 | **mutate** |
| mutation-11 | cusp | 4 | 4 | 5 | 5 | 3 | 4 | 25 | **mutate** |
| mutation-12 | cling | 4 | 4 | 4 | 3 | 3 | 3 | 21 | keep |
| mutation-13 | sow | 4 | 5 | 5 | 5 | 3 | 4 | 26 | **mutate** |
| mutation-14 | pin | 5 | 4 | 5 | 4 | 5 | 5 | 28 | **mutate** |
| mutation-15 | invert | 5 | 5 | 5 | 5 | 5 | 5 | 30 | **mutate** |
| mutation-16 | chime | 4 | 4 | 5 | 5 | 3 | 3 | 24 | keep |
| mutation-17 | perch | 4 | 5 | 5 | 5 | 4 | 4 | 27 | **mutate** |
| mutation-18 | stint | 4 | 4 | 4 | 4 | 3 | 3 | 22 | keep |
| mutation-19 | erst | 5 | 5 | 5 | 4 | 3 | 4 | 26 | **mutate** |
| mutation-20 | doze | 4 | 5 | 5 | 4 | 3 | 4 | 25 | **mutate** |
| mutation-21 | lode | 4 | 5 | 5 | 5 | 3 | 4 | 26 | **mutate** |
| reimpl-01 | stencil | 3 | 4 | 5 | 3 | 5 | 2 | 22 | keep |
| reimpl-02 | dwelt | 3 | 4 | 5 | 5 | 5 | 2 | 24 | keep |

Σ is a diagnostic, not a ranking key. Invert is not “the winner.” It is the inverse-printf *filter*. Pin is not “second place.” It is a different object (PRIOR_ART gap: durable pin).

---

## Per-lineage cards

Evidence tags:

- **PARENT** — `lab/SHIPS.md` / `lab/WAVE2.md` / `lab/WAVE3.md` parent re-run.
- **BAKEOFF** — `lab/judges/UNFMT_BAKEOFF.md`.
- **DESTROYER** — `lab/judges/DESTROYER_PIN_INVERT.md`.
- **CRITIC** — `lab/judges/DISTINCT.md` or `lab/judges/GHOST_CLUSTER.md`.
- **AUTHOR** — lineage `CANDIDATE.md` / `demo.sh` transcript only.
- **UNVERIFIED** — WAVE2 `author 0` or no parent/critic execution.

Suggested mutations are for keep/mutate only.

---

### Inverse printf

#### candidate-08 — unfmt

**Primitive.** Paste a runtime string; walk a tree for the format template that could have produced it.

**Scores.** N4 U4 P5 C3 E5 Ev2 = 23

**Verdict.** park

**Mutation.** Do not grow this walker. If one-shot `-C` is needed, wrap invert’s kernel in an `rg` producer.

**Evidence.** PARENT demo PASS 28/28 (`lab/SHIPS.md`). BAKEOFF 4/5: miss on sitbone nested Swift quotes `camera presence enabled` (`lab/judges/UNFMT_BAKEOFF.md`). Cleanest *walker* rank on kizu, not the lineage vehicle.

#### candidate-13 — unfmt

**Primitive.** Same inverse printf, independently; named hole bindings, slower walk.

**Scores.** N4 U4 P5 C3 E5 Ev2 = 23

**Verdict.** park

**Mutation.** Holes already harvested into invert. Do not keep a second ignore policy.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). BAKEOFF 5/5, noisier kizu rank, slowest walker. WAVE3: invert harvested unfmt-13 holes into a sluice-shaped filter (46/46).

#### reimpl-01 — stencil

**Primitive.** Clean-room unfmt-08: paste instance, walk for template.

**Scores.** N3 U4 P5 C3 E5 Ev2 = 22

**Verdict.** keep (walker spare)

**Mutation.** None this wave. Spare only if invert must grow an optional producer.

**Evidence.** BAKEOFF 5/5. WAVE3: beats original on sitbone `camera presence enabled` (nested Swift quotes) without reading source. Still anonymous holes; leaks `git {} failed`.

#### mutation-02 — sluice

**Primitive.** Inverse printf as a filter: templates on a stream, no implicit walk.

**Scores.** N4 U5 P5 C5 E5 Ev2 = 26

**Verdict.** keep

**Mutation.** Invert already is the named-hole sluice. Keep sluice as the simpler kernel; do not walk.

**Evidence.** PARENT demo PASS 40/40 (`lab/WAVE2.md`). `rg -n --type rust 'format!|anyhow!' \| ./sluice` is the composition that killed `-C`.

#### mutation-15 — invert

**Primitive.** Stream inverse-printf that **binds names** and reports leftover prefix as a **span**.

**Scores.** N5 U5 P5 C5 E5 Ev5 = 30

**Verdict.** mutate

**Mutation.** Prefix-of-holed-template. No-hole prefix must not outrank a hole that binds. Refuse rustc/compiler grammar (different tool). `--any` should stop printing. Concat (`"open " + path`) is a sibling mutation, not a patch. Binary stdin must fail closed (DESTROYER: `UnicodeDecodeError` on urandom).

**Evidence.** BAKEOFF 5/5, lineage vehicle. WAVE3 46/46. DESTROYER: 7-hole sitbone still binds `score=1.12`; truncated logs miss as designed; documentation decoy `failed to spawn` (0 holes) beats `failed to spawn `{cmd}`` (`score=0.67` vs `0.48`). Selftest still 0 after attacks. `lab/lineages/mutation-15__invert/CANDIDATE.md`.

#### hybrid-01 — moor

**Primitive.** One-pass bind of a log *instance* to a current `path:line` **and** the holes that produced it.

**Scores.** N5 U4 P4 C5 E4 Ev3 = 25

**Verdict.** keep

**Mutation.** `moor mint` as `(template, hole values, line fingerprint)` if pin × invert needs a joint token. Do not concatenate `slip \| unfmt`.

**Evidence.** PARENT demo PASS 25/25 (`lab/WAVE2.md`). Decoy exact test literal `user 42 not found` loses to production `user {uid}` once locator proximity after split is in the score (`lab/lineages/hybrid-01__moor/CANDIDATE.md`).

---

### Durable address

#### candidate-16 — slip

**Primitive.** Rewrite stale `file:line` from snapshot A onto B by content fingerprint, not blame.

**Scores.** N4 U5 P5 C4 E5 Ev3 = 26

**Verdict.** keep

**Mutation.** Pin is the object; flume is the stream. Slip stays the fingerprint backend.

**Evidence.** PARENT PASS including kizu `app.rs` split `529 → layout.rs:17` (`lab/SHIPS.md`, `lab/EMERGING.md`).

#### mutation-04 — flume

**Primitive.** Gitless stdin→stdout rewrite of every locator in a compiler/test log between two directories.

**Scores.** N4 U5 P5 C5 E2 Ev4 = 25

**Verdict.** mutate

**Mutation.** ANSI-aware matching. JSON compiler streams (`cargo --message-format=json`). rustc multi-hunk gutters that are not `old_line+k`. Fail closed on truncated tokens the same way pin should.

**Evidence.** UNVERIFIED at parent (WAVE2 author 0). AUTHOR: kizu `app.rs` split, rustc gutter carry, sitbone shifted `detect()`, stub git that never fires (`lab/lineages/mutation-04__flume/CANDIDATE.md`). The gutter feature is why this is a filter, not a slip flag.

#### mutation-14 — pin

**Primitive.** Mint a self-contained locus token; resolve it onto any later tree with no `path:line` and no origin SHA.

**Scores.** N5 U4 P5 C4 E5 Ev5 = 28

**Verdict.** mutate

**Mutation.** Ambiguous must not emit `1.000` twice. Neighbor body must beat a leftover stub at the old path (file-split story dies if the wrapper remains). Bind a repo/tree hint or refuse a `--to` that does not exist (typo looks like deletion). NFC-normalize paths. Truncated `pin1.` fail closed (`resolve` currently porcelain-success unless `--strict`). DESTROYER, do not rewrite in a drive-by.

**Evidence.** DESTROYER transcript `/tmp/destroy-pin-invert/transcript.txt`. Unique kizu `seen_hunk_fingerprint` does **not** hallucinate onto voidtrace/tenaoshi. Stub `src/calc.py` after split scores 1.000 on the leftover wrapper. Identical helpers: walk order picked `z/calc.py`. `lab/lineages/mutation-14__pin/CANDIDATE.md`. PRIOR_ART named this gap.

---

### Occupancy / eras

#### candidate-09 — held

**Primitive.** Contiguous eras of history where an arbitrary predicate is true (not one bisect cut).

**Scores.** N5 U5 P5 C5 E5 Ev3 = 28

**Verdict.** keep

**Mutation.** `tell A B | held --range A..main`. Witness splits live on perch.

**Evidence.** PARENT PASS 33/33 sitbone/skills/kizu/voidtrace (`lab/SHIPS.md`). First real deleted file beat `git log -- path`. Empty `exists` was the v1 footgun.

#### reimpl-02 — dwelt

**Primitive.** Clean-room held from CLI behavior only.

**Scores.** N3 U4 P5 C5 E5 Ev2 = 24

**Verdict.** keep (proof, not a second occupancy tool)

**Mutation.** Harvest merge-birth naming (`e1098c8` vs merge SHA) into held/perch. Do not evolve dwelt as a product.

**Evidence.** PARENT PASS: matches held on sitbone/skills (`lab/WAVE3.md`). Then beat ancestor on kizu first-parent occupancy starting at a merge.

#### mutation-17 — perch

**Primitive.** Occupancy eras that also split when the **witness set** changes.

**Scores.** N4 U5 P5 C5 E4 Ev4 = 27

**Verdict.** mutate

**Mutation.** Default grain that names README-only tenure as a different era from source tenure (already the skills lesson). Pipe `tell` predicates into perch. Do not become `git log --name-only -S`.

**Evidence.** WAVE3: skills `preact-zero-mock` last 16 commits are README-only while `grep` occupancy stays TRUE. sitbone `FocusRiverView` holder splits 1→2→1 files (`lab/lineages/mutation-17__perch/CANDIDATE.md`). `--boolean` recovers held.

#### mutation-03 — tell

**Primitive.** Two trees in; emit the shortest predicates that distinguish them.

**Scores.** N5 U4 P5 C5 E4 Ev5 = 28

**Verdict.** mutate

**Mutation.** Emit a `held`/`perch` command line. Shortest *set* under a length budget. `--follow` so a rename is one identity.

**Evidence.** PARENT PASS (`lab/WAVE2.md`). After v2, sitbone `14b1d6e^..14b1d6e` cover is `grep FocusRiverView` not `grep 'がるパ'` / `grep site` (`lab/lineages/mutation-03__tell/CANDIDATE.md`). Inverse of held: you do not have to know the question.

#### mutation-18 — stint

**Primitive.** Interval occupancy of files/symbols born and killed between two refs, plus `--pick` last blob. No leftover-name search.

**Scores.** N4 U4 P4 C4 E3 Ev3 = 22

**Verdict.** keep

**Mutation.** Keep `--pick` as archaeology. Do not reattach remnants (that is wraith).

**Evidence.** AUTHOR: skills ranking `preact 31 vs circuit-breaker 6 vs scout 1`; `--pick circuit-breaker/` restores the plugin. sitbone `FocusRiverView` occupancy 11 matches held without naming the path (`lab/lineages/mutation-18__stint/CANDIDATE.md`).

---

### Path-condition

#### candidate-20 — when

**Primitive.** Given `file:line` (or a diff, or grep), emit the nested predicates still in force, including fallthrough `given`.

**Scores.** N5 U5 P5 C5 E5 Ev3 = 28

**Verdict.** keep

**Mutation.** Overlay an unapplied patch so `--diff` is the post-image. Nested total early-returns (`parse.rs` quoted-path miss).

**Evidence.** PARENT PASS (`lab/WAVE2.md`). DISTINCT top-6. Object is a condition stack, not a function name.

#### mutation-10 — under

**Primitive.** Name a predicate snippet; emit every locus whose path-condition contains it.

**Scores.** N4 U5 P5 C5 E3 Ev4 = 26

**Verdict.** mutate

**Mutation.** `--same-as` lives on chime; under stays the invert. Do not reduce to grepping the `if` and printing the body.

**Evidence.** AUTHOR (`lab/lineages/mutation-10__under/CANDIDATE.md`). `when parse.rs:60` and `under --kind given 'a/'` are the same object from opposite ends. This is the query you type when you do not yet know the line.

#### mutation-16 — chime

**Primitive.** Name a locus; emit loci with the same condition stack, or a superset (deeper nest).

**Scores.** N4 U4 P5 C5 E3 Ev3 = 24

**Verdict.** keep

**Mutation.** Keep `--exact` vs prefix-superset labels. Do not collapse into `under --same-as` without those labels.

**Evidence.** AUTHOR. Third verb next to when/under.

---

### Protocol tokens / kinship

#### candidate-02 — aka

**Primitive.** One protocol token across inflections (`has_more` / `hasMore` / `HAS_MORE`); fail a patch that updates only some files.

**Scores.** N4 U4 P5 C5 E5 Ev3 = 26

**Verdict.** keep

**Mutation.** sic owns exact wire keys. aka keeps inflection identity. Do not merge.

**Evidence.** PARENT PASS on tenaoshi/kizu/sitbone/skills (`lab/SHIPS.md`, `lab/EMERGING.md`). `git diff | aka --check`.

#### mutation-01 — sic

**Primitive.** Exact serialized wire key only. Inflection neighbors are a **fork**, not one identity.

**Scores.** N4 U5 P5 C5 E4 Ev4 = 27

**Verdict.** mutate

**Mutation.** Key-*path* identity (`pagination.has_more` vs `meta.has_more`). `--strict` leftover code+config, ignore docs. Codable/serde implicit keys only when the type is actually serialized.

**Evidence.** PARENT PASS (`lab/WAVE2.md`). Dual-serialization on kizu/voidtrace; 10-key leftover on tenaoshi dirty spec migration; identifier false positives gone.

#### candidate-01 — akin

**Primitive.** Files that split from shared content; that blob is a merge-base git never recorded; `--port` is 3-way.

**Scores.** N3 U3 P3 C4 E4 Ev3 = 20

**Verdict.** mutate

**Mutation.** Keep `--port` only. Drop similarity / same-basename invented bases (once already did exact-blob). v1 exact-simultaneous-blob died on real repos (0 kin on sitbone/kizu/voidtrace/skills/tenaoshi) — right death, wrong next oracle.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). DISTINCT: akin `--port` only. `lab/lineages/candidate-01__akin/CANDIDATE.md`.

#### mutation-09 — once

**Primitive.** If two current paths ever contained the same git blob, they are kin; that blob is the merge-base; `git merge-file` is the port. Exact object identity only.

**Scores.** N3 U4 P4 C4 E2 Ev3 = 20

**Verdict.** keep

**Mutation.** `--sync FROM`. Occupancy in pretty already landed. Refuse SequenceMatcher bases forever.

**Evidence.** UNVERIFIED at parent (WAVE2 author 0). AUTHOR: skills `SKILL.md` ↔ `SKILL_claude.md` via blob `2b16be83128c`; dignity-guide old-version chapters 4/4 `--port`. Similarity lookalike is not kin (exit 2).

---

### Ghost / leftover cluster

CRITIC (`lab/judges/GHOST_CLUSTER.md`): four objects under one metaphor. Do not collapse the night to leftover names. One ghost-name survivor: **wraith**. **zanei** is a different object (claims). **deja** is diff-vs-history. **reverb** is change-as-query.

#### candidate-05 — haunt

**Primitive.** Inverse dead-code: definitions that died in history but the living tree still talks about.

**Scores.** N3 U2 P2 C3 E4 Ev1 = 15

**Verdict.** kill

**Mutation.** —

**Evidence.** PARENT PASS (`lab/SHIPS.md`) — execution is real, the *object* is not distinct. CRITIC: worse wraith; lost skills `preact-zero-mock`. v1 haunts on skills were basename false positives (`SKILL.md`, `init.sh`). Inverse-of-dead-code join is wraith’s untyped-fringe hunt with a weaker filter. Stop.

#### candidate-12 — wraith

**Primitive.** Names that lost their last definition; hunt the untyped fringe (docs, configs, scripts, comments, strings) a compiler will never see.

**Scores.** N4 U4 P4 C4 E3 Ev3 = 22

**Verdict.** keep

**Mutation.** `--check` on a branch with docs ignored. Do not reimplement haunt.

**Evidence.** AUTHOR demo 0 at SHIPS harvest; later transcript: skills README advertising deleted skill; kizu false “still exists” after module split cut (`lab/lineages/candidate-12__wraith/CANDIDATE.md`). CRITIC: the leftover-*name* lineage.

#### candidate-03 — wisp

**Primitive.** Files/symbols born and killed between two refs (invisible in the net diff), then remnants of those names at HEAD.

**Scores.** N3 U3 P3 C3 E3 Ev2 = 17

**Verdict.** park

**Mutation.** Occupancy + last blob is **stint**. Remnants are **wraith**. Do not keep the pair glued.

**Evidence.** SHIPS author demo 0. CRITIC: mutate — keep interval-ephemeral files; drop remnants. stint already did that.

#### candidate-04 — reverb

**Primitive.** Treat the preimage of a diff as a search query; find remaining copies of the old code.

**Scores.** N4 U4 P4 C4 E4 Ev3 = 23

**Verdict.** keep

**Mutation.** Keep as “the intent of this diff, elsewhere.” Do not become leftover-name search.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). tenaoshi: one header-line fix, two adapters still wrong, no query typed by hand.

#### candidate-07 — zanei

**Primitive.** Print leftover **claims** a diff just made false (bound name/value, rename, polarity). Diff in, afterimages out, linter exit.

**Scores.** N5 U5 P5 C5 E4 Ev4 = 28

**Verdict.** mutate

**Mutation.** Stay a filter (`git diff A B | zanei --diff -`). Tighten fact extraction so version bumps do not drown in plan files. Do not become a review platform.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). kizu `Cargo.toml` 0.3.0→0.7.0 still claimed by `plugin/plugin.json` `"version": "0.3.0"`. sitbone hysteresis commit leftover `threshold 0.4` in CLAUDE.md. CRITIC: strongest leftover, not a ghost.

#### candidate-06 — deja

**Primitive.** Score a diff against the repo’s memory: RELAPSE / RESURRECT / UNDOFIX.

**Scores.** N4 U4 P4 C4 E4 Ev3 = 23

**Verdict.** keep

**Mutation.** Keep the three statuses. Kill only if `git log -S` plus a wrapper matches precision (v1 showed it does not).

**Evidence.** PARENT PASS (`lab/SHIPS.md`). Not a ghost: diff-vs-history.

---

### Dirty tree / tests as lock

#### candidate-15 — winnow

**Primitive.** Partition uncommitted hunks into the smallest set that reproduces a command’s current behavior (wheat) vs the rest (chaff).

**Scores.** N4 U5 P4 C4 E4 Ev3 = 24

**Verdict.** keep

**Mutation.** File grain is glean. Pass/fail lockset is cinch. winnow keeps fingerprint-of-command.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). v1 lied without `PYTHONDONTWRITEBYTECODE=1`. Not git-bisect: bisect has no uncommitted-hunk object.

#### mutation-07 — glean

**Primitive.** Same ddmin at **file** grain; untracked files are first-class; never hunks.

**Scores.** N3 U5 P4 C5 E4 Ev3 = 24

**Verdict.** keep

**Mutation.** `--format drop` as the product (`git restore`/`rm`). Hybrid/oracle later, not a rewrite.

**Evidence.** PARENT PASS (`lab/WAVE2.md`). tenaoshi 108-file dirty tree: 15 trials, one wheat path.

#### candidate-24 — alibi

**Primitive.** Transplant current tests onto another revision’s production; tests that fail are the production diff’s alibi.

**Scores.** N5 U4 P4 C3 E3 Ev3 = 22

**Verdict.** keep

**Mutation.** Per-hunk overlay. Not `git stash -k && test` (that reverts the new tests too).

**Evidence.** AUTHOR: LOOSE `demo.sh`, LOCKED witnesses. Did not run cargo/swift/vitest splices on kizu/sitbone/voidtrace.

#### hybrid-03 — cinch

**Primitive.** 1-minimal **production** hunks the current tests require. Tests stay NEW. Predicate is pass/fail, not fingerprint.

**Scores.** N5 U4 P5 C4 E3 Ev4 = 25

**Verdict.** mutate

**Mutation.** Always run NEW (test-only red suite is BROKEN, not CLEAN). `--commit-wheat`. Coverage hint before isolation. Do not recover lockset by `alibi --per-path` then winnow — winnow’s predicate is still fingerprint (debug `print` becomes wheat).

**Evidence.** AUTHOR demo PASS. Same dirty tree: winnow wheat = debug print **and** `return a + b`; cinch wheat = the return. tenaoshi v1 EMPTY vs BROKEN fixed (`lab/lineages/hybrid-03__cinch/CANDIDATE.md`).

---

### Semantic merge / use-site lag

#### candidate-11 — rift

**Primitive.** Identifier-level conflicts (def vs use, deleted def vs new use, split-brain) between two changesets git merge would accept as clean.

**Scores.** N4 U4 P4 C4 E4 Ev3 = 23

**Verdict.** keep

**Mutation.** Useful path is `rift main...HEAD` plus CI `-q`. `--audit` on GitHub-style history is weak.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). DISTINCT: right verb, planted evidence — do not spend Gen-2 slots re-proving it.

#### mutation-05 — zure

**Primitive.** Same identifier conflicts between **recent history** and the **uncommitted** tree. Pre-commit semantic merge with yourself.

**Scores.** N4 U4 P4 C4 E2 Ev3 = 21

**Verdict.** keep

**Mutation.** `--alive`: blast radius of the commit you are about to make (HEAD uses of work-changed defs). Three-layer dirty: history vs index vs unstaged.

**Evidence.** UNVERIFIED at parent (WAVE2 author 0). AUTHOR: live tenaoshi deletion; v0.1 `let abs =` as a def fixed.

#### candidate-14 — unseen

**Primitive.** Given a use-site, show the definition as it existed when that line was last touched, then diff it against HEAD.

**Scores.** N5 U4 P4 C3 E3 Ev3 = 22

**Verdict.** keep

**Mutation.** Signature-lag CI is **doze**. unseen keeps the body-diff archaeology.

**Evidence.** AUTHOR: kizu `insert_scar` JSX/`ScarInsert` contract; tenaoshi `writeBack` `AXUIElement?` → `Scope`. v1 ranking looked like a word-frequency toy.

#### mutation-20 — doze

**Primitive.** `--check` exits 1 if any use-site last saw a different **signature** than HEAD. Body diffs and ghost ranking are not the product.

**Scores.** N4 U5 P5 C4 E3 Ev4 = 25

**Verdict.** mutate

**Mutation.** Compiled callers vs plan-file mentions without bringing English-word ranking back. `--body` stays opt-in.

**Evidence.** AUTHOR: `--check insert_scar` on kizu fails on `Result<()>` / `text: &str` vs HEAD `Result<Option<ScarInsert>>` in ~0.5s. Body-only `trim` does not fail CI.

#### mutation-08 — skew

**Primitive.** Caller *files* whose save/commit clock is behind the callee file’s clock; no `git blame`.

**Scores.** N4 U3 P4 C4 E2 Ev3 = 20

**Verdict.** keep

**Mutation.** Live without line blame for cases like tenaoshi `writeBack` (caller file clock is not the use-site clock). Dirty callee uses mtime.

**Evidence.** UNVERIFIED (WAVE2 author 0). Different object from unseen (file clock vs blame-of-line).

---

### Brink / argument worlds / folk

#### candidate-17 — nigh

**Primitive.** Constructed literals vs branch cuts: CLOSED / NIGH / BRINK, including string-edit NIGH.

**Scores.** N3 U2 P3 C3 E2 Ev1 = 14

**Verdict.** park

**Mutation.** Cusp already specialized to numeric/enum brink. NIGH (`ENOENT`≈`event`) is name-alias soup.

**Evidence.** UNVERIFIED (WAVE2 author 0). WAVE3: nigh → cusp.

#### mutation-11 — cusp

**Primitive.** Predicates whose constructed values sit on the cut: exclusive/inclusive bounds, off-by-one, sentinels, adjacent enum variants. No string-edit distance.

**Scores.** N4 U4 P5 C5 E3 Ev4 = 25

**Verdict.** mutate

**Mutation.** `--probe` invert stays. Cut 0/1 soup harder. TSV is the interface.

**Evidence.** AUTHOR: v0.1 50 OFFBYs were 0/1 soup; leftover after the cut is 401/400, suffix(2), `.unknown`. Fixtures name BRINK/OFFBY/SENTINEL/NEIGHBOR.

#### candidate-18 — cleave

**Primitive.** A function is the argument worlds its callers inhabit; report when tests and production do not live in the same worlds.

**Scores.** N5 U4 P5 C4 E2 Ev3 = 23

**Verdict.** keep

**Mutation.** Tilt report stays here. Fixture stream is sow.

**Evidence.** UNVERIFIED (WAVE2 author 0). AUTHOR: sitbone six untested production browser names; v0.2 cut voidtrace tilts 3× by refusing test helpers as the SUT.

#### mutation-13 — sow

**Primitive.** Production callers are source of truth; emit untested production worlds as test-generator input. No tilt report.

**Scores.** N4 U5 P5 C5 E3 Ev4 = 26

**Verdict.** mutate

**Mutation.** JSON/NDJSON/`--emit pytest` is the product. Rename-follow. Do not grow a coverage dashboard.

**Evidence.** AUTHOR: same sitbone finding becomes six stubs; kizu four terminal backends become four stubs; v0.2 recovered 91 kizu defs by not reading lifetimes as strings.

#### candidate-19 — folk

**Primitive.** Mine unwritten call-pair handshakes from path-sensitive sequences; emit half-pairs as a table.

**Scores.** N4 U2 P4 C3 E2 Ev3 = 18

**Verdict.** park

**Mutation.** When a repo actually has half-pairs: `--pin protocols.tsv` / `folk check` against a committed protocol file. Kill `--stat` as a default forever. **schism** (caller clusters by protocol halves) only after orphans exist in the wild.

**Evidence.** UNVERIFIED (WAVE2 author 0). DISTINCT: **0 real orphans after honesty filter.** v0.2: sitbone 1 pair 0 orphans (`beginConfiguration`/`commitConfiguration` both paths commit); kizu 2 pairs 0 orphans (`set_var`/`remove_var`, `push_back`/`pop_front`). Toy fixture orphans are planted. Object is sharp; the CI gate is empty. Park, do not kill — the handshake table is not a linter.

---

### Wait / quiescence

Not filters in the `rg |` sense. JSON + wait-source is still a Unix object if it stays small. Do not keep six tools.

#### candidate-21 — spoor

**Primitive.** waitpid is not completion; the *wake* (late writes, leaked children, leftover paths, collisions) is a first-class diffable object.

**Scores.** N5 U4 P4 C3 E2 Ev3 = 21

**Verdict.** keep

**Mutation.** `spoor replay report.json --fail-if late_writes`. Attach is cling. Pipeline wait-source is knot. Do not absorb those.

**Evidence.** UNVERIFIED (WAVE2 author 0). AUTHOR: voidtrace slow FSEvents / pnpm-store false orphans; kizu tests leave no wake.

#### candidate-25 — coast

**Primitive.** The interval between waitpid returning and process-group + watched files becoming still.

**Scores.** N3 U3 P3 C4 E3 Ev2 = 18

**Verdict.** park

**Mutation.** `coast wait` as `sleep 2` replacement is real, and it is a subset of spoor’s wake. Do not evolve in parallel.

**Evidence.** AUTHOR: `TMPDIR` is where tests actually write.

#### mutation-12 — cling

**Primitive.** Attach to a pid you did **not** spawn; SIGINT reports the same wake without killing the subject.

**Scores.** N4 U4 P4 C3 E3 Ev3 = 21

**Verdict.** keep

**Mutation.** Not a flag on spoor. Snapshot of tmux/hermes heap we did not allocate is the point.

**Evidence.** AUTHOR: demo green; kizu exec named; SIGINT leaves subject up. WAVE3: coast/cling as post-waitpid / attach-pid.

#### candidate-22 — pinch

**Primitive.** A pipeline is a conversation of blocking; name who waited for whom, including a hidden child.

**Scores.** N4 U3 P4 C3 E2 Ev2 = 18

**Verdict.** park

**Mutation.** Absorbed by knot. Do not keep a pipeline-only sibling.

**Evidence.** UNVERIFIED (WAVE2 author 0).

#### candidate-23 — hitch

**Primitive.** Wait-for graph of a process tree: OS sleep joined to pipe/socket/fifo/child-wait peers.

**Scores.** N4 U3 P4 C3 E2 Ev2 = 18

**Verdict.** park

**Mutation.** Absorbed by knot.

**Evidence.** UNVERIFIED (WAVE2 author 0).

#### hybrid-02 — knot

**Primitive.** One wait-for conversation spanning pipe meters **and** process tree, walked to a wait-source.

**Scores.** N4 U4 P5 C4 E3 Ev3 = 23

**Verdict.** keep

**Mutation.** Stream JSONL *during* the run so a timeout killer can print the knot. Stacks when the knot is leaf `sleep`. Invert: kill the blocker, not the waiter.

**Evidence.** AUTHOR: argv-wipe, wrap-false-instrument, node→pkl walk that concatenation would have split across pinch and hitch. Sub-200ms pipelines remain noise-floor.

---

### Env ABI / guise

#### candidate-28 — due

**Primitive.** A program has an environment ABI; harvest the names it consults and join two environments on just those names.

**Scores.** N4 U4 P4 C4 E3 Ev2 = 21

**Verdict.** park

**Mutation.** The miss was the image: `PYTHONHOME` lives in libpython. That is lode. due’s `--app src --vs .env` source harvest can stay as a producer for lode.

**Evidence.** AUTHOR: Homebrew `python3` / framework stub: 0 names.

#### mutation-21 — lode

**Primitive.** Env ABI of a program is the env ABI of its **load image set** (`otool -L` / `ldd` + getenv names across those images).

**Scores.** N4 U5 P5 C5 E3 Ev4 = 26

**Verdict.** mutate

**Mutation.** Help-table / runtime-bare extraction stay. `--trace` getenv interposer as a second column (`DUE` vs `LATENT`). Do not scan 70MB libnode by default without a cap.

**Evidence.** AUTHOR: `lode python3` prints `PYTHONHOME` from libpython; `lode rustc` prints `RUSTC_LOG` from `librustc_driver`. WAVE3 names due as `ldd` for getenv; lode is the flipped image.

#### candidate-30 — orbit

**Primitive.** A command name’s guise (PATH bind, rustup/xcselect/shebang payload, this-copy rpath, SIP/DYLD filter). Dump it. Diff it.

**Scores.** N4 U4 P4 C3 E3 Ev3 = 21

**Verdict.** keep

**Mutation.** `--cwd` for rustup toolchain files. Not lode: lode is names; orbit is *which binary will run*.

**Evidence.** AUTHOR: v0.2 harvest matches guise vs payload. Shell functions (`git` as zsh wrapper) are outside the binary orbit.

---

### Generation lots / oracles / occupancy of patches

#### candidate-26 — kiln

**Primitive.** Reconstruct a firing **lot** from artifact claims, generator recipes, and imports; report whether the claim still holds and whether siblings split.

**Scores.** N4 U4 P4 C3 E3 Ev2 = 20

**Verdict.** park

**Mutation.** Convergent with clutch. Vehicle is sinter.

**Evidence.** AUTHOR: real eight-day split in a clean git tree (relico). WAVE3: clutch convergent with kiln.

#### candidate-27 — clutch

**Primitive.** A generated file’s **receipt** (parent, stamp, generator, machine) is testimony; files citing the same parent are a clutch git never recorded.

**Scores.** N4 U4 P4 C3 E3 Ev2 = 20

**Verdict.** park

**Mutation.** Same lot object as kiln, witnessed from receipts. sinter fuses claim+receipt.

**Evidence.** AUTHOR: relico 0/1/4 lag; VoidTrace 28-commit cold sibling. v0.2 dropped `.pnpm-store` flood.

#### hybrid-04 — sinter

**Primitive.** Fuse claim-lot and receipt-lot into one firing; assay RAGGED / STALE / CLEAN with why=content|clock|dirty-parent.

**Scores.** N4 U4 P5 C4 E3 Ev3 = 23

**Verdict.** keep

**Mutation.** `--repair` for STALE members only. Watch `just spec-gen` and show RAGGED→CLEAN. Do not evolve kiln and clutch in parallel.

**Evidence.** AUTHOR: relico eight-day split, tenaoshi headerless JSON lot, VoidTrace 29-commit cold sibling as one command. v0.2 from a dump of 59 pkl paths, not concatenated flags.

#### candidate-29 — yoke

**Primitive.** Spec clause × generated witnesses, polarity taut/slack/hand/split/riven, keyed by clause id, without running the generator.

**Scores.** N4 U4 P4 C3 E3 Ev3 = 21

**Verdict.** keep

**Mutation.** Clause-window riven, not file-wide. Different object from sinter (clause polarity vs firing lot).

**Evidence.** AUTHOR: tenaoshi in-progress rewrite is not just “dirty files.”

#### candidate-31 — lees

**Primitive.** Subtract live env/host dictionary from an oracle so two transcripts compare **modulo substitution**. Empty residue ⇒ the machines differ.

**Scores.** N5 U4 P5 C5 E3 Ev4 = 26

**Verdict.** mutate

**Mutation.** `--visa`: emit the machine condition an oracle implies. Join with alibi (LOCKED-and-MACHINE vs LOCKED-and-SPEC). Parse assertion literals, not comments. `--from-fail` more grammars.

**Evidence.** AUTHOR demo 24/24. `--par` alice vs CI → `verdict=MACHINE`, empty residue. sitbone v0.1 false TAINTED on `annenpolka` in a window-title **fixture**; v0.2 `kind=fixture`, `--check` 0. kizu `--foreign` 46 path oracles, `--check` still 0. Not `diff`, not snapshot serializers.

#### candidate-32 — veil

**Primitive.** Production diff cover-type against tests: LIVE / VEIL (tests only see a mock) / BARE.

**Scores.** N4 U4 P4 C4 E3 Ev3 = 22

**Verdict.** keep

**Mutation.** `git diff | ./veil --diff -`. Public/`export`/`pub` names as the default review object (already the first improvement). Collaborator mock vs SUT veil.

**Evidence.** AUTHOR: soul-writer real VEIL (`vi.mock('./cerebras.js')` hides `formatLastError` / `getRetryAfterMs`). alibi would call a mocked SUT LOCKED.

#### candidate-34 — sate

**Primitive.** A unified diff is before→after image claims; report how a tree occupies each (APPLIED / PENDING / MIXED / DUPLEX / SUPERSEDED).

**Scores.** N5 U5 P5 C5 E3 Ev4 = 27

**Verdict.** mutate

**Mutation.** `sate log --pick SUPERSEDED` as a patch. `--against :` (index). GitHub `suggestion` fences already parse — keep them as hunks, not a second tool. Binary patches stay SKIP.

**Evidence.** AUTHOR demo 31/31. Sandwich invariant: `sate --git C --against C` APPLIED; `--against C^` PENDING. v1 false DUPLEX on pure additions (voidtrace 21, tenaoshi 3) — prefix rule fixed. kizu `--log 8`: v0.6.0 `Cargo.toml` SUPERSEDED (now 0.7.0), one `Cargo.lock` hunk still PENDING. `git apply --check` cannot say that.

---

### Birth cohort

#### candidate-10 — also

**Primitive.** Birth cohort of a line: siblings introduced together that shared distinctive tokens; which still agree, which drifted.

**Scores.** N5 U4 P5 C4 E4 Ev3 = 25

**Verdict.** keep

**Mutation.** Inflection of natal names is erst. also keeps FILE:LINE addressing.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). sitbone leftover `0.4`; fixture `TIMEOUT=60` still-`30` docs/tests.

#### mutation-06 — owe

**Primitive.** Given a commit or a diff (never FILE:LINE), recover every birth cohort that change touches; list unpaid kin at HEAD.

**Scores.** N4 U4 P4 C4 E3 Ev2 = 21

**Verdict.** park

**Mutation.** erst already adds inflection (`t1` ↔ `driftDelay`). owe is the intermediate.

**Evidence.** AUTHOR: `owe e9b0f75` leftover 0.4 tests and docs without naming `PresenceArbiter.swift:33`.

#### mutation-19 — erst

**Primitive.** Cohorts of a change, natal keys as identities that **inflect**, so renamed siblings still count as unpaid kin.

**Scores.** N5 U5 P5 C4 E3 Ev4 = 26

**Verdict.** mutate

**Mutation.** Rename-follow via `git log -L`. Domain tags so `0.4`-threshold ≠ `0.4`-opacity. `--pr`: `gh pr diff | erst -`.

**Evidence.** WAVE3: erst shipped. AUTHOR: `erst e9b0f75` leftover `threshold` *and* `0.4` without a FILE:LINE; `erst 1fcdec6` leftover `T1`/`T2` from a lint SHA. aka does not pair `t1`↔`driftDelay`. owe is silent when the number did not move.

---

## What not to spend Gen-3 slots on

1. **Leftover-name search.** haunt is dead. wisp remnants are dead. wraith is the spare. zanei is claims, not names.
2. **A second inverse-printf walker.** Bakeoff closed this. invert + optional `rg` producer.
3. **Folk as a linter.** 0 real orphans. Park.
4. **NIGH string distance.** cusp owns the cut.
5. **Pinch ∥ hitch ∥ knot.** knot is the wait-source.
6. **Kiln ∥ clutch ∥ sinter.** sinter is the fused lot.
7. **Similarity merge-bases.** once’s exact blob, akin `--port` only.
8. **Platforms, LSPs, dashboards.** Filters, exit codes, TSV.

---

## Suggested Gen-3 pipes (composition, not winners)

```
git diff A B | zanei --diff - -C repo
git diff | sic --check
rg -n --type rust 'format!|anyhow!' repo | invert --templates - 'paste'
tell -C repo A B --held | perch -C repo
when file.rs:60          # stack
under --kind given 'a/'  # invert
chime file.rs:60         # rhyme
pin mint --from SHA file:line | pin resolve --to HEAD
flume --from-dir old --to-dir new < ci.log
sate --git HEAD --against HEAD
sow f --emit json |  # fixture worlds
lees --par local.snap ci.snap
cinch -- pytest
doze --check insert_scar
cusp --offby --format tsv src | cut -f1,2,3,6,10
lode python3
erst HEAD
```

Sixteen vehicles. Several clusters. Haunt dead. Folk parked. No single winner before Generation 3.
