# FIRST HERETIC — first selection

Source: CANDIDATE.md under `lab/lineages/`, plus `lab/judges/{DISTINCT,GHOST_CLUSTER,UNFMT_BAKEOFF,DESTROYER_PIN_INVERT}.md`, SHIPS/WAVE notes. This judge did not re-run binaries. Empirical 4 cites a real-repo transcript in CANDIDATE plus a parent/demo note; 5 requires an independent later judge (bakeoff / destroyer). UNVERIFIED means README-only.

Mandate: keep the *object* a developer has not typed before. Kill conventional even if they would use it tomorrow. CLI polish, demo count, and “it found a leftover name” do not save you.

Axes: Novelty / Utility / Primitive / Composability / Empirical / Evolution. Integer 0–5. Novelty is the veto: a 5 on utility cannot buy a keep if the object is ddmin, knip inverted, `ldd`, or `git apply --check` with extra flags.

---

## The objects that must live

Twelve objects. Vehicles named. Do not collapse to one winner.

| # | Object (not the CLI) | Vehicle | Also-carry (same object) |
| --- | --- | --- | --- |
| 1 | Path-condition **stack**, including fallthrough `given` | **when** | chime (rhyme), under (invert) |
| 2 | Occupancy **tenure**: TRUE splits when the holder set changes | **perch** | held (`--boolean`), dwelt (proof) |
| 3 | Two trees emit the **predicate you would have typed** | **tell** | |
| 4 | Inverse printf that **binds names**; leftover prefix is a **span** | **invert** | sluice (stream shape); stencil (walker spare) |
| 5 | A **pin token** is the address; `path:line` is refused | **pin** | |
| 6 | **Natal cohort** of a change; keys inflect (`t1`↔`driftDelay`) | **erst** | also (FILE:LINE), owe (exact keys) |
| 7 | Leftover **claims** a diff just made false (not leftover names) | **zanei** | |
| 8 | Current tests spliced onto **old production** | **alibi** | veil (LIVE/VEIL/BARE) |
| 9 | Oracle verdict is a **substitution**, not a bool | **lees** | |
| 10 | Hunk occupancy: APPLIED / PENDING / MIXED / DUPLEX / SUPERSEDED | **sate** | |
| 11 | Generation **receipt** as testimony; a clutch git never recorded | **clutch** | kiln (same lot) |
| 12 | The interval after `waitpid` until the machine is still | **coast** | cling (attach, do not spawn) |

A thirteenth that is not a family of the above: **sow** — production **argument worlds** as a fixture stream (not a tilt report). Carry it. cleave dies.

---

## Survivors, scored

Primitive restated in one sentence. Decision. Mutation. Evidence.

### when — condition stack

N5 U4 P5 C4 E4 X5. **Keep.**

The object is the nested predicates still in force at `file:line`, including the negation of early returns as `given`. `git diff -W` names the function. Debuggers answer dynamically. Nobody answers it statically as a Unix question-word.

Evidence: kizu `src/git/parse.rs:60` after v2 is four `given` frames (`¬(len<5+2)`, `inner.is_multiple_of(2)`, `bytes.starts_with(b"a/")`, `b/` separator) then `let b_side`. sitbone `PresenceArbiter.swift:81` is `guard isEnabled`. voidtrace `compare.ts:84` is `given actual.has` / `given expected.has`. WAVE2 parent demo PASS. DISTINCT already ranked this.

Mutate: infer `given ¬(P)` for fully-exiting *nested* ifs (the quoted-form miss). Overlay unapplied `--diff` on the post-image. Do not add a TUI.

### chime — control-flow rhyme

N5 U3 P5 C4 E4 X4. **Mutate of when, not a second product.**

Same object, third verb: loci whose effective `(kind, pred)` stack is identical or a prefix-superset. `comm(1)` for path-conditions.

Evidence: `chime kizu/src/git/parse.rs:60 --explain` → same `:60`, deeper `:61-62 return None`, deeper `:64 Some(bytes_to_path(a_side))` — not the closing `}`. Direction is the verb: `:54` lists `:60` as deeper; `:60` does not list `:54`.

Kill the moment it becomes `under --same-as` without exact/superset labels.

