# Toolsmith Judge — final jury

Source: judge-02, isolated worktree, 2026-08-20 final jury. Axis of record is **utility**: would a real developer type this tomorrow, on a dirty tree, without being reminded?

Does not collapse to one winner. Does not rank by polish. FIRST_TOOLSMITH, FIRST_SKEPTIC, DESTROYER_*, bakeoffs, and CANDIDATE transcripts are evidence, not a ranking to rubber-stamp.

Scores are 0–5 integers: Novelty / Utility / Primitive / Composability / Empirical / Evolution. A 4+ on Empirical requires a run, not a README. This session re-ran cheap selftests and live probes on kizu / sitbone; the rest cite author demos plus destroyer transcripts.

Scope: named vehicles **invert / cinch / ambit / pin / when / held / winnow / zanei / plait / berth / lien / tacit / beck** and the harvested Gen3 peels (lurch, holt, noun, preen, innard, shim, stile, shoal, rune, proxy, binom, hydra, tilde, seed, badge, solder). Other Gen-1 PATH entries (slip, reverb, sic, due, sate, zure) are mentioned only where they contradict this ranking.

## The question

A toolsmith keeps a verb that collapses a recurring loop into one command. Occupancy eras, omission vs restatement, and inverse-printf are allowed to be strange **if they already paid rent** on kizu / sitbone / tenaoshi / voidtrace. Peels of a paid-rent primitive are flags, not extra PATH entries, unless the ancestor’s default was a lie.

---

## Tomorrow-install (would run on a real repo)

Eight verbs. Not one product. Each is a different object. Lineage peels sit next to the verb, not as a ninth CLI.

| # | install | id | primitive | why tomorrow |
| --- | --- | --- | --- | --- |
| 1 | **invert** | mutation-15 | inverse printf as a filter: paste → template + named holes + span leftover | every error/log paste |
| 2 | **winnow** | candidate-15 | ddmin uncommitted hunks against a command fingerprint | "which of these 12 dirty hunks made it red?" |
| 3 | **cinch** 0.3 | mutation-48 | 1-minimal *production* hunks the current tests veto; timeout is unknown | review: drop the debug print, keep the return |
| 4 | **zanei** | candidate-07 | leftover *claims* a diff just made false | after a rename / bound-value flip, human scan |
| 5 | **when** | candidate-20 | path-condition + fallthrough `given` at `file:line` | reading a nested early-return |
| 6 | **preen** | mutation-106 | TACIT/SHADOW/OVERRIDE/BOUND of a defaulted slot; unfold from the *constructed* default | about to change `presentThreshold` / clap `--agent` |
| 7 | **noun** | mutation-105 | `git diff \| noun` CI gate on leftovers of that change’s **(package, noun)** natal | release PR that left `plugin.json` at `0.3.0` |
| 8 | **holt** | mutation-104 | file-identity occupancy from all-reachable R; leftover name is a new roost | `git log -- path` empty; `git mv` is one era |

Lineage next to those, not extra PATH entries:

- invert: **stile** (distinctive proving string) / **solder** (reimpl of expr-first concat). Do not ship weld/lede/splice as products.
- when: **ambit** is `rg \|` of the same object; **seed** is the honest default (a bag of stacks is not a seed). `--under` / `--same-as` flags, not three CLIs.
- zanei: **lien** is the CI-shaped ancestor; **noun** is the install. **binom** is `FILE:LINE → falsifying commit` of that package.
- tacit: **preen** is the install. tacit 0.2’s 27 TACIT gold holds; constructed-default ≠ signature-default and clap-as-invocation do not.
- held: **holt** is the install. **berth**’s default first-parent never-held the dead name. **hydra** is merge k-of-n, a specialist flag.
- cinch: still 0.3 after LOCKSET_BAKEOFF / LOCKSET_TOCK. tock/snug/hasp are transcripts, not PATH.
- beck: **innard** harvests `$()` / mid-command `2>&1`. Preserve, do not PATH.

---

## Preserve (strange, already paid rent)

Do not kill these because they are not "everyday grep." They already answered a question git/rg/tee cannot phrase on the dogfood trees. They are not tomorrow-morning PATH.

