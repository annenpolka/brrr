# FINAL_UNIX — 08:20 JST Unix Judge (final jury)

Judge: **judge-01**. Clock window: 2026-08-20 08:20–08:40 JST. Isolated worktree only. Did not merge to main. Did not rewrite tools. Did not implement a CLI.

Values: **tiny orthogonal primitives and composition**. Prefer stdin/stdout filters, exit codes, TSV/JSON, one verb. Hate wrappers, walkers, kitchen-sink CLIs, occupancy dashboards, and “mint a token into a ticket.” Do not rank by polish, LOC, README length, or UI.

This ranking is **independent**. FIRST_UNIX (03:00) is a prior cut, not a template to rubber-stamp. Gen-2 vehicles, destroyers, and Gen-3 peels changed which objects still deserve a PATH slot.

Axes (0–5 integer). A 4+ on Empirical requires execution evidence, not README claims. Σ is a diagnostic, not the ranking key.

| code | axis |
| --- | --- |
| N | Novelty |
| U | Utility |
| P | Primitive strength |
| C | Composability |
| E | Empirical credibility |
| Ev | Evolution potential |

This session **sampled** CANDIDATEs and destroyer transcripts; it did not re-run every `./demo.sh`. Empirical 4+ cites DESTROYER / bakeoff / parent harvest / author transcripts that themselves executed.

Read (sample, not every lineage): Master Prompt Final Jury; `lab/JUDGE_RUBRIC.md`; `lab/judges/FIRST_UNIX.md`; `lab/STATE.md` vehicles; DESTROYER_* for pin/invert, cinch, scarp, plait, berth, lien, tacit, beck, xref, weld, keel, gist, peal, maiden, zanei, assay, occupancy; CANDIDATEs of invert, cinch 0.3, ambit, scarp, plait, berth, lien, weld, keel, xref, tacit, beck, maiden; Gen3 peels lurch → solder.

---

## Stance

The night still produced too many *join-history-to-the-living-tree* walkers and too many second verbs glued onto a good first verb. The Unix cut did not change:

> **one object, one verb, a stream if possible.**

What *did* change after 03:00: several mutations actually flipped the buried assumption (walker → stream, spawn → two cuts, `git apply --check` boolean → occupancy, leftover *name* → leftover *claim*, env-shaped bytes → getenv proof). Several others spent Gen-3 **peeling the same object** (pin origin, berth roost, lien noun, weld proving-string, occupancy lattice) until the primitive was a policy engine.

Rank the **object**. Peels are mutations, not extra PATH entries. Do not keep two inverse-printf walkers. Do not keep weld and invert as two nightly habits — they are siblings, not clones, and invert is the one I type. Do not keep under *and* ambit *and* peal *and* seed as four products. Do not keep pin *and* keel *and* shoal. Do not keep cinch *and* tock *and* snug.

Haunt stays dead. Folk stays parked. No single winner.

---

## Ranked survivors (top 8)

Eight **different objects**. Pipe them; do not merge them.

| # | object | vehicle | N | U | P | C | E | Ev | Σ | why Unix |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | inverse printf + named holes + span | **invert** (mutation-15) | 5 | 5 | 5 | 5 | 5 | 4 | 29 | `rg \| invert`; no walker |
| 2 | which clock explains the gap | **scarp** (mutation-46) | 5 | 4 | 5 | 5 | 5 | 4 | 28 | two cuts in, name out; **no spawn** |
| 3 | leftover *claims* a diff made false | **zanei** (candidate-07) | 5 | 5 | 5 | 5 | 4 | 3 | 27 | `git diff \| zanei`; linter exit |
| 4 | 1-minimal production lockset | **cinch 0.3** (mutation-48) | 5 | 5 | 5 | 4 | 5 | 3 | 27 | one verb; tests stay NEW; patch out |
| 5 | path-condition invert as a file stream | **ambit** (mutation-35) | 4 | 5 | 5 | 5 | 4 | 3 | 26 | `rg \| ambit`; no cwd walk |
| 6 | composition algebra of suggestion strands | **plait** (candidate-38) | 5 | 3 | 5 | 5 | 4 | 4 | 26 | JSONL in; COMMUTE/JAM; exit 0/1/2 |
| 7 | hunk occupancy vs a tree | **sate** (candidate-34) | 5 | 4 | 5 | 4 | 3 | 3 | 24 | SUPERSEDED is a noun `git apply --check` lacks |
| 8 | path-condition stack at a locus | **when** (candidate-20) | 5 | 4 | 5 | 4 | 5 | 2 | 25 | question-word; `file:line` → stack |

