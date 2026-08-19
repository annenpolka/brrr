# FINAL_DISAGREE — predicted/observed splits (judge-16)

Disagreement judge. Clock window: 2026-08-20 08:20 JST. Isolated worktree. Did **not** read other `FINAL_*` (independence). Sources: `lab/judges/FIRST_{UNIX,TOOLSMITH,HERETIC,SKEPTIC}.md`, `lab/FIRST_SELECTION.md`, DESTROYER_* / bakeoffs, `lab/STATE.md` vehicles.

**Do not force consensus.** The four first-round vetoes are orthogonal. A ranking that averages them is a fifth judge in a trenchcoat. Preserve the split as evidence.

---

## The four vetoes (why they cannot agree)

| Judge | Axis of record | Keep means | Kill means |
| --- | --- | --- | --- |
| **Unix** | one object, one verb, a stream | orthogonal primitive you can pipe | two tools for one object; a walker that owns ignore policy |
| **Toolsmith** | would a developer type this *tomorrow* on a dirty tree | paid rent on kizu/sitbone/tenaoshi/voidtrace | clone of a paid-rent primitive |
| **Heretic** | novelty veto | an interaction nobody has typed | conventional even if U=5 (ddmin, knip inverted, `ldd`, `git apply --check`) |
| **Skeptic** | would *I* type this *instead of* `git`/`rg`/`jq` | Unix one-liner is the *wrong object* | demo-pretty; `rg` already lands; minting a token I will not paste |

Utility is not one number. Toolsmith U=5 is “a developer could.” Skeptic U is “I will.” Heretic treats U=5 as a trap. Unix does not rank by U.

Σ is diagnostic. Invert’s 30/28/28/27 is not a winner. Winnow’s 24/28/19/23 is a **split**, not a score.

---

## Observed FIRST ledger (the split that already happened)

Verdicts collapsed to: **M** mutate / **K** keep-PATH or keep-object / **P** preserve/park-object / **X** kill product. “Park” and “preserve” are not the same as kill; they are “do not spend a rewrite slot.”

| object | Unix | Toolsmith | Heretic | Skeptic | Coordinator (`FIRST_SELECTION`) |
| --- | --- | --- | --- | --- | --- |
| **invert** | M (filter) | K PATH | K object | **K** (one of four) | intersection |
| **zanei** | M | K PATH | K object | **K thin** (one of four) | intersection |
| **winnow** | K | K PATH | **X ddmin** | **K** (one of four) | *cinch* as compromise |
| **cinch** | M | K PATH | **X ddmin** (with winnow) | **K** (one of four) | keep cinch |
| **when** | K | K PATH | **K object** | **P** open the file | intersection; Skeptic **drops** |
| **sate** | M | K PATH | K object | **P** `git apply --check --reverse` | intersection; Skeptic **drops** |
| **held** | K | K PATH | `--boolean` ancestor | **P** `--full-history` | intersection as held→perch; Skeptic **drops** |
| **perch** | M | P | **K object** | P README tenure is `rg` | intersection; Skeptic **drops** |
| **tell** | M | P (mutation of held) | **K object** | P `git diff --stat` | Unix/Heretic; Toolsmith not PATH |
| **pin** | M | P (not PATH) | **K object**; kill slip | **P** I will not mint | intersection; Skeptic **drops** |
| **slip** | K backend | **K PATH** | **X relocator** | P `rg` the name | keep pin; slip = ancestor |
| **flume** | M | P | **X relocator stream** | P | with pin |
| **erst** | M | P | **K object** | P `git show` + `rg` | intersection; Skeptic **drops** |
| **sow** | M | P | **K object**; kill cleave | P quarterly | intersection; Skeptic **drops** |
| **coast** | **P** (subset of spoor) | P | **K object**; knot is known picture | P I type `sleep 2` | intersection; Skeptic **drops** |
| **knot** | **K** wait-source | P | **P for Unix**; object is coast | **X** `pstree`/`strace` | not in intersection |
| **alibi** | K | **P** (cinch is the hunk) | **K object** | P no cargo/swift splice | keep (Heretic+Unix) |
| **lees** | M | **P** niche | **K object** | P I compare snaps rarely | keep (Heretic+Unix) |
| **clutch** | P (sinter is fused) | **X product** → sinter | **K object**; kiln harvest | P spec-gen niche | keep **sinter** as vehicle |
| **sinter** | K | P | clutch is the object | P | coordinator already picked sinter |
| **due** | P (miss was the image) | **K PATH** | **X** `strings`+`ldd` | **X** `rg getenv` | keep **orbit+lode** |
| **lode** | M | P→due `--images` | **X** | **X** | keep as mutation |
| **sic** | M | **K PATH** | **P** linter | **P** `rg -i` | park as incremental |
| **aka** | K | P | P | P | park |
| **zure** | K | **K PATH** | **P** for Toolsmith | P I `rg` what I deleted | not intersection |
| **reverb** | K | **K PATH** | **X** clone-detect | **X** `git grep` minus lines | not intersection |
| **wraith** | K one leftover-*name* | P archaeology | **X** knip inverted | **X** even one is too many | haunt dead; wraith undecided |
| **veil** | K | **X** coverage+grep | mutate cover-type | **X** | not intersection |
| **moor** | K | P | **X** two objects in a trenchcoat | **X** | not intersection |
| **under/chime** | under M; chime K | **P→flags on when** | mutate of when | P→flags | Unix/Heretic keep verbs |
| **cusp** | M | P | mutate (cut, not spelling) | P static analysis | nigh dead |
| **doze** | M | P (CI form of unseen) | P signature-check | P CI not tomorrow | Unix vehicle |
| **folk** | **P** | **P** | **X** | **P** | parked (0 orphans) |
| **haunt** | **X** | **X** | **X** | **X** | **converged kill** |