| tool | rent | this-session probe |
| --- | --- | --- |
| **when** / **ambit** | kizu `parse.rs:60` is four early-return `given`s, including `let b_side` which `rg 'return None;'` never printed | `when parse.rs:60` depth=5; `rg -n 'return None;' parse.rs \| ambit --kind given 'a/'` emits `let b_side` |
| **held** | sitbone `FocusRiverView.swift`: `git log -- path` empty; `--full` TRUE 11 commits then deleted | re-ran; first-parent hints `--full` |
| **holt** | kizu R100 `deep-research-ai-agent-hooks.md → docs/…` is one 187-commit roost from either name | berth default on the dead name = never-held; holt default = `true=187/244` both names |
| **zanei** | sitbone `e9b0f75` leftover `threshold 0.4` in CLAUDE.md tests after hysteresis | `--min-score 70` → 2 afterimages, both CLAUDE.md |
| **noun** | kizu `9349dc5` crate `0.6.0→0.7.0`, dest `plugin.json` still `0.3.0` | `git diff \| lien` silent rc=0; `git diff \| noun` rc=1 one dest-line |
| **preen** / **tacit** | sitbone `presentThreshold` **27 TACIT, 0 SHADOW**. Hysteresis tests ride 0.45 without passing it | both CLIs reprint that table |
| **invert** | kizu timestamp is a *span*, not a strip | `failed to spawn \`git apply --reverse\`` → `revert.rs:46` prefix=`2026-08-19T23:50:01Z ERROR` |
| **winnow** | hunk split: header comment is chaff, `return a - b` is wheat; pycache does not poison HEAD | `./demo.sh` all cases passed |
| **cinch** 0.3 | winnow wheat includes `print("debug")`; cinch wheat is the return; FAST timeout is budget not wheat | units 15/15; bakeoff 4/4 vs 0.2 |
| **plait** | cli/cli PR #7 two suggestions COMMUTE; overlap JAMS before the third GitHub click | `--selftest` 23/23; PR #7 PARALLEL one plait |
| **beck** / **innard** | `git status \| cat` fatal is git’s **stderr**; tee of the pipe is 0 bytes | beck MINT stage 0 stderr, tee MISS; innard `$()` first-producer is inner `tr` |
| **seed** | `rg 'return None;'` is 9 stacks, not the quoted-form miss peal chimed as first locator | gold `let b_side` same as `when :60`; bag refused |
| **pin** | kizu godfile split `src/app.rs:529 → layout.rs:17` | mint+resolve porcelain `moved … 1.000` |

---

## Overbuilt toys (kill the product)

Novelty that does not collapse a loop a developer already runs. Harvest the one fact; do not install.

| toy | clone / peel of | why not tomorrow |
| --- | --- | --- |
| **lurch** / scarp | clock-cut stream | lid-close vs NTP vs adjtime slew is real and this session’s selftest is 10/10. I will not type it on a dirty app repo. |
| **shoal** / keel | pin origin | signed remotes + required witnesses so `git remote add` is not `--any-repo`. Ceremony around a token I already will not mint into a ticket. |
| **hydra** | held / ford | k-of-n occupancy at an octopus merge. Specialist lattice, not a daily verb. |
| **rune** | gist / slip | dest-own LSP `character` as UTF-16. An editor plugin, not a CLI I type. |
| **shim** / xref | due / assay | getenv allowlist + rustup trampoline. I will `rg getenv` / `rg env::var`. |
| **badge** | maiden | never-red keyed by (suite, class, method), `<flakyFailure>` is red. Quarterly audit. |
| **proxy** | vow | follow `expected = home = getenv` before classifying a failing assertion. One pytest dump. |
| **tilde** as product | plait × sate | NFC path+line occupancy of the *composed* after-image. Flag on plait. |
| **binom** as product | smolder × noun | leftover dest locus → falsifying *package* commit. `noun --blame`. |
| **solder** as product | weld reimpl | proof expr-first concat is not an accident of one file. Transcript, not PATH. |
| **stile** as product | weld / invert | distinctive proving string vs `visible < 4`. Harvest into invert; do not ship a fifth inverse-printf. |
| **berth** as product | held `--follow` | pitch “old name or new name, occupancy stays TRUE” is **false on default first-parent**. This session: dead name never-held. holt is the object. |