### under — invert the stack query

N4 U3 P4 C4 E3 X3. **Mutate of when.** Name a predicate, emit the lines. Needed so `when` is not only “I already know the line.” Token-boundary + polarity is load-bearing (v1 hit `unknownID` ⊂ `unknownSelectionUnitID`).

### perch — tenure

N5 U4 P5 C3 E4 X4. **Keep.**

`held` compresses a boolean. Occupancy that never dies while the holder becomes README is a *different lie* than bisect. The object is who is currently holding a still-true fact.

Evidence: `perch -C skills grep preact-zero-mock` → TRUE 21 (SKILL.md) / TRUE 10 (README+SKILL) / TRUE 16 (README only) with `ghost: definition left`. `held`/`--boolean` reports one 47-commit TRUE whose witnesses start at the definition; HEAD does not have that file. sitbone `FocusRiverView` splits when NotchOverlay starts and stops naming the type (`kind=shrink`, not ghost). WAVE3 names this split. demo 57 assertions, exit 0.

Mutate: `--follow` so rename is one perch. Pipe `tell A B | perch --range A..main`.

### held / dwelt — boolean occupancy (ancestor)

N4 U4 P5 C4 E5 X3. **Keep as `--boolean`, not as the product.**

The founding interval object. sitbone `git log -- FocusRiverView.swift` is empty; `held --full exists` is TRUE 11 / FALSE 78. Parent demo 33/33. dwelt rebuilt from behavior and matched, then beat held on kizu merge-birth (`e1098c8` vs the merge). That is proof the object is real, not a reason to ship two walkers.

### tell — inverse occupancy

N5 U3 P5 C4 E4 X4. **Keep.**

You do not know the question. Two snapshots emit the shortest unary predicates that split them. Diff is a file list. Bisect/held need you to already know what to grep.

Evidence: after the CJK-ngram kill, `tell -C sitbone --cover 14b1d6e^ 14b1d6e` → `grep FocusRiverView` / `exists *FocusRiverView*`. Death certificate of the same path is the same predicate, opposite side (`70ec7df`). voidtrace refuses `breakpoint` because it is already true on A; emits `finite-breakpoint-analysis`. Parent demo PASS.

Mutate: occupancy-greedy cover must never beat a name (`site` vs `SiteObserver` was v1). Emit held-shaped predicates only.

### invert — named holes + span

N5 U4 P5 C5 E5 X4. **Keep. Lineage vehicle for inverse-printf.**

Runtime string on one channel, templates on the other, no walk. `{idle}=12`. A timestamp wrapper is a reported span, not a discarded prefix. Silently stripping the wrapper (sluice/unfmt) made `--exact` meaningless.

Evidence: UNFMT_BAKEOFF 5/5; demo 46/46; sitbone 7-hole Logger binds all seven names at score 1.10; camera nested-quote binds `{self.isCameraEnabled}=enabled`; kizu paste reports `prefix: 2026-08-19T23:50:01Z ERROR` `span=27-64`; `--exact` refuses it. DESTROYER: keep and mutate (no-hole prefix outranks a holed template; rustc is a different grammar; concat is not a template; truncated paste misses).

Mutate: span leftover as the *next* query (template chain). No-hole prefix must not beat a hole that binds. Refuse compiler-diagnostic streams. Do not grow a walker.

Kill unfmt-08, unfmt-13, sluice-as-product. stencil stays a walker spare. moor is composition, not an object — **kill** (see below).

### pin — the token is the address

N4 U4 P4 C4 E4 X5. **Keep.**

Mint once. Resolve takes no `path:line` and no origin SHA. Tickets cannot hold `slip --from b4e6a5d src/app.rs:529`.

Evidence: `pin resolve` of a locator exits 2. kizu `src/app.rs:529` → `src/app/layout.rs:17` from stored `pin1.…` with no path. `git log --follow -L` still refuses the split. DESTROYER: leftover stub at the old path scores 1.000 and steals the pin; identical helpers emit 1.000 twice; missing `--to` looks like deletion; truncated token porcelain-succeeds. Unique kizu tokens do **not** hallucinate onto voidtrace.