Intersection that *all four* keep: **invert**, **zanei**. That is two tools. Coordinator listed nine plus cinch. Skeptic listed four. Heretic listed thirteen objects. Those three lists are **not a ranking disagreement**. They are three different questions.

---

## Load-bearing splits (do not collapse)

### 1. Skeptic four vs Heretic keep-strange

The night’s main fracture.

- **Skeptic PATH:** winnow, cinch, invert, zanei (thin).
- **Heretic objects:** when, perch, tell, invert, pin, erst, zanei, alibi, lees, sate, clutch, sow, coast.
- **Overlap:** invert, zanei.
- **Heretic kills Skeptic’s other two** (winnow/cinch as 1970s ddmin).
- **Skeptic parks Heretic’s museum** (when/perch/tell/pin/erst/sate/alibi/lees/clutch/sow/coast).

`FIRST_SELECTION`: “Coordinator does **not** collapse to four. Skeptic vetoes daily PATH, not evolution slots.” That is a policy, not a resolution. Skeptic’s text is the opposite: an unseen question-word I will not type is **not a survivor**. Do not paper this over with “breeding pool.”

**What not to collapse:** installing twelve because they are strange **or** deleting eleven because a skeptic will `rg`. Keep both lists. Report them as two columns.

### 2. Winnow / cinch — utility corpse vs lockset object

| | winnow | cinch |
| --- | --- | --- |
| Unix | keep (fingerprint wheat) | **mutate** (pass/fail lockset) |
| Toolsmith | **PATH** | **PATH** |
| Heretic | **KILL** N=1 | **KILL** with the family |
| Skeptic | **K** N=2; substrate is dirty hunks | **K**; this is the one I type when the command is a test |

DESTROYER / bakeoff **strengthens the object split**, not the keep/kill:

- `lab/judges/DESTROYER_CINCH.md`: mutate both cinch and hasp; empty suite / timeout / test-only-red are occupancy lies, not a missing primitive.
- `lab/judges/LOCKSET_BAKEOFF.md`: debug-print vs `return a + b` is unanimous LOCKED wheat=`app.py#2`. cinch 0.2 still reports a **red suite as CLEAN**. cinch 0.3 treats timeout as unknown (FAST is budget). Carry **cinch 0.3**. No fourth cinch.
- `lab/judges/LOCKSET_TOCK.md`: tock does not beat 0.3; same kernel, new name.

Unix and Toolsmith and Skeptic will **keep cinch 0.3** and will **not** elect tock. Heretic will still kill the family: “the most useful tool of the night. 1970s algorithm.” Novelty veto vs tomorrow-test is the disagreement. Bakeoff honesty does not convert Heretic.

**What not to collapse:** “cinch won, so winnow dies” (Skeptic types both; predicates differ). “ddmin is conventional, so lockset dies” (Skeptic/Toolsmith/Unix keep the *substrate*: uncommitted hunks, tests@NEW). “tock is a new object” (critic already said no).

### 3. Pin token vs slip relocator vs `rg` the name

| | pin | slip | flume |
| --- | --- | --- | --- |
| Unix | **M** durable token (PRIOR_ART gap) | K fingerprint backend | **M** gitless log filter |
| Toolsmith | P (not PATH) | **K PATH** last night’s CI log | P |
| Heretic | **K object**; `path:line` refused | **X** source maps / `blame --reverse` | **X** |
| Skeptic | **P** I will not mint `pin1.eNpt…` | P `rg seen_hunk_fingerprint` lands `:17` | P |

