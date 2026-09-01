# FINAL_NOVELTY — judge-15 (New-primitives)

Isolated worktree. Branch `judge-15-final-novelty`. Never merged to `main`.

**Axis of record is the object.** Polish, LOC, demo count, and “would I type this tomorrow instead of `rg`” are other judges. This one asks: *is there an interaction worth remembering if every Python file tonight is deleted?*

Assigned reading: invert, zanei, held/when, cinch, pin, tacit, beck, vow, scarp, plait, xref DUE-as-proof, maiden never-red.

`held/when` is a coordinator hyphen, not a primitive. They are two objects. They stay two.

This session re-ran selftests and the money-shot probes named in §7. Destroyer / bakeoff transcripts are cited, not rubber-stamped.

---

## 1. Named primitives (one sentence each)

| Verb | One sentence |
| --- | --- |
| **invert** | A runtime string is a query against format templates: bind the named holes and report leftover wrapping as a **span**, never as a discarded prefix. |
| **zanei** | A unified diff makes bound facts false; print the dest-tree lines that still assert the old fact — **belie**, not leftover-name search. |
| **held** | Emit the contiguous **eras** of history where an arbitrary predicate is true, without bisect’s monotonicity or `git log -- path`’s simplification lie. |
| **when** | At a source locus, emit the nested predicates still in force — including fallthrough **`given`** from early-return guards — as a condition stack, not a function name. |
| **cinch** | Given a dirty tree, emit the **1-minimal production hunks the current tests veto** (the lockset): tests stay NEW; the predicate is pass/fail, not a command fingerprint. |
| **pin** | Mint a self-contained locus **token** once and resolve it onto a later tree without re-supplying `path:line`; leftover stubs are pointers, not identity. |
| **tacit** | A defaulted slot is not a value: classify each call-site as **TACIT** (omitted; rides a future default), **SHADOW** (restated the current default; will not follow), OVERRIDE, or BOUND; a default-moving diff is BLAST plus FOSSIL. |
| **beck** | Name the earliest pipeline stage whose stdout or stderr already contains this needle, with its **fd** and whether it minted, carried, or wrapped earlier pieces. |
| **vow** | A failing assertion implies **two oaths** — the expected-literal machine and the actual-side machine — as skip/apply predicates, not one substitution residue. |
| **scarp** | Two clock-cuts on stdin; emit which clock explains the gap (`SLEEP` / `DILATE` / `STEP` / `REST`) without spawning the work. |
| **plait** | Review-suggestion strands **compose with each other** (`COMMUTE` / `STACK` / `ECHO` / `SPLIT` / `SUBSUME` / `JAM`) before anyone occupies a tree. |
| **xref** | The env ABI of a load-image set has two columns, and **DUE is a getenv-shaped use** (a call site), not an env-shaped token in the binary. |
| **maiden** | The never-red set is a **fold over recorded outcomes** of a test identity, not `rg PASS` on the newest log. |

Inflections of the same objects (not extra founding primitives): **`perch`** (held + holder: same TRUE, new witness set, new era), **`under`** (when inverted: name a predicate, emit the lines), **`given`** (the noun `when` discovered — negation of an early return still in force).

---

## 2. Implementations to forget

Forget the *product*. Harvest the one fact it proved. Do not install a second ignore-policy walker, a fourth cinch, or a leftover-name search.

### Inverse printf

| Forget | Why |
| --- | --- |
| **unfmt-08, unfmt-13** | Walkers. UNFMT_BAKEOFF already closed them. Invert is the filter. |
| **sluice as a product** | Stream shape without names. Invert harvested the shape and kept the payload. |
| **stencil as PATH** | Walker spare only. One-shot `-C repo` is a producer (`rg`, `git grep`), not a second kernel. |
| **moor** | slip × unfmt in one trenchcoat. Composition, not an object. |
| **lede, splice, weld, rime, caulk, stile, solder** as PATH entries | Concat / prefix-of-instance / proving-string peels of **one** invert kernel. They flipped real DESTROYER lies; they are not new verbs. |

### Leftover claims vs leftover names

| Forget | Why |
| --- | --- |
| **haunt, wraith, wisp remnants** | Leftover *names*. Different object; already over-bred. |
| **nagori as a second product** | Clean-room of zanei. Transcript, not PATH. |
| **ember / cinder / smolder / sire / helm / tinder** as PATH | Typed-fact / ash / dest→falsifying-diff peels. Keep the inverse *idea* (smolder: which diff falsified this claim). Do not ship six belie binaries. |

