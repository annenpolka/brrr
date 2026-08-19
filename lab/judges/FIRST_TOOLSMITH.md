# Toolsmith Judge — first selection

Source: first-selection critic on 2026-08-20. Axis of record is **utility**: would a real developer type this tomorrow, on a dirty tree, without being reminded?

Does not collapse to one winner. Does not rank by polish. Other judges (DISTINCT, GHOST_CLUSTER, UNFMT_BAKEOFF, DESTROYER_PIN_INVERT) are taken as evidence, not as a ranking to rubber-stamp.

Scores are 0–5 integers: Novelty / Utility / Primitive / Composability / Empirical / Evolution. A 4+ on Empirical requires a run, not a README. This session re-ran a cheap subset of `./demo.sh` from the worktrees; the rest cite parent/author transcripts.

## The question

A toolsmith keeps a verb that collapses a recurring loop into one command. Ghost-name search, occupancy eras, and inverse-printf are allowed to be strange **if they already paid rent** on kizu / sitbone / tenaoshi / voidtrace. Clones of a paid-rent primitive are not extra survivors.

---

## Carry on PATH (would run tomorrow)

Twelve verbs. Not one product. Each is a different object.

| # | tool | id | primitive | why tomorrow |
| --- | --- | --- | --- | --- |
| 1 | **invert** | mutation-15 | inverse printf as a filter: paste → template + named holes + span leftover | every error/log paste |
| 2 | **slip** | candidate-16 | rewrite stale `file:line` by fingerprint | last night's CI log after a split |
| 3 | **winnow** | candidate-15 | ddmin uncommitted hunks against a command | "which of these 12 dirty hunks made it red?" |
| 4 | **when** | candidate-20 | path-condition + fallthrough `given` at `file:line` | reading a nested return |
| 5 | **zanei** | candidate-07 | leftover *claims* a diff just made false | after a rename / bound-value flip |
| 6 | **reverb** | candidate-04 | preimage of this diff as a search query | after a one-line fix, other copies |
| 7 | **sic** | mutation-01 | exact wire-key pact; one-sided patch fails | `git diff \| sic --check` |
| 8 | **due** | candidate-28 | env ABI of a program vs `.env` / process | missing `KIZU_*` / `TMUX` |
| 9 | **sate** | candidate-34 | hunk occupancy APPLIED/PENDING/MIXED/DUPLEX/SUPERSEDED | review suggestion already taken? |
| 10 | **zure** | mutation-05 | identifier conflict: recent history ⋈ dirty tree | pre-commit, no second branch |
| 11 | **held** | candidate-09 | occupancy *eras*, not one bisect cut | sitbone `FocusRiverView` is invisible to `git log -- path` |
| 12 | **cinch** | hybrid-03 | 1-minimal *production* hunks the current tests veto | lockset ≠ fingerprint (debug print is chaff) |