DESTROYER closed holes and **did not close the vetoes**:

- `DESTROYER_PIN_INVERT.md`: leftover stub scores 1.000; identical helpers emit 1.000 twice; truncated token porcelain-succeeds. Unique kizu tokens do **not** hallucinate onto voidtrace. **Mutate, do not kill.**
- `DESTROYER_STUMP_PIN.md`: those holes **closed** on v0.3. New holes are overcorrection / refuse-rule narrower than the pitch. Still mutate.
- `DESTROYER_PIN_V5.md`: extract-and-keep / leftover-wrapper closed on the fixtures they wrote. New lie: leftover is not a pointer; origin-body identity is not file identity.
- `DESTROYER_KEEL.md`: remotes are config (`git remote add` is `--any-repo`); missing origin allowed. Depth-1 clone of the same project should resolve. Still mutate.

Skeptic’s live probe still holds after hardening: `rg -n 'seen_hunk_fingerprint' kizu` hits `src/app/layout.rs:17`. The PRIOR_ART gap (`git log -L` stops at the split) is real and is **not** a reason Skeptic will paste a token into a ticket. Heretic’s object is still the token. Toolsmith will still type `slip --from b4e6a5d`. Unix will still want pin **and** flume as different objects (gist later is the LSP stream of flume).

**What not to collapse:** “pin v0.5 fixed DESTROYER so pin is PATH” (Skeptic still will not mint). “slip is conventional so only pin lives” (Toolsmith’s tomorrow log). “flume/gist are slip flags” (Unix: gutter/LSP schema is why they are filters).

### 4. When-stack vs open-the-file vs three CLIs

Unix: when keep, **under mutate**, chime keep (three verbs, one object from opposite ends).
Toolsmith: **when PATH**; under/chime are `--same-as` / `--under` flags.
Heretic: **when is the question-word**; chime = `comm(1)` for stacks; under so you do not already know the line.
Skeptic: **park**. Live `parse.rs:60` reprints four early-return guards already on screen. `layout.rs:17` is depth=0.

Bakeoff later: `AMBIT_AMID_BAKEOFF.md` — **under as `rg |` stream**. Carry **ambit** (2/3 pipes); amid spare. `DESTROYER_PEAL.md`: chime as that filter; gold `rg -n 'let b_side' | peal --explain` matches `chime parse.rs:60` including a span rg never printed. Mutate, do not kill. Do not elect a third under-stream.

Predicted FINAL: Unix keeps under/ambit/peal as **pipes**. Toolsmith still wants one `when` with flags. Heretic still keeps the stack object (whence matched 133/133 — proof, not a second product). Skeptic still opens the file. DESTROYER_PEAL’s gold pipe will not convert Skeptic; it will convert Unix.

**What not to collapse:** merging under/chime/peal/ambit into `when --flag` overnight (Unix loses the invert query). Shipping four binaries named after one stack (Toolsmith/Skeptic). Killing the stack because `git diff -W` names the function (Heretic’s point).

### 5. Occupancy eras vs `git log --full-history`

Skeptic’s probe: `git log -- path` empty is a known footgun; `--full-history` already prints add+delete; held adds `TRUE 11 / FALSE 78` compression. Pretty. Not a new question.
Heretic: held is the ancestor; **perch** (holder set) and **tell** (you do not know the question) are the heresies. skills README-only tenure is a *different lie* than bisect.
Unix: perch + tell mutate; held keep; stint keep `--pick`.
Toolsmith: **held PATH**; perch/tell/stint preserve (paid rent, not daily).

`DESTROYER_OCCUPANCY.md`: mutate, do not kill. Timeout is not FALSE; empty `--now` cannot see a dirty tree; binary is empty air; a walk of `git log --reverse` is not the lattice.
`DESTROYER_FORD.md`: merge occupancy is parent **trees**, not a boolean on the merge SHA. kizu `CLAUDE.md` at `0ea3916` is `FALSE ⊓ TRUE`, origin `e1098c8`. `--boolean` never computes the lattice. Octopus cannot tell 1-of-3 from 2-of-3.
`DESTROYER_BERTH.md`: file-identity occupancy across rename. Default first-parent walk **does not** keep TRUE when you query the old name. Leftover-blob copy is not a follow.

Predicted FINAL: Heretic **adds ford + berth** to keep-strange (lattice and identity are unseen). Unix **mutates** them as occupancy peels (do not merge perch×ford×berth into one walker). Toolsmith preserves, does not PATH. Skeptic still types `--full-history` / `-S` / `rg`.

