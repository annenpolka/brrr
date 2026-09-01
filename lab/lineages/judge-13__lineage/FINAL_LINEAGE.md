# FINAL_LINEAGE — judge-13 (Lineage-tree Judge)

Independent. Isolated worktree. Not a merge. Compact history for `EVOLUTION_REPORT.md` §8.

Clock: 2026-08-20 08:20–08:40 JST. Sources: `lab/STATE.md`, `lab/EMERGING.md`, `lab/FIRST_SELECTION.md`, `lab/STATUS.md`, `lab/heartbeat.md`, `lab/judges/*`, directory names and `CANDIDATE.md` primitives under `lab/lineages/`. I do not grade my own lineage. I do not collapse first-selection disagreement.

**Shape:** candidate → mutation → hybrid → survivor.

**Notation**

| mark | meaning |
| --- | --- |
| `C-` `M-` `H-` `R-` `D-` | candidate / mutation / hybrid / clean-room reimpl / destroyer |
| ★ | survivor vehicle (one object, one verb) |
| † | extinct as a product; keep the transcript |
| ⟳ | independent convergent discovery |
| ! | book-ID or tool-name collision (not kinship) |

Destroyers listed below all said **mutate, do not kill**, unless marked †. Peels stay peels. Do not ship two kernels of the same object.

---

## Survivors (paste-ready for §8)

```
candidate → mutation → hybrid → survivor

inverse-printf        unfmt-08/13 → sluice → invert → stump → lede → splice → weld → rime → caulk → stile
                      hybrid: moor (slip×unfmt)     reimpl: stencil†  solder
                      ★ invert   concat peel: weld/solder   no walker

leftover-claims       zanei → ember → cinder → smolder → tinder → binom
                      reimpl: nagori               hybrid: kith → lien → sire / noun
                      ★ zanei (forward)  ★ smolder (invert)  ★ lien (natal CI)

path-conditions/when  when → under → chime → graft → ambit → peal → liken → wane
                      reimpl: whence               hybrid: thatch → neap → dirge; tenure; seed
                      ★ when   ★ under   ★ ambit   ★ peal   amid† spare

occupancy/held        held → perch → stead → berth-52 → ford → weir → hydra
                      reimpl: dwelt, roost         hybrid: tenure
                      copy peel: ditto → crib → pup    all-R: holt
                      ★ held   ★ perch   ★ berth (file id)   ★ ford (merge join)

lockset               winnow/alibi (ancestors, not this object) → cinch 0.2 → cinch 0.3
                      reimpl: snug → tock†         hybrid: hasp, gage → brand → sear
                      invert: mute, scree-62†
                      ★ cinch 0.3   no fourth cinch

pin                   slip → pin v0.2 → v0.3 → v0.4 → v0.5 → keel → shoal
                      leftover-pointer peel: shunt → helm → cleat
                      locator stream (sibling): flume → gist
                      ★ pin v0.5   origin peel: keel/shoal   ★ flume is not pin

env-ABI               due → lode → assay → xref → lash → wad → shim
                      sibling: orbit, latent       reimpl: prove
                      ★ assay (KIND)   ★ xref (DUE = getenv proof)

suggestion-algebra    ply (grain) → plait → wale → braid → hank → quire
                      ⟳ spar                       hybrid: tilde
                      sandwich occupancy (sibling, not algebra): sate → lodge → dreg
                      ★ plait   ★ braid occupies the fold

clocks                lapse → scarp → twixt / yaw → lurch
                      reimpl: scree-R08
                      ★ scarp   stream peel: twixt/lurch   SLEW peel: yaw   lapse† as product

tacit                 tacit → aloud → unsay → preen
                      ★ tacit

beck                  beck → facet / innard
                      ★ beck

maiden                maiden → badge
                      ★ maiden
```

---

## 1. inverse-printf

Object: paste a runtime string; bind the source template that could have produced it. Unix mouth is a **stream filter**, not a tree walker.