Σ is not the order. **when** outranks **sate** on evidence and still sits at 8 because ambit already is the composable invert of the same object — when is the named-line mouth, kept because the object is a stack, not a grep. **plait** outranks tools I would type more often because the algebra is a real Unix object (stream + exit codes) and braid/tilde are the occupancy that would ruin it.

---

### 1. invert — mutation-15

**Primitive.** Runtime string on argv/stdin, templates on the other channel; bind names; leftover prefix is a **span**. No implicit walk.

**Scores.** N5 U5 P5 C5 E5 Ev4 = 29. **Keep (the filter).**

**Why this rank.** Still the night's best Unix tool. `rg -n --type rust 'format!|anyhow!' | invert 'paste'` is the composition that killed `-C`. Named holes and span are the payload sluice threw away. Concat is a **sibling** (weld), not a patch on this kernel.

**Mutation (do not spend another walker).** Binary stdin fail-closed (DESTROYER: `UnicodeDecodeError` on urandom). Prefix-of-holed-template must not lose to a no-hole decoy. `--any` stops printing. Refuse rustc grammar.

**Evidence.** BAKEOFF 5/5. WAVE3 46/46. DESTROYER_PIN_INVERT: 7-hole sitbone still binds; truncated logs miss; documentation decoy vs holed template. `lab/lineages/mutation-15__invert/CANDIDATE.md` — kizu timestamp is a span (`prefix: 2026-08-19T23:50:01Z ERROR`); sitbone camera nested quotes bind `{self.isCameraEnabled}=enabled`; `awayRecovered` 7 holes score 1.10. PARENT/WAVE3 executed.

Ev 4 not 5: concat harvested into weld; remaining holes are fail-closed, not a new object.

---

### 2. scarp — mutation-46

**Primitive.** Two timestamps or two clock-cuts on stdin; emit which clock explains the gap (`SLEEP` / `DILATE` / `STEP` / `REST`). **No spawn.**

**Scores.** N5 U4 P5 C5 E5 Ev4 = 28. **Keep (clock-cut).** Stream form: **lurch** (honorable).

**Why this rank.** FIRST_UNIX never saw this. Ancestor `lapse` wrapped a command (`Popen` / `wait4`). scarp flipped the assumption: the shell sandwiches work; a logger already has the readings; `{ ./scarp cut; sleep 0.35; ./scarp cut; } | scarp` is **DILATE without scarp forking sleep**. That is a Unix filter. `time(1)` names wall. scarp names the disagreement.

**Mutation.** Classify **every adjacent pair** (that is lurch). Repeated `key=value` must keep both timestamps of that key (DESTROYER: interleaved `wall=0 / wall=10` is REST of wall only). `ntp=` is adjtime slew, not NTP — rename or add SLEW (yaw already named it). Do not wrap `sleep`.

**Evidence.** DESTROYER_SCARP: `{cut; sleep 0.35; cut} | scarp` still DILATE without spawn; `fixtures/slew.txt` still SLEEP not STEP; wall+python.monotonic since boot still SLEEP not a 29-hour NTP step. Victim `./scarp` executed. `lab/lineages/mutation-46__scarp/CANDIDATE.md`. Gen3 **lurch** on the same JSONL emits DILATE then SLEEP; ancestor scarp emitted DILATE only (`lab/lineages/mutation-103__lurch/CANDIDATE.md`).

This is the largest FIRST_UNIX miss. It would have been a Gen-3 vehicle at 03:00.

---

### 3. zanei — candidate-07

**Primitive.** A unified diff mints facts (bound name/value, rename, polarity). Print dest lines that still assert the old fact. Exit 0 clean, 1 leftovers, 2 error.

**Scores.** N5 U5 P5 C5 E4 Ev3 = 27. **Keep (claims filter).**

**Why this rank.** `git diff A B | zanei --diff -` is the leftover object that is **not** a ghost-name search. kizu `Cargo.toml` 0.3.0→0.7.0 still claimed by `plugin.json` `"version": "0.3.0"` is the “why doesn’t this exist?” moment. lien/noun walk the dest tree as a natal **gate**; they are CI clothing on this object plus erst. Unix keeps the filter.

**Mutation.** Quoted JSON keys are facts (nagori). Stem match token-bounded. Binary stdin / `--diff FILE` fail closed. Do not become a review platform. Do not merge with lien.

**Evidence.** PARENT PASS (`lab/SHIPS.md`). DESTROYER_ZANEI: mutate both zanei and nagori, do not kill; Cargo.toml→plugin.json survived; JSON silence is a grammar. sitbone hysteresis leftover `threshold 0.4` in CLAUDE.md. GHOST_CLUSTER: strongest leftover, not a ghost.

---

### 4. cinch 0.3 — mutation-48