**What not to collapse:** held = perch = tenure = ford = berth. Boolean era, witness split, merge lattice, and rename identity are four objects. Also do not collapse “Skeptic parked occupancy” into “occupancy is fake” — DESTROYER says the verb is real and the walk is a lie.

### 6. Env ABI — due PATH vs lode image vs assay KIND vs `rg getenv`

Toolsmith: **due PATH** (`KIZU_*` / `TMUX` tomorrow). lode is `--images`. orbit is a footnote.
Unix: **lode mutate** (`ldd` for getenv of the load image). due parked (Homebrew python3: 0 names). orbit keep (which binary will run).
Heretic: **kill due/lode** (`strings`+`ldd`+`which`). Park orbit.
Skeptic: **kill** the same way.

`DESTROYER_ASSAY.md`: KIND is real on a compiled host (`PYTHON_GIL` DUE / `PYTHONHOME` LATENT). DUE on rustc is a **strings flood** (~12k names). There is **no Mach-O xref** to a getenv call site. Mutate, do not kill. Later: xref / lash / wad / shim try to make DUE a getenv proof (`STATE.md`: “assay KIND is real; xref makes DUE a getenv proof”).

Predicted FINAL: Unix keeps assay+xref as the lode vehicle. Toolsmith still wants a `due` verb a human types. Heretic/Skeptic still say `otool -L` / `strings` / `rg getenv`. DESTROYER’s flood will **help** Skeptic (rustc DUE is unusable tomorrow) and **not** kill Unix’s two-column object.

**What not to collapse:** due = lode = assay = xref = orbit. Names vs load-image vs KIND vs call-site proof vs guise/payload/SIP are five questions. Coordinator already collapsed to “orbit + lode” — that is one compromise, not the split.

### 7. Coast vs knot (waitpid is a lie vs wait-for graph)

Heretic: **coast** is the missing object (`sleep 2` / `waitpid` do not name the side-effect cloud). knot is a known picture (`offcputime`, `pstree`). Kill spoor (spawn-wrap). Carry cling (attach, do not spawn).
Unix: **knot keep** (one wait-source spanning pipe meters ∩ process tree). coast park (subset of spoor). pinch/hitch absorbed.
Toolsmith: both preserve; coast is the daily `sleep 2`; knot for “where’s it wedged?”
Skeptic: park/kill. I write `sleep 2`. AUTHOR-only; I did not run it.

`DESTROYER_SCARP.md` (later clock-cut filter): `{cut; sleep 0.35; cut} | scarp` is still DILATE without spawn. `ntp=` is adjtime slew, not NTP. Mutate, do not kill. This is **not** coast. Do not fold clock-gap into post-waitpid.

**What not to collapse:** coast = knot = scarp = cling = spoor. Heretic vs Unix on *which wait object is new* survives DESTROYER because DESTROYER never attacked coast/knot as a pair.

### 8. Alibi / lees / clutch — Heretic survive vs “unproven”

Heretic predicted Skeptic would call these unproven. Observed: Skeptic **parked** them (E=3 on alibi: no cargo/swift splice; lees “I compare snapshots rarely”; clutch “spec-gen niche”). Toolsmith parked alibi/lees, preserved **sinter**. Unix: lees mutate, alibi keep, sinter keep, clutch park.

`DESTROYER_VOW.md`: expected×actual is **not** lees `--par`. Gold pytest stays `EXPECTED-BOUND vs ACTUAL-BOUND`. Mutate, do not kill. Heretic will keep vow as a sibling of lees. Skeptic will park (“`diff` + sed `$HOME`”). Unix will want both pipes.

Clutch vs sinter: Heretic vehicle is **receipt as testimony**. Toolsmith/Unix/coordinator vehicle is **sinter** (RAGGED/STALE/CLEAN × content/clock/dirty-parent). Agree: do not ship kiln ∥ clutch. Disagree: which binary.

**What not to collapse:** lees = vow = alibi = veil (test-truth family has four objects: splice, substitution residue, two oaths, mock cover-type). clutch = sinter = yoke.

### 9. Leftover *claims* vs leftover *names* vs leftover *occupancy*

GHOST_CLUSTER: four objects under one metaphor. One leftover-*name* survivor (**wraith**) plus **zanei** (claims).
Unix: kill haunt; keep wraith; mutate zanei; keep deja/reverb as other objects.
Toolsmith: kill haunt; park wraith; **zanei PATH**; **reverb PATH**.
Heretic: kill haunt **and wraith**; keep zanei; **kill reverb**.
Skeptic: kill haunt/wraith/reverb; **zanei K thin** (`rg 0.3.0` reproduced the kizu poster).

