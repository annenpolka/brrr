# FINAL_SKEPTIC — final jury

Source: judge-04 (Skeptic) on 2026-08-20, isolated worktree. Axis of record is still the **tomorrow-test**: would I actually type this tomorrow *instead of* `git` / `rg` / `jq`? Default **no**. Everything is unnecessary until a dirty tree, a log paste, or a leftover *claim* forces it. Prefer `rg | awk`.

FIRST_SKEPTIC's four (winnow, cinch, invert, zanei) are a hypothesis. This session re-ran Unix-first probes on `~/ghq/github.com/annenpolka/{kizu,sitbone,tenaoshi}`, then the candidate only when `git`/`rg` missed. It also ran the lockset bakeoff fixtures that FIRST_SKEPTIC left UNVERIFIED.

`lab/STATUS.md`'s "tomorrow-test shortlist" is a breeding catalog. It is not PATH.

Scores 0–5 integers: Novelty / Utility / Primitive / Composability / Empirical / Evolution. **Utility is the veto.** U≥4 only if this judge would type the verb instead of a 15-second Unix pipeline. A 4+ on Empirical requires a run, not a README. Peels that close a destroyer hole are **flags**, not extra argv[0].

Several survivors. Not one winner. Haunt stays dead. Folk stays parked. Pin stays unminted.

---

## The question

A skeptic keeps a verb only when the Unix one-liner is the wrong *object*, not merely the uglier spelling.

`rg` the static prefix. `rg 0.3.0`. `git log --full-history -- path`. `git log --all -- '*FocusRiver*'`. `git apply --check --reverse`. `git log -S`. `rg seen_hunk_fingerprint`. `rg getenv` / `rg std::env::var`. Those are not prior-art footnotes. They are what I will type at 10:00 unless the tool names a question those commands cannot ask.

Gen-3 peels that claim to "close holes" are unnecessary until the closed hole was the reason I would type the verb. A ranking fix is not a new product. A JSON regex is not a new product. `--grain file` is not a new product.

---

## Overturns vs FIRST_SKEPTIC

Keep the four *objects*. Change two *binaries*. Refuse the peel explosion.