Mutate toward DESTROYER: ambiguous (never 1.000 twice); neighbor body beats leftover stub; bind a tree hint; truncated tokens fail closed. NFC-normalize paths. The object remains the token, not a pinfile registry — unless a later mutation proves the reverse.

Kill slip and flume as *products*. They are relocators. Source maps and `blame --reverse` are the conventional cousins. pin is the new object; they can be backends.

### erst — natal cohort from a change

N5 U4 P4 C4 E4 X4. **Keep.**

Siblings born in the introducing commit, unpaid at HEAD, keys allowed to inflect. Not blame, not clone detection, not co-change, not aka (no shared stem).

Evidence: `erst -C sitbone e9b0f75` (never FILE:LINE) → leftover `0.4` tests and ADR `threshold`, paid `presentThreshold: 0.45`. `erst 1fcdec6` → leftover `T1`/`T2` from a lint SHA that renamed `t1`→`driftDelay`. owe is silent when the number did not move. aka cannot pair those names. also needs `PresenceArbiter.swift:33`.

Carry **also** as the FILE:LINE spelling, **owe** as exact-key. Vehicle is erst: reviewers have a SHA.

Mutate: rename-follow; domain tags so `threshold=0.7` in SiteObserver never returns (v2 already dropped it).

### zanei — leftover claims

N4 U4 P4 C5 E4 X3. **Keep.**

A *fact* is a bound name/value, rename, or polarity from a unified diff. An *afterimage* is a remaining line that still asserts the old fact. This is not leftover *names* (wraith/haunt). `rg` does not know this diff changed `0.3.0 → 0.7.0`.

Evidence: kizu `Cargo.toml` 0.3.0→0.7.0, `plugin/plugin.json` still `"version": "0.3.0"`. sitbone hysteresis v1: 11 afterimages including SiteObserver homonym; v2: 2 real CLAUDE.md pre-hysteresis tests. voidtrace 3670 → 0. Parent demo PASS. GHOST_CLUSTER already called this the strongest leftover, correctly, because the object is claims.

Do not grow a review platform. Mutate: typed facts (version, threshold) over prose remames.

### alibi — new tests on old production

N5 U3 P5 C3 E3 X5. **Keep.**

TDD assumes the new tests go red on the old production tree. CI runs tests on HEAD. `git stash -k && test` reverts the new tests too. Coverage says a line executed. Mutation testing perturbs operators. alibi perturbs *your actual production diff* and keeps tests at *new*.

Evidence: self vs `fa08ea3` LOCKED on the new tests; `--per-path` splits `alibi.py` LOCKED / `demo.sh` LOOSE. kizu dirty `AGENTS.md` honestly CLEAN (docs are not production). **Did not** splice `cargo test` / `swift test` on kizu/sitbone/voidtrace source diffs (CANDIDATE says so). Empirical capped at 3.

Mutate: per-hunk overlay. Join **lees** on the splice failure (LOCKED-and-MACHINE vs LOCKED-and-SPEC). Run one real cargo/swift splice before anyone calls this useful.

### veil — cover-type

N4 U3 P4 C3 E3 X4. **Mutate of the test-truth family, keep the object.**

LIVE / VEIL / BARE. alibi can call a mocked SUT LOCKED (delete the function, the mock setup still needs the module). veil is the static question: is the test looking at the new body, or at a fake?

Evidence: soul-writer `vi.mock('./cerebras.js')` VEIL on `formatLastError` / `getRetryAfterMs` while `CerebrasClient` is LIVE. kizu HEAD~5 BARE flood on a file-split (582). tenaoshi `Tests/` misfiled as production in v1.

Mutate: public/`export` names as the review object (the planned v2). Do not drown in unexported helpers.

### lees — substitution verdict

N5 U3 P5 C4 E4 X5. **Keep.**

Empty residue means the test is not failing — the machines differ. `diff` does not know `$HOME`. Snapshot serializers normalize going forward; they do not audit goldens you already committed.

Evidence: `--par` alice vs runner → `verdict=MACHINE`, PATH/CLOCK substitutions, empty residue. Same pair with `timeout: 60` vs `30` → MIXED/SPEC. sitbone v1 TAINTED on `annenpolka` in a GitHub *window-title fixture*; v2 `kind=fixture`, `--check` 0 (25 clean). kizu `--foreign`: 46 `/home/user` path oracles, `--check` still 0. demo 24/24.