---

## Disagreements with FIRST_TOOLSMITH

Independent rank. FIRST_TOOLSMITH’s PATH twelve was invert, slip, winnow, when, zanei, reverb, sic, due, sate, zure, held, cinch. Utility-first still, the night evolved, and several of those twelve would not be typed tomorrow.

| FIRST_TOOLSMITH | this jury | why |
| --- | --- | --- |
| **held** on PATH | preserve ancestor; install **holt** | sitbone rent is real. Default occupancy that cannot follow a rename is not the verb. berth’s first-parent dead-name never-held is a product-killing lie. |
| **pin** preserve (not PATH) | **park** harder | kizu split still lands. DESTROYER_PIN_V5 leftover-as-pointer still loses to stem-split / unique non-basename decoy. I will `rg seen_hunk_fingerprint`, not mint `pin1.eNpt…`. |
| **when** on PATH, under/chime as flags | **when** on PATH; **ambit** preserve as the stream; **seed** harvests peal’s first-locator lie | agree on one review verb. Do not PATH when+ambit+peal+seed. Live `layout.rs:17` is still depth=0 (skeptic was right that the rent is nested returns, which `parse.rs:60` still pays). |
| **due** on PATH | **kill as PATH** | FIRST_SKEPTIC already. shim/xref did not make `rg getenv` the wrong object. |
| **sic / sate / zure / reverb / slip** on PATH | out of this named set; **would not re-PATH** | slip’s kizu scar is pin’s ancestor transcript. sate occupancy sandwich lost to plait on review-suggestion day and to `git apply --check` on a clean HEAD. reverb is `git diff` minus lines → `rg`. |
| **cinch** on PATH (hybrid-03 v0.2) | **cinch 0.3** on PATH | agree on the object. 0.2 reported test-only red as CLEAN. Bakeoff 4/4 only on 0.3. tock is the same kernel. |
| **winnow** on PATH | **keep** | agree. This session `./demo.sh` still all pass. Different predicate from cinch; both stay. |
| **zanei** on PATH | **keep**, and add **noun** as the CI twin | FIRST had no natal gate. `git diff \| lien` is green on kizu `9349dc5` while `plugin.json` still says 0.3.0. noun fails that line. Do not PATH zanei+lien+noun: human zanei, CI noun. |
| no **tacit** | **preen** on PATH | 27 TACIT riders of `presentThreshold` is a question `rg presentThreshold` cannot ask. FIRST never saw the object. Install preen (constructed unfold + clap invocation), not tacit 0.2. |
| no **plait** | **preserve, not PATH** | COMMUTE/JAM is not occupancy. Review-day verb. Not every morning. |
| no **beck** | **preserve, not PATH** | unpiped stderr is a real miss of `tee \| grep`. Weekly pipeline debug, not a dirty-tree loop. |
| “mutate PATH twelve in place; no thirteenth leftover-name” | **keep that kill**; Gen3 peels are mostly flags | lurch/shoal/hydra/rune/shim/badge/proxy are thirteenth-objects of the wrong kind. holt/noun/preen/seed/innard/stile are the peels that closed destroyer lies. |

Skeptic kept four (winnow, cinch, invert, zanei thin). This judge keeps those four **and** when / preen / noun / holt, because each names a question git/rg cannot ask and already paid rent on the dogfood trees. Skeptic vetoes daily PATH for held/pin; this judge agrees, and still installs holt for the rename occupancy git log will not say.

---

## Ranked survivors

Utility first, then primitive. Σ is unweighted and must not override a U=2 peel.

### PATH (install these)