### Occupancy and path-condition

| Forget | Why |
| --- | --- |
| **hyphenating held/when** | Time-as-eras ≠ space-as-stack. Collapsing them is how both die into “git helpers.” |
| **dwelt, roost as products** | Reimpls of held/perch. Proof the object is real, not a reason for two walkers. |
| **chime / peal / ambit as extra PATH** | Same-stack rhyme and `rg \|` stream are `when`/`under` inflections. One engine. |

### Lockset

| Forget | Why |
| --- | --- |
| **cinch 0.2** | Test-only red reported CLEAN (occupancy of nothing, rc=0). Timeout minted FAST as wheat. LOCKSET_BAKEOFF. |
| **winnow as the lockset** | Fingerprint wheat. Demo case 1: winnow keeps `print("debug")`; cinch drops it. That is the whole point. |
| **`alibi \| winnow`** | Concatenation. File grain plus fingerprint, not 1-minimal veto. |
| **snug, tock, hasp as PATH** | Reimpl / timeout-peel / PR-range grain. Carry cinch 0.3. No fourth cinch. |

### Durable address

| Forget | Why |
| --- | --- |
| **slip, flume as products** | Relocators. `path:line` in, `path:line` out. pin is the token. |
| **pin v0.1–v0.4 as products** | Leftover stub scored 1.000 (DESTROYER_PIN_INVERT). v0.5 closed extract-and-keep vs stub-as-pointer. Keep the token, not the version zoo. |
| **gist / rune as a second pin** | LSP locator rewrite is flume on a nested document. Backend, not a verb. |

### Default omission, first-producer, oaths, clocks, strands, env ABI, never-red

| Forget | Why |
| --- | --- |
| **`rg foo(` + comma counting** | Loses keywords, Swift labels, unfold, and the only distinction that matters (TACIT vs SHADOW of the same world). |
| **treating tacit as sow or zanei** | Those are values and leftover *claims*. tacit is whether the value was **said**. |
| **aloud / unsay / preen as PATH** | Emit / unfold peels of tacit. |
| **`tee \| grep -n` as beck** | Unpiped stderr is 0 piped bytes; exact grep names the wrap. Live this session: git fatal is `MINT stage 0 stderr`, tee MISS. |
| **facet as a second beck** | JSON field-cover is honesty of pieces, not a new object. Mutate into beck. |
| **visa whole-file; oath expected-only** | Ancestors. vow is the pair. |
| **lees as the same object as vow** | lees is residue (MACHINE vs SPEC). vow is two unary machines. Pipe them; do not merge. |
| **troth / onset / writ / proxy as PATH** | Apply / held-of-actual / locked-expected peels. |
| **lapse as a product** | Spawn-wrapper. scarp is the filter. |
| **twixt / yaw / scree / lurch as PATH** | Stream / slew / repeated-kv / cuts-as-stream peels. Harvest **SLEW** as a missing scarp name (`ntp=` is adjtime, DESTROYER_SCARP). Do not ship four clocks. |
| **plea / sate / lodge as plait** | Occupancy against a tree. plait is composition of the comments. |
| **braid as a second plait** | Occupancy of the *composed* after-image. Hybrid of plait×sate. Keep the fold idea; do not rename plait. |
| **assay DUE; due as one-column strings** | DUE meant “env-shaped bytes exist.” rustc printed 12,596 LLVM opcodes. The column was a flood. |
| **`--loose` as KIND promotion; `COLOR_FORCE` prefix-peel** | Packed/orphan tokens and prefix harvest are search aids, not proofs of use. |
| **lash / wad / shim / prove as PATH** | Wrapper / inlined-CString / rustup-shim / clean-room peels of xref. prove is the reimpl transcript. |
| **`rg PASS` latest.xml; maiden `--latest` as the product** | 2019-fail + 2024-green: `--latest` maidens `pkg.T::alpha`; the fold scars it. Live this session. |
| **census-as-roster; badge as a second maiden** | Identity is (suite, class, method) across rename, not a source `fn` name and not a second binary. Mutate into maiden. |

---

## 3. Verbs to keep

Thirteen founding verbs. Inflect them; do not breed them.