```
C-08 unfmt (walker, anonymous holes)          C-13 unfmt (walker, named holes) ⟳
        |                                              |
        |                         names + span harvested
        v                                              |
M-02 sluice  stream; no implicit walk  <---------------+
        |
        v
M-15 invert ★  names + leftover span; bakeoff 5/5  [lab/judges/UNFMT_BAKEOFF.md]
        |
        +-- R-01 stencil †  walker spare (beats unfmt-08 on sitbone camera)
        +-- H-01 moor       slip × unfmt: one-pass locator + holes (adjacent)
        |
        v
M-23 stump     prefix-of-instance; rustc locators refused
        |      D DESTROYER_PIN_INVERT / DESTROYER_STUMP_PIN: mutate
        v
M-33 lede      bind prefix only; later holes unbound; middle-drop is a miss
        |
        v
M-34 splice    concat "lit" + expr + "lit"  (string-first)
        |      ! book-ID collision with pin v0.4
        v
M-59 weld      expr-first concat; proving string backward
        |      D-17 DESTROYER_WELD: mutate
        +-- R-11 solder  weld rebuilt from DESTROYER_WELD behavior
        |
        v
M-79 rime      leftover of a partial bind → next concat template
        |
        v
M-91 caulk     leftover must be a complete concat operand
        |
        v
M-109 stile    proving string must be distinctive (not a newline/fence)
```

**Survivor: invert.** Concat (splice → weld → rime → caulk → stile) is one peel family. Do not grow a second ignore policy. unfmt-08/13 and stencil stay transcripts. Coordinator: “no leftover-name, no inverse-printf walker” — agreed.

---

## 2. leftover-claims

Object: a *fact* a diff just made false; dest still asserts it. **Not leftover names.**

Ghost cluster (`lab/judges/GHOST_CLUSTER.md`) is a different tree: haunt † (worse wraith), wraith (name holdouts), wisp (interval ghosts), reverb (change-as-query), deja (RELAPSE/UNDOFIX). Do not breed another leftover-name search.

```
C-07 zanei ★  diff in → afterimages out; linter exit 0/1
        |
        +-- R-03 nagori  clean-room gold (sitbone 0.4, kizu version)
        |      D DESTROYER_ZANEI: mutate both (JSON-only vs prose leftover)
        v
M-32 ember     typed facts: version token; calendar month ≠ integer; JSON key
        |
        v
M-37 cinder    regenerated dest is ash, not a believer
        |
        +-- H-09 kith    ember × erst: natal-record leftovers (claim+kin)
        |         |
        |         v
        |    M-57 lien ★  `git diff |` natal CI gate
        |         |       D-13 DESTROYER_LIEN: mutate (homonym `version`)
        |         +-- M-68 sire   leftover locator → natal change (invert of lien)
        |         +-- M-105 noun  natal identity is (package, noun)
        |
        v
M-63 smolder ★ leftover locus → falsifying commit; ash says regenerate
              D-21 DESTROYER_SMOLDER: mutate
        |
        +-- M-81 tinder   --follow dest-file identity
        +-- M-113 binom   fact identity (crate, noun, dest)
```

Pin leftover-as-pointer is **not** leftover-claims (it is pin §6):

```
DESTROYER_PIN_V5 → M-66 shunt → M-80 helm → R-10 cleat
```

**Survivor: zanei** (forward), **ember/cinder** (typed + ash), **smolder** (invert), **lien** (natal CI). Coordinator tomorrow-test listed zanei/ember/cinder only; I keep smolder and lien as orthogonal mouths of the same object.

---

## 3. path-conditions / when

Object: the nested predicates still in force at a locus (`given` frames), not the function name and not a hunk window.