The surprise is the object: recording leak vs identity-as-data. Mutate: `--visa` (machine condition as a skip predicate). Join alibi.

### sate — patch occupancy

N4 U4 P5 C4 E4 X4. **Keep.**

`git apply --check` is a boolean lie. A hunk has two images. MIXED / DUPLEX / SUPERSEDED are occupancies. Review ` ```suggestion ` is the same sandwich.

Evidence: occupancy sandwich `sate --git C --against C` APPLIED, `--against C^` PENDING — held on kizu/sitbone/relico first try. v1 false-DUPLEX on pure additions (voidtrace 21, tenaoshi 3); v2 prefix rule, unanimous. kizu `--log 8`: `88362116` SPLIT PENDING=1 SUPERSEDED=1 (`Cargo.toml` now 0.7.0, one lockfile hunk still PENDING). voidtrace ancestor PENDING = HEAD restored a preimage (revert without a revert commit). demo 31/0.

Mutate: `sate log --pick SUPERSEDED` as a patch. Assay (oracle expected-values as RATCHET/FLIPFLOP) is a different object — do not fold it in.

### clutch — generation testimony

N4 U4 P4 C3 E4 X4. **Keep.** kiln is the same object (convergent); do not ship both.

The colophon the artifact already carries is the object. Files that cite the same parent are one generation event git never recorded. `ninja -d explain` needs a graph. `spec-check` regenerates. clutch cross-examines without firing.

Evidence: voidtrace one clutch, ages 0–28, `AI_UX.md` COLD 28, stamp-join of `capabilities.generated.json`. relico RAGGED 0–4 (unit/e2e COLD, SPEC.md FRESH) on a clean git tree. kiln independently: same relico eight-day split, BLIND `patterns.pkl`, content reasons not mtime. Negative: kizu/sitbone/skills 0 lots.

Vehicle: clutch (receipt as testimony). Harvest kiln’s content-reason `why` and BLIND undeclared imports. Kill yoke (spec-check with extra polarities).

### sow — production worlds as fixtures

N4 U4 P4 C4 E4 X4. **Keep.**

Coverage cannot phrase a missing *value*. cleave printed tilts both ways. sow kills the comparison: production inhabitance minus what tests already pin, emitted as generator input. Test-only worlds silent.

Evidence: sitbone `isBrowser` six untested browser names as `{appName="Brave Browser"}` stubs. `SiteObserver.record` `{duration=1}` — tests use 5..300, never 1. kizu `run_split_command` four terminal backends vs tests’ `"sh failing split"`. v0.2: Rust lifetime `'a` no longer swallows `prompt.rs`; `#[cfg(test)]` literals are not production worlds.

Kill **cleave** (the report). Mutate: mixed-world emit is already v2; next is a real test-generator consuming the NDJSON.

### coast — post-waitpid interval

N5 U3 P5 C4 E4 X4. **Keep.**

Developers write `sleep 2` after tests. Unix gives `waitpid`. The missing object is the side-effect cloud: late writes, stragglers, intra-run generations, until the machine is still.

Evidence: `Popen.communicate()` after waitpid *swallowed the coast* (children inherit stdout). `--root .` showed COAST 0.000s because every interesting write was under `TMPDIR`. After `--isolate-tmp`: `tmp_late.py` COAST 0.368s, HAZARD `secret.bin`, straggler argv via lsof not `(Python)`. Nested coasts are layers; inner wait is happens-before.

Carry **cling**: attach to a pid you did not spawn; SIGINT reports the same wake without killing the subject. Kill spoor-as-product (spawn wrap is the conventional shape). Kill pinch/hitch as products; **knot** harvested the wait-for graph — park it for the Unix judge. `clot` (streaming vs batch from byte-arrival) remains the interesting unbuilt mutation.

### stint — ephemeral occupancy + last blob

N4 U3 P4 C3 E4 X3. **Mutate of occupancy, keep `--pick`.**