| rank | tool | N | U | P | C | E | V | Σ | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | invert | 4 | 5 | 5 | 5 | 5 | 4 | 28 | runtime string on one channel, templates on the other; named holes; leftover prefix is a span |
| 2 | winnow | 4 | 5 | 5 | 5 | 5 | 3 | 27 | smallest hunk set that reproduces a command fingerprint |
| 3 | cinch 0.3 | 4 | 5 | 5 | 4 | 5 | 3 | 26 | smallest *production* hunks the current tests veto; timeout ≠ fail |
| 4 | zanei | 5 | 4 | 5 | 5 | 5 | 3 | 27 | leftover *facts* (bound value / rename / polarity) after a diff |
| 5 | when | 4 | 4 | 5 | 5 | 5 | 3 | 26 | nested predicates still in force at a locus, including `given` |
| 6 | preen | 4 | 4 | 5 | 4 | 5 | 2 | 24 | omitted vs restated vs overridden default; unfold from the constructed expression |
| 7 | noun | 4 | 4 | 4 | 5 | 5 | 3 | 25 | this change’s version, whose package, which dest manifest still speaks it |
| 8 | holt | 4 | 4 | 5 | 4 | 5 | 3 | 25 | file identity from all-reachable R; leftover path is a new roost |

Invert still ranks first because paste-a-log is the most frequent loop. Winnow vs cinch: both U=5; winnow is the “why is this red *right now*” verb (faster to reach for); cinch is the reviewer lockset. Do not merge them. Preen ranks below when because default-moving days are rarer than nested-return review, but the 27 TACIT table is a unique object. Noun is the CI form I would actually wire. Holt is weekly archaeology that git log will not do.

### Preserve / harvest (not PATH)

| tool | N | U | P | C | E | V | Σ | verdict | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ambit | 3 | 4 | 4 | 5 | 5 | 3 | 24 | **P** | `rg \|` of when; pin-recovery of LINE:text. Flag `--under` if when absorbs it |
| seed | 3 | 3 | 4 | 5 | 5 | 2 | 22 | **P** | harvest into peal/ambit: a bag of stacks is not a seed |
| plait | 5 | 3 | 5 | 4 | 5 | 3 | 25 | **P** | review-suggestion algebra; GitHub-click day |
| beck | 5 | 3 | 5 | 4 | 5 | 3 | 25 | **P** | first producer of a byte; tee cannot see unpiped stderr |
| innard | 4 | 3 | 5 | 4 | 5 | 2 | 23 | **P** | harvest into beck: `$()` / mid `2>&1` |
| tacit | 5 | 4 | 5 | 4 | 5 | 2 | 25 | PARK→preen | 27 TACIT gold; clap TACIT was command-shaped comments |
| lien | 3 | 4 | 4 | 5 | 5 | 2 | 23 | PARK→noun | dest-line CI gate; two packages named `version` are one noun |
| held | 5 | 3 | 5 | 4 | 5 | 2 | 24 | PARK→holt | eras, not one bisect cut; `--boolean` of holt |
| pin v0.5 | 5 | 3 | 5 | 4 | 5 | 3 | 25 | PARK | token is a real object; leftover-pointer vote order is still a lie |
| stile | 3 | 3 | 4 | 5 | 5 | 2 | 22 | **P** | harvest into invert: proving string must be distinctive |
| solder | 2 | 3 | 5 | 5 | 4 | 1 | 20 | PARK | clean-room weld; keep the transcript |

### Kill products / overbuilt

| tool | N | U | P | C | E | V | Σ | verdict | harvest |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| berth | 4 | 2 | 4 | 4 | 5 | 2 | 21 | KILL product | holt (all-reachable R + tip occupant) |
| lurch | 4 | 1 | 3 | 4 | 5 | 2 | 19 | KILL product | scarp `--stream` if anyone debugs clocks |
| shoal | 3 | 1 | 3 | 3 | 4 | 2 | 16 | KILL product | pin origin is not a daily verb |
| hydra | 4 | 2 | 4 | 3 | 4 | 2 | 19 | PARK | `--lattice` on holt |
| rune | 3 | 2 | 3 | 4 | 4 | 2 | 18 | PARK | editor LSP rewriter |
| shim | 3 | 2 | 3 | 4 | 4 | 2 | 18 | PARK | `rg getenv` |
| badge | 4 | 2 | 4 | 3 | 4 | 2 | 19 | PARK | never-red identity |
| proxy | 3 | 2 | 3 | 3 | 4 | 2 | 17 | PARK | follow expected=name |
| tilde | 3 | 2 | 3 | 4 | 4 | 2 | 18 | KILL product | plait `--occupy` + NFC keys |
| binom | 4 | 3 | 4 | 4 | 4 | 3 | 22 | PARK→flag | noun `--blame` |