```
C-20 when ★  file:line (or diff / grep) → condition stack
        |
        +-- R-04 whence     clean-room; kizu parse.rs:60 gold
        |
        +-- M-10 under ★    invert: name a snippet, print the loci
        |         |
        |         +-- M-35 ambit ★  `rg |` file stream; bakeoff over amid
        |         |         M-35 amid ⟳ † spare (json/derive mouth)
        |         |         ! book-ID collision: ambit / amid / graft
        |         v
        |    M-51 peal ★    chime as that stream
        |              D-24 DESTROYER_PEAL: mutate (first-locator / pins[:16])
        |         |
        |         v
        |    H-19 seed      seed is one content pin, not first locator
        |
        +-- M-16 chime      same stack, or superset (deeper nest)
        |
        +-- M-35 graft      unapplied-patch post-image
        |         |
        |         v
        |    M-61 liken     invert graft: added lines that share a stack
        |
        +-- H-10 thatch     covering stacks of two trees, then occupy
        |         |
        |         v
        |    M-58 wane      exclusive-A stack deaths
        |         |
        |         v
        |    H-14 neap      liken × wane: overlay deaths
        |         |
        |         v
        |    M-100 dirge    sibling-arm obituary (if/elif as one death)
        |
        +-- H-05 tenure     when stack occupies history (cross-link §4)
```

**Survivor: when** (the noun), **under** (invert), **ambit** (file stream), **peal** (chime as that filter). amid spare. No third ambit. Coordinator listed ambit/peal as carry; I refuse to drop `when` — the stream mouths are not the object.

---

## 4. occupancy / held

Object: contiguous **eras** where a predicate holds. Bisect is one cut. `git log -- PATH` lies for deleted files.

Sandwich occupancy (`sate` / `plea` / `lodge` / `dreg`) is a **different object** (image-claim vs a tree). Braid occupies a *composed suggestion fold*. Neither is held.

```
C-09 held ★  eras of exists / grep / exec
        |
        +-- R-02 dwelt      behavior match sitbone / skills
        +-- M-03 tell       shortest predicates that distinguish two trees
        +-- M-18 stint      interval occupancy of born-and-killed; no leftover names
        |
        v
M-17 perch ★  same TRUE, different witness set → new era
        |
        +-- R-05 roost      perch gold + merge origin
        +-- H-05 tenure     when × perch (stack + holders)
        |
        v
M-36 stead     TRUE / FALSE / UNKNOWN / SHALLOW / EMPTY
        |      failed probe is not FALSE
        |      ! book-ID collision with assay
        v
M-52 berth ★  file identity: `git mv` is one roost
              D-12 DESTROYER_BERTH: mutate (first-parent default; leftover-name exists)
        |
        +-- M-67 rove       path-limited grep along identity
        +-- M-104 holt      all-reachable R is the default
        +-- M-66 ditto      COPY vs FOLLOW covering predicates
        |         +-- M-84 crib   occupy new holder of this blob
        |         +-- M-94 pup    ditto | crib without sh
        |
        v
M-62 ford ★  merge occupancy is join of parent *trees*
              D-22 DESTROYER_FORD: mutate (`--boolean` downcast; octopus fold)
        |
        v
M-86 weir      merge-parent that is a merge contributes occupancy, not tree
        |
        v
M-114 hydra    n-parent lattice (how many parents held), not folded meet
```

**Name collision:** `M-56 berth` is leftover occupancy at **identity birth** (erst / brood family). Not this tree. Harvested as `mutation-56__berth`.

**Survivor: held** (eras), **perch** (holders), **berth-52** (file identity), **ford** (merge join). weir/hydra are lattice peels. Copy (ditto/crib/pup) is a holder-kind peel.

---

## 5. lockset

Object: the **1-minimal production hunks the current tests veto**. Tests stay at NEW. Predicate is pass/fail, not a command fingerprint. Not `alibi | winnow`.

```
C-15 winnow     ddmin dirty tree vs command output     ─┐  ancestors
C-24 alibi      current tests × old production         ─┘  not the lockset
                    \
                     v
                H-03 cinch 0.2
                     |     D DESTROYER_CINCH: test-only red = CLEAN; timeout = fail
                     |
                     +-- R-06 snug     closes test-only-red independently
                     |         |
                     |         v
                     |    M-55 tock †  timeout ≠ wheat; ties 0.3; not PATH
                     |                 [lab/judges/LOCKSET_TOCK.md]
                     v
                M-48 cinch 0.3 ★  always-run NEW; timeout = unknown
                     |            bakeoff honest 4/4  [lab/judges/LOCKSET_BAKEOFF.md]
                     |
                     +-- H-06 hasp     PR-range lockset
                     |         +-- M-40 mute    unlocked production of a range
                     +-- M-62 scree †  largest unlocked (invert transcript)
                     |                 ! name collision with R-08 clock scree
                     +-- H-12 gage     lockset clearance: LOCKED-and-BOUND vs OPEN
                     |         |       ! book hybrid-13 harvested as hybrid-12__gage
                     |         v
                     |    H-15 brand   gage × mint: visa-birth lockset
                     |         |
                     |         v
                     |    M-101 sear   --follow visa slot identity
                     +-- H-16 writ     troth × alibi: locked expected vs actual
```