Files born and killed between two refs, invisible in the net diff, plus the last body. Not remnant names (wraith). `held exists PATH` needs the path. `git checkout DELETE^ -- PATH` needs the death.

Evidence: skills `preact-zero-mock` occupied 31 vs `circuit-breaker` 6 vs `scout.sh` 1; `--pick circuit-breaker/` restores blob `de055581`. sitbone `FocusRiverView.swift` occupied 11, matches held without naming the path. kizu 244 commits: 0 ephemeral *files* (honest).

Kill wisp remnants. Keep `--pick` as recover-lost-work for unnamed interval ghosts.

---

## Killed because conventional (even if useful)

Novelty ≤ 2 unless noted. Utility is not a defense.

| Tool | Object, honestly | Why dead |
| --- | --- | --- |
| **winnow / glean** | ddmin on the dirty tree | The most useful tool of the night. 1970s algorithm. Toolsmith’s winner. Heretic kill. |
| **aka / sic** | inflection pact / exact wire key | Developers have renamed all casings. `--check` on a patch is a linter. sic is sharper; still not unseen. Park sic for Unix, do not spend Gen-3 slots. |
| **slip / flume** | relocatable `file:line` | Source maps, `blame --reverse`, patch fuzz. The new object is the **pin**. |
| **unfmt-08 / unfmt-13 / sluice** | inverse printf as a walker or anonymous filter | Convergent and real. The new object is **named holes + span** (invert). Do not keep two walkers (UNFMT_BAKEOFF). |
| **moor** | one-pass slip × unfmt | Composition. Demo case neither parent gets right is still two objects in a trenchcoat. Kill. |
| **haunt / wraith** | inverse dead-code; leftover names | knip inverted. Compiler-ignored fringe is a search. GHOST kept wraith; heretic keeps **zanei** (claims) and kills names. haunt already lost `preact-zero-mock`. |
| **wisp remnants** | leftover names of interval ghosts | Same cluster. Occupancy half survives as stint. |
| **reverb** | preimage of a diff as a search query | Adjacent to clone-detect + `git grep` of the minus lines. tenaoshi header-line hit is real and still conventional. Kill. |
| **folk** | unwritten call-pair handshakes | Honesty filter: 0 real orphans. DISTINCT parked. Kill. |
| **nigh** | string-edit distance to branch cuts | `ENOENT`≈`event`. **cusp** (value on the cut: 401/400, exclusive 3) is the leftover column — **mutate cusp**, kill nigh. |
| **akin** | similarity merge-base | Clone detection + `merge-file`. **once** (exact blob identity, ever-held) is smaller and still git. Park once; do not evolve similarity. |
| **rift / zure** | identifier conflicts a clean merge accepts | Semantic-merge research. Useful pre-commit. Not an interaction nobody has imagined. Park zure for Toolsmith. |
| **unseen / skew** | caller-file clock vs callee | Temporal blame of the other file. **doze** (`--check` on sleeping *signatures* only) is the only CI-shaped remainder — park, do not rank. |
| **cleave** | test vs prod inhabitance *report* | sow is the interaction (emit fixtures). A tilt sentence is a dashboard. |
| **due / lode / orbit** | env ABI / `ldd` of getenv / guise vs payload | `strings` + `ldd` + `which`. orbit’s rustup/xcselect/SIP filter is the least conventional of the three and still a dump. Park orbit; kill due/lode. |
| **yoke** | spec-clause polarity vs generated | spec-check with more words. clutch/kiln already occupy testimony. |
| **pinch / hitch / knot** | wait-for graph | `offcputime`, `strace`, `pstree`. knot is a good harvest; Unix may keep it. Heretic object is **coast** (waitpid is a lie), not the graph. |
| **spoor** | residue, but you must be the parent | spawn-wrap is `time` with extras. cling flipped the assumption. |
| **deja** | RELAPSE / UNDOFIX / RESURRECT | Closest conventional cousin: `git log -S` plus “was this a fix.” v2 got quieter; the scoring of *this* diff against memory is real and still too close to review-bot déjà vu. **Park** (not cluster-kill). Mutate only if UNDOFIX can beat move/split without a 217-finding firehose. |
| **stencil / dwelt** | clean-room reimpls | Proofs, not products. stencil beats unfmt-08 on camera; invert still carries. dwelt beats held on merge-birth; perch carries. |