| Keep | Object (remember this word) | Vehicle if anyone ships code | Do not also ship |
| --- | --- | --- | --- |
| **invert** | named holes + span | invert (stream; no walk) | unfmt-*, sluice, lede, splice, weld |
| **zanei** | belie (leftover *claims*) | zanei | haunt/wraith, ember/cinder as PATH |
| **held** | occupancy eras | held `--boolean` | dwelt |
| **when** | condition stack + `given` | when | chime/peal as products |
| **cinch** | lockset | cinch 0.3 | 0.2, winnow-as-lockset, tock, snug, hasp |
| **pin** | token is the address | pin v0.5 | slip, flume |
| **tacit** | omission polarity | tacit | sow, zanei, aloud |
| **beck** | first-producer + fd + pieces | beck | tee\|grep, facet |
| **vow** | expected × actual | vow | visa, oath, lees-as-pair |
| **scarp** | which clock owns the gap | scarp (+ name SLEW) | lapse, twixt, yaw, scree |
| **plait** | strand composition algebra | plait | sate-as-plait, braid-as-plait |
| **xref** | DUE is a use-proof | xref (KIND: DUE/LATENT/BOTH) | assay DUE, due, lash/wad as PATH |
| **maiden** | never-red as a fold | maiden (not `--latest`) | rg PASS, badge as PATH |

Keep as **inflections of the above**, one engine each: `perch` (held + holder), `under` (when inverted), `smolder` (zanei inverted: dest claim → falsifying diff).

Do **not** keep winnow as a novelty survivor. It is useful ddmin. It is not a new object next to cinch. Skeptic’s four-verb PATH (winnow, cinch, invert, zanei) is a tomorrow-test, not a primitives list.

---

## 4. Scores (novelty-weighted)

Axes 0–5 integer: Novelty / Utility / Primitive / Composability / Empirical / Evolution. **Novelty is the veto on “forget the concept.”** Utility cannot buy a keep if the object is `rg` / ddmin / `ldd` / `git apply --check`. A 4+ on Empirical requires a run this session or a named destroyer/bakeoff transcript.

| Verb | N | U | P | C | E | X | Σ | Verdict | Primitive restated |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| invert | 5 | 5 | 5 | 5 | 5 | 4 | 29 | **keep** | instance → template + names + span |
| when | 5 | 4 | 5 | 5 | 5 | 4 | 28 | **keep** | condition stack + `given` |
| tacit | 5 | 4 | 5 | 4 | 5 | 5 | 28 | **keep** | TACIT vs SHADOW of the same world |
| beck | 5 | 4 | 5 | 5 | 5 | 4 | 28 | **keep** | first-producer, fd, pieces |
| plait | 5 | 3 | 5 | 4 | 5 | 4 | 26 | **keep** | COMMUTE/STACK/JAM of strands |
| cinch | 5 | 5 | 5 | 4 | 5 | 3 | 27 | **keep** (0.3) | lockset ≠ fingerprint |
| maiden | 5 | 3 | 5 | 4 | 4 | 5 | 26 | **keep concept; mutate id** | never-red fold, not latest PASS |
| held | 4 | 4 | 5 | 5 | 5 | 3 | 26 | **keep** | eras, not one cut |
| zanei | 4 | 5 | 4 | 5 | 5 | 3 | 26 | **keep** | leftover claims |
| pin | 4 | 3 | 5 | 4 | 5 | 4 | 25 | **keep** | token, not `path:line` |
| vow | 4 | 3 | 5 | 4 | 5 | 4 | 25 | **keep** | two oaths |
| xref | 4 | 4 | 4 | 4 | 5 | 4 | 25 | **keep DUE-as-proof** | use, not env-shaped bytes |
| scarp | 4 | 3 | 4 | 5 | 5 | 3 | 24 | **keep verb; mutate SLEW** | two cuts, named clock |

held is N4, not N5: `exists PATH` is adjacent to `git log --full-history -- path`. The unusual part is *arbitrary predicate + rebirth + era as a value*. perch’s witness-set split is the N5 mutation of that object (skills `preact-zero-mock` last 16 commits are README-only). Score above is the founding boolean.

maiden is N5 / U3: the concept is the night’s sharpest TDD question; the binary is still parser × string id (DESTROYER_MAIDEN: go/bun/nextest red vanish; Surefire `<flakyFailure>` maidens). Keep the fold. Mutate the key.

scarp is the weakest keep: lapse already named the clocks; the new interaction is *consume two cuts*. DESTROYER_SCARP: `ntp=` is kernel slew, unlabeled streams are a duration bag, a log is `cuts[0], cuts[1]`. The verb survives. The field names do not.

---

## 5. Independent disagreements