**Primitive.** Dirty tree vs `--base`. Tests stay at NEW. Wheat is the 1-minimal **production** subset the current command requires. Predicate is pass/fail, not fingerprint. NEW always runs. Timeout is unknown, not fail.

**Scores.** N5 U5 P5 C4 E5 Ev3 = 27. **Keep (lockset).** No fourth cinch. tock/snug are transcripts, not PATH.

**Why this rank.** Not a `rg |` filter. It is still Unix: one verb, a predicate, patch on stdout, exit codes, user tree never rewritten. `git bisect` has no uncommitted-hunk object. winnow’s wheat includes `print("debug")`. cinch’s wheat is `return a + b`. That split is the object.

C4 not C5: it owns isolation. You do not pipe rg into it. You type `cinch -- pytest`.

**Mutation.** Always-run-NEW and timeout≠fail already landed in 0.3. Coverage hint before isolation. `--commit-wheat`. Do not recover lockset by `alibi --per-path` then winnow.

**Evidence.** DESTROYER_CINCH: mutate, do not kill; debug-print vs return still disagrees with winnow; binary stdout fail-closed. LOCKSET_BAKEOFF: cinch 0.3 **4/4** on destroyer fixtures (debug-print, test-only red BROKEN, FAST timeout wheat=VALUE budget=FAST, empty EMPTY). LOCKSET_TOCK: tock does not beat 0.3 — same kernel, new name. Carry cinch 0.3. `lab/lineages/mutation-48__cinch/CANDIDATE.md`.

---

### 5. ambit — mutation-35

**Primitive.** Name a predicate snippet; emit every locus whose path-condition contains it, scanning the files **stdin locators named**. Reverse of `when`. Mutation of `under`. No cwd walk.

**Scores.** N4 U5 P5 C5 E4 Ev3 = 26. **Keep (the under-stream).** amid spare. No third under-stream.

**Why this rank.** FIRST_UNIX mutated **under**. The harvest is this pipe: `rg -n 'return None;' parse.rs | ambit --kind given 'a/'` hits `let b_side`, which rg never printed. Walking a tree is rg’s job. Filtering grep *lines* cannot see fallthrough `given`. Locators name the **file**. That is the sluice lesson applied to path-conditions.

**Mutation.** `--same-as` lives on peal/chime. Do not grep the `if` and print the body. JSON rg is amid’s one win — do not grow a second parser unless a producer needs it.

**Evidence.** AMBIT_AMID_BAKEOFF: ambit **2/3** (LINE:text pin recovery + `return None;` invert); amid 1/3 (JSON only). Both refuse cwd walk rc=2. `lab/lineages/mutation-35__ambit/CANDIDATE.md` — kizu `parse.rs` five `given` frames including `let b_side`. `./demo.sh` rc=0 (24 tests + kizu slice).

---

### 6. plait — candidate-38

**Primitive.** A review suggestion is a strand (span + before→after). plait is the **composition of those strands with each other** (COMMUTE / STACK / ECHO / SPLIT / SUBSUME / JAM), not occupancy against a tree and not GitHub “outdated”. Exit 0 composable, 1 SPLIT, 2 JAMMED, 3 error.

**Scores.** N5 U3 P5 C5 E4 Ev4 = 26. **Keep (the algebra).** braid/tilde/hank occupy or emit the fold — different verbs, not this product.

**Why this rank.** `gh api repos/cli/cli/pulls/7/comments | plait` is a Unix filter. Schedules (`line` / `time` / `topo`) are witnesses, not a dashboard. U3: I will not type this every morning; I will type it when two nits share a file. That is enough. Occupancy of the composed after-image is **sate’s family**, not a flag on plait.

**Mutation.** ECHO is locus-identity, not image-identity (DESTROYER). Empty markdown before is not a silent SPLIT you cannot name. Binary stdin fail-closed. Do **not** absorb braid.

**Evidence.** DESTROYER_PLAIT: mutate, do not kill. Gold commute PARALLEL rc=0; jam JAMMED rc=2; cli/cli PR #7 `#333030758,#333031216` still commuting. `--selftest` 23/23; `./demo.sh` PASS=35 FAIL=0. Attacks executed. `lab/lineages/candidate-38__plait/CANDIDATE.md`.

---

### 7. sate — candidate-34

**Primitive.** A unified diff is before→after image claims; report how a tree occupies each (APPLIED / PENDING / MIXED / DUPLEX / SUPERSEDED).

**Scores.** N5 U4 P5 C4 E3 Ev3 = 24. **Keep.**

**Why this rank.** `git apply --check` is a boolean lie: it cannot say MIXED or SUPERSEDED, and it fails when context drifted while the change-core is in the tree. Sandwich: `sate --git C --against C` APPLIED; `--against C^` PENDING. GitHub `suggestion` fences are hunks, not a second tool. C4: needs a tree, not only a stream.