**cusp** (N4): value sitting on a predicate’s cut, not spelling. voidtrace/sitbone unconstructed discriminants after nigh’s lexer noise died. **Mutate** (keep the cut, never bring NIGH string distance back). Not a top-12 object because it is still “static analysis of comparisons,” which developers have seen — the join (constructed value × bound) is the only new column.

---

## Disagreements

### vs DISTINCT (early critic)

| DISTINCT | Heretic |
| --- | --- |
| slip in top 6 | slip is a relocator. **pin** is the object. |
| unfmt → sluice | sluice is the stream. **invert** (names + span) is the object. |
| held in top 6 | held is the ancestor. **perch** (tenure) and **tell** (inverse) are the heresies. |
| also in top 6 | also needs FILE:LINE. **erst** takes a SHA and inflects natal keys. |
| unseen in top 6 | temporal blame. Kill. |
| when in top 6 | **Agree.** |
| winnow keep-not-top | **Kill.** Utility is the trap. |
| aka keep | Park. Inflection pacts are seen. |
| folk park | Kill. |
| do not reimplement ghost-name search | **Agree**, and go further: kill wraith too. |

### vs GHOST_CLUSTER

One ghost survivor was wraith, plus zanei. Heretic: leftover *names* are inverted knip. Leftover *claims* (zanei) and leftover *occupancy* (perch ghost tenure, stint `--pick`) are different objects. haunt stays dead.

### vs UNFMT_BAKEOFF

Carry invert. Agree. Add: the battery’s 5/5 is not why invert lives. It lives because the leftover prefix became a span and holes kept names. DESTROYER’s no-hole-prefix ranking failure is the next mutation, not a kill.

### vs DESTROYER pin × invert

Mutate, do not kill. Agree. Stub-steals-pin and 1.000-twice are conceptual; the token is still the object. Invert’s rustc false bind is a different grammar — refuse it, do not teach invert compiler diagnostics.

### vs Toolsmith (predicted)

Toolsmith will save winnow, aka, slip, unfmt-walker, rift/zure, glean. Those are tomorrow’s commands. They are not new interactions. Let that judge keep a working set. This judge will not.

### vs Unix (predicted)

Unix will love invert, when, tell, sate, pin, coast-as-`wait`. Agree on invert/when/tell/sate/pin. Unix may prefer knot over coast; heretic does not — a wait-for graph is a known picture, a named coast is not.

### vs Skeptic (predicted)

Skeptic will call lees, clutch, chime, erst, alibi unproven. Partial credit: alibi has no real cargo/swift splice (E3). lees and clutch have real-repo numbers. Do not wait for polish to keep the object.

---

## What I am not ranking on

- Line count, README length, `--json` completeness.
- Convergent evolution as a merit badge (unfmt×2, kiln×clutch). Convergence means the object is real; pick one vehicle.
- “It found `preact-zero-mock`.” That string is a shared fixture, not a primitive.
- Ghost-name search of any spelling.
- Hybrids that do not change the object (moor, knot-as-product).

---

## Suggested Gen-3 spend (heretic slots)

Spend on objects, not polish.

1. **when**: nested-exit `given`; chime exact-arm as `--same-as` (do not fork a third binary forever).
2. **perch × tell**: `tell A B | perch --range` — emit the predicate, then walk who held it.
3. **invert**: span leftover → next template; no-hole prefix must lose to a binding hole.
4. **pin**: DESTROYER list (ambiguous, leftover stub, fail-closed tokens). Not a pinfile product.
5. **erst**: domain tags; SHA in, unpaid inflected kin out.
6. **alibi × lees**: splice, then substitution-verdict the failure. One real `cargo test` splice.
7. **clutch**: harvest kiln `why` (content + BLIND imports). One binary.
8. **coast**: `coast wait` as the replacement for `sleep 2`; cling attach. Not another process-tree TUI.
9. **sate**: `--pick SUPERSEDED`.
10. **sow**: NDJSON consumed by an actual generator, not prettier tilts.

