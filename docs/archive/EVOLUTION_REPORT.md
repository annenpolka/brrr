# Overnight Developer Tool Evolution Lab — Evolution Report

- Window: **2026-08-19 23:45 – 2026-08-20 09:00 JST**
- Repo (coordinator only): `lab/` reports; implementations live in isolated worktrees under `~/.grok/worktrees/annenpolka-brrr/`
- This file: **08:45 JST** preservation pass. Sources: `lab/judges/FINAL_*.md`, `DESTROYER_*.md`, bakeoffs, `lab/STATE.md`, harvested `lab/lineages/*/CANDIDATE.md`
- **Do not collapse disagreement.** Four vetoes (Unix / Toolsmith / Heretic / Skeptic) are orthogonal. Averaging them is a fifth judge in a trenchcoat.

---

## 1. Executive summary

An overnight autonomous lab spawned ~16 isolated inventors at a time for ~9 hours. They were not asked to ship a product. They were asked to invent **developer-tool primitives that do not meaningfully exist yet**, then mutate, hybridize, reimplement from behavior, and destroy the survivors.

What actually happened:

1. **Cambrian explosion (Gen 1).** Sixteen independent CLIs in the first hour. Convergent accidents: two `unfmt` walkers; later `ambit`∥`amid`; `kiln`∥`clutch`.
2. **First selection (~03:00).** Unix / Toolsmith / Heretic / Skeptic already split. Intersection kept invert, zanei, cinch (as a lockset, not as winnow), when, pin-as-token. Haunt died. Folk parked. Skeptic’s tomorrow-test was four objects: **winnow, cinch, invert, zanei**.
3. **Gen 2 breeding until 06:30.** Vehicles formed: cinch 0.3, ambit, scarp, plait, berth, lien, invert/lede/splice, pin v0.5, assay/xref. A 04:32 parent+loop collision double-spawned mutation-59..68; harvest is **by tool name**.
4. **Dedicated destroyers 06:30–07:30.** Sixteen DESTROYER reports. **Every dedicated destroyer said mutate, do not kill.** That is a breeding instruction, not an install list.
5. **Gen 3 07:30–08:20.** Sixteen peels aimed at those holes (lurch, holt, noun, …, solder). FINAL_GEN3: most holes **partially** closed, none fully papered, none fully sealed.
6. **Final jury 08:20–08:40.** Sixteen independent FINAL_* reports. They still do not agree on PATH. They do agree on objects.

The night produced **several usable prototypes** and stronger evidence: which unexplored verbs are real (even if you should not install sixteen of them tomorrow).

Coordinator process: parent tree is reports-only. Heartbeat `01a01b54e731` every 15m. Hard end 09:00 JST.

---

## 2. Survivors

Rank the **object**. Peels are mutations, not extra PATH entries. No single winner.

### Objects that survived destroyers *and* a second inventor

| Object | Vehicle (STATE / FINAL_VEHICLES) | Why it survived |
| --- | --- | --- |
| Inverse printf + named holes + span | **invert** (lede closes middle-drop stuffing; concat sibling **weld/stile/solder**) | UNFMT_BAKEOFF; DESTROYER_PIN_INVERT / STUMP_PIN: 7-hole paste binds; walkers died |
| 1-minimal production lockset | **cinch 0.3** | DESTROYER_CINCH + LOCKSET_BAKEOFF 4/4 honest; 0.2 CLEAN-on-red is extinct; snug clean-room recovered always-run-NEW; tock ties, does not unseat |
| Leftover *claims* a diff made false | **zanei** forward; **ember/cinder** typed fact + ash; **smolder** invert | DESTROYER_ZANEI: JSON silence lethal → ember; October≠timeout 10; generated dest is ash not believer |
| Path-condition stack (`given`) | **when**; stream invert **ambit** | kizu `parse.rs:60` prints fallthrough `given` `rg` never printed; AMBIT_AMID carried ambit |
| File identity / occupancy eras | **held/perch**; file-id **berth** default should be **holt** (all-reachable R) | DESTROYER_BERTH: first-parent default lied; holt either-name TRUE 187/244 |
| Clock-cut filter (no spawn) | **scarp** pair oracle; stream **lurch** | DESTROYER_SCARP: Darwin monotonic is uptime-raw; `ntp=` is adjtime; two-cuts vs stream |
| Suggestion composition algebra | **plait**; occupy-the-fold **braid** | DESTROYER_PLAIT mutate; COMMUTE/JAM gold; ECHO is locus |
| Env ABI two columns | **assay** KIND; **xref/shim** DUE = getenv *use* | DESTROYER_ASSAY rustc 12k DUE flood; xref collapsed to tens; shim refuses `*getenv` suffix |
| Pin token (not relocator) | **pin v0.5**; origin peel **keel/shoal** | leftover stub / extract-and-keep closed; origin=live remotes is a lie → shoal |
| Natal CI | **lien**; package-scoped **noun** | DESTROYER_LIEN workspace `version` homonym; noun `(package, noun)` |