**Mutation.** `sate log --pick SUPERSEDED` as a patch. `--against :` (index). Binary patches stay SKIP. Do not become braid.

**Evidence.** AUTHOR demo 31/31 (`lab/lineages/candidate-34__sate/CANDIDATE.md`). kizu `--log 8`: v0.6.0 `Cargo.toml` SUPERSEDED (now 0.7.0). FIRST_UNIX mutated sate at 27 with E3 — I keep E3 (no later destroyer on sate itself) and still keep the object. UNVERIFIED at parent WAVE2; do not inflate E.

---

### 8. when — candidate-20

**Primitive.** Given `file:line` (or a diff, or grep), emit the nested predicates still in force, including fallthrough `given`.

**Scores.** N5 U4 P5 C4 E5 Ev2 = 25. **Keep (the question-word).** Invert is ambit. Rhyme is peal. Do not ship four CLIs.

**Why this rank.** `git diff -W` names the function. Debuggers answer dynamically. `when parse.rs:60` is four `given` frames then `let b_side`. That is a Unix question-word next to `which` / `whatis`. Ev 2: ambit/peal already spent the stream mutations. when stays small.

**Mutation.** Overlay an unapplied patch so `--diff` is the post-image. Nested total early-returns. No TUI.

**Evidence.** PARENT PASS (`lab/WAVE2.md`). DISTINCT top-6. FIRST_UNIX E5. kizu `src/git/parse.rs:60` after v2 is the invert ambit reproduces from the other end. I did not re-run when this session; E5 is inherited from parent+first-selection execution, not from a new destroyer.

---

## Honorable mentions

Not PATH clutter. Each is a **different object** or a **correct peel** of a top-8. Rank independently of FIRST_UNIX’s “also keep” laundry list.

| tool | object | N | U | P | C | E | Ev | Σ | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **weld** (mutation-59) | concat inverse-printf, expr-first | 4 | 4 | 5 | 5 | 4 | 3 | 25 | `rg \| weld`; splice missed `response() + "\nDone."`; DESTROYER_WELD mutate. **stile** is the distinctive-proving-string peel. **solder** is a reimpl — spare, not a second binary. |
| **lurch** (mutation-103) | scarp as a stream of adjacent pairs | 4 | 4 | 4 | 5 | 4 | 2 | 23 | JSONL dilate-then-sleep is two rows. This is the scarp I would actually pipe a log into. |
| **sic** (mutation-01) | exact wire key; forks are not aka | 4 | 5 | 5 | 5 | 4 | 2 | 25 | `git diff \| sic --check`. I would **install** this tomorrow; it is not top-8 because the object is a linter on a known token, not a new noun. aka stays the inflection listing. |
| **tell** (mutation-03) | two trees → shortest distinguishing predicate | 5 | 3 | 5 | 5 | 4 | 3 | 25 | Inverse of held. Producer, not a walker. Pipe into perch; do not become `git diff --stat`. |
| **xref** (mutation-69) | DUE is a getenv *use*, not env-shaped bytes | 4 | 4 | 5 | 4 | 4 | 3 | 24 | `ldd`/`nm` family. DESTROYER_ASSAY: KIND real, 12k rustc DUE is strings. DESTROYER_XREF: rustc 44 names not 12596; `PYTHON_GIL` DUE / `PYTHONHOME` LATENT holds. **lode/due die as products.** shim/lash/wad are peels. |
| **beck** (candidate-41) | first pipeline stage that already contains this byte | 5 | 3 | 5 | 3 | 4 | 3 | 23 | Object is Unix (`tee \| grep` cannot see unpiped git stderr). **Implementation is a spawn wrapper** — I will not put a wrapper in top 8. Gold: `git -C /tmp status \| cat` is MINT stage 0 **stderr**, `piped_bytes=0`. **innard** peels `$()` / mid `2>&1`. |
| **tacit** (candidate-40) | TACIT / SHADOW / OVERRIDE / BOUND; BLAST of a default-moving diff | 5 | 4 | 5 | 3 | 4 | 3 | 24 | Omission is a real noun sow/zanei/erst lack. **Walker**, not a filter. sitbone `presentThreshold` 27 TACIT 0 SHADOW; `e9b0f75` BLAST 54 (DESTROYER_TACIT). **preen** unfolds constructed `Thresholds(driftDelay: 20)`. |
| **peal** (mutation-51) | chime as `rg \|` filter | 4 | 4 | 4 | 5 | 4 | 3 | 24 | `rg -n 'let b_side' parse.rs \| peal` = `chime parse.rs:60` including lines rg never printed. DESTROYER_PEAL mutate. **seed** refuses a bag of stacks. |
| **sluice** (mutation-02) | inverse printf kernel, anonymous holes | 4 | 4 | 5 | 5 | 5 | 1 | 24 | Keep as invert’s simpler kernel. Do not walk. Do not ship two filters. |
| **pin** (mutation-14 → v0.5) | durable locus token; `path:line` refused | 5 | 3 | 5 | 3 | 5 | 2 | 23 | **Park, do not evolve this wave.** PRIOR_ART gap is real. Unique kizu `seen_hunk_fingerprint` still lands. Gen-3 **keel/shoal** proved origin identity is a tar pit (remotes are config, witnesses are occupancy). I will `rg` the function name tomorrow. Token stays interesting; it is not a Unix filter. |