`DESTROYER_ZANEI.md`: mutate, do not kill. Complementary holes: zanei cannot *see* a JSON-only fact; nagori sees it then throws away the prose leftover. ISO-date month `10` is leftover timeout. `generated/` is a leftover *build*, not a leftover *claim*.
`DESTROYER_SMOLDER.md`: invert of zanei (locus in, falsifying commit out). Gold kizu `plugin.json:4` is still `53cbd1a` Cargo.toml bump, **not** `git blame`. Mutate, do not kill. Do not repeat DESTROYER_ZANEI.

Predicted FINAL: Skeptic keeps zanei thinner (October/generated). Unix mutates zanei **and** smolder as opposite ends of one object. Heretic keeps claims, still kills names. Toolsmith still PATH zanei, still PATH reverb (tenaoshi `Content-Type`). Wraith stay/kill remains a three-way (Unix keep / Toolsmith park / Heretic+Skeptic kill).

**What not to collapse:** the night to leftover names (GHOST already forbade this). zanei = smolder = lien = erst (forward afterimage, invert-to-commit, natal CI gate, inflected cohort). reverb into zanei.

### 10. Sic / aka — PATH linter vs park

Unix: sic mutate (exact wire key; inflection is a fork). aka keep (inflection identity). Do not merge.
Toolsmith: **sic PATH** `git diff | sic --check`. aka preserve.
Heretic: park both. Inflection pacts are seen. Do not spend Gen-3.
Skeptic: park. `rg -i has_more`.

Coordinator already parked as incremental. That is a collapse of Unix/Toolsmith. Preserve: sic is a sharper linter, not an unseen object. Unix still wants the exact-key filter as a vehicle. Heretic still will not spend a slot.

### 11. Reverb / zure / veil / moor — PATH vs conventional

These four are where Toolsmith “tomorrow” and Heretic “seen it” fight without Skeptic in the middle (Skeptic kills/parks all four).

| tool | Toolsmith | Heretic | Unix | Skeptic |
| --- | --- | --- | --- | --- |
| reverb | PATH | kill | keep | kill |
| zure | PATH | park | keep | park |
| veil | kill | mutate cover-type | keep | kill |
| moor | preserve | kill composition | keep | kill |

**What not to collapse:** moor into pin×invert (Unix may still want a joint token; Heretic says trenchcoat). veil into alibi (Heretic: alibi can call a mocked SUT LOCKED). zure into rift (dirty vs two committed branches).

---

## Predicted FINAL lists (after DESTROYER + Gen-3 peels)

Independent prediction. If `FINAL_UNIX` etc. differ, **that difference is more evidence**, not a bug in this file.

### Unix — still several orthogonal mutate vehicles, still no winner

Will **not** shrink to Skeptic four. Will **not** elect invert as “the” tool.

Predicted mutate/carry (pipe them, do not merge):

- invert (filter); **weld** as concat sibling (DESTROYER_WELD: splice misses `response() + "\nDone."`; weld binds). Hold **stump** as invert peel (DESTROYER_STUMP: non-prefix tails stuffed into last hole — do not promote over invert).
- pin v0.5 + **keel** (origin = remotes+tips, not root SHAs). flume → **gist** (LSP 0-based stream).
- tell, perch, **ford** (lattice), **berth** (file identity).
- sate → **braid** (occupy the composed after-image, not N strand rows).
- erst → **lien** (`git diff |` natal CI).
- sic, sow, zanei → **smolder** (invert).
- lode → **assay** + xref (KIND, then getenv proof).
- lees → **vow** (two oaths, not residue).
- **cinch 0.3** (not tock, not 0.2, not a fourth).
- under → **ambit**; chime → **peal**. No third under-stream.
- cusp, doze.
- **beck** (first pipeline stage that produced this byte — not knot, not `tee | grep`).

Still kill haunt. Still park folk. Still: pinch∥hitch∥knot wait-source is knot; kiln∥clutch∥sinter is sinter. Still refuse a second inverse-printf **walker**.

Predicted fight with others: Unix will keep **more peels than Toolsmith will PATH** and **more conventional filters than Heretic will bless** (sic, cinch, gist, assay).

### Toolsmith — PATH is still “type tomorrow,” clones still die

Predicted PATH (not sixteen, not four):