**Survivor: cinch 0.3.** snug is the reimpl transcript. tock is the snug-lineage peel (same four honest answers; does not unseat). No fourth cinch. 0.2 is †.

---

## 6. pin

Object: mint a self-contained **token** once; resolve it onto a later tree without re-supplying `path:line`. The token is allowed to refuse.

```
C-16 slip      relocate file:line by fingerprint (still needs locator + SHA)
        |
        +-- M-04 flume ★   gitless locator *stream* (log in, log out)
        |         |        Unix first-selection vehicle; do not collapse into pin
        |         +-- M-67 gist    LSP 0-based publishDiagnostics rewriter
        |         +-- M-83 blot    empty diagnostics:[] is a document
        |         +-- M-93 flare   1-based cargo/SARIF → 0-based publish
        |
        v
M-14 pin v0.2  the token
        |      D DESTROYER_PIN_INVERT: leftover stub / uniqueness / foreign repo
        v
M-22 pin v0.3  leftover stubs are not identity; uniqueness in both snapshots
        |      D DESTROYER_STUMP_PIN: extract-and-keep reported as a move
        v
M-34 pin v0.4  extract-and-keep is identity if origin still holds the body
        |      ! book-ID collision with splice
        v
M-47 pin v0.5 ★  stub origin prefers extracted body over basename bait
              D DESTROYER_PIN_V5: leftover is not a pointer
        |
        +-- M-66 shunt     leftover re-export is an import pointer
        |         +-- M-80 helm    relative to the leftover file
        |         +-- R-10 cleat   from DESTROYER_PIN_V5 behavior
        |
        v
M-60 keel      origin = remotes + tip witnesses, not root SHAs
              D-18 DESTROYER_KEEL: remotes are config; witnesses are object occupancy
        |      ! book-ID collision with yaw
        v
M-110 shoal    signed remotes at mint; adding a stranger is not --any-repo
```

**Survivor: pin v0.5** (the address object). keel/shoal are origin peels. shunt/helm/cleat are leftover-pointer peels. **flume** is a sibling Unix vehicle (locator stream), not a pin version.

---

## 7. env-ABI

Object: a program has an environment ABI with **two columns**. DUE is a getenv-shaped *use*, not an env-shaped token. LATENT is what the image documented.

```
C-28 due       owed getenv names; join two environs
        |
        +-- C-30 orbit     guise PATH vs payload vs SIP (sibling, keep)
        |
        v
M-21 lode      load image set (otool -L / ldd + @rpath)
        |
        v
M-36 assay ★   DUE (getenv cstrings) vs LATENT (help tables / $VAR / NAME =)
              D DESTROYER_ASSAY: rustc 12,596 DUE is LLVM opcodes
        |      ! book-ID collision with stead
        |
        +-- M-45 latent    DUE owed vs names a *traced run* actually consulted
        |
        v
M-69 xref ★    DUE = getenv call-site proof (not env-shaped bytes)
              D-16 DESTROYER_XREF: 24-insn window; no hop; *getenv suffix
        |
        +-- R-09 prove     xref rebuilt from DESTROYER_ASSAY
        +-- M-82 lash      one-hop wrappers (arg → x0 → bl getenv)
        +-- M-92 wad       inlined Rust env::var via CString
        +-- M-108 shim     rustup / xcselect hop; *getenv suffix is not DUE
```

**Survivor: assay** (the KIND split is real) and **xref** (DUE is a proof). lash/wad/shim/prove are proof peels. due/lode stay ancestors. Do not ship `strings(1)` as DUE.

---