Also-keep as **spares / backends**, not honorable PATH: **held** (`--boolean` occupancy), **perch** (holder-set splits), **flume** (gitless locator rewrite of logs), **gist/rune** (0-based LSP rewrite — a filter, specialized), **sow** (production worlds as JSON), **lees** (oracle modulo substitution), **cusp** (BRINK/OFFBY TSV), **aka** (inflection identity), **winnow/glean** (fingerprint/file grain next to cinch), **erst** (natal inflection; FILE:LINE-free), **stencil** (walker spare for invert only).

---

## What I would install tomorrow

PATH is not a museum. Eight binaries. Each a different mouth.

```
invert   # rg | invert 'the paste'
scarp    # { scarp cut; sleep 0.3; scarp cut; } | scarp
         # (lurch if the input is already a clock log)
zanei    # git diff origin/main...HEAD | zanei --diff -
cinch    # cinch -- pytest          # 0.3 only
ambit    # rg -n 'return None;' | ambit --kind given 'a/'
sic      # git diff | sic --check
when     # when src/git/parse.rs:60
sate     # sate --git HEAD --against HEAD
```

**plait** I would install the week I review GitHub suggestion batches, not before breakfast. **xref** I would run on a mystery binary (`xref --app python3`), not on every commit. **weld** when the log was obviously concat (`response() + "\nDone."`); invert first. **tell** when I am staring at two trees and do not know the grep. **beck** when `tee | grep` of a pipeline dump is empty and I still saw the line.

I would **not** install pin, keel, shoal, lien, noun, berth, holt, hydra, maiden, badge, braid, tilde, knot, sinter, lode, under, chime, tock, solder.

---

## What is not Unix

Not “bad.” Not “kill the idea.” **Not a Unix product.** The object may live as a spare, a peel, or a parked noun.

### Walkers that own ignore policy

unfmt-08, unfmt-13, stencil-as-product, under-as-cwd-scan, chime-as-DIR-walk. Inverse printf and path-condition both already flipped this. A directory operand without `--walk` is exit 2.

### Occupancy dashboards

held + perch + stint + dwelt + berth + holt + ford + weir + hydra + tenure is **one family wearing nine hats**. The Unix half is **tell** (emit a predicate) and **held --boolean** (consume it). hydra’s k-of-n merge lattice is a real observation (`FALSE ⊓ TRUE` is not `TRUE`) and a terrible CLI. Default all-reachable R (holt) is `git log --full-history` with more words.

### Token minting as a ticket product

`pin1.eNpt…` is not `file:line`, which was the pitch. After DESTROYER_PIN_V5 / KEEL / SHOAL the token is a repo-identity protocol: remotes, witnesses, leftover pointers, NFC, truncated `pin1.`, `--any-repo`. That is a platform. The fingerprint backend is **slip**. The log filter is **flume**. The LSP filter is **gist**. Minting is optional.

### Dest-tree natal scanners dressed as filters

`git diff | lien` **looks** like Unix. It parses stdin then **walks `-C`**. Wrong `-C` is fail-open rc=0 (DESTROYER_LIEN). Two packages named `version` are one noun until **noun**. That is zanei + erst + a tree walk. Keep zanei.

### Review platforms

plait is the algebra. braid occupies the fold. hank emits the covering. quire is multi-file emit. tilde NFC-keys occupancy. That is four verbs. Unix ships plait. Occupancy is sate. Emit is `hank --emit | git apply` as a peel, not a suite.

### Spawn wrappers and wait-for graphs

beck’s **object** is first-producer; the binary wraps bash. knot / pinch / hitch / spoor / cling / coast are wait-source archaeology. `pstree`, `strace`, `wait` exist. Park the wake-as-diffable-object; do not PATH six tracers.

### Parser farms

maiden / badge fold junit+cargo+swift+xcresult+CI logs into never-red. The object (“this id has no recorded `<failure>`”) is sharp. The CLI is a census. DESTROYER_MAIDEN: sitbone `swift test list` is 213 UNKNOWN; rename is a new string id. Not `rg PASS` — and not a filter.