- invert (paste a log).
- slip (last night’s CI after a split) — **not** pin.
- winnow + **cinch 0.3**.
- when (nested return).
- zanei (after a bound-value flip).
- sic `--check`.
- sate (suggestion already taken?).
- zure (pre-commit vs yourself).
- held (FocusRiverView still the poster).
- due *or* assay if the flood is capped — Toolsmith wanted due live (`MISSING KITTY_LISTEN_ON`). DESTROYER_ASSAY rustc flood will **scare** this judge toward `--app` / cap, not toward kill.

Likely **add** as CI tomorrow: **lien** (erst as a hook), **woof** (docs PR leaked code ply). Maybe **maiden `--check MAIDEN`** as a TDD gate — only if UNKNOWN on sitbone/kizu (213 / 489) does not make it a firehose.

Still kill: haunt, unfmt walkers, sluice-as-product, nigh, pinch/hitch, kiln/clutch products, veil, akin similarity, tock-as-PATH, amid-as-PATH.

Still preserve-not-PATH: pin, perch, erst, sow, sinter, coast, knot, stencil spare.

Predicted fight: Toolsmith will still PATH **slip, winnow, due, sic, zure, reverb** that Heretic/Skeptic reject. Will still **flag** under/chime/glean that Unix wants as verbs.

### Heretic — keep the unseen object; kill the useful corpse

Predicted keep-strange (objects, not CLIs):

when, perch, tell, invert, pin, erst, zanei, alibi, lees, sate, clutch, sow, coast.

**Add** (DESTROYER named new interactions):

- **ford** — occupancy is a lattice, not `git log --reverse`.
- **maiden** — never-red is not `rg PASS` (DESTROYER_MAIDEN: gold 2019-fail+2024-green still SCARRED; sitbone 213 UNKNOWN is the honesty, not a kill).
- **tacit** — omitted vs restated default (sitbone `presentThreshold` 27 TACIT / 0 SHADOW; `e9b0f75` BLAST 54). Not leftover-claims.
- **beck** — first producer of a byte; `git fatal` never entered the pipe; `tee | grep` is the skeptic and it misses.
- **vow** — two oaths, not lees residue.
- **smolder** — leftover invert (blame is the wrong commit).
- **weld** — concat starts at expr (Unix sibling; Heretic still the invert object).
- **berth** — file identity ≠ path.

Still **kill winnow/cinch** after LOCKSET_BAKEOFF. Honesty of timeout≠fail does not make ddmin a new interaction.
Still **kill slip/flume/gist** as relocators. Pin is the object. DESTROYER hardening is mutation of the token, not a reason to keep slip.
Still **kill due/lode/assay** as `strings`+`ldd` unless xref actually proves getenv (even then: conventional ABI dump).
Still **kill aka/sic, reverb, wraith, folk, moor, knot-as-product**.
Still clutch not sinter (receipt as testimony).

Predicted fight: Heretic list **grows** with DESTROYER objects that Skeptic will park as “I already had the file open.” That is the same museum/PATH fight as 03:00, with new exhibits.

### Skeptic — still four; DESTROYER did not mint a fifth

Predicted survivors: **winnow, cinch 0.3, invert, zanei (thinner)**.

- cinch **strengthened** (debug-print vs return is the object; 0.3 closed CLEAN-on-red).
- zanei **weakened** (poster is `rg 0.3.0`; October/`generated/` are conceptual lies). Keep is still the unnamed 40-hunk PR, not the version bump.
- invert **held** (instance digits not in source). Do not ship stump until prefix-of-instance is honest (DESTROYER_STUMP).
- winnow **unchanged** (dirty hunks are not `git bisect`).

Still drop from coordinator intersection: when, sate, held/perch, pin, erst, sow, coast.
Still will not mint pin (v0.5 / keel closed old attacks; tomorrow-test is fingers, not fixtures).
Still `git log --full-history` for FocusRiverView.
Still `git apply --check --reverse` for sate’s sandwich (rc=0 on HEAD is the boolean working).
Maiden UNKNOWN flood (213/489) is a Skeptic exhibit **against** PATH.
Assay rustc 12k DUE is a Skeptic exhibit **against** env-ABI PATH.
Woof/lien are linters (`rg -i` / “I know what I deleted”). Predicted **park**, not a fifth.

Predicted fight: Skeptic four vs everyone else’s breeding pool. Coordinator already refused to collapse. Final jury must **name** that refusal, not silently install twelve.

---

## Later-object splits (Gen-2/3 inherit the same fight)

Do not treat peels as new consensus. Each peel is a new place the four vetoes re-apply.