Do not spend slots on winnow grain, aka inflection tables, slip stream dialects, wraith ignore lists, or a second inverse-printf walker.

---

## Compact scoreboard (vehicles + notable kills)

N U P C E X. Sum is not a ranking — Novelty vetoes.

| ID | tool | N | U | P | C | E | X | Σ | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| c-20 | when | 5 | 4 | 5 | 4 | 4 | 5 | 27 | KEEP object |
| m-16 | chime | 5 | 3 | 5 | 4 | 4 | 4 | 25 | mutate of when |
| m-10 | under | 4 | 3 | 4 | 4 | 3 | 3 | 21 | mutate of when |
| m-17 | perch | 5 | 4 | 5 | 3 | 4 | 4 | 25 | KEEP object |
| c-09 | held | 4 | 4 | 5 | 4 | 5 | 3 | 25 | `--boolean` ancestor |
| r-02 | dwelt | 3 | 3 | 5 | 4 | 5 | 2 | 22 | proof, not product |
| m-03 | tell | 5 | 3 | 5 | 4 | 4 | 4 | 25 | KEEP object |
| m-18 | stint | 4 | 3 | 4 | 3 | 4 | 3 | 21 | mutate occupancy; keep `--pick` |
| m-15 | invert | 5 | 4 | 5 | 5 | 5 | 4 | 28 | KEEP object |
| m-02 | sluice | 3 | 4 | 4 | 5 | 5 | 2 | 23 | stream shape only |
| c-08 | unfmt | 3 | 4 | 4 | 3 | 4 | 2 | 20 | KILL walker |
| c-13 | unfmt | 3 | 4 | 4 | 3 | 4 | 2 | 20 | KILL walker |
| r-01 | stencil | 3 | 4 | 4 | 3 | 5 | 2 | 21 | walker spare |
| h-01 | moor | 2 | 4 | 3 | 4 | 4 | 2 | 19 | KILL composition |
| m-14 | pin | 4 | 4 | 4 | 4 | 4 | 5 | 25 | KEEP object |
| c-16 | slip | 2 | 5 | 3 | 4 | 4 | 2 | 20 | KILL (relocator) |
| m-04 | flume | 2 | 4 | 3 | 5 | 4 | 2 | 20 | KILL (relocator stream) |
| m-19 | erst | 5 | 4 | 4 | 4 | 4 | 4 | 25 | KEEP object |
| c-10 | also | 4 | 4 | 4 | 4 | 4 | 3 | 23 | FILE:LINE spelling |
| m-06 | owe | 4 | 4 | 4 | 4 | 4 | 3 | 23 | exact-key spelling |
| c-07 | zanei | 4 | 4 | 4 | 5 | 4 | 3 | 24 | KEEP object |
| c-24 | alibi | 5 | 3 | 5 | 3 | 3 | 5 | 24 | KEEP object |
| c-32 | veil | 4 | 3 | 4 | 3 | 3 | 4 | 21 | mutate; keep cover-type |
| c-31 | lees | 5 | 3 | 5 | 4 | 4 | 5 | 26 | KEEP object |
| c-34 | sate | 4 | 4 | 5 | 4 | 4 | 4 | 25 | KEEP object |
| c-27 | clutch | 4 | 4 | 4 | 3 | 4 | 4 | 23 | KEEP object |
| c-26 | kiln | 4 | 4 | 4 | 3 | 4 | 4 | 23 | harvest into clutch |
| m-13 | sow | 4 | 4 | 4 | 4 | 4 | 4 | 24 | KEEP object |
| c-18 | cleave | 3 | 3 | 3 | 3 | 4 | 2 | 18 | KILL report |
| c-25 | coast | 5 | 3 | 5 | 4 | 4 | 4 | 25 | KEEP object |
| m-12 | cling | 4 | 3 | 4 | 3 | 3 | 4 | 21 | mutate of coast |
| c-21 | spoor | 3 | 3 | 3 | 3 | 3 | 2 | 17 | KILL spawn-wrap |
| m-11 | cusp | 4 | 3 | 4 | 4 | 4 | 3 | 22 | mutate (cut, not spelling) |
| c-17 | nigh | 2 | 2 | 2 | 3 | 3 | 1 | 13 | KILL |
| c-15 | winnow | 1 | 5 | 3 | 4 | 4 | 2 | 19 | KILL ddmin |
| m-07 | glean | 1 | 5 | 3 | 4 | 4 | 2 | 19 | KILL ddmin |
| c-02 | aka | 2 | 4 | 3 | 4 | 4 | 2 | 19 | park |
| m-01 | sic | 2 | 4 | 3 | 4 | 4 | 2 | 19 | park |
| c-12 | wraith | 2 | 3 | 2 | 3 | 4 | 1 | 15 | KILL names |
| c-05 | haunt | 1 | 2 | 2 | 2 | 3 | 1 | 11 | KILL |
| c-03 | wisp | 2 | 2 | 2 | 2 | 3 | 1 | 12 | remnants kill; occupancy → stint |
| c-04 | reverb | 2 | 3 | 2 | 3 | 4 | 1 | 15 | KILL |
| c-19 | folk | 2 | 1 | 2 | 2 | 2 | 1 | 10 | KILL |
| c-01 | akin | 2 | 2 | 2 | 3 | 3 | 1 | 13 | KILL similarity |
| m-09 | once | 2 | 2 | 3 | 3 | 3 | 2 | 15 | park exact-blob |
| c-11 | rift | 2 | 3 | 3 | 4 | 4 | 2 | 18 | park |
| m-05 | zure | 2 | 4 | 3 | 4 | 3 | 2 | 18 | park |
| c-14 | unseen | 2 | 3 | 3 | 3 | 3 | 2 | 16 | KILL |
| m-08 | skew | 2 | 3 | 3 | 3 | 3 | 2 | 16 | KILL |
| m-20 | doze | 3 | 3 | 3 | 3 | 3 | 2 | 17 | park signature-check |
| c-06 | deja | 3 | 3 | 3 | 4 | 4 | 2 | 19 | park |
| c-28 | due | 2 | 3 | 2 | 3 | 3 | 2 | 15 | KILL |
| m-21 | lode | 2 | 3 | 2 | 3 | 3 | 2 | 15 | KILL |
| c-30 | orbit | 3 | 3 | 3 | 3 | 3 | 2 | 17 | park |
| c-29 | yoke | 2 | 3 | 2 | 3 | 3 | 2 | 15 | KILL |
| c-22 | pinch | 2 | 3 | 3 | 4 | 3 | 2 | 17 | park for Unix |
| c-23 | hitch | 2 | 3 | 3 | 4 | 3 | 2 | 17 | park for Unix |
| h-02 | knot | 2 | 3 | 3 | 4 | 3 | 2 | 17 | park for Unix |