### Generation-lot assays and spec polarity

kiln, clutch, sinter, yoke. Real on relico/tenaoshi. Not tiny. Not tomorrow.

### Kitchen-sink env ABI

lode unioned DUE+LATENT. assay split them and then DUE’d 12,596 LLVM opcodes. xref is the column. due’s source harvest can feed xref. orbit is `which` plus rpath. Do not ship the union.

### Inverse-printf walkers and concat walkers

Coordinator banned them. weld/stile/solder that start the scanner at every identifier die. Directories on `--templates` exit 2.

### NLP / speech-act / leftover-name

vow, rejoin, foil-as-product, haunt, wisp remnants, helm, shunt. GHOST_CLUSTER already split names vs claims vs diff-vs-history. One leftover-*name* spare: **wraith**. Stop.

---

## Disagreements with FIRST_UNIX

FIRST_UNIX was a good 03:00 cut. I am not restating it. These are the places this judge **refuses** that ranking.

1. **scarp/lurch would have been evolution vehicles.** FIRST_UNIX’s sixteen missed clock-cuts because `lapse` still spawned. The Unix object is two cuts, no `Popen`. I rank scarp **#2**, above pin, tell, held, when. That is not polish; it is `{cut; cut} | scarp`.

2. **Demote pin from mutate-vehicle to park.** FIRST_UNIX scored pin 28 and mutated it. DESTROYER_PIN_INVERT / PIN_V5 / KEEL / SHOAL then spent the night on origin identity. Unique kizu `app.rs:529 → layout.rs:17` still works; `rg seen_hunk_fingerprint` also lands `:17`. I will not mint a token into a ticket tomorrow. Primitive remains 5. Utility and composability do not. **slip** is the fingerprint backend. **flume/gist** are the filters.

3. **ambit replaces under as the ranking unit.** FIRST_UNIX mutated under. The harvest is `rg | ambit`. under-the-walker is not a product. Same for **peal** vs chime.

4. **cinch’s vehicle is 0.3 (mutation-48), not hybrid-03.** FIRST_UNIX mutated hybrid-03 correctly. LOCKSET_BAKEOFF / TOCK closed the occupancy lies (test-only CLEAN, timeout-as-wheat). tock is not a fourth cinch.

5. **plait is Unix; braid is not this product.** FIRST_UNIX never saw plait. JSONL + exit 0/1/2 is the shape FIRST_UNIX asked for. Occupancy of the fold is a second verb.

6. **xref replaces lode.** FIRST_UNIX mutated lode. Assay proved KIND; rustc 12k DUE proved DUE-as-bytes is `strings(1)`. xref’s 44-name rustc is the env ABI I would keep. due/orbit as products die.

7. **weld is the concat sibling FIRST_UNIX named, and it must not merge into invert.** DESTROYER_STUMP_PIN: concat is a sibling mutation. weld binds `{response}` where splice missed. stile owns the proving-string floor. One invert on PATH; weld when the template starts at an expression.

8. **held / perch / erst are not top-8.** FIRST_UNIX scored them 26–28. They are git-walkers with a true object (eras, holder splits, natal inflection). Unix keeps **tell** as the producer and held as `--boolean`. I will not install occupancy pretty-printers.

9. **knot is not a keep-as-product.** FIRST_UNIX kept knot (pinch×hitch). Wait-for graphs are not filters. Park.

10. **lien is not a survivor over zanei.** FIRST_UNIX did not have lien. `git diff | lien` scans dest and fail-opens on wrong `-C`. Natal CI is a linter clothing. Claims stay zanei.

11. **flume is not the locator-stream vehicle anymore.** FIRST_UNIX mutated flume (E2 UNVERIFIED at parent). **gist** is the schema-honest 0-based LSP filter (`528 → 16`, not 17); flume is rustc-log gutters. Neither is top-8. I would not mutate flume this wave.

12. **beck is a wrapper.** FIRST_UNIX hated wrappers. I honorable the object (unpiped stderr vs tee). I will not rank a bash-spawner with invert.

13. **maiden is heretic-interesting and not Unix.** Never-red is not `rg PASS`. It is also a parser farm. Park.

14. **FIRST_UNIX’s “sixteen vehicles” is too many for a Unix PATH.** Several were the right *objects* at 03:00 (sow, lees, cusp, doze, erst, perch, under). After Gen-3, most are peels or parked. This jury’s install list is eight, not sixteen.

Agreements, so this is not contrarianism: haunt dead; folk parked; invert is the inverse-printf filter; zanei is claims not names; cinch ≠ winnow; no second unfmt walker; pinch∥hitch∥knot collapse; kiln∥clutch∥sinter collapse; Σ is not the ranking key; invert is not “the winner,” it is the inverse-printf filter.