| FIRST_SKEPTIC | this session | why |
| --- | --- | --- |
| install **cinch** (hybrid-03) | install **cinch 0.3** (mutation-48) | Live: 0.2 reports test-only red as CLEAN. 0.3 BROKEN. Timeout FAST is budget, not wheat. LOCKSET_BAKEOFF 4/4. |
| install **zanei** (cand-07) | install **ember** (mut-32); **park zanei** | Live JSON-only plugin hunk: zanei `0 fact(s)`. ember extracts `0.3.0 → 0.7.0` and the three kizu leftovers. DESTROYER_ZANEI called JSON silence lethal. It was. |
| invert, not stump | invert, not stump/**lede/splice/weld/rime/caulk/stile** | lede closed middle-drop stuffing (live miss on `awayRecovered=0`). That is invert's kernel, not a second PATH entry. Concat is still `rg "open "`. |
| winnow UNVERIFIED binary | **keep**, now run | Same debug-print fixture: winnow wheat = print **and** return; cinch wheat = return only. Two objects. |
| zanei U=3 thin | ember U=3 thin (do not raise) | Gold kizu is still `rg 0.3.0` (same three hits). Keep is the unnamed 40-hunk PR, not the version bump. |

Do not promote STATUS's twelve. Do not promote smolder as "zanei inverted" — this session `git blame plugin.json:4` is `bff820fb`; `git log -S '0.3.0' -- Cargo.toml` is `53cbd1a`. Archaeology. I will `rg` then open Cargo.toml.

---

## Survivors (would type instead of git/rg/jq)

Four verbs. Not twelve. Not sixteen. Not the Gen-3 peel zoo.

| # | install | lineage | primitive | why the Unix one-liner loses |
| --- | --- | --- | --- | --- |
| 1 | **cinch 0.3** | hybrid-03 → mutation-48 | 1-minimal *production* hunks the current tests veto; timeout is unknown; NEW always runs | `git add -p` + rerun is a 20-minute loop. winnow wheat includes `print("debug")`. Coverage says a line executed. This says drop it and the tests go red. |
| 2 | **winnow** | candidate-15 | smallest *uncommitted hunks* that reproduce a command fingerprint | Same loop, different predicate. When the command is not pass/fail (stdout, snapshot, compiler), lockset is the wrong object. `git bisect` has no dirty-hunk object. |
| 3 | **invert** | mutation-15 (lede kernel, not lede product) | instance → template + **named holes** as a filter | `rg 'user 42 not found'` is 0 hits on `user {uid} not found`. `rg 'not found'` is a guess. Spawn/`awayRecovered` static prefixes are `rg` — invert is the unpacker for the hole case. |
| 4 | **ember** | zanei → nagori → mutation-32 | leftover *claims* a typed diff just made false | Barely. `rg 0.3.0` is the version bump. After a 40-hunk rename/value PR I will not remember every old literal. zanei cannot *see* a JSON-only fact; ember can. |

Lineage spares, not extra PATH entries:

- **glean** = `winnow --grain file`
- **snug / tock** = cinch transcripts (tock did not beat 0.3; LOCKSET_TOCK did not even spawn the binary)
- **hasp** = cinch `--base A...B` with a different test-name rule; MUTE vs LOCKED is a demo, not a daily verb
- **scree** = cinch chaff (`--format patch` already emits wheat; I do not need the invert as a product)
- **lede** = invert truncation that is actually a prefix of an instance (DESTROYER_STUMP stuffing closed)
- **sluice / stencil** = walker/stream spares
- **cinder** = ember `--ash` / skip `generated/`
- **nagori** = proof the leftover-claim object is not one file

stump stays unpromoted. DESTROYER_STUMP_PIN: non-prefix tails stuffed into the last hole; a 10-char static prefix is a confident hit. lede closed that lie. Still not a second filter on PATH.

---

## What survived a destroyer

"Survived" means the *object* is still true after the attacks, not that the first binary was honest.

| object | destroyer | what lived | what the peel actually closed | still open (not a new product) |
| --- | --- | --- | --- | --- |
| lockset | DESTROYER_CINCH | debug-print vs `return a + b`; 80-chaff → 1 wheat; BROKEN on NEW-red; EMPTY on real zero-collect | cinch 0.3: test-only red is BROKEN not CLEAN; timeout FAST is budget not wheat. Live this session on `/tmp/lockset-bakeoff/fixtures`. snug independently recovered always-run-NEW. | exit-5 magic, `generated/` as suite, nested untracked git as outer prod, `--max-trials` on all-required |
| inverse-printf + names | DESTROYER_PIN_INVERT, DESTROYER_STUMP_PIN | 7-hole full paste binds; `user {uid}` binds `42`; empty stream honest; no walk | stump: rustc `-->` refuse, `--any` stops, binary stdin rc=2, no-hole prefix of query cannot beat a binding. **lede**: middle-drop is a miss (live). | concat (`"open " + path`) — splice/weld exist; I still `rg 'open '`. rustc *messages* still bind. 2 MB `--templates` omit |
| leftover claims | DESTROYER_ZANEI | kizu Cargo.toml→plugin.json; sitbone `threshold 0.4` in CLAUDE.md | ember: quoted JSON keys, full version token (not nagori's `0.3` truncate), ISO month ≠ integer 10. cinder: Cargo.lock is ash (live `--include-generated`). | workspace `version` homonym, `DEBUG` keyword, `present`⊂`presentation` (zanei), binary `--diff -` exit 1 |
| leftover-claim invert | DESTROYER_SMOLDER | gold kizu `plugin.json:4` → `53cbd1a` Cargo bump, not blame | tinder follows dest rename | dest identity, leftover-name of dest text. Unix: `git log -S`. **Park smolder** |
| pin token | DESTROYER_PIN_INVERT → STUMP_PIN → PIN_V5 | unique kizu pin still lands `layout.rs:17` | leftover stub / extract-and-keep / truncated token / missing `--to` | overcorrection, origin=roots, `--to-dir` 1.000. **I will not mint.** Object survived. Tomorrow-test failed. |
| occupancy eras | DESTROYER_OCCUPANCY | sitbone FocusRiver add+delete exist | — | timeout as FALSE, binary as air. Unix: `--full-history`. **Park.** |

winnow had **no dedicated destroyer**. It survived a *contrast* (same fixture, different wheat). Do not pretend it was adversarially proven. Do not spend a slot inventing DESTROYER_WINNOW after 08:20.

---

## What is still unnecessary

STATUS.md install list, the Unix sixteen as PATH, the Heretic museum, and every Gen-3 peel that renamed a flag.

If I will not type it at 10:00, it is not a survivor. Novelty is how we got a lab full of walkers.

### STATUS shortlist — do not install

| STATUS name | Unix I will type | leftover fact |
| --- | --- | --- |
| pin v0.5 / keel / shoal | `rg seen_hunk_fingerprint` → `layout.rs:17` (live) | durable pin is a literature gap, not a finger gap |
| when / whence / graft / ambit / peal | open the file; `git diff -W` | `given` fallthrough is a noun. `parse.rs:60` is four early returns I already read |
| held / perch / tenure / stead / berth | `git log --full-history -- path` (live empty without it; two SHAs with it); `git log --all -- '*FocusRiver*'` | era compression is pretty |
| erst / brood | `git show $SHA` + `rg` natal keys | review companion |
| sate / lodge / dreg | `git apply --check --reverse` (live rc=0 on kizu HEAD) | SUPERSEDED is archaeology |
| sow / hatch / till | `rg` call sites vs tests | quarterly audit |
| plait / spar | read the two suggestions | COMMUTE/JAM are real and I still will not pipe GitHub JSONL tomorrow |
| assay / xref / lash / shim / prove | `rg std::env::var` (live kizu `KIZU_*`) / `strings` / `otool -L` | DESTROYER_ASSAY: KIND is a strings partition, not a getenv proof |
| kith / lien | `rg` leftover natal keys | CI gate on a parked object |
| coast | `sleep 2` | AUTHOR-only |
| weld / rime / caulk / stile / solder | `rg` the proving string | DESTROYER_WELD: `{body}abcd` matches every log line. Completeness of concat, not a daily verb |
| snag `--forbid number` | `git diff \| rg '^[+-]'` | tripwire on a ply I already see |
| gage / brand / sear | not a lockset | visa of worlds. I run CI |
| tacit / aloud / maiden / beck / … | open the file / `rg` | Gen-3 Cambrian leftovers. Park unless a new condition |

### FIRST_SKEPTIC kills — stay dead

haunt, wraith-as-product, reverb (`git diff` minus lines → `rg`; tenaoshi still has three `Content-Type` adapters — I `rg Content-Type`), unfmt-08/13 walkers, sluice-as-product, moor, due/lode/orbit, aka/sic as products, nigh, akin similarity, pinch/hitch/knot, spoor, cleave, yoke, veil, skew, folk, kiln/clutch as products.

---

## `rg` in a costume

If the honest object is an existing command plus flags, the product dies. Harvest at most one fact. Gen-3 does not make a costume into a verb.

| costume | honest object | Unix |
| --- | --- | --- |
| **zanei** on the kizu gold | search for the old literal the diff named | `rg '0\.3\.0' kizu -g '!target/**' -g '!*.lock'` — live, same three hits |
| **ember** on a one-fact bump | same | same `rg`. ember earns rent only when the diff names facts I have not named |
| **stump** 10-char prefix hit | search for the leading static | `rg 'failed to spawn'` / `rg 'cannot reach'` |
| **invert** on spawn / `awayRecovered` | search for the static | `rg -n 'failed to spawn' kizu` already lands `revert.rs:46`. invert adds a span report of a line I have |
| **reverb** | minus lines as query | `git diff \| rg '^-' \| rg -v '^---'` then `rg` |
| **perch** README-only tenure | who still mentions the name | `git log -S` + `rg` at HEAD |
| **when --explain** | reprint the guards | the buffer I already have open |
| **held --full exists** | birth and death of a path | `git log --full-history -- path` |
| **sate APPLIED** | reverse-apply succeeds | `git apply --check --reverse` |
| **slip / pin resolve** of a unique token | search for the function | `rg seen_hunk_fingerprint` |
| **due / assay DUE** | env names in the image | `rg getenv` / `rg std::env::var` / `strings` |
| **smolder** of a version leftover | pickaxe the old token | `git log -S '0.3.0' -- Cargo.toml` |
| **weld** leftover `\nDone.` | concat suffix | `rg 'Done\.'` |
| **cinder** skip generated | ignore policy | `rg -g '!generated/**' -g '!*.lock'` |
| **scree** unlocked set | cinch chaff column | already in the JSON |
| **tock** | cinch 0.3 | new name |
| **snag --forbid number** | did a digit move | glance at the diff |

The hole case is **not** a costume: `rg 'user 42 not found'` → 0 hits; invert binds `{uid}=42`. Live. That is invert's keep.

The lockset is **not** a costume: winnow wheat is print+return; cinch wheat is `return a + b` and the patch is only that hunk. Live. `git add -p` does not emit 1-minimal veto.

---

## Per-lineage scores

`Σ` is unweighted and is not a ranking. **Keep follows Utility**, then "can Unix phrase this."

Legend: **K** = I would type it tomorrow. **P** = preserve the object, no PATH. **PARK**. **KILL**.

### Dirty tree / tests as lock

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-48 | cinch 0.3 | 3 | 5 | 5 | 4 | 5 | 3 | 25 | **K** | 1-minimal production hunks NEW tests veto; timeout unknown; NEW always occupied |
| cand-15 | winnow | 2 | 4 | 4 | 5 | 4 | 2 | 21 | **K** | smallest hunk set that reproduces a command fingerprint |
| hyb-03 | cinch 0.2 | 3 | 2 | 5 | 4 | 5 | 1 | 20 | KILL product | test-only red CLEAN (live). Occupancy of nothing, exit 0 |
| reimpl-06 | snug | 3 | 3 | 5 | 4 | 4 | 1 | 20 | PARK transcript | always-run-NEW recovered independently; FAST still wheat |
| mut-55 | tock | 3 | 2 | 5 | 4 | 2 | 1 | 17 | PARK name | same object as 0.3; critic did not spawn it |
| hyb-06 | hasp | 3 | 2 | 4 | 4 | 4 | 2 | 19 | PARK | MUTE vs LOCKED is the hybrid pitch; I type `cinch --base origin/main` |
| mut-07 | glean | 2 | 3 | 4 | 5 | 4 | 1 | 19 | PARK→flag | `winnow --grain file` |
| mut-62 | scree | 2 | 2 | 4 | 4 | 3 | 1 | 16 | PARK→flag | cinch chaff as emit |
| hyb-12 | gage | 3 | 1 | 3 | 3 | 3 | 2 | 15 | PARK | lock visa / world. Not a fourth cinch |
| cand-24 | alibi | 4 | 2 | 4 | 3 | 3 | 3 | 19 | PARK | tests@NEW × prod@OLD; no cargo/swift splice on dogfood |

Novelty of winnow is still 2 (ddmin, 1970s). Heretic still kills it. Skeptic still keeps it because the *substrate* is the dirty tree and this session typed it. cinch is the one I type when the command is a test suite. 0.3 is the one I install.

### Inverse printf

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-15 | invert | 4 | 4 | 5 | 5 | 5 | 2 | 25 | **K** | runtime instance on one channel, templates on the other; named holes; leftover prefix is a span |
| mut-33 | lede | 3 | 2 | 5 | 5 | 5 | 2 | 22 | PARK kernel | truncated match **is** a prefix of an instance; middle-drop misses (live) |
| mut-23 | stump | 4 | 2 | 4 | 5 | 5 | 1 | 21 | PARK | DESTROYER_STUMP stuffing; 10-char prefix hit |
| mut-34 | splice | 3 | 2 | 4 | 5 | 4 | 2 | 20 | PARK | `"open " + path` as one template. `rg 'open '` |
| mut-59 | weld | 3 | 2 | 4 | 5 | 4 | 2 | 20 | PARK | expr-first concat. DESTROYER_WELD `{body}abcd` |
| mut-79 / 91 / 109 | rime / caulk / stile | 2 | 1 | 3 | 4 | 3 | 1 | 14 | KILL products | leftover-of-a-bind as a new CLI. Composition of a costume |
| mut-02 | sluice | 3 | 2 | 4 | 5 | 5 | 1 | 20 | PARK kernel | invert without names |
| reimpl-01 | stencil | 3 | 2 | 5 | 3 | 5 | 1 | 19 | PARK spare | walker. `rg` is the producer |
| cand-08/13 | unfmt | 3 | 2 | 4 | 3 | 5 | 1 | 18 | KILL | walker; UNFMT_BAKEOFF |
| hyb-01 | moor | 2 | 1 | 3 | 4 | 4 | 1 | 15 | KILL | two objects in a trenchcoat |

Mutate invert (in-place): take lede's prefix-of-instance rule. Do not grow a walker. Do not ship stump. Concat stays a sibling I will not install.

### Leftover claims (not leftover names)

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-32 | ember | 4 | 3 | 4 | 5 | 5 | 2 | 23 | **K** thin | typed facts: JSON keys, full version token, month ≠ 10 |
| cand-07 | zanei | 4 | 2 | 4 | 5 | 5 | 1 | 21 | PARK ancestor | JSON-only `0 fact(s)` live. Gold path still works with a Cargo.toml sidecar |
| mut-37 | cinder | 3 | 2 | 4 | 5 | 5 | 1 | 20 | PARK→flag | generated dest is ash (live Cargo.lock cinders). `rg -g '!*.lock'` |
| reimpl-03 | nagori | 3 | 2 | 4 | 5 | 4 | 1 | 19 | PARK proof | JSON-only timeout hunk; then truncates `0.3.0`→`0.3` and throws the leftover away |
| mut-63 | smolder | 4 | 2 | 4 | 3 | 4 | 2 | 19 | PARK | leftover in → falsifying commit. `git log -S` / not `git blame` |
| mut-81 | tinder | 3 | 1 | 3 | 3 | 3 | 1 | 14 | PARK peel | dest rename follow |
| cand-04 | reverb | 2 | 1 | 2 | 4 | 4 | 1 | 14 | KILL | `git grep` of the minus lines |
| cand-05/12 | haunt / wraith | 1 | 1 | 2 | 2 | 3 | 1 | 10 | KILL | leftover names |

ember U=3: this session `rg 0.3.0` reproduced the kizu poster exactly. JSON-only ember recovers the same three hits without a Cargo.toml sidecar — that is a grammar fix, not a new tomorrow. Stay a filter (`git diff origin/main \| ember --diff -`). Do not grow a review platform.

---

## Disagreements

### vs FIRST_SKEPTIC (same axis, later evidence)

Agree on the cut: four objects, not the coordinator twelve, not the Unix sixteen. Haunt dead, folk parked, pin unminted, when/held/sate/erst/sow/coast are demos.

Disagree on the leftover-claims *binary*: zanei is JSON-blind on the plugin-manifest path the pitch used as gold. ember is the vehicle. Disagree on installing hybrid-03 cinch: 0.2's CLEAN-on-red is an occupancy lie this session reproduced (`status CLEAN` on test-only-red). Disagree on treating invert descendants as optional vehicles on a shortlist — STATUS already did; this judge refuses.

### vs STATUS.md tomorrow-test shortlist

STATUS would install invert/stump/lede/splice, pin, when/ambit/peal, held/perch/berth, zanei/ember/cinder, erst, cinch/hasp/tock, sate, sow, plait, assay, kith/lien.

This judge installs **cinch 0.3, winnow, invert, ember**. Everything else is a parked object, a Unix clone, or a peel in a new trenchcoat.

### vs Toolsmith (PATH twelve)

Toolsmith: invert, slip, winnow, when, zanei, reverb, sic, due, sate, zure, held, cinch.

Skeptic: **winnow, cinch 0.3, invert, ember**. Parks slip/when/sate/held. Kills reverb/due. Parks sic/zure. Replaces zanei with ember.

Toolsmith U=5 on slip/when/sate/held/due is "a developer could." This judge's U is "I will." Those are still different numbers. Gen-3 did not convert "could" into "will."

### vs Heretic (unseen objects)

Heretic kills winnow as ddmin and keeps when / perch / tell / pin / erst / alibi / lees / sate / clutch / sow / coast.

Skeptic **keeps the corpse heretic buried** (winnow/cinch) and **parks the museum heretic loves**. Live lockset contrast is the reason. An unseen question-word I will not type is not a survivor.

Agree: haunt dead, folk parked, invert is the inverse-printf vehicle, unfmt walkers die, one leftover-name search is already too many.

### vs Unix (sixteen mutate vehicles)

Unix wants invert, pin, flume, tell, perch, sate, erst, sic, sow, zanei, lode, lees, cinch, under, cusp, doze as vehicles.

Skeptic mutate/install list is **cinch 0.3, winnow, invert, ember**. Unix's list was a breeding pool. The pool produced peels. Peels are not PATH.

Agree: haunt dead, folk parked, invert is a filter not "the winner," do not merge the survivors, do not grow a second walker.

### vs DESTROYER (mutate, do not kill)

Agree on cinch / invert / leftover-claims: mutate, do not kill. The objects survived.

Disagree that every mutate-toward is a new binary. lede is invert's kernel. ember is zanei's grammar. cinder is a skip list. tock is a name. weld is concat I will `rg`. pin's closed destroyer list still fails the tomorrow-test (I will not mint). smolder survived as invert of leftover-claims and still loses to `git log -S`.

---

## Evidence of this session (Unix first, then the tool)

Worktrees under `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/`. Dogfood: `~/ghq/github.com/annenpolka/{kizu,sitbone,tenaoshi}`. Bakeoff fixtures: `/tmp/lockset-bakeoff/fixtures/`.

### cinch 0.3 vs winnow vs cinch 0.2 — lockset ≠ fingerprint, 0.2 occupancy lie

```
$ ./cinch-0.3 -C $DEBUG --format patch -- python3 test.py
--- a/app.py
+++ b/app.py
@@ -1,4 +1,4 @@
 def add(a, b):
     x = 0
-    return 0
+    return a + b
# JSON wheat=['app.py#2']  chaff=['app.py#1']  (the print)

$ ./winnow -C $DEBUG --format json -- python3 test.py
wheat: app.py#1 (print) AND app.py#2 (return)
wip.summary: exit=0 debug

$ ./cinch-0.3 -C $RED --json -- python3 test.py
status BROKEN   # test-only assert == 99; production unchanged

$ ./cinch-0.2 -C $RED --json -- python3 test.py
status CLEAN    # live occupancy lie. trials skipped. rc=0

$ ./cinch-0.3 -C $FAST --json --timeout 0.5 -- python3 test.py
wheat=['app.py#2']  budget=['app.py#1']   # VALUE locked, FAST unknown
```

### invert — spawn poster is `rg`; hole poster is not

```
$ rg -n 'user 42 not found' invert/fixtures
# 0 hits

$ rg -n -g '*.py' 'f"' invert/fixtures | invert --templates - 'user 42 not found'
fixtures/src/user.py:2:20  tmpl: user {uid} not found  {uid}=42
# this is the keep. instance digits are not in the source.

$ rg -n 'failed to spawn' kizu -g '*.rs' | head -1
kizu/src/git/revert.rs:46:        .context("failed to spawn `git apply --reverse`")?;
# first hit is already the invert landing.

$ rg -n -g '*.rs' -g '!target/**' 'failed to spawn' kizu \
    | invert --templates - '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
…/revert.rs:46:18  score=0.66  holes=0  prefix: 2026-08-19T23:50:01Z ERROR  span=27-64
# invert adds a span report. I already had the file.
```

### lede — DESTROYER_STUMP stuffing closed (not a PATH reason)

```
$ rg -n -g '*.swift' awayRecovered lede/fixtures | lede --templates - \
    'transition focused → idle awayRecovered=0'
— no template for: transition focused → idle awayRecovered=0
# stump bound {to}=idle awayRecovered=0. lede misses. honest.

$ … | lede --templates - 'transition focused → idle reason=timeout idle=12s'
{from}=focused {to}=idle {reason}=timeout {idle}=12  truncated: deserted=…
```

### zanei vs ember — gold is `rg`; JSON-only is the grammar that zanei lacks

```
$ rg -n '0\.3\.0' kizu -g '!target/**' -g '!*.lock'
plugin/plugin.json:4:  "version": "0.3.0",
plans/v0.3.md:103: - [ ] version bump to 0.3.0
plans/v0.3.md:451: "version": "0.3.0"

$ git -C kizu diff v0.3.0 v0.7.0 -- Cargo.toml | zanei --diff - -C kizu --min-score 70
FACT version: 0.3.0 → 0.7.0
  103 plugin/plugin.json:4
   84 plans/v0.3.md:103
   84 plans/v0.3.md:451
# same three hits as rg.

$ cat plugin-only.diff | zanei --facts-only --diff - -C kizu
zanei: 0 fact(s)

$ cat plugin-only.diff | ember --facts-only --diff - -C kizu
ember: 1 fact(s)  version: '0.3.0' → '0.7.0'
# then the same three afterimages, no Cargo.toml sidecar.
```

cinder `--include-generated` on the Cargo.toml gold: same three leftovers plus Cargo.lock cinders at 71. Ash is a skip list. Not a verb.

### leftover-claim invert is `git log -S`, not blame — and still not tomorrow

```
$ git -C kizu blame -L 4,4 plugin/plugin.json
bff820fb (Annenpolka 2026-04-16 …)   "version": "0.3.0",

$ git -C kizu log --oneline -S '0.3.0' -- Cargo.toml
53cbd1a chore: bump version to 0.3.1
87a54a4 release: bump version to 0.3.0
# smolder's gold is 53cbd1a. Unix already names it if you know to look in Cargo.toml.
# I know. It is a version.
```

### held / sate / pin — Unix still wins (reconfirmed)

```
$ git -C sitbone log --oneline -- Sources/SitboneUI/FocusRiverView.swift
# empty

$ git -C sitbone log --oneline --full-history -- Sources/SitboneUI/FocusRiverView.swift
70ec7df Clean up: remove unused FocusRiverView + SettingsWindowController
14b1d6e Focus River settings UI + dropdown settings button

$ git -C kizu diff HEAD^ HEAD | git -C kizu apply --check --reverse; echo rc=$?
rc=0

$ rg -n 'seen_hunk_fingerprint' kizu -g '*.rs'
src/app/layout.rs:17:pub fn seen_hunk_fingerprint(
```

### due / reverb costumes — `rg` this session

```
$ rg -n 'std::env::var' kizu -g '*.rs' -g '!target/**' | head -3
src/app.rs:577:    std::env::var("KIZU_SESSION_ID")
src/main.rs:140:   std::env::var("KIZU_EVENT_TTL_SECS")
src/paths.rs:10:   std::env::var("KIZU_CONFIG")

$ rg -n 'Content-Type' tenaoshi | head -3
# three adapters still set application/json. minus-line search is rg.
```

---

## Revised tomorrow-test

### Install (PATH, in this order)

1. **cinch 0.3** — `lab/lineages/mutation-48__cinch` / worktree `subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27`. Dirty tree, tests are the command.
2. **winnow** — `lab/lineages/candidate-15__winnow` / `subagent-01a01a85-bf36-7370-8d54-8bed7c40c0c8`. Dirty tree, fingerprint is the command.
3. **invert** — `lab/lineages/mutation-15__invert` / `subagent-01a01ad1-c9bb-74f2-a42f-2d465380e59f`. `rg | invert` on a paste with holes. Fold lede's prefix-of-instance miss into this binary later; do not install lede.
4. **ember** — `lab/lineages/mutation-32__ember` / `subagent-01a01b45-0fff-7093-ac6a-fc8050650bef`. `git diff origin/main | ember --diff -` after a fat bound-value PR. Do not install zanei.

No fifth.

### Do not install

- STATUS.md's twelve-plus (pin, when, held, sate, erst, sow, plait, assay, kith, ambit, peal, tock, hasp, cinder, stump, lede, splice, weld, …).
- Any peel whose CANDIDATE opens with "Parent already computed X; this emits Y."
- A second inverse-printf walker. A second leftover-name search. A third cinch. A fourth cinch.
- pin tokens, occupancy TUIs, wait-for graphs, env-ABI dumps, generation lots, GitHub suggestion algebras.
- hybrid-03 cinch 0.2 (CLEAN-on-red).
- zanei as the leftover-claims vehicle (JSON-blind).
- smolder as "the invert of zanei" (`git log -S`).

### Do not spend remaining slots on

when-flags, pinfile registries, leftover-name ignore lists, rime/caulk leftover chains, gage visas, snag ply tripwires, weld proving-string floors, maiden/beck/tacit/woof.

If a later report needs a short list: **cinch 0.3, winnow, invert, ember**.

---

## What this judge is not doing

- Not picking a single winner. cinch is not "the" tool. invert is not "the" tool.
- Not grading polish, LOC, demo counts, or peel depth.
- Not keeping two walkers, two leftover-name miners, two wait-graph CLIs, two generation-lot CLIs, nine inverse-printf CLIs, or a pin token I will not mint.
- Not killing winnow because Heretic said "1970s." Live wheat is print+return. I will type it when the command is not a test.
- Not keeping when / pin / perch / sate / erst / sow / coast / plait / assay because they are strange and the destroyer transcript is pretty. Strange and unused is still unused. A closed destroyer hole is not a tomorrow keystroke.
- Not rubber-stamping FIRST_SKEPTIC's four names when the binaries moved. The objects held. Two vehicles changed.

Next hour (preservation, not invention): ship the four. Fold lede into invert. Fold cinder's skip list into ember. Do not invent a fifth leftover-name search. Do not install the coordinator's twelve.