---

## Per-candidate (named vehicles)

Keep decisions follow Utility first, then Primitive. Novelty does not save a clone. Mutate = harvest into the install verb; do not spend a rewrite slot inventing a sibling CLI.

### invert — KEEP PATH

N4 U5 P5 C5 E5 V4. Inverse printf as a stream filter; named holes; prefix is a span.

Mutate: distinctive proving string (stile); expr-first concat (solder/weld) as `--concat`, not a walker. Truncated-log prefix of a holed template. `--any` stops. DESTROYER_PIN_INVERT stuffing / 4-char floor stay load-bearing.

Evidence: `./invert --selftest` ok; live kizu `rg 'failed to spawn' \| invert '2026-08-19T23:50:01Z ERROR failed to spawn \`git apply --reverse\''` → `src/git/revert.rs:46:18` score=0.66 via=span prefix=`2026-08-19T23:50:01Z ERROR`.

### winnow — KEEP PATH

N4 U5 P5 C5 E5 V3. Smallest uncommitted hunks that reproduce a command fingerprint.

Mutate: default fingerprint that does not need `PYTHONDONTWRITEBYTECODE` is already in; `--grain file` eats glean. Do not grow a lockset predicate (that is cinch).

Evidence: this session `./demo.sh` — all cases passed (guilty file, joint wheat, pycache, traceback line-shift, hunk split, nested git).

### cinch 0.3 — KEEP PATH

N4 U5 P5 C4 E5 V3. 1-minimal production hunks the current tests veto. Tests stay NEW. Timeout is unknown (budget), not fail.

Mutate: empty-suite must not be exit 5 alone (DESTROYER_CINCH). Demote `generated/` / `vendor/`. Nested `.git` is not outer production. Still Python hunk apply — FOREIGN Swift stays a hole.

Evidence: `cinch 0.3.0`; units 15/15 in 3.1s this session. LOCKSET_BAKEOFF: test-only red BROKEN, FAST budget not wheat, debug-print chaff, empty EMPTY. tock is the same object (LOCKSET_TOCK).

### zanei — KEEP PATH

N5 U4 P5 C5 E5 V3. Leftover claims a diff just made false.

U=4 not 5: after `0.3.0 → 0.7.0` I will still `rg 0.3.0`; high `--min-score` is conservative (2 sitbone hits) while noun is the hungry CI. DESTROYER_ZANEI: ISO-date `2024-10-01` is leftover timeout 10; `generated/` is a believer. Stay a filter (`diff in → claims out`).

Evidence: `./zanei self-test` ok; sitbone `e9b0f75^ e9b0f75 --min-score 70` → 2 afterimages, both CLAUDE.md `@Test(… threshold 0.4)`.

### when — KEEP PATH

N4 U4 P5 C5 E5 V3. Path-condition stack at `file:line`, including fallthrough `given`.

Mutate: `--same-as` / `--under` (ambit/seed) as flags. `--explain` default on a tty. Do not PATH chime/peal/amid.

Evidence: `./when kizu/src/git/parse.rs:60 --explain` → four `given`s, `here let b_side`, depth=5. `layout.rs:17` is still `here pub fn seen_hunk_fingerprint` depth=0.

### ambit — PRESERVE (stream of when)

N3 U4 P4 C5 E5 V3. Name a predicate; emit loci whose stack contains it; scan files stdin locators named. No cwd walk.

Mutate: harvest **seed** (refuse a bag; stripped LINE:text identity). JSON rg (amid’s 1/3 bakeoff win) if the stream needs it. AMBIT_AMID_BAKEOFF carried ambit 2/3.

Evidence: `cd kizu && rg -n 'return None;' src/git/parse.rs \| ambit --kind given 'a/' --explain` → span `:59-60` `here let b_side` under `given bytes.starts_with(b"a/")`.