## 8. suggestion-algebra

Object: composition of review-suggestion **strands** with each other (COMMUTE / STACK / ECHO / SPLIT / SUBSUME / JAM). Not occupancy against a tree. Not GitHub “outdated”.

```
C-37 ply       typed syntactic strata of a patch (grain, not algebra)
C-35 twain     a diff is two patches (oracle vs production) — adjacent
        |
        v
C-38 plait ★   strand composition; no tree
              D DESTROYER_PLAIT: mutate (ECHO was image-identity)
        |
        +-- M-49 spar ⟳    two suggestion *patches*; no tree
        |
        v
M-64 wale      ECHO is locus ∩ image, not image-identity
        |
        v
H-12 braid ★   occupy the *single composed after-image*
              D-23 DESTROYER_BRAID: mutate (STACK mid-state; NFC; covering canvas)
        |      ! book hybrid-12 also harvested gage
        |
        +-- M-87 hank      --emit covering of the fold | git apply
        +-- M-97 quire     multi-file COMMUTE as one tree-image
        +-- H-18 tilde     NFC-equivalent path + line keys
```

Sibling **sandwich occupancy** (do not fold into plait):

```
C-34 sate → M-24 plea → H-08 lodge → M-39 dreg
```

Docs-class gate (ply grain, not algebra): `M-50 weft → M-90 woof → M-99 tally` / invert `M-61 snag`.

**Survivor: plait** (algebra). **braid** (occupancy of the fold). wale is the ECHO peel. Coordinator: “wale = locus-ECHO peel; braid occupies the fold” — agreed.

---

## 9. clocks

Object: which clock explains a gap between two (or N) **cuts**. `time(1)` is one number. This is four objects and a name for when they stop agreeing.

```
C-36 lapse     spawn a command; wall / machine / awake / proper disagree
        |
        v
M-46 scarp ★   two cuts in; SLEEP / DILATE / STEP / REST; no spawn
              D-11 DESTROYER_SCARP: mutate (`ntp=` is adjtime slew)
        |
        +-- R-08 scree     scarp from behavior; repeated key=value is two cuts
        |                  ! name collision with lockset M-62 scree
        +-- M-59 twixt     N cuts → one named interval per adjacent pair
        |                  ! book-ID collision with weld
        +-- M-60 yaw       kernel SLEW (POSIX CLOCK_MONOTONIC − RAW)
        |                  ! book-ID collision with keel
        v
M-103 lurch    stream of cuts + scarp leftover columns (`sleep=` / `ntp=`)
```

`C-33 tide` (oracle careers STABLE/DRIFT/RATCHET/…) is **not** this tree.

**Survivor: scarp** (pair filter). twixt/lurch are stream peels. yaw names SLEW. lapse is the spawn ancestor — do not ship as the product. Coordinator: “twixt/yaw/reimpl-08 scree are peels” — agreed.

---

## 10. tacit

Object: a slot with a default is not a value. Omitted (TACIT) vs restated-equal (SHADOW) vs OVERRIDE vs BOUND. A default-moving diff is a BLAST of riders plus FOSSIL of restatements. New at 04:56 JST. Not leftover-claims, not invert, not sow.

```
C-40 tacit ★   omit / restate / override / bind; BLAST + FOSSIL
              D-14 DESTROYER_TACIT: mutate (unfold reads signature, not construct)
        |
        v
M-88 aloud     BLAST survivor that later *says* the new default
        |
        v
M-98 unsay     emit the diff that unspeaks ALOUD → TACIT
        |
        v
M-106 preen    unfold the constructed default; clap TACIT is omitted --flag
```

**Survivor: tacit.** sitbone `presentThreshold` 27 TACIT / 0 SHADOW and `e9b0f75` BLAST 54 still name the object after DESTROYER_TACIT.

---

## 11. beck

Object: earliest pipeline stage whose output already contains this needle — fd, mint/carry/wrap, and earlier pieces when a later stage assembled the exact bytes. Empirically not `tee | grep -n` (git fatal never enters the pipe).