This judge did not grade a lineage it authored. Disagreement with other first-selection / coordinator notes is the point.

1. **Invert is not the winner.** It is the inverse-printf filter. Unix already said this; the coordinator still lists invert first on every board. Novelty-equal peers tonight: when, tacit, beck, plait, maiden (concept), cinch.
2. **Do not hyphenate held/when.** FIRST_SELECTION’s intersection table put them on separate rows, then STATE and STATUS started saying “when / held” as if they were one stack. They are not. held is time. when is the predicates that make a line legal.
3. **Skeptic’s four is a PATH diet, not a primitives list.** Dropping when/held/pin because `git log --full-history` / `rg seen_hunk_fingerprint` exist answers tomorrow, not “is the object new.” `rg presentThreshold` still cannot see 27 TACIT riders. `tee | grep` still cannot see git’s fatal. Those Unix one-liners are the *skeptic pipeline*, and they name the wrong object.
4. **Toolsmith kept slip on PATH and parked pin as a vehicle.** Reverse that. slip is the relocator ancestor. The new object is the token (PRIOR_ART gap #8). kizu `src/app.rs:529` → `layout.rs:17` is real either way; only pin is an address you can store.
5. **xref is not a founding primitive equal to invert.** due → lode → assay already had “env ABI.” Assay’s KIND split was real and its DUE column was a flood. DUE-as-proof is the honesty mutation that made the column mean something. Keep the proof. Forget the 12k-opcode implementation.
6. **Coordinator “vehicles (carry)” over-keeps peels.** lede/splice, twixt/yaw, ember/cinder, braid-as-fold, peal-as-third-under-stream: those are nights of breeding, not nights of objects. Novelty’s carry list is §3, thirteen verbs.
7. **Maiden is not “just alibi on HEAD.”** alibi splices new tests onto old production. maiden folds outcome history. A test written after the fix, a skip-only stub, and a 2019 scar that has been green since 2024 are the same line in the latest XML and three different maiden verdicts. Live: `--latest` SCARRED 0 MAIDEN 3; fold SCARRED 1 MAIDEN 2 SKIPPED 1.
8. **Plait is not occupancy.** GitHub “outdated” is line identity. sate is APPLIED/PENDING against a tree. plait’s gold `COMMUTE` / `JAMMED` and cli/cli PR #7 (`#333030758,#333031216` independent) are a different question: *can these comments be committed together?* braid occupies the fold — that is sate after plait, not plait.

---

## 6. Concepts worth remembering if every implementation is discarded

This is the report the night was for. Underlying interaction concepts. Rebuild from the sentence; throw away the Python.

### 6.1 Inverse instance

A filled-in string is a query. The source is a template with **names**. Whatever you pasted that the template did not consume is a **span** (evidence), not noise to strip so `--exact` can lie. Silently eating `2026-08-19T23:50:01Z ERROR` made `--exact` meaningless (invert v0.1; DESTROYER_PIN_INVERT). Concatenation is a chain of templates, not one hole stuffed with the tail (lede vs stump).

*Why this does not already exist:* `rg 'user 42 not found'` is 0 hits on `user {uid} not found`. Semgrep is not inverse printf.

### 6.2 Belie

A diff binds facts (name/value, rename, polarity). The dest tree may still **assert the old fact**. That leftover is an afterimage of *this change*, not a ghost name the compiler forgot. `rg 0.3.0` after `0.3.0 → 0.7.0` is the skeptic pipeline and the reason kizu’s `plugin.json` stayed at `"version": "0.3.0"` while `Cargo.toml` moved — zanei found it from a two-line hunk.

Leftover **names** (haunt/wraith) are a different concept and a worse one. Do not rebuild them.

### 6.3 Occupancy interval

Truth over history is **eras**, not a cut. Bisect assumes monotonicity and returns one SHA. `git log -- path` lies when a file lived only on a side branch that merged after the file was already gone (sitbone `FocusRiverView.swift`: this session, first-parent FALSE 31, hint TRUE 11 off-mainline). The Unix value is the interval.

**Tenure:** same boolean TRUE, different holders, is a new era. A fact that moved from a definition to a README is not still “held” in the sense anyone means (perch / skills `preact-zero-mock`).

### 6.4 Condition stack / given

“When does this line run?” is not the function name (`git diff -W`) and not a debugger pause. It is the nested predicates still in force, including the **negation of the last four early returns**. That negation is a noun: `given`. Live this session, kizu `parse.rs:60`:

```
given  ¬(len<5+ 2)
given  inner.is_multiple_of(2)
given  bytes.starts_with(b"a/")
given  bytes.get(b_prefix_start..b_prefix_start+ 3)== Some(b" b/")
here   let b_side = …
```

Invert the query (`under`): name a predicate, emit the lines. Rhyme (`chime`): same stack or prefix-superset. Three verbs, one object.

### 6.5 Lockset ≠ fingerprint

The hunks that change a command’s stdout are not the hunks the tests **veto**. A debug print is wheat to winnow and chaff to cinch. Tests stay at NEW — they are the lock, never the wheat. A red suite with no production units is BROKEN, not CLEAN. A timeout is **unknown**, not fail (or FAST becomes wheat). Occupancy of “we did not run” is a lie about the lockset.

### 6.6 Token address

`path:line` is a rendering. A pin is an address you mint once and resolve without repeating the rendering. Leftover re-exports at the old path are **pointers**, not identity; extract-and-keep while the origin still holds the body is identity, not a move. 1.000 at two dest copies is not uniqueness (DESTROYER_PIN_INVERT). The token is allowed to refuse (`ambiguous`, truncated → fail closed).

### 6.7 Omission polarity

Two call-sites can inhabit the same world (`presentThreshold = 0.45`) with **opposite futures**. TACIT rides the next default change. SHADOW restated the literal and will not follow. OVERRIDE named a different world. BOUND named an expression. A default-moving diff **BLASTs** the tacit riders and leaves **FOSSILs** that still pass the old literal.

Live this session: sitbone `presentThreshold` is **27 TACIT, 0 SHADOW**. `rg presentThreshold` cannot see those 27. The hysteresis tests override `emaAlpha` and omit the thresholds they are about — coverage still says they ran.

### 6.8 First-producer

The first exact match of a pipeline needle is often the **wrap**. The substance and the **fd** are earlier. `tee | grep` cannot see unpiped stderr (0 bytes crossed `|`) and names `jq` / `sed` as the inventor of bytes they only spelled. Mint / carry / wrap, plus greedy earlier fragments, is the object. Field-cover is the honesty mutation (do not steal `@0.7.0` from `notify-debouncer-full@0.7.0`).

Live this session:

```
BECK  MINT  stage 0  stderr  git -C /tmp status
      tee     MISS
```

### 6.9 Two oaths

A failing `assert expected == actual` implies **two** skip/apply machines: the golden demands Alice; this run was the runner. lees subtracts them into a residue and a bool (MACHINE vs SPEC). The daily loop wants both objects. Comments are not oaths. HOST-as-soft and “expected-only `--apply`” are peels, not the pair.

### 6.10 Clock leftover

A gap between two cuts has an **owner**: the host slept, the CPU dilated, the wall stepped, or the clocks agree. The tool must not spawn the work — a logger already has the readings. Wall − RAW on Darwin is **adjtime slew**, not NTP (DESTROYER_SCARP, ~7.3s on this host). A stream of unlabeled ticks is not an NTP step. Name SLEW; do not invent a second clock tool for it.

### 6.11 Strand algebra

Review suggestions are strands (span + before→after). They **compose with each other** before they occupy HEAD. COMMUTE is apply-in-any-order. STACK is after(a) == before(b), often *across* `original_commit_id`. SPLIT is one span, two after-images. JAM is overlapping incompatible replacement. ECHO is image identity, not locus identity. GitHub “outdated” and `git apply --check` do not answer “can I commit these five suggestions without the third failing because the second shifted lines?”

Occupancy of the *composed* after-image is a later verb (braid). Do not confuse the algebra with the occupancy.

### 6.12 DUE is a proof

An owed environment name is a **call to getenv** (or `env::var` with `(ptr, len)`), not a cstring that looks like `SNAKE_CASE`. Documented-but-unread is LATENT. Intersection is BOTH. `*getenv` suffix is not libc getenv (`not_a_getenv` / `forgetenv` — DESTROYER_XREF). Prefix peel of `CLICOLOR_FORCE` is not `COLOR_FORCE`. rustc’s 12k LLVM opcodes were never DUE. The missing Unix column is a static xref, not `strings(1)` and not `strace -e getenv` (SIP).

### 6.13 Never-red

TDD requires red first. The latest green log cannot tell a maiden from a scar from a skip from a test that has never been observed. Never-red is a **fold**: ≥1 pass and 0 fail → MAIDEN; any fail → SCARRED; only skip → not maiden; roster without outcomes → UNKNOWN, not maiden. `--skeptic` is latest-PASS ∩ history-FAIL — the set `--latest` launders.

Identity is not a string spelling and not a source `fn` name. It is the runner’s (suite, class, method) across rename and alias. `<flakyFailure>` is a red. An unparsed dialect is occupancy of nothing, not UNKNOWN.

---

## 7. Evidence of runs (this session)

UNVERIFIED would mean README-only. These ran.

| Probe | Worktree / command | Result |
| --- | --- | --- |
| invert `--selftest` | `…/2d465380e59f/invert --selftest` | `selftest: ok` |
| invert named hole | `invert --chdir … 'user 42 not found'` on `user {uid} not found` | `{uid} = 42`, `span=0-17` |
| when kizu `:60` | `when $KIZU/src/git/parse.rs:60 --explain` | four `given`, `here let b_side`, depth=5 |
| tacit sitbone | `tacit -C sitbone --summary presentThreshold` | TACIT=27 SHADOW=0 OVERRIDE=0 BOUND=0 |
| tacit `--selftest` | `…/72c70d715bf7/tacit --selftest` | 33 ok including BLAST/FOSSIL |
| beck gold | `beck --needle 'fatal: not a git repository' --sh 'git -C /tmp status \| cat \| cat'` | `MINT stage 0 stderr`; tee MISS |
| beck `--selftest` | same tree | 14/14 |
| plait `--selftest` | `…/437a44b4b3bf/plait --selftest` | 23/23 |
| plait commute | `plait fixtures/commute.jsonl` | `COMMUTE` / `PARALLEL` `#alice,#bob` |
| zanei `self-test` | `…/5c00e96ceb84/zanei self-test` | ok (homonym, prose remames, needle bounds) |
| held sitbone | `held -C sitbone exists Sources/SitboneUI/FocusRiverView.swift` | FALSE 31 first-parent; hint TRUE 11 off-mainline |
| cinch version | `…/cb9797ff4a27/cinch --version` | `cinch 0.3.0` |
| pin `selftest` | `…/d92ea07fa7a5/pin selftest` | `selftest: ok` (`--selftest` is not a flag) |
| scarp `selftest` | `…/7bf303f098fd/scarp selftest` | 7/7, backend=darwin |
| scarp unlabeled pair | `printf '1000\n1001\n' \| scarp` | `REST` (v0.2 pair; streams remain a hole) |
| vow pair | `vow --from-fail < fixtures/pytest_fail.txt` | `EXPECTED-BOUND vs ACTUAL-BOUND` alice vs runner |
| xref fixture | `cc host.c && xref --app /tmp/xref-host-judge15` | BOTH / DUE / LATENT / LATENT as advertised |
| xref `--selftest` | same tree | `selftest: ok` (orphan not DUE) |
| maiden fold | 2019-fail.xml + 2024-green.xml | alpha SCARRED, beta/delta MAIDEN, gamma SKIPPED |
| maiden `--latest` | same files | `SCARRED 0  MAIDEN 3` — the `rg PASS` lie, named |
| maiden `--selftest` | `…/7e115d7932c1/maiden --selftest` | 28/28 |

Destroyer / bakeoff files read (not re-destroyed): `lab/judges/DESTROYER_{PIN_INVERT,PIN_V5,ZANEI,CINCH,TACIT,BECK,VOW,SCARP,PLAIT,XREF,MAIDEN,ASSAY}.md`, `UNFMT_BAKEOFF.md`, `LOCKSET_BAKEOFF.md`, `LOCKSET_TOCK.md`, `GHOST_CLUSTER.md`, `FIRST_{HERETIC,UNIX,SKEPTIC,TOOLSMITH}.md`.

---

## 8. What to tell the 08:40 report

Preserve the **thirteen sentences** in §1 and the **thirteen concepts** in §6.

Ship at most one binary per row of §3, or ship none and keep the sentences. The night already proved the objects are real: invert binds `{uid}=42` and sitbone’s 7-hole Logger; when prints four `given`s on kizu `:60`; tacit counts 27 silent riders of `0.45`; beck names git’s unpiped stderr; maiden refuses to maiden a 2019 scar; xref refuses an orphan cstring; cinch 0.3 is the lockset after two occupancy lies; pin v0.5 still lands kizu `app.rs:529` → `layout.rs:17` without a path.

Forget the rest of the nouns. They were how we found these.