### pin v0.5 — PARK

N5 U3 P5 C4 E5 V3. Mint a self-contained fingerprint; resolve without re-supplying `path:line`. Origin holding the body is identity; leftover stub is supposed to be a pointer.

The token is a real object. I will not type `pin mint` tomorrow. DESTROYER_PIN_V5: unique stem-split still beats a leftover that names `src.math.ops`; unique non-basename decoy lands while the extract is called basename bait. shoal’s signed remotes do not make me mint tokens.

Evidence: mint `src/app.rs:529` at kizu `b4e6a5d` → resolve HEAD `moved src/app.rs:529 src/app/layout.rs:17 1.000`. `./pin --selftest` is not a flag (`selftest` subcommand).

### held — PARK ancestor

N5 U3 P5 C4 E5 V2. Contiguous eras a predicate held; not one bisect cut.

Rent vs `git log -- path` is real. Daily form is holt. `--boolean` stays.

Evidence: sitbone `git log -- Sources/SitboneUI/FocusRiverView.swift` empty; `./held exists` first-parent FALSE 31 with `--full` hint; `--full` TRUE 11 / FALSE 78, now=FALSE.

### plait — PRESERVE

N5 U3 P5 C4 E5 V3. Composition algebra of review-suggestion strands (COMMUTE / STACK / ECHO / SPLIT / SUBSUME / JAM), not occupancy against a tree.

Mutate: `--occupy` NFC keys (tilde) as a flag; `--apply` write the topo patch. DESTROYER_PLAIT: ECHO is image-identity; empty markdown before is SPLIT; inverted clock + both-images looks `same-tree`. COMMUTE and JAM survive.

Evidence: `--selftest` 23/23; `fixtures/cli-pr7.json` → COMMUTE `#333030758@347` × `#333031216@400`, one PARALLEL plait.

### berth — KILL product

N4 U2 P4 C4 E5 V2. `--follow` occupies a file identity from the *walk’s* name-status.

DESTROYER_BERTH + this session: default first-parent `exists deep-research-ai-agent-hooks.md` is never-held (merge added dest as A, no R on mainline). The pitch is false. Copy-vs-rename still holds (C is not follow). holt is the vehicle.

Evidence: berth dead-name FALSE 24/24; holt same query identity stitch TRUE 187/244.

### lien — PARK → noun

N3 U4 P4 C5 E5 V2. `git diff \|` CI gate on leftovers of that change’s natal record; dest-line, silent on success.

The CLI shape is right. DESTROYER_LIEN: two packages named `version` are one noun, so kizu `plugin.json` 0.3.0 is a homonym of Cargo `0.6.0→0.7.0` and CI is green. Sitbone `e9b0f75` both-rows still fail (this session, 12 current liens, CLAUDE.md:329/332). Install noun.

Evidence: `./lien self-test` 55 ok; sitbone pipe prints CLAUDE.md both-rows; kizu `9349dc5` lien rc=0.

### tacit — PARK → preen

N5 U4 P5 C4 E5 V2. A defaulted slot is TACIT / SHADOW / OVERRIDE / BOUND; a default-moving diff is BLAST / FOSSIL.

Object is omission. 27 TACIT `presentThreshold` is the money shot. DESTROYER_TACIT: unfold reads `Foo`’s *signature*, not `Thresholds(driftDelay: 20)`; clap TACIT is a command-shaped line (comments). preen closed both and kept the gold.

Evidence: `--selftest` ok; `--summary presentThreshold` on sitbone → TACIT=27 SHADOW=0 OVERRIDE=0 BOUND=0.

### beck — PRESERVE

N5 U3 P5 C4 E5 V3. Earliest pipeline stage whose output already contains this needle; name fd, mint/carry/wrap, earlier pieces.

`tee \| grep` is the wrong object on unpiped stderr and on `jq` wraps. Weekly, not daily. DESTROYER_BECK: `$()` is one outer stage; mid-command `2>&1` is stdout; greedy cover of `kizu@0.7.0` steals `@0.7.0` from `notify-debouncer-full`. innard / facet harvest those.