### Judge disagreement on *which* survivors are PATH

| Judge | Would put on PATH / keep as daily verb |
| --- | --- |
| **Unix** (FINAL_UNIX) | invert, scarp, zanei, cinch 0.3, ambit, plait, sate, when — eight *different* objects, pipe them |
| **Toolsmith** (FINAL_TOOLSMITH) | invert, winnow, cinch 0.3, zanei, when, **preen**, **noun**, **holt** |
| **Heretic** (FINAL_HERETIC) | when, tacit, beck, tell, invert, perch, plait, coast, alibi, lees, smolder, maiden, weld, braid, vow, zanei — kills winnow/cinch as ddmin |
| **Skeptic** (FINAL_SKEPTIC) | **four objects**: cinch 0.3, winnow, invert, ember (zanei parked for JSON silence) |
| **Tomorrow** (FINAL_TOMORROW) | **four binaries**: winnow, cinch 0.3, **lede**, **cinder** (swaps invert→lede, zanei→cinder) |

Haunt stays dead. Folk stays parked. Pin’s *object* survived; Skeptic/Tomorrow still will not mint. That split is evidence.

---

## 3. Weirdest discoveries

From FINAL_WEIRD (surprise, not utility):

1. **Which clock owns the leftover** (`scarp`). Two cuts → SLEEP / DILATE / STEP / REST. Darwin `time.monotonic()` is `CLOCK_UPTIME_RAW`. Lid-close is a day of sleep, not a 29-hour NTP step. `ntp=` is adjtime. The misname *is* the discovery.
2. **Omission as occupancy of a future** (`tacit`). Two call-sites inhabit `0.45` with opposite futures (TACIT vs SHADOW). Compilers do not warn. Coverage is green. sitbone hysteresis tests omit the thresholds they are about.
3. **First producer of a byte, including the fd that never entered the pipe** (`beck`). `git status | cat` fatal is `MINT stderr`, `piped_bytes=0`. `tee | grep` is a different question.
4. **This leftover claim, which commit made it false?** (`smolder`). kizu `plugin.json:4` *blame* is `bff820fb`; *falsifier* is `53cbd1a` Cargo.toml `0.3.0→0.3.1`. Named lockfile dest says **regenerate**.
5. **Review suggestions compose with each other**, not with the tree (`plait`: COMMUTE / STACK / JAM). GitHub “Commit suggestion” is untyped.
6. **DUE is a getenv-shaped use**, not an env-shaped token (`xref`). assay rustc 12,596 DUE → tens. `/bin/ls` is `CLICOLOR_FORCE`, not prefix-peel `COLOR_FORCE`.
7. **One failing assertion is two machines** (`vow`: EXPECTED-BOUND vs ACTUAL-BOUND). Comments are not oaths.
8. **Never-red is a history fold; no records is UNKNOWN** (`maiden`). `--latest` maidens a 2019-fail; `--skeptic` is the anti-`rg PASS`.
9. **Occupancy of a merge is a join**, not a boolean on the merge SHA (`ford`). Snapshot-has-it is not birth.
10. **Concat may start at an expression** (`weld`). Invert’s unfinished sibling, not a second family.

Toys sitting on verbs: weld-as-PATH; tacit clap TACIT=6; beck greedy `@0.7.0`; xref `--loose`; maiden string-id; scarp unlabeled duration-bag.

---

## 4. Convergent evolution

Independent invention or assigned clean-room that recovered the **same object** (FINAL_CONVERGE):

| Pair | Object |
| --- | --- |
| unfmt-08 ∥ unfmt-13 | inverse printf (walkers; invert harvested names+span) |
| kiln ∥ clutch | generation lots from artifact testimony → sinter fused |
| ambit ∥ amid | `under` as `rg \|` file stream (bakeoff **carried ambit**) |
| held ∥ dwelt | occupancy *eras*, not a bisect cut |
| perch ∥ roost | TRUE splits when the holder set changes |
| when ∥ whence | path-condition stack including fallthrough `given` |
| zanei ∥ nagori | leftover *claims* a diff just made false |
| cinch ∥ snug | 1-minimal production hunks current tests veto |
| erst ∥ brood | natal cohort of a *change*; keys inflect |
| xref ∥ prove | DUE = getenv-shaped *use* |
| weld ∥ solder | concat may start at an expression |
| helm ∥ cleat | leftover re-export relative to leftover *file* |
| scarp ∥ reimpl-08 scree | two clock cuts, no spawn |

**Not convergence:** name collisions (`scree` lockset-invert vs clock-cut; `berth` file-id vs identity-birth); lineage peels; leftover-*names* vs leftover-*claims*.