Lineage vehicles next to those, not extra PATH entries: **flume** (slip as gitless log filter), **pin** (slip as a durable token), **stencil** (one-shot walker spare for invert), **aka** (sic's inflection *listing*), **doze** (unseen as `--check` on signatures).

---

## Preserve (strange, already paid rent)

Do not kill these because they are not "everyday grep." They already answered a question git/coverage/blame cannot phrase on the dogfood trees.

| tool | rent |
| --- | --- |
| **held** / **dwelt** | sitbone `FocusRiverView.swift`: `git log -- path` empty; `--full` TRUE 11 commits then deleted. kizu `CLAUDE.md` birth is a merge on first-parent. |
| **slip** / **pin** | kizu `src/app.rs:529` → `src/app/layout.rs:17` (this session). Unique `seen_hunk_fingerprint` pin does not hallucinate onto voidtrace/tenaoshi (DESTROYER). |
| **invert** | sitbone 7-hole Logger binds names; camera nested quotes bind; kizu timestamp is a *span*. Live this session: `failed to spawn \`git apply --reverse\`` → `src/git/revert.rs:46`. |
| **aka** / **sic** | tenaoshi `has_more`/`hasMore` across spec/code/docs; kizu `hook_event_name`; sitbone `awayRecovered`. |
| **erst** / **also** | sitbone `e9b0f75` leftover `0.4` / `threshold` after hysteresis, nobody named `PresenceArbiter.swift:33`. |
| **sow** / **cleave** | sitbone six untested production browser names; kizu four terminal backends as pytest stubs. |
| **sinter** | relico unit/e2e oracles eight days behind a clean tree; tenaoshi 39-member lot `RAGGED why=dirty-parent`; voidtrace ages 0–29. |
| **zure** | live tenaoshi dirty tree: `ContractCase` deleted in work, still constructed in oracles/`specs/tenaoshi.pkl`. |
| **reverb** | tenaoshi one header-line fix, two adapters still `Content-Type`. |
| **winnow** / **glean** / **cinch** | tenaoshi 108-file dirty overlay; cinch drops the debug-print wheat that winnow keeps. |
| **perch** | skills `preact-zero-mock` last 16 commits are README-only; `held` boolean occupancy lies. |
| **stint** | wisp occupancy without remnant-name search; `--pick` restores `circuit-breaker/`. |
| **cusp** | nigh's only leftover that is a Unix column: constructed value on a predicate cut (401/400, suffix(2), `.unknown`). |
| **moor** | kizu CI log is simultaneously a file-split *and* an inverse-printf; one pass. |
| **coast** | `sleep 2` replacement; TMPDIR is where the tests actually write. |
| **knot** | one wait-for conversation over pipe meters ∩ process tree (pinch×hitch, not concatenation). |

---

## Clone kills

Kill the *product*. Harvest the one fact they proved.

| kill | clone of | why |
| --- | --- | --- |
| **haunt** | wraith | worse leftover-name join; lost skills `preact-zero-mock`. GHOST_CLUSTER already killed it. |
| **wisp remnants** | wraith | interval-ephemeral *files* survive as **stint**; leftover *names* are wraith. Do not ship both searches. |
| **unfmt-13** | invert / stencil | named holes harvested into invert; walker slower and noisier on kizu. UNFMT_BAKEOFF. |
| **unfmt-08** as a product | stencil | same one-shot walker. Stencil beats original on sitbone `camera presence enabled`. Keep stencil as the spare `-C`, not two ignore policies. |
| **sluice** as a product | invert | the stream assumption is invert's. Invert adds names + span. |
| **nigh** | cusp | firehose of string-distance; cusp is the cut. |
| **akin** similarity `--port` | once | invented merge-bases. DISTINCT: keep `--port` only on exact blob. |
| **pinch**, **hitch** as products | knot | same wait-for object; knot is the smaller report. |
| **kiln**, **clutch** as products | sinter | convergent generation-lots. sinter is the fused assay (RAGGED/STALE/CLEAN × content/clock/dirty-parent). |
| **yoke** | sinter | clause-shaped join on the same spec-gen repos. |
| **orbit** | due / lode | guise vs payload vs SIP is a footnote on `due --vs-program`, not a second ABI tool. |
| **skew** | doze / unseen | file-clock coarseness *is* the miss (tenaoshi `writeBack`). doze is the CI form. |
| **veil** | — | mock cover-type. Would not run tomorrow; coverage+grep already nibble LIVE/BARE. |

---

## Park (not kill, not PATH)

Empty or rare on the four dogfood trees, or a mutation that should not occupy a Gen-2 slot.

| park | note |
| --- | --- |
| **folk** | honesty filter: 0 keepers on skills / voidtrace / tenaoshi. DISTINCT parked it. Do not spend slots on handshake mining. |
| **once** | exact blob kinship is the right akin. 0 kin on kizu / sitbone / voidtrace / tenaoshi (the interesting splits never committed an identical blob). Hits `SKILL.md` clones elsewhere. `--port` stays; do not re-implement copy search. |
| **lees** | oracle-as-substitution is a real object; sitbone "taint" was the author's GitHub handle used as fixture data. Niche until `--par` on two CI transcripts. |
| **alibi** | tests@NEW × prod@OLD is real; **cinch** is the hunk lockset a reviewer actually wants. Keep the splice idea inside cinch. |
| **rift** | two-branch identifier conflicts. Daily form is **zure** (dirty vs recent history). Keep rift for `main...HEAD` on actually diverged branches, not as a second pre-commit. |
| **wraith** | one leftover-*name* survivor. Archaeology, not a daily filter. zanei is the post-diff verb. |
| **under**, **chime** | same condition-stack as **when**. Inverse/same-as are flags, not PATH entries. |
| **owe** | commit-shaped also; **erst** inflects natal keys. Carry erst. |
| **cleave** | diagnostic of **sow**. Carry sow (`--emit pytest`). |
| **lode** | due on the load-image set (`python3` → `PYTHONHOME` in libpython). Next hour on due, not a sibling CLI. |
| **spoor**, **cling** | coast `wait` is the daily `sleep 2`. Attach-pid is a flag. |
| **dwelt** | clean-room reimpl of held. Evidence the primitive is real; do not ship two occupancy CLIs. |
| **glean** | file-grain + untracked winnow. Keep as `--grain file` on winnow if a slot opens. |
| **tell** | inverse of held (two trees → shortest predicate). Mutation of held, not PATH. |
| **perch**, **stint**, **cusp**, **moor**, **coast**, **knot** | preserved above; mutate in place, do not duplicate. |

---

## Per-candidate scores

`Σ` is unweighted. **Keep decisions follow Utility first**, then Primitive. Novelty does not save a clone.

Legend: K = keep/PATH, P = preserve/mutate, KILL, PARK.

### Inverse printf

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-15 | invert | 4 | 5 | 5 | 5 | 5 | 4 | 28 | **K** | runtime string on one channel, templates on the other; named holes; leftover prefix is a span |
| reimpl-01 | stencil | 3 | 4 | 5 | 4 | 5 | 3 | 24 | **P** | same invert of a *tree*; walker spare; nested Swift quotes beat unfmt-08 |
| hyb-01 | moor | 4 | 4 | 4 | 5 | 4 | 4 | 25 | **P** | one pass: stale locator *and* format holes corroborate |
| cand-08 | unfmt | 4 | 4 | 5 | 4 | 5 | 2 | 24 | KILL product | one-shot `-C` ancestor; harvest ignore policy into `rg \| invert` / stencil |
| cand-13 | unfmt | 4 | 3 | 4 | 3 | 4 | 2 | 20 | KILL | named holes already in invert; slower walker |
| mut-02 | sluice | 4 | 4 | 4 | 5 | 5 | 2 | 24 | KILL product | stream assumption; invert is the vehicle |

Mutate invert: prefix-of-a-holed-template; no-hole prefix must not outrank a binding; refuse rustc grammar; `--any` must stop printing (DESTROYER). Do not grow a walker.

### Relocatable locus

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-16 | slip | 4 | 5 | 5 | 5 | 5 | 4 | 28 | **K** | `file:line` is relocatable by content fingerprint, not blame |
| mut-04 | flume | 4 | 5 | 5 | 5 | 4 | 4 | 27 | **P** | the log is the object: stdin locators → stdout locators, two directories, no git |
| mut-14 | pin | 5 | 4 | 5 | 4 | 5 | 5 | 28 | **P** | the object is the token; `resolve` refuses `path:line` |

Mutate pin (DESTROYER, do not rewrite now): ambiguous ≠ 1.000 twice; leftover stub at the old path must lose to neighbor body; missing `--to` ref is not `deleted`; truncated `pin1.` fails closed. Mutate flume: rustc gutter carry is already the proof the stream is real.

### Dirty tree / tests as lock

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-15 | winnow | 4 | 5 | 5 | 5 | 5 | 4 | 28 | **K** | smallest hunk set that reproduces a command fingerprint |
| hyb-03 | cinch | 4 | 5 | 5 | 4 | 4 | 4 | 26 | **K** | smallest *production* hunks the current tests veto; tests never wheat |
| mut-07 | glean | 3 | 4 | 4 | 5 | 4 | 3 | 23 | PARK→flag | file grain + untracked units; `--format drop` |
| cand-24 | alibi | 4 | 3 | 4 | 3 | 4 | 3 | 21 | PARK | tests@NEW on prod@OLD; file grain of cinch |

Mutate winnow: default fingerprint that does not need `PYTHONDONTWRITEBYTECODE`. Mutate cinch: detect empty suite (already EMPTY≠BROKEN); `--base origin/main`.

### Occupancy / time as intervals

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-09 | held | 5 | 4 | 5 | 5 | 5 | 4 | 28 | **K** | contiguous eras a predicate held; not one bisect cut |
| reimpl-02 | dwelt | 2 | 4 | 5 | 5 | 5 | 2 | 23 | PARK | clean-room held; named kizu merge-birth `e1098c8` |
| mut-03 | tell | 4 | 4 | 5 | 5 | 4 | 4 | 26 | **P** | two trees in, shortest distinguishing predicate out |
| mut-17 | perch | 4 | 3 | 5 | 4 | 4 | 4 | 24 | **P** | occupancy splits when the *witness set* changes |
| mut-18 | stint | 4 | 3 | 4 | 4 | 4 | 4 | 23 | **P** | born-and-killed occupancy + `--pick` last blob; no remnant search |

Mutate held: first-parent merge-birth should name the feature commit (dwelt already did). Mutate perch: default for `grep` queries; `--boolean` is the ancestor.

### Path-condition

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-20 | when | 4 | 5 | 5 | 5 | 4 | 4 | 27 | **K** | nested predicates still in force at a locus, including `given` |
| mut-10 | under | 3 | 3 | 4 | 5 | 3 | 3 | 21 | PARK→flag | name a condition, emit the lines |
| mut-16 | chime | 3 | 3 | 4 | 4 | 3 | 3 | 20 | PARK→flag | other loci with the same (or prefix-superset) stack |

Mutate when: `--same-as` (chime), post-image diff, `--explain` default on a tty. Live `layout.rs:17` / `PresenceArbiter.swift:33` are depth=0 (headers); the rent is nested returns, which the fixture demo showed.

### Wire keys / inflection

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-01 | sic | 4 | 5 | 5 | 5 | 4 | 3 | 26 | **K** | exact serialized wire key; inflection is a fork |
| cand-02 | aka | 4 | 4 | 5 | 5 | 5 | 3 | 26 | **P** | one identity across `has_more` / `hasMore`; list + `--check` |

Mutate sic: identifier inflection of natal names is erst's job, not sic's. Keep the exact-key check boring.

### Leftovers (not one ghost)

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-07 | zanei | 5 | 5 | 5 | 5 | 4 | 4 | 28 | **K** | leftover *facts* (bound value / rename / polarity) after a diff |
| cand-04 | reverb | 4 | 5 | 5 | 5 | 5 | 4 | 28 | **K** | the preimage of this change, elsewhere |
| cand-06 | deja | 4 | 3 | 4 | 4 | 4 | 3 | 22 | **P** | RELAPSE / UNDOFIX / RESURRECT vs the repo's own memory |
| cand-12 | wraith | 3 | 3 | 4 | 4 | 4 | 3 | 21 | PARK | dead defs, living mentions in the untyped fringe |
| cand-05 | haunt | 2 | 2 | 3 | 3 | 4 | 1 | 15 | KILL | worse wraith |
| cand-03 | wisp | 3 | 2 | 3 | 3 | 4 | 2 | 17 | KILL remnants | occupancy → stint |

Mutate zanei: stay a filter (`diff in → claims out`). Mutate reverb: identifier-renamed clones without becoming a second jscpd. Mutate deja: kill `fix` regex matching `fixed pellet`.

### Semantic merge / use-site lag / birth cohort

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-05 | zure | 4 | 5 | 5 | 4 | 4 | 4 | 26 | **K** | identifier conflicts of *yourself* vs recent history |
| cand-11 | rift | 4 | 3 | 4 | 4 | 4 | 3 | 22 | PARK | same join on two committed changesets `git merge` would accept |
| cand-14 | unseen | 4 | 4 | 5 | 4 | 4 | 3 | 24 | **P** | definition as last seen by this use-site, diffed against HEAD |
| mut-20 | doze | 3 | 5 | 5 | 5 | 4 | 3 | 25 | **P** | `--check` if any use-site last saw a different *signature* |
| mut-08 | skew | 3 | 3 | 3 | 4 | 4 | 2 | 19 | PARK | file mtime/commit clock; the coarseness is the miss |
| cand-10 | also | 4 | 4 | 5 | 4 | 4 | 3 | 24 | **P** | birth cohort of a `FILE:LINE` |
| mut-06 | owe | 3 | 4 | 4 | 4 | 3 | 3 | 21 | PARK | birth cohort of a commit/diff |
| mut-19 | erst | 4 | 4 | 5 | 4 | 5 | 4 | 26 | **P** | owe + natal keys inflect (`t1`↔`driftDelay`) |

Mutate zure: `--staged -q` as the CI path; replay on squash-merge history is not the product. Mutate doze: compiled callers vs plan-file mentions without bringing ranking back.

### Argument worlds / generation lots / env / patch occupancy

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-13 | sow | 4 | 4 | 5 | 4 | 5 | 4 | 26 | **P** | production argument worlds minus what tests pin, as generator input |
| cand-18 | cleave | 4 | 3 | 5 | 3 | 4 | 3 | 22 | PARK | same inhabitance join, as a tilt report |
| hyb-04 | sinter | 4 | 4 | 5 | 4 | 5 | 4 | 26 | **P** | recipe lot ⋈ colophon receipt → RAGGED/STALE/CLEAN |
| cand-26 | kiln | 4 | 3 | 4 | 3 | 4 | 2 | 20 | KILL product | lot from claims; fused into sinter |
| cand-27 | clutch | 4 | 3 | 4 | 3 | 4 | 2 | 20 | KILL product | clutch from receipts; fused into sinter |
| cand-29 | yoke | 3 | 3 | 3 | 3 | 3 | 2 | 17 | PARK | clause polarity on the same spec-gen world |
| cand-28 | due | 4 | 5 | 5 | 5 | 5 | 4 | 28 | **K** | owed env names with evidence, joined to an env file / image |
| mut-21 | lode | 3 | 4 | 4 | 4 | 3 | 3 | 21 | PARK→due | owed names of the *load image set* |
| cand-30 | orbit | 3 | 3 | 3 | 3 | 4 | 3 | 19 | PARK | guise vs payload vs this-copy rpath vs SIP |
| cand-34 | sate | 4 | 5 | 5 | 5 | 5 | 4 | 28 | **K** | a hunk's two images as occupancy, not `git apply --check` boolean |

Mutate due: dylib walk (lode) as `--images`. Mutate sate: GitHub suggestion extract is already the review object; keep it a filter.

### Wait / near-cut / kinship / other

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-25 | coast | 3 | 4 | 4 | 5 | 4 | 3 | 23 | **P** | interval after waitpid until the machine is still |
| hyb-02 | knot | 4 | 4 | 4 | 4 | 4 | 3 | 23 | **P** | one wait-for conversation, pipe meters ∩ process tree |
| cand-21 | spoor | 3 | 3 | 4 | 4 | 4 | 3 | 21 | PARK | wake after quiescence as a diffable object |
| mut-12 | cling | 3 | 3 | 4 | 4 | 3 | 3 | 20 | PARK | attach to a pid you did not spawn |
| cand-22 | pinch | 3 | 3 | 4 | 4 | 4 | 2 | 20 | KILL product | pipeline blocking conversation → knot |
| cand-23 | hitch | 3 | 3 | 4 | 4 | 4 | 2 | 20 | KILL product | process-tree wait-for graph → knot |
| mut-11 | cusp | 4 | 3 | 4 | 4 | 4 | 3 | 22 | **P** | constructed values on a predicate cut |
| cand-17 | nigh | 3 | 2 | 3 | 3 | 3 | 1 | 15 | KILL | distance field of literals vs cuts; firehose |
| cand-01 | akin | 3 | 2 | 3 | 3 | 4 | 2 | 17 | KILL | similarity merge-base for `--port` |
| mut-09 | once | 3 | 2 | 4 | 4 | 4 | 2 | 19 | PARK | exact blob identity as kin; empty on the four dogfood trees |
| cand-19 | folk | 4 | 1 | 3 | 3 | 3 | 1 | 15 | PARK | unwritten call-pair handshakes; 0 keepers after the honesty filter |
| cand-31 | lees | 4 | 2 | 4 | 3 | 4 | 3 | 20 | PARK | oracle compared modulo host substitution |
| cand-32 | veil | 3 | 2 | 3 | 3 | 3 | 2 | 16 | KILL | LIVE/VEIL/BARE cover-type of a production diff |

---

## Suggested mutations (only for K / P)

Do not spend Gen-2 slots re-implementing ghost-name search, a second unfmt walker, or handshake mining.

1. **invert** — truncated-log prefix of a holed template; ranking so a no-hole prefix cannot beat a binding; binary stdin refuse (DESTROYER). Optional producer wrap (`rg -n \| invert`), not a walker.
2. **slip / flume** — pinfile of locators rewritten on HEAD movement (kizu scar-review companion). Gutter carry is already in flume.
3. **pin** — ambiguous status; stub-at-old-path loses; NFC paths; truncated token fails closed.
4. **winnow / cinch** — cinch `--base origin/main` as the PR verb; winnow `--grain file` eats glean.
5. **held** — harvest dwelt's merge-birth naming; perch `--witness` as the grep default.
6. **when** — `--same-as` / `--under` flags rather than three CLIs.
7. **zure** — `--staged -q` hook; ignore hunk-header ghosts.
8. **due** — `--images` (lode) so `python3` prints `PYTHONHOME`.
9. **erst** — `git log -L` locate + rename-follow; `erst HEAD` as the review companion to zanei.
10. **sow** — `--emit` for the language under test, not only pytest stubs.
11. **sinter** — `--check` in spec-gen CI (relico already fails content-RAGGED on a green tree).
12. **doze** — `doze --check insert_scar` on kizu as the poster CI; drop body ranking forever.
13. **sate** — stdin GitHub review JSON → TAKEN/OPEN table.
14. **coast** — `coast wait -- cmd` as the documented `sleep 2` replacement; knot for "where's it wedged?"

---

## Evidence of run (this session)

All from worktrees under `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/`. Originals not mutated.

| tool | command | result |
| --- | --- | --- |
| when | `./demo.sh` | PASS (18 unit + nested/`given`/Rust match/Swift guard) |
| zanei | `./demo.sh` | PASS 24/24 |
| winnow | `./demo.sh` | PASS (hunk split, pycache, nested git, restore) |
| slip | `./demo.sh` | PASS including **kizu `src/app.rs:529` → `src/app/layout.rs:17` score 0.919** |
| invert | `./demo.sh` | PASS 46/46 including kizu/voidtrace/sitbone/tenaoshi + 7-hole + camera |
| aka | `./demo.sh` | PASS; tenaoshi `has_more`, kizu `hook_event_name`, sitbone `away_recovered`, skills `input_summary` |
| sate | `./demo.sh` | PASS 31/31; sandwich HEAD=APPLIED / parent=PENDING on kizu, sitbone, voidtrace, tenaoshi, relico |
| due | `./demo.sh` | PASS 47/47; kizu source⋈image `KIZU_CONFIG` / packed `ZELLIJ` |
| cinch | `./demo.sh` | PASS; lockset wheat is the return hunk, winnow wheat includes the debug print |
| sinter | `./demo.sh` | PASS 38/38; relico RAGGED why=content; tenaoshi dirty-parent 39 members; voidtrace ages 0–29 |
| held | `./demo.sh` | PASS 33/33; sitbone `git log -- path` empty, `--full` 11 TRUE commits |
| reverb | `./demo.sh` | PASS; tenaoshi leftover `Content-Type` in two adapters |
| doze | `./demo.sh` | PASS; `--check` exit 1 on signature lag, exit 0 on body-only `trim` |
| sow | `./demo.sh` | PASS; sitbone 6 due browser members; kizu 4 `run_split_command` contexts |
| erst | `./demo.sh` | PASS; sitbone `e9b0f75` leftover `0.4`/`threshold`; `1fcdec6` leftover `T1`/`T2` |

Live probes (not demos):

```
$ invert --templates - -e 'failed to spawn `git apply --reverse'`   # rg on kizu
kizu/src/git/revert.rs:46:18  score=1.06  tmpl: failed to spawn `git apply --reverse`

$ due --app kizu/src
MISSING  KITTY_LISTEN_ON / KIZU_CONFIG / KIZU_STATE_DIR / ZELLIJ   evidence=call
DUE      TMUX   /private/tmp/tmux-501/…

$ pin mint --repo kizu src/app/layout.rs:17
pin1.eNptkN1K…     # token minted

$ when --repo kizu --explain src/app/layout.rs:17
here   pub fn seen_hunk_fingerprint(    engine braces  depth=0
```

UNVERIFIED this session (cite parent/author, Empirical still 4 where parent already PASS): flume, zure, rift, unseen, wraith, tell, perch, stint, cusp, knot, coast, sluice, stencil, pin `./demo.sh` (mint live only), glean, lode, folk, haunt, nigh, once, akin, veil, lees, yoke, orbit, alibi, under, chime, owe, cling, hitch, pinch, kiln, clutch, wisp, deja, dwelt.

---

## What this judge is not doing

- Not picking a single winner. Invert is not "the" tool. Winnow is not "the" tool. The night produced **several Unix verbs**.
- Not grading polish. cinch's CLI is younger than unfmt-08 and still PATH, because the lockset object is the one a reviewer wants.
- Not keeping two walkers, two leftover-name miners, two wait-graph CLIs, or two generation-lot CLIs.
- Not killing held / pin / perch / stint / cusp / sow / sinter for being strange. They already paid rent.

Next hour: mutate the PATH twelve in place. Do not invent a thirteenth leftover-name search.