| later object | DESTROYER | Unix will | Toolsmith will | Heretic will | Skeptic will |
| --- | --- | --- | --- | --- | --- |
| **stump / lede / splice / weld** | STUMP, WELD: mutate; concat is sibling | weld mutate; stump peel of invert | invert PATH; weld if paste is concat | invert object; weld mutation | invert only; hold stump |
| **pin v0.5 / keel / shoal** | PIN_V5, KEEL: mutate; remotes are config | pin+keel vehicles | slip PATH; pin preserve | pin is the object | will not mint |
| **ambit / amid / peal** | AMBIT bakeoff; PEAL mutate | ambit+peal pipes | flags on when | stack object | open the file |
| **cinch 0.3 / snug / tock / hasp / gage** | CINCH; LOCKSET bakeoff+tock | cinch 0.3 only | cinch+winnow PATH | kill family | cinch+winnow |
| **assay / xref / shim** | ASSAY: KIND real, DUE flood | assay+xref | due / capped assay | kill `ldd` | kill `strings` |
| **ford / weir / hydra** | FORD: lattice | occupancy peel | preserve | **keep-strange** | `--full-history` |
| **berth / holt / crib** | BERTH: first-parent miss | identity peel | preserve | keep-strange | `git log --follow` |
| **lien / kith / sire** | LIEN: two `version` nouns | erst as `git diff \|` | **CI PATH?** | erst object | `git show` + `rg` |
| **smolder / tinder / binom** | SMOLDER: not blame | zanei invert | after leftover | keep-strange | `git blame` / `-S` |
| **maiden / badge** | MAIDEN: parser × string id | observation fold | **TDD PATH?** | **keep-strange** | `rg PASS`; UNKNOWN flood |
| **tacit / aloud / preen** | TACIT: not leftover-claims | default-slot filter | maybe after BLAST 54 | **keep-strange** | I read the call |
| **beck / innard / facet** | BECK: not `tee \| grep` | first-producer filter | when the log is empty | **keep-strange** | look at git stderr |
| **vow / troth / writ** | VOW: not lees `--par` | two-oath pipe | park with lees | **keep-strange** | `diff` + sed |
| **braid / plait / hank** | BRAID: occupy the fold | sate peel | sate PATH; braid preserve | sate object | `git apply --check` |
| **gist / blot / rune** | GIST: 0-based LSP | flume schema | slip companion | **kill relocator** | `rg` the name |
| **woof / weft / tally** | WOOF: no path exception | ply filter | **docs-PR PATH?** | kill linter | park linter |
| **scarp / twixt / yaw** | SCARP: `ntp=` is adjtime | clock-cut filter | park | not coast; maybe keep | I know the lid closed |
| **sow / hatch / till / seep** | (author + later) | sow vehicle | preserve | sow object; kill cleave | quarterly `rg` |

`STATE.md` carry list (cinch 0.3, ambit, scarp, plait, berth, lien, invert/weld, pin v0.5, assay/xref) is a **coordinator shortlist**. It already leans Unix+Toolsmith. Heretic extras (coast, clutch, alibi, tacit, maiden, beck) and Skeptic deletions (everything but four) are not represented. Do not treat STATE vehicles as jury verdict.

---

## What already converged (safe to collapse)

These are not disagreements. Do not re-litigate them as if they were.

1. **haunt is dead.** All four. GHOST_CLUSTER. Lost skills `preact-zero-mock`. Worse wraith.
2. **folk is parked.** 0 real orphans after honesty filter. DISTINCT. Do not spend handshake-mining slots. (Heretic would kill; the rest park. Either way: no Gen-3.)
3. **nigh is dead.** String-edit `ENOENT`≈`event`. **cusp** owns the cut. All four.
4. **akin similarity is dead.** Invented merge-bases. **once** exact-blob / `--port` only. All four.
5. **unfmt-08 / unfmt-13 as products are dead.** Invert is the inverse-printf vehicle. Stencil is walker spare. UNFMT_BAKEOFF. No second walker. Coordinator ban held through Gen-3.
6. **pinch ∥ hitch as products are dead.** Knot harvested the wait-source. (Unix keep knot / Heretic park knot is a *different* split, above.)
7. **kiln ∥ clutch as two products are dead.** One lot object. (Vehicle name is the split: sinter vs clutch.)
8. **No thirteenth leftover-name search.** All four. zanei is claims, not names.
9. **Invert: mutate, do not kill.** DESTROYER_PIN_INVERT + STUMP. Binary fail closed. No-hole prefix must not beat a binding. Refuse rustc grammar.
10. **Pin: mutate, do not kill.** DESTROYER list then v0.3 then v0.5 then keel. Unique kizu tokens do not hallucinate onto voidtrace/tenaoshi. (PATH vs object vs `rg` is the split, not live/die.)
11. **Lockset ≠ fingerprint.** All three lockset binaries drop `print("debug")` and keep `return a + b`. That empirical fact is shared. (Keep/kill of the family is the split.)
12. **No fourth cinch. No third under-stream. No second pin-v0.5 destroyer.** Process decisions, already held.