Bakeoffs that still hold: **UNFMT** → invert; **AMBIT_AMID** → ambit; **LOCKSET** → cinch 0.3.

---

## 5. Extinctions

Promising ideas that failed empirical testing (FINAL_KILL / FINAL_EXTINCT / first selection):

| Dead product | Why |
| --- | --- |
| **haunt** | Inverse-dead-code; v0.1 false positives; v0.2 honesty printed 0 on skills and lost the poster wraith already had |
| **leftover-name search as a class** | haunt/wraith-as-PATH/wisp remnants. `rg` the dead name. Not zanei |
| **nigh as default** | String-distance firehose (lifetimes as strings, ENOENT~event). **cusp/kerf** remain as the cut |
| **cinch 0.2** | DESTROYER_CINCH: test-only red → CLEAN rc=0, NEW skipped. Occupancy of nothing. Object lives as **0.3** |
| **unfmt-08 / unfmt-13 as products** | Walkers. Invert is the filter |
| **folk** | Parked: 0 real orphans on dogfood (handshake object empty, not destroyed) |
| **amid as vehicle** | Independent rebuild of ambit; json/derive spare. Zombie, not PATH |
| **akin similarity / pinch / hitch / kiln / clutch / moor / cleave / yoke / sluice-as-PATH** | Clones, fusions, or stream-without-names |

**Do not kill without new evidence** (every dedicated DESTROYER: mutate): invert, pin v0.5, zanei, cinch 0.3, held/when/ambit, plait, scarp, beck, tacit, xref, smolder, maiden, vow, berth/holt, lien/noun, weld-as-sibling.

Gen3 did **not** extinct those objects. FINAL_GEN3: lurch/holt/noun/stile/shim/shoal/… **partial** closes. solder still hits weld’s truncated-fence success (reimpl recovered the ancestor’s lie). badge still empty-`{}` on go-fail. hydra still continues TRUE 17 commits after a 1-of-2 merge.

---

## 6. New primitives

Worth remembering if every Python file tonight is deleted (FINAL_NOVELTY, one sentence each):

| Verb | Primitive |
| --- | --- |
| **invert** | Runtime string queries format templates; bind named holes; leftover wrap is a **span** |
| **zanei** | A unified diff makes bound facts false; print dest lines that still assert the old fact (**belie**, not leftover-name) |
| **held** | Contiguous **eras** where a predicate holds; not bisect, not `git log -- path` |
| **when** | Nested predicates still in force at a locus, including fallthrough **`given`** |
| **cinch** | 1-minimal **production** hunks current tests veto; tests stay NEW; not a command fingerprint |
| **pin** | Mint a self-contained locus **token**; leftover stubs are pointers, not identity |
| **tacit** | Defaulted slot is not a value: TACIT / SHADOW / OVERRIDE / BOUND; default-moving diff is BLAST+FOSSIL |
| **beck** | Earliest pipeline stage that already contains this byte; name the **fd** |
| **vow** | A failing assertion is **two oaths** (expected-literal vs actual-side machines) |
| **scarp** | Two clock-cuts → which clock explains the gap; **no spawn** |
| **plait** | Suggestion strands **compose with each other** before anyone occupies a tree |
| **xref** | Env ABI has two columns; **DUE is a getenv-shaped use**, not an env-shaped token |
| **maiden** | Never-red is a **fold over recorded outcomes** of a test identity; no records is UNKNOWN |

Inflections, not extra founding verbs: perch (held + holder set), under (when inverted), given (the noun when discovered).

Forget as PATH: unfmt walkers, cinch 0.2, snug/tock as products, nagori as a second belie, peal/seed as a third ambit, pin+keel+shoal as three mint tools, weld+lede+splice as three inverse-printfs.

---

## 7. Tomorrow test

Which tools a human should **actually install and try** tomorrow. Empty slots are load-bearing.

### Skeptic / Tomorrow (strict: instead of git/rg)

Four binaries. Coordinator STATUS’s eleven families is a **breeding board**, not PATH.

| Install | Lineage | Smoke |
| --- | --- | --- |
| **winnow** | `lab/lineages/candidate-15__winnow/` | `./demo.sh` — dirty-hunk ddmin vs a command fingerprint |
| **cinch 0.3** | `lab/lineages/mutation-48__cinch/` | `./demo.sh` — lockset wheat is `return a+b`; debug print is chaff; test-only red is BROKEN |
| **lede** *or* **invert** | `mutation-33__lede/` / `mutation-15__invert/` | Tomorrow installs **lede** (middle-drop miss). Skeptic installs **invert** (lede is a flag). Unix installs invert. **Do not install both.** |
| **cinder** *or* **ember** | `mutation-37__cinder/` / `mutation-32__ember/` | Tomorrow: **cinder** (ash ≠ believer). Skeptic: **ember** (JSON facts). FIRST kept **zanei**. **One leftover-claim binary.** |