---

## Kill list

Kill the **product**. Harvest at most one fact. Do not spend another slot.

| kill | honest object / harvest | why |
| --- | --- | --- |
| **haunt** | — | already dead. Worse wraith. GHOST_CLUSTER. |
| **wisp remnants** | stint occupancy; wraith names | do not glue interval-ephemeral files to leftover names |
| **unfmt-08 / unfmt-13** as products | invert + stencil spare | UNFMT_BAKEOFF closed two walkers |
| **under / chime** as cwd-walk products | ambit / peal | stream harvest exists |
| **pinch, hitch** | park knot’s wait-source | one conversation, not three CLIs |
| **knot** as product | park the wait-source object | not a filter; `pstree`/`strace` |
| **kiln, clutch** as products | sinter if anyone needs a spec-gen assay | convergent lots |
| **yoke** | sinter / a spec-check | clause polarity dashboard |
| **nigh** | cusp | string-edit `ENOENT`≈`event` |
| **akin similarity** | once exact-blob; `--port` only | invented merge-bases |
| **due, lode, orbit** as products | xref (+ due as a producer if needed) | union / guise footnotes |
| **tock** as PATH | cinch 0.3 | LOCKSET_TOCK: same object, new name |
| **snug** as PATH | cinch 0.3 | bakeoff spare |
| **solder** as PATH | weld (stile peel) | reimpl-11 is proof, not a second concat filter |
| **badge** as PATH | maiden parked | string-id peel; do not ship two never-red censuses |
| **fourth cinch / third ambit** | — | coordinator already banned |
| **inverse-printf walkers** | — | banned; invert/weld are filters |
| **leftover-name products** (helm, shunt, haunt) | wraith spare | stop |
| **moor** as product | pin × invert is composition, not a trenchcoat | `slip \| invert` |
| **folk** as linter | parked handshake table | 0 real orphans after honesty filter |
| **coast** as product | `sleep 2` / park spoor’s wake | subset |
| **hydra / ford** as products | park merge-occupancy lattice | k-of-n is a fact, not a daily verb |
| **braid / tilde** as products | plait algebra; sate occupancy | second verb |
| **lien / noun** as products | zanei + erst | dest walk, fail-open `-C` |
| **keel / shoal** as products | park pin | origin tar pit |
| **vow / proxy** as products | park oath-from-assert | assertion NLP |
| **smolder / binom** as products | zanei invert is dest-locus archaeology | not a stdin filter |
| **woof / weft** as PATH suites | one prose-class check if anyone needs CI | still a dialect of the path (DESTROYER_WOOF) |

Park, do not kill (object sharp, product empty or overgrown): **folk**, **pin**, **maiden**, **beck** (wrapper), **tacit** (walker), **sinter**, **held/perch**, **knot**’s wake object, **gist** (specialized filter).

---

## Gen-3 peels — not PATH entries

Sampled `mutation-103__lurch` through `reimpl-11__solder`. All harvested Keep. Unix cut: **peel the ancestor; do not mint sixteen new verbs.**

| peel | ancestor | keep as |
| --- | --- | --- |
| **lurch** | scarp | the stream form of clock-cuts (honorable) |
| **holt** | berth | all-reachable R default — occupancy policy, park |
| **noun** | lien | (package, noun) natal — still a dest walker |
| **preen** | tacit | constructed-default unfold — mutation, not a second omission CLI |
| **innard** | beck | `$()` / mid `2>&1` — mutation of a wrapper |
| **shim** | xref | rustup/xcselect hop + getenv allowlist — mutation |
| **stile** | weld | distinctive proving string — mutation of concat invert |
| **shoal** | keel | signed remotes at mint — still pin origin |
| **rune** | gist | dest-own UTF-16 `character` + origin `diagnostics: []` — mutation |
| **proxy** | vow | follow `expected=name` — still oath NLP |
| **binom** | smolder/lien | package-scoped leftover invert — not a filter |
| **hydra** | ford | n-parent lattice — occupancy dashboard |
| **tilde** | braid | NFC occupancy of the fold — second verb |
| **seed** | peal | refuse a bag of stacks — mutation |
| **badge** | maiden | (suite, class, method) + flakyFailure — second census |
| **solder** | weld | clean-room concat invert — spare |

---

## Cluster map (final)