---

## What not to collapse overnight (the preservation list)

Write these as two columns in `EVOLUTION_REPORT.md`. A single “survivors” bullet is a lie.

1. **Skeptic four** (winnow, cinch, invert, zanei) **vs Heretic keep-strange** (when, perch, tell, invert, pin, erst, zanei, alibi, lees, sate, clutch, sow, coast, **plus** ford/maiden/tacit/beck/vow/smolder). Overlap is two tools. Do not average to nine.
2. **Winnow/cinch keep vs Heretic ddmin kill.** Bakeoff honesty is not a novelty waiver. Do not bury winnow because cinch 0.3 exists; predicates differ.
3. **Pin token vs slip PATH vs `rg` the name.** Hardening closed DESTROYER bugs; it did not close Skeptic’s fingers or Heretic’s object.
4. **When as PATH vs under/peal as pipes vs open-the-file.** Three CLIs vs flags vs “I had L43–57 on screen.”
5. **Occupancy family: held boolean vs perch witness vs tell invert vs ford lattice vs berth identity.** DESTROYER says each walk lies in a different way. Do not ship one `occupancy` dashboard. Do not delete the family because `--full-history` exists.
6. **due PATH vs lode/assay KIND vs kill `ldd`.** rustc DUE flood is evidence for Skeptic and a mutation for Unix, not a unanimous kill.
7. **coast (waitpid is a lie) vs knot (wait-for graph).** Heretic vs Unix. scarp is a third object (which clock explains a gap).
8. **clutch testimony vs sinter assay.** One lot; two vehicles. Coordinator already picked sinter — that pick is **not** Heretic’s.
9. **alibi / lees / vow** as unseen test-truth vs E=3 / “I compare snaps rarely.” Do not drop because no cargo splice; do not PATH because the object is sharp.
10. **zanei thin-keep vs reverb PATH vs wraith spare.** Leftover *claims* / *copies* / *names* stay three objects. DESTROYER_ZANEI/SMOLDER mutate claims; they do not resurrect names.
11. **sic/aka as Unix/Toolsmith linter vs Heretic/Skeptic park.** Coordinator “park as incremental” hides Unix’s mutate vehicle.
12. **maiden never-red vs `rg PASS`.** UNKNOWN on real suites is honesty for Heretic and a firehose for Skeptic.
13. **tacit omission vs zanei claims.** DESTROYER_TACIT: nothing in the battery turned omission into leftover-name search. Do not fold.
14. **beck first-producer vs knot vs `tee | grep`.** Gold `git fatal` on stderr never entered the pipe. Do not fold into wait-graphs.
15. **STATE.md / STATUS.md shortlists.** They lean Unix+Toolsmith carry. They omit Heretic extras and Skeptic deletions. Using them as the jury ballot **is** collapsing overnight.

---

## How to read other FINAL_* (when they land)

If `FINAL_SKEPTIC` is still four and `FINAL_HERETIC` still kills winnow: **the split held.** Report it.
If `FINAL_UNIX` elects weld+ambit+assay+ford and `FINAL_TOOLSMITH` still PATH slip+due+winnow: **the split held.**
If any FINAL file presents a single ranked twelve: that file collapsed what this one forbids. Prefer the four-column ledger.

Coordinator (`FIRST_SELECTION`) is a fifth voice that already split differences (cinch not winnow; sinter not clutch; orbit+lode not due; pin not slip). Treat that as **one proposed treaty**, not as observed agreement.

---

## This judge is not doing

- Not picking a winner. Invert is the inverse-printf *filter*. Cinch is the lockset *predicate*. When is a *question-word*. Pin is a *token*. They are not competitors.
- Not averaging Σ. Heretic N-veto and Skeptic U-veto are designed to disagree with Unix P/C and Toolsmith U.
- Not promoting DESTROYER “mutate, do not kill” into PATH. Mutate-not-kill is live/die. PATH is tomorrow. Object is novelty. Three questions.
- Not installing STATE vehicles as the night’s result.
- Not killing held / pin / perch / sate / erst / sow / coast because Skeptic parked them.
- Not keeping winnow because it is useful **if the report pretends Heretic agreed**.

Haunt stays dead. Folk stays parked. Several survivors. **The survivors are not the same set.** That is the result.