```
C-41 beck ★   first-producer of a byte
              D-15 DESTROYER_BECK: mutate (greedy JSON cover; wrappers)
        |
        +-- M-96 facet     same-object JSON field cover, not greedy substring
        +-- M-107 innard   inner $() stages; mid-command 2>&1 is a merge
```

**Survivor: beck.** facet/innard are cover and inner-stage peels.

---

## 12. maiden

Object: tests whose recorded outcome history contains **zero failures**. Not `rg PASS` on the newest run. Skip-only is not maiden. No records is UNKNOWN. Not alibi (alibi splices current tests onto old production).

```
C-42 maiden ★  fold of junit / cargo / swift / CI / jsonl; zero <failure>
              D-25 DESTROYER_MAIDEN: mutate (parser × string id)
        |
        v
C-43 badge     identity is (suite, class, method) across rename / alias;
               <flakyFailure> is a red
```

**Survivor: maiden.** badge is the identity peel. sitbone 213 / kizu 489 UNKNOWN (no records) is the honest refuse.

---

## Collisions (do not invent kinship)

Book IDs collided when parent and the 15m loop both assigned mutation-59..68. Harvest by **tool name**. These are not crosses:

| collision | objects |
| --- | --- |
| C-08 / C-13 unfmt | ⟳ walkers; invert harvested 13’s names |
| M-34 pin v0.4 / M-34 splice | pin token vs concat filter |
| M-35 ambit / amid / graft | two stream reimpls + overlay |
| M-36 assay / stead | env KIND vs occupancy UNKNOWN |
| M-52 berth / M-56 berth | file-identity occupancy vs natal leftover occupancy |
| M-59 weld / M-59 twixt | expr-first concat vs clock-log stream |
| M-60 keel / M-60 yaw | pin origin vs kernel slew |
| M-62 ford / M-62 scree | merge lattice vs unlocked lockset |
| R-08 scree / M-62 scree | clock filter reimpl vs lockset invert |
| H-12 braid / H-12 gage | suggestion-fold occupancy vs lockset clearance |

---

## Independent notes (for the report writer)

1. **One vehicle per object.** Peels that closed a destroyer hole do not unseat the vehicle (tock ≁ cinch 0.3; stencil ≁ invert; amid ≁ ambit; keel ≁ pin v0.5).
2. **Three occupancy words.** held = eras. sate = image-claim vs a tree. braid = occupancy of a composed suggestion. Pipe them; do not merge them.
3. **Two leftover words.** zanei = claims a *diff* made false. wraith = names whose defs died. Haunt is †. Coordinator: no leftover-name breed — agreed.
4. **when is still the noun.** ambit/peal are the `rg |` mouths. Dropping `when` would leave a filter without a word for the stack.
5. **smolder and lien belong on the leftover-claims survivor line** even if the 04:32 tomorrow-test shortlist omitted them. Forward / invert / natal-CI are three mouths.
6. **tacit, beck, maiden** are Gen-2/3 *candidates*, not mutations of the first-selection sixteen. They survived dedicated destroyers. They are new §8 rows, not peels of zanei / invert / alibi.
7. **First-selection disagreement is still evidence.** Skeptic’s four (winnow, cinch, invert, zanei) are PATH-tomorrow, not the breeding pool. This tree keeps Unix/Heretic objects as vehicles or named peels.
8. **Extinct as products inside these twelve:** unfmt-08/13 walkers, stencil-as-product, cinch 0.2, lapse-as-product, amid, tock-as-PATH, lockset scree-as-PATH. Everything else in these trees is Keep or Mutate.

Lineage directories consulted: `lab/lineages/{candidate,mutation,hybrid,reimpl,destroyer}-*`. Judge transcripts: `lab/judges/{UNFMT,AMBIT_AMID,LOCKSET}_BAKEOFF.md`, `LOCKSET_TOCK.md`, `GHOST_CLUSTER.md`, `DESTROYER_{ZANEI,CINCH,PIN_INVERT,STUMP_PIN,PIN_V5,ASSAY,PLAIT,SCARP,BERTH,LIEN,TACIT,BECK,XREF,WELD,KEEL,SMOLDER,FORD,BRAID,PEAL,MAIDEN}.md`.