Worktrees are in each lineage `WORKTREE.txt`. Python 3.9+/3.10+, `git`, no SaaS.

Do **not** install: cinch 0.2, haunt, nigh, amid, pin (object real; you will not mint), when (open the file — Skeptic), occupancy dashboards, Gen3 peels as extra argv[0], a fourth cinch, a third ambit, a second inverse-printf walker.

### Toolsmith (would run on a dirty tree)

Adds **when**, **preen** (tacit constructed-default), **noun** (lien workspace identity), **holt** (berth all-reachable R) to the four-object core.

### Heretic (unseen interaction)

Will **not** install winnow/cinch (ddmin). Will keep **when, tacit, beck, tell, perch, plait, coast, alibi, maiden**. That is a museum, not a morning PATH — and it is useful evidence about what was actually new.

Copy-paste (Tomorrow’s four):

```bash
# 1. dirty-tree fingerprint
cd "$(cat lab/lineages/candidate-15__winnow/WORKTREE.txt)" && ./demo.sh
# 2. production lockset (not 0.2)
cd "$(cat lab/lineages/mutation-48__cinch/WORKTREE.txt)" && ./demo.sh
# 3. inverse printf (lede; or invert)
cd "$(cat lab/lineages/mutation-33__lede/WORKTREE.txt)" && ./demo.sh
# 4. leftover claims (cinder; or ember/zanei)
cd "$(cat lab/lineages/mutation-37__cinder/WORKTREE.txt)" && ./demo.sh
```

---

## 8. Lineage tree

Compact history from FINAL_LINEAGE. `★` vehicle; `†` extinct product; `⟳` independent discovery; `!` name collision.

```
inverse-printf        unfmt-08/13 ⟳ → sluice → invert★ → stump → lede → splice → weld → rime → caulk → stile
                      hybrid: moor (slip×unfmt)     reimpl: stencil†  solder
                      ★ invert   concat peel: weld/solder   no walker

leftover-claims       zanei★ → ember → cinder → smolder★ → tinder → binom
                      reimpl: nagori               hybrid: kith → lien★ → sire / noun
                      leftover-name haunt† / wraith zombie   not this family

path-conditions/when  when★ → under → chime → graft → ambit★ → peal → liken → wane
                      reimpl: whence               hybrid: thatch → neap → dirge; seed
                      amid† spare (same object as ambit)

occupancy/held        held★ → perch★ → stead → berth-52 → holt★ → ford★ → weir → hydra
                      reimpl: dwelt, roost         copy: ditto → crib → pup
                      ! berth-56 is identity-birth, not file-id

lockset               winnow (fingerprint ancestor) → cinch 0.2† → cinch 0.3★
                      reimpl: snug → tock (tie, not PATH)   hybrid: hasp, gage
                      no fourth cinch

pin                   slip → pin v0.2..v0.5★ → keel → shoal
                      leftover-pointer: shunt → helm → cleat
                      locator stream sibling: flume → gist → blot → rune

env-ABI               due → lode → assay★ → xref★ → lash → wad → shim★
                      reimpl: prove

suggestion-algebra    ply → plait★ → wale → braid★ → hank → quire → tilde
                      ⟳ spar                     occupancy sibling: sate → lodge → dreg

clocks                lapse → scarp★ → twixt / yaw → lurch★
                      reimpl: scree-R08   ! mutation-62 scree is lockset chaff

tacit                 tacit★ → aloud → unsay → preen
beck                  beck★ → facet / innard
maiden                maiden★ → badge
```

Book-ID collisions (04:32 parent+loop): harvest by **tool name** (`mutation-59__weld` vs `mutation-59__twixt`).

---

## Appendix — where to look

| What | Where |
| --- | --- |
| Constitution | `Overnight Developer Tool Evolution Lab — Master Prompt.md` |
| Live board | `lab/STATE.md`, `lab/heartbeat.md`, `lab/STATUS.md` |
| First selection | `lab/FIRST_SELECTION.md`, `lab/judges/FIRST_*.md` |
| Bakeoffs | `lab/judges/{UNFMT,AMBIT_AMID,LOCKSET}_BAKEOFF.md`, `LOCKSET_TOCK.md` |
| Destroyers | `lab/judges/DESTROYER_*.md` |
| Final jury | `lab/judges/FINAL_*.md` |
| Lineage reports | `lab/lineages/<id>__<tool>/` (`CANDIDATE.md`, `README.md`, `demo.sh`, `WORKTREE.txt`) |
| Implementations | isolated worktrees; **not merged onto main** |

Preservation rule honored: prototypes stay in worktrees; this repo keeps the evidence.

*Report written 2026-08-20 08:45 JST. Loop `01a01b54e731` remains until 09:00, then stop spawning and delete the scheduler.*