Evidence: `--selftest` 14/14; `--needle 'fatal: not a git repository' --sh 'git -C /tmp status | cat'` → MINT stage 0 **stderr**, tee MISS.

---

## Gen3 peels

All harvested Keep by their authors. This jury does not rubber-stamp that. A peel that closed a destroyer lie on the *install* lineage is harvested. A peel that is a new CLI for a niche object is a toy.

| peel | of | N | U | P | C | E | V | Σ | verdict | this-session / cite |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **holt** | berth | 4 | 4 | 5 | 4 | 5 | 3 | 25 | **KEEP PATH** | dead name = dest name = 187/244; berth never-held |
| **noun** | lien | 4 | 4 | 4 | 5 | 5 | 3 | 25 | **KEEP PATH** | kizu `9349dc5` plugin.json rc=1; lien rc=0; origin Cargo.toml not lockfile |
| **preen** | tacit | 4 | 4 | 5 | 4 | 5 | 2 | 24 | **KEEP PATH** | `--selftest` ok; same 27 TACIT; PinProfile OVERRIDE 20 not TACIT 15 |
| **innard** | beck | 4 | 3 | 5 | 4 | 5 | 2 | 23 | harvest | `--selftest` 27/27; `echo $(printf kizu \| tr k K)` WRAP inner `tr` |
| **seed** | peal | 3 | 3 | 4 | 5 | 5 | 2 | 22 | harvest | `let b_side` gold; `return None;` bag = 9 stacks refuse |
| **stile** | weld | 3 | 3 | 4 | 5 | 5 | 2 | 22 | harvest | `--selftest` ok |
| **solder** | weld | 2 | 3 | 5 | 5 | 4 | 1 | 20 | PARK reimpl | DESTROYER_WELD behavior rebuilt; not a product |
| **binom** | smolder | 4 | 3 | 4 | 4 | 4 | 3 | 22 | flag on noun | package-scoped falsifier; cite CANDIDATE kizu plugin vs Cargo |
| **tilde** | braid | 3 | 2 | 3 | 4 | 4 | 2 | 18 | flag on plait | NFC keys; covering is of the nits |
| **lurch** | scarp | 4 | 1 | 3 | 4 | 5 | 2 | 19 | KILL product | selftest 10/10 Darwin; DILATE then SLEEP both survive |
| **shim** | xref | 3 | 2 | 3 | 4 | 4 | 2 | 18 | PARK | getenv allowlist + rustup hop |
| **shoal** | keel | 3 | 1 | 3 | 3 | 4 | 2 | 16 | KILL product | origin cannot be typed into `git remote add` |
| **rune** | gist | 3 | 2 | 3 | 4 | 4 | 2 | 18 | PARK | UTF-16 `character` + origin `diagnostics: []` |
| **proxy** | vow | 3 | 2 | 3 | 3 | 4 | 2 | 17 | PARK | follow expected=name |
| **hydra** | ford | 4 | 2 | 4 | 3 | 4 | 2 | 19 | PARK | k-of-n at a merge |
| **badge** | maiden | 4 | 2 | 4 | 3 | 4 | 2 | 19 | PARK | (suite, class, method); flakyFailure is red |

UNVERIFIED this session (cite author/destroyer; Empirical still 4 where those already PASS): binom, tilde, shim, shoal, rune, proxy, hydra, badge, solder `./demo.sh`. lurch/seed/stile/holt/noun/preen/innard were run.

---

## Suggested mutations (only for PATH / preserve)

Do not spend leftover slots on a sixth inverse-printf, a second leftover-name search, pin origin cryptography, or clock-cut dashboards.