Sums lie. winnow’s 19 is a useful corpse. when’s 27 is an unseen question-word. Prefer the object column over Σ.

---

## Survivors, restated as interactions a developer has not had

1. `when parse.rs:60` — *when does this line run?* (stack, not function name)
2. `chime parse.rs:60` — *what else is in this arm?*
3. `perch grep preact-zero-mock` — *who is holding this still-true name?*
4. `tell A B` — *what question splits these two trees?*
5. `rg format! \| invert 'the log line'` — *which template, and bind the holes; the timestamp is a span*
6. `pin mint` once, paste `pin1.…` into a ticket, `pin resolve` on whatever tree exists
7. `erst $SHA` — *what natal kin did this change leave unpaid, after the names inflected?*
8. `git diff \| zanei` — *what claims did this diff make false that the tree still asserts?*
9. `alibi HEAD~` — *do these new tests actually go red on the old production?*
10. `lees --par local.snap ci.snap` — *is this failure a spec, or a substitution?*
11. `sate --git HEAD` — *how does this tree occupy each hunk’s two images?*
12. `clutch -C repo` — *were these eggs re-laid together?* (read the receipts, do not regenerate)
13. `sow --emit pytest isBrowser` — *production inhabited Brave; tests never did*
14. `coast wait -- cmd` — *waitpid returned; the machine is not still*

If a later jury needs a short list: **when, perch, tell, invert, pin, erst, zanei, alibi, lees, sate, clutch, sow, coast**.

Kill winnow anyway.