```
inverse printf     invert, sluice, stencil(spare), weld, stile, solder(spare), lede/splice
clock-cut          scarp, lurch, yaw/twixt (peels), lapse (spawn ancestor — dead as product)
path-condition     when, ambit, peal, seed
leftover claims    zanei, nagori; lien/noun are dest-scan clothing
lockset            cinch 0.3; winnow fingerprint; glean file; tock/snug spare
suggestion algebra plait; sate occupies a tree; braid/tilde occupy the fold (park products)
wire tokens        sic exact; aka inflection
occupancy          tell (producer); held --boolean; perch holder; berth/holt/hydra park
durable address    slip backend; flume logs; gist/rune LSP; pin/keel/shoal park
env ABI            xref (DUE=use); assay KIND; lode/due/orbit dead as products
omission           tacit, preen
first-producer     beck object, innard peel, wrapper implementation
never-red          maiden park, badge kill-as-product
generation lots    sinter if needed; kiln/clutch/yoke dead as products
wait / wake        park
ghost names        wraith spare; haunt dead
natal cohort       erst spare; also FILE:LINE; owe intermediate
```

---

## Pipes (composition, not winners)

```
rg -n --type rust 'format!|anyhow!' repo | invert 'paste'
rg -n --type js 'response()' repo | weld $'{"ok":true}\nDone.'
{ scarp cut --json; sleep 0.35; scarp cut --json; } | scarp
lurch < clocklog.jsonl
git diff origin/main...HEAD | zanei --diff - -C repo
git diff | sic --check
rg -n 'return None;' src/git/parse.rs | ambit --kind given 'a/'
rg -n 'let b_side' src/git/parse.rs | peal --explain
when src/git/parse.rs:60
tell -C repo A B --held
sate --git HEAD --against HEAD
cinch -- pytest
gh api repos/cli/cli/pulls/7/comments | plait
xref --app python3
```

Eight survivors. Eight installable. Haunt dead. Folk parked. Pin parked. Occupancy dashboards parked. No single winner. Invert is not the winner; it is the inverse-printf **filter**. Scarp is not second place because it is fashionable; it is the clock-cut **filter** FIRST_UNIX never got to rank.

---

## Evidence index

| claim | where |
| --- | --- |
| invert 7-hole / span / camera | `lab/lineages/mutation-15__invert/CANDIDATE.md`; `lab/judges/DESTROYER_PIN_INVERT.md`; `lab/judges/UNFMT_BAKEOFF.md` |
| scarp no-spawn DILATE | `lab/judges/DESTROYER_SCARP.md`; `lab/lineages/mutation-46__scarp/CANDIDATE.md` |
| lurch adjacent pairs | `lab/lineages/mutation-103__lurch/CANDIDATE.md` |
| zanei claims | `lab/lineages/candidate-07__zanei_/CANDIDATE.md`; `lab/judges/DESTROYER_ZANEI.md`; `lab/judges/GHOST_CLUSTER.md` |
| cinch 0.3 4/4 | `lab/judges/LOCKSET_BAKEOFF.md`; `lab/judges/LOCKSET_TOCK.md`; `lab/judges/DESTROYER_CINCH.md`; `lab/lineages/mutation-48__cinch/CANDIDATE.md` |
| ambit 2/3 bakeoff | `lab/judges/AMBIT_AMID_BAKEOFF.md`; `lab/lineages/mutation-35__ambit/CANDIDATE.md` |
| plait COMMUTE/JAM | `lab/judges/DESTROYER_PLAIT.md`; `lab/lineages/candidate-38__plait/CANDIDATE.md` |
| sate SUPERSEDED | `lab/lineages/candidate-34__sate/CANDIDATE.md` |
| when parse.rs:60 | FIRST_UNIX / WAVE2 parent; `lab/lineages/candidate-20__when/CANDIDATE.md` |
| weld expr-first | `lab/judges/DESTROYER_WELD.md`; `lab/lineages/mutation-59__weld/CANDIDATE.md` |
| xref not strings | `lab/judges/DESTROYER_XREF.md`; `lab/judges/DESTROYER_ASSAY.md` |
| beck ≠ tee\|grep | `lab/judges/DESTROYER_BECK.md`; `lab/lineages/candidate-41__beck/CANDIDATE.md` |
| tacit omission | `lab/judges/DESTROYER_TACIT.md`; `lab/lineages/candidate-40__tacit/CANDIDATE.md` |
| peal = chime invert | `lab/judges/DESTROYER_PEAL.md` |
| pin origin tar pit | `lab/judges/DESTROYER_PIN_V5.md`; `lab/judges/DESTROYER_KEEL.md`; `lab/lineages/mutation-110__shoal/CANDIDATE.md` |
| lien dest walk | `lab/judges/DESTROYER_LIEN.md`; `lab/lineages/mutation-105__noun/CANDIDATE.md` |
| maiden parser×id | `lab/judges/DESTROYER_MAIDEN.md` |
| vehicles board | `lab/STATE.md` |
| first cut | `lab/judges/FIRST_UNIX.md` |