1. **invert** — harvest stile’s distinctive static + solder’s expr-first concat as flags. Keep the stream. Refuse binary stdin (DESTROYER).
2. **winnow / cinch** — keep two predicates. cinch: empty-suite banner not exit 5; `--base origin/main` as the PR verb.
3. **zanei / noun** — zanei stays the human filter; noun stays `git diff \|` with `(package, noun)`. `noun --blame` eats binom.
4. **when** — `--under` / `--same-as` absorb ambit/seed. Default refuse a bag of stacks.
5. **preen** — `--emit` rewrite TACIT→SHADOW (pin the current default). Config-key TACIT (`impl Default` vs omitted TOML) is the next real object, not more clap regex.
6. **holt** — `--now` leftover-vs-dest is already the v2 fix; `--first-parent` stays opt-in. hydra k-of-n as `--lattice`.
7. **plait** — `--occupy` NFC (tilde) optional; do not merge with sate.
8. **beck** — harvest innard inner stages; facet field-cover so `kizu@0.7.0` is not `notify-debouncer-full@0.7.0`.

---

## Evidence of run (this session)

All from original worktrees under `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/`. Originals not mutated. Dogfood: `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone}`.

| tool | command | result |
| --- | --- | --- |
| invert | `--selftest`; live kizu timestamp paste | selftest ok; `revert.rs:46` via=span |
| winnow | `./demo.sh` | all demo cases passed |
| cinch 0.3 | `--version`; `python3 -m unittest discover -s tests -q` | `cinch 0.3.0`; 15/15 OK |
| zanei | `self-test`; sitbone `e9b0f75` `--min-score 70` | self-test ok; 2 CLAUDE.md afterimages |
| when | `parse.rs:60 --explain`; `layout.rs:17` | depth=5 `let b_side`; depth=0 fingerprint |
| ambit | `rg -n 'return None;' parse.rs \| ambit --kind given 'a/'` | `here let b_side` under `given a/` |
| pin | mint `src/app.rs:529@b4e6a5d`; resolve HEAD | `moved … layout.rs:17 1.000` |
| held | sitbone `exists FocusRiverView.swift` ± `--full` | git log empty; `--full` TRUE 11 |
| plait | `--selftest`; `fixtures/cli-pr7.json` | 23/23; PARALLEL COMMUTE |
| berth vs holt | kizu `exists deep-research-ai-agent-hooks.md` | berth never-held; holt 187/244 either name |
| lien vs noun | kizu `git diff 9349dc5^ 9349dc5 \|` | lien rc=0; noun rc=1 `plugin.json:4` origin `Cargo.toml:3` |
| tacit / preen | `--selftest`; sitbone `--summary presentThreshold` | both 27 TACIT 0 SHADOW |
| beck | `--selftest`; git fatal pipe | 14/14; MINT stderr, tee MISS |
| innard | `--selftest`; `echo $(printf kizu \| tr k K)` | 27/27; WRAP inner `tr` |
| seed | `rg let b_side \| seed`; `rg return None \| seed` | gold `:60`; 9-stack refuse |
| stile | `--selftest` | ok |
| lurch | `selftest` | 10/10 Darwin |

Live contrast that changed a keep:

```
$ git -C kizu diff 9349dc5^ 9349dc5 | lien -C kizu
# silent  rc=0

$ git -C kizu diff 9349dc5^ 9349dc5 | noun -C kizu
plugin/plugin.json:4: claim: crate:kizu VERSION  0.6.0 → 0.7.0: "version": "0.3.0",
# rc=1
```

```
$ berth -C kizu exists deep-research-ai-agent-hooks.md
FALSE  24 commits   hint: rerun with --full

$ holt -C kizu exists deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/deep-research-ai-agent-hooks.md
TRUE   13 + TRUE 174   now=TRUE  true=187/244
```

---

## What this judge is not doing

- Not picking a single winner. Invert is not "the" tool. Cinch is not "the" tool. The night produced **several Unix verbs**.
- Not grading polish. cinch 0.3’s CLI is younger than unfmt-08 and still PATH, because the lockset object is the one a reviewer wants.
- Not keeping two occupancy CLIs, two natal CI gates, two tacit classifiers, or five inverse-printf filters.
- Not killing held / when / preen / holt / noun for being strange. They already paid rent.
- Not installing lurch, shoal, hydra, rune, shim, badge, proxy, tilde, or berth as products. Dogfood > novelty theater.
- Not rewriting any tool.

Next: install the eight. Harvest peels into them. Do not invent a ninth leftover-name search or a sixth inverse-printf walker.
