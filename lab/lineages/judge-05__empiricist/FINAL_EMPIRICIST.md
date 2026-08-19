# FINAL_EMPIRICIST — judge-05

Source: final jury, 2026-08-20 ~08:20 JST. Isolated worktree
`subagent-01a01c4f-d862-7dc1-94b1-fcc0e4d23122`. Axis of record is
**evidence**: `./demo.sh` this session, DESTROYER transcripts still on
disk, and independent probes on kizu / sitbone. A CANDIDATE without a
runnable demo is vapor. A gold claim DESTROYER named a lie is a lie
even if `demo.sh` exits 0.

Other judges (FIRST_*, DESTROYER_*) are **exhibits**, not a ranking to
rubber-stamp. Scores 0–5 integers: Novelty / Utility / Primitive /
Composability / Empirical / Evolution. **A 4+ on Empirical requires a
run, not a README.** This session re-ran the named batteries from live
worktrees. Destroyer `/tmp/destroy-*/transcript.txt` files still exist
(4087-line cinch, 2324-line beck, …).

Several survivors. Not one winner. Haunt stays dead. Folk stays parked.

---

## The question

Did the binary actually run, on the trees the night named, and does the
*claimed meaning* still hold?

`passed=N failed=0` is occupancy of the author’s fixture. DESTROYER is
occupancy of the claimed object. Independent `git log -- PATH` /
`git diff | lien` / `*getenv` binaries are occupancy of the poster.
Credibility is the intersection. Demo-only gold is a well-tested toy.

---

## This-session runs (live worktrees)

All EXIT=0. Logs: `/tmp/judge05-empiricist/*.log`. Dogfood trees
`/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone}` present.

| tool | id | worktree suffix | demo this session | dogfood in that demo |
| --- | --- | --- | --- | --- |
| invert | mut-15 | `…2d465380e59f` | **46/46** | sitbone camera nested quotes; 7-hole Logger |
| cinch | hyb-03 | `hybrid-03-cinch` | **demo OK** (13 cases; lockset ≠ debug print) | units + synthetic git |
| scarp | mut-46 | `…7bf303f098fd` | **demo 0 ok** | live Darwin `cut \| scarp` SLEEP |
| xref | mut-69 | `…cb96e7158c54` | **78/78** | kizu source⋈image `KIZU_CONFIG`; Homebrew git `GIT_DIR` |
| weld | mut-59 | `…caff208a0972` | **84/84** | tenaoshi `{response}\nDone.`; 4-hole wrap |
| berth | mut-52 | `…cbf1c493bd9a` | **79/79** (`./demo.sh 0`) | kizu dest origin `321a830 as <old>` |
| tacit | cand-40 | `…72c70d715bf7` | **32/32** | sitbone 27 TACIT `presentThreshold`; BLAST 54 |
| beck | cand-41 | `…1108ac34ccbe` | **33/33** | kizu/sitbone `git log \| rg` mint at git |
| maiden | cand-42 | `…7e115d7932c1` | **27/27** (`--selftest` 28/28) | sitbone 213 UNKNOWN; kizu 489 UNKNOWN |
| dwelt | reimpl-02 | `…36f636b01a05` | **39/39** | sitbone / skills / voidtrace eras |
| nagori | reimpl-03 | `…2cffa17ef5e5` | **27/27** | (demo fixtures; sitbone probed separately) |
| prove | reimpl-09 | `…111c7624da18` | **78/78** | same kizu/git dogfood as xref |
| cleat | reimpl-10 | `…7e22b5f4b733` | **all checks passed** | kizu `app.rs:529 → layout.rs:17`; voidtrace identity; tenaoshi line 12 |
| solder | reimpl-11 | `…a8a24a7d1c61` | **84/84** | same tenaoshi battery as weld |
| lurch | mut-103 | `…a7bef4531e96` | **demo 0 ok** | live Darwin SLEEP + stream fixtures |
| holt | mut-104 | `…a7c21cde45fa` | **112/112** (`./demo.sh 0`) | kizu either-name `true=187/244` |
| noun | mut-105 | `…a7dcb7b045d8` | **51/51** | kizu `9349dc5` plugin.json leftover; sitbone both-rows |
| badge | cand-43 | `…a89983a67baf` | **32/32** (`--selftest` 46/46) | flakyFailure + gha undo scar |

286 `WORKTREE.txt` targets exist (`missing=0`). Harvested
`lab/lineages/subagent-*` dirs without `demo.sh` are incomplete harvests,
not original vapor. Destroyer harvests are reports; they are not products.

---

## Independent probes (not `demo.sh`)

### 1. Occupancy vs `git log -- PATH` — dwelt gold holds

```
$ git -C sitbone log --oneline -- Sources/SitboneUI/FocusRiverView.swift
# (empty)   count=0

$ ./dwelt -C sitbone --full exists Sources/SitboneUI/FocusRiverView.swift
FALSE  11 commits  a2512fe..74363dc
TRUE   11 commits  14b1d6e..1fefafb   witnesses: FocusRiverView.swift
FALSE  78 commits  70ec7df..094769d
now=FALSE  true=11/100
```

The poster is not a README. `git log -- PATH` is the lie; dwelt is the
era compression DESTROYER_OCCUPANCY still called a real verb.

### 2. berth “either name” — DESTROYER_BERTH gold is a lie; holt closes it

```
$ ./berth -C kizu exists docs/deep-research-ai-agent-hooks.md
now=TRUE  true=21/24  origin: 321a830 as deep-research-ai-agent-hooks.md

$ ./berth -C kizu exists deep-research-ai-agent-hooks.md
now=FALSE  true=0/24
hint: never held on first-parent, but existed in 13 reachable commits
```

Default first-parent `exists` of the **dead name** is never-held.
CANDIDATE “query the old name or the new name; occupancy stays TRUE”
is false on the advertised walk (DESTROYER_BERTH intro + § leftover
recreate).

```
$ ./holt -C kizu exists deep-research-ai-agent-hooks.md
identity: deep-research-ai-agent-hooks.md → docs/…
now=TRUE  true=187/244  aka=old,docs/…

$ ./holt -C kizu --first-parent exists deep-research-ai-agent-hooks.md
now=TRUE  true=21/24  origin: 321a830 as <old>
```

Gen3 holt is the advertised object. berth `--full` dest gold is still
true; the *symmetry* claim is not.

### 3. lien workspace version — DESTROYER_LIEN §6 gold is a CI lie; noun closes it

HEAD still has `plugin/plugin.json "version": "0.3.0"` and
`Cargo.toml version = "0.7.0"`.

```
$ git -C kizu diff 9349dc5^ 9349dc5 | ./lien --facts-only -C kizu
lien: 1 natal record(s)
  value    VERSION  0.6.0 → 0.7.0  (Cargo.lock:920)

$ git -C kizu diff 9349dc5^ 9349dc5 | ./lien --no-color -C kizu
# silent   lien_rc=0

$ git -C kizu diff 9349dc5^ 9349dc5 | ./noun --no-color -C kizu
plugin/plugin.json:4: claim: crate:kizu VERSION  0.6.0 → 0.7.0: "version": "0.3.0",
noun_rc=1
```

A release CI job `git diff | lien` is green while the Claude plugin
still advertises 0.3.0. That is not a leftover-name miss; it is
`merge_natals` collapsing two packages named `version`. noun’s demo
asserts the same (`kizu 9349dc5 default check fails (lien was green)`).

### 4. invert no-hole prefix — DESTROYER_PIN_INVERT §7 still live

Re-ran destroyer fixture `/tmp/destroy-pin-invert/invfix/prefix.rs`:

```
$ ./invert --templates prefix.rs -n 3 \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
prefix.rs:7:13: score=0.67 holes=0 via=full
  tmpl:  2026-08-19T23:50:01Z ERROR failed to spawn
  note:  suffix=' `git apply --reverse`'
prefix.rs:2:13: score=0.48 holes=1 via=span
  tmpl:  failed to spawn `{1}`
  {1} = git apply --reverse
```

The documentation decoy **beats** the holed spawn. invert’s own
`./demo.sh` still 46/46 (sitbone 7-hole / camera). Demo gold ≠ ranking
gold.

### 5. scarp `ntp=` — DESTROYER_SCARP §1 still live; SLEEP gold holds

```
$ python3 ./scarp cut | python3 ./scarp --explain
SLEEP  explains=machine  kind=host
  sleep        1d05h03m   machine − awake
  ntp           -7.354s   wall − machine
```

Lid-close as SLEEP is real. The field named `ntp` is adjtime slew
(`CLOCK_MONOTONIC − CLOCK_MONOTONIC_RAW`), not NTP. Live number matches
the destroyer’s −7.333s class.

### 6. tacit sitbone — 27 TACIT / 0 SHADOW holds

```
$ ./tacit -C sitbone --summary presentThreshold
PresenceArbiter  presentThreshold  0.45  TACIT=27 SHADOW=0 OVERRIDE=0 BOUND=0
```

The omission object is real. Pairing / clap / `*args` lies stay DESTROYER_TACIT
(not re-litigated as kills).

### 7. nagori leftover claims — sitbone `e9b0f75` holds

```
$ ./nagori --no-color -C sitbone e9b0f75^ e9b0f75 --min-score 55
FACT threshold: 0.4 → 0.45
   84 docs    CLAUDE.md:329   … threshold 0.4 …
   84 docs    CLAUDE.md:332   … threshold 0.4 …
```

Same two rows DESTROYER_ZANEI and zanei gold named. Primitive survived
a clean-room rebuild.

### 8. xref/prove `*getenv` — DESTROYER_XREF §1 still live on both

`nm bins/false-O0`: `T _not_a_getenv`, `T _forgetenv`. No `_getenv`.

```
$ ./xref --app bins/false-O0
DUE  FALSE_DUE_NAME   call  getenv
DUE  FORGET_ENV_NAME  call  getenv

$ ./prove --app bins/false-O0
DUE  FALSE_DUE_NAME   call  getenv
```

prove dropped `forgetenv` (partial). `not_a_getenv("FALSE_DUE_NAME")`
is still DUE. DUE is still “a call to something *named* getenv,” not
libc `getenv`. The 12k rustc flood **is** closed (xref demo 78/78;
prove 78/78; DESTROYER_ASSAY poster).

### 9. maiden `<flakyFailure>` — DESTROYER_MAIDEN gold is a lie; badge closes it

Same destroyer fixture `/tmp/destroy-maiden/fixtures/junit/flaky-then-green.xml`
(`<flakyFailure message="boom">` on `pkg.T::alpha`):

```
$ ./maiden --no-ledger --header flaky-then-green.xml
MAIDEN  pkg.T::alpha
MAIDEN  pkg.T::beta

$ ./badge --no-ledger --header flaky-then-green.xml
SCARRED pkg.T::alpha
MAIDEN  pkg.T::beta
```

maiden’s never-red is parser × child-tag set. badge’s fold scars
`<flakyFailure>`. That is a Gen3 closure, not a maiden v0.2 fix.

---

## Credibility ranking

Rank is **honesty of the claimed object after contact with evidence**,
not polish and not “would I type this tomorrow” (Skeptic’s veto).
`E=5` on a liar still means the binary ran.

### A — gold meaning still true (demo + destroyer + this-session probe)

| rank | tool | why the poster is not a toy |
| --- | --- | --- |
| 1 | **cinch** | DESTROYER_CINCH money shot survived; this-session demo case 1 still drops `print("debug")`, keeps `return a + b`. EMPTY/timeout are named edges, not the lockset. Transcript 4087 lines. |
| 2 | **dwelt** (held) | Independent of held (sha `bfb0efc0` ≠ `e874d20f`). sitbone `FocusRiverView` 11/100 vs empty `git log -- PATH` **this session**. DESTROYER_OCCUPANCY: occupancy is still a verb. |
| 3 | **nagori** (zanei) | Independent (sha `057b265b` ≠ `3c35359d`). CLAUDE.md:329/332 **this session**. DESTROYER_ZANEI: complementary JSON/prose holes, primitive stands. |
| 4 | **beck** | DESTROYER_BECK gold: `git -C /tmp status \| cat` is MINT stderr, `piped_bytes=0`, tee miss. This-session demo 33/33 including kizu/sitbone mint-at-git. |
| 5 | **cleat** | Independent of pin v0.5 (sha `d181253f` ≠ `7b4eba80`). This-session resolve `src/app.rs:529 → src/app/layout.rs:17`. Relative leftover is the DESTROYER_PIN_V5 mutation, rebuilt. |
| 6 | **weld / solder** | Independent hashes; **both** 84/84 this session; tenaoshi expr-first `{response}\nDone.` is the splice miss DESTROYER_STUMP_PIN named. Leftover `\n` is a named hole, not the money shot. |
| 7 | **tacit** | sitbone 27 TACIT / 0 SHADOW **this session**. Two inhabitants of `0.45` is a real split. DESTROYER_TACIT clap/`*args` are mutations. |
| 8 | **noun** (lien peel) | This-session `lien_rc=0` / `noun_rc=1` on kizu `9349dc5`. Closes DESTROYER_LIEN §6 without killing natal-record. |

### B — demo gold holds; advertised *meaning* is a DESTROYER lie

| rank | tool | surviving gold | the lie |
| --- | --- | --- | --- |
| 9 | **scarp / lurch** | live SLEEP 1d05h03m; `{cut; sleep 0.35; cut}` DILATE no spawn; lurch streams the pair scarp drops | `ntp=` is adjtime (this session −7.354s). Two-cut window, not a log (DESTROYER_SCARP). lurch closes the window, not the field name. |
| 10 | **berth / holt** | `--full` R100 `true=187`; copy is not a follow; sitbone island | default “either name” FALSE on first-parent (this session). holt closes it. |
| 11 | **xref / prove** | not `strings(1)`; `PYTHON_GIL` DUE; rustc tens not 12k; `/bin/ls` `CLICOLOR_FORCE`; 78/78 both | DUE is `*getenv` suffix. `FALSE_DUE_NAME` still DUE on prove **this session**. KIND has no neither (DESTROYER_XREF / DESTROYER_ASSAY). |
| 12 | **maiden / badge** | 2019 fail + 2024 green scars alpha; sitbone 213 UNKNOWN (not `rg PASS`) | never-red is parser × string id. maiden maidens `<flakyFailure>` **this session**. badge scars it. bun/go/nextest vanish (DESTROYER_MAIDEN). |
| 13 | **invert** | sitbone 7-hole + camera 46/46; empty stream honest; directories refused | no-hole prefix outranks a binding (this session 0.67 > 0.48). rustc `-->` binds a test fixture (DESTROYER_PIN_INVERT §3). concat is not a template (§2). |
| 14 | **lien / weft / woof** | sitbone `t1↔driftDelay` both-rows; mixed-line `30→60` still FAIL number | lien: two packages named `version` are one noun (this session green CI). weft: `--only docs` is a path glob; backtick fence swallows number (DESTROYER_WEFT). woof closed the glob and then treated a new bash sample as 114 ident inserts (DESTROYER_WOOF). |
| 15 | **pin / keel** | unique kizu pins still land the godfile split (via cleat this session; DESTROYER_PIN_V5 “verified fixed” extract-and-keep) | leftover is not a pointer (stem-split beats named extract). `origin_holds_body==1.0` follows the unedited clone (DESTROYER_PIN_V5 §12). keel: `git remote add` is `--any-repo`; missing origin returns True (DESTROYER_KEEL). |

### C — exercised, not independently re-probed this session

peal, gist, vow, smolder, ford, braid, plait: DESTROYER says mutate-not-kill, victim `demo.sh` still 0 after the battery, transcripts on disk. I did not re-run those demos. Empirical credit is the destroyer’s, marked **UNVERIFIED-by-this-judge** for the binary, **VERIFIED** for the existence of the transcript.

assay: DESTROYER_ASSAY 12k DUE is the ancestor xref/prove closed. Not re-run.

---

## Gold claims that are lies (cite DESTROYER)

A gold claim is a lie when the tool still emits the poster *and* the
claimed semantics are false. Demo PASS does not pardon it.

| claimed gold | actual | cite | this session |
| --- | --- | --- | --- |
| invert: holed template wins; leftover is a span | no-hole prefix of the paste scores 0.67 over the hole 0.48 | DESTROYER_PIN_INVERT §7 | **reproduced** on `invfix/prefix.rs` |
| invert: rustc locator is refused / not a template | `--> src/git/revert.rs:46:18` binds `src/{i}.rs` `{i}=git/revert` (test fixture) | DESTROYER_PIN_INVERT §3 | transcript only |
| invert: concat `+` is inverse-printf | `"open " + path` is holes=0 static=`open `; sibling `fmt.Errorf` is the accidental hit | DESTROYER_PIN_INVERT §2 | transcript only |
| pin: file-split still resolves | leftover stub at the old path scores 1.000 identity; the extract never votes | DESTROYER_PIN_INVERT §2; DESTROYER_STUMP_PIN leftover then closed on *stem-split* fixtures and reopened as “leftover is a pointer” | DESTROYER_PIN_V5 §1 stem-split still beats unique leftover |
| pin: leftover re-export is a pointer | vote is `form in enclosing-function-blob` + unique `oldstem/…` first | DESTROYER_PIN_V5 §1 | not re-attacked; cleat demo is the relative-leftover rebuild |
| pin: origin body is identity | one-line dest edit → follow the unedited clone (`moved … src/math/ops.py`) | DESTROYER_PIN_V5 §12 | transcript only |
| pin: huge file is handled | `MAX_FILE_BYTES` silent omit; dest sibling → `deleted` rc=0 | DESTROYER_PIN_INVERT §1; DESTROYER_STUMP_PIN §6 | transcript only |
| keel: remotes+tips are repo identity | `git remote add` the pin’s URL spelling is `--any-repo`; `origins_match` if either side has no origin | DESTROYER_KEEL §1 | transcript only |
| cinch: EMPTY means no tests | `exit_code == 5` first; a runner that `sys.exit(5)` is EMPTY | DESTROYER_CINCH §1 | not re-attacked; demo EMPTY case is unittest-zero |
| cinch: test-only red is occupancy | production-unchanged red suite is CLEAN; tests are **not run** | DESTROYER_CINCH §1 | transcript only |
| cinch: timeout hunk is unknown | timeout is wheat / fail | DESTROYER_CINCH mutate-toward | transcript only |
| scarp: `ntp=` is NTP | field is wall−RAW = adjtime slew; STEP floor hides it | DESTROYER_SCARP §1 | **reproduced** `ntp=-7.354s` on SLEEP |
| scarp: a log is classified | `cuts[0], cuts[1]`; 1000 JSONL cuts → first pair | DESTROYER_SCARP §2 | lurch demo closes stream; scarp unchanged |
| scarp: unlabeled ticks are two timestamps | duration bag / first eight fields; `1000\n1001` REST is the v0.2 hold, four epoch ticks are not | DESTROYER_SCARP §2 | transcript + scarp demo REST pair |
| scarp: porcelain round-trips | porcelain 0-fills missing clocks; REST 1s wall re-ingested as STEP | DESTROYER_SCARP §6 | transcript only |
| xref/assay: DUE = could getenv / did getenv | DUE = env-shaped bytes (assay) or `endswith("getenv")` (xref) | DESTROYER_ASSAY; DESTROYER_XREF §1 | **reproduced** `FALSE_DUE_NAME` DUE on xref **and** prove |
| xref: KIND is a partition of use vs docs | `kind_of` else-branch is DUE; `--loose` / needles print as use; no neither | DESTROYER_XREF primitive table | transcript |
| xref: rustup/xcselect `(no owed names)` is empty ABI | they are shims; payload never walked | DESTROYER_XREF §7 | transcript |
| weld: leftover proving string is inverse-printf of concat | `cleaned + "\n"` is invisible; hydrate floods the file | DESTROYER_WELD §1 | **reproduced** weld **and** solder extract flood on kizu `teardown.rs` |
| weld: truncation is prefix-of-instance | sibling-template stuffing into the last hole | DESTROYER_WELD mutate-toward | transcript |
| berth: either name, occupancy TRUE | first-parent dead name never-held; leftover recreate occupies the *other* file | DESTROYER_BERTH intro + leftover | **reproduced** dead-name `true=0/24` |
| tacit: `*args` / TS `name =` are keywords | `splat(1)` OVERRIDE timeout (reality TACIT); TS `delay = 200` is positional | DESTROYER_TACIT §1 | transcript |
| tacit: clap TACIT is omitted `--flag` | command-shaped line regex; kizu TACIT=6 is not six riders | DESTROYER_TACIT §4 / dogfood | transcript; sitbone 27/0 holds |
| tacit: unfold is the constructed default | reads `Foo` signature, not `Foo(driftDelay: 20)` | DESTROYER_TACIT mutate-toward | transcript |
| tacit: e9b0f75 pairing is identity | BLAST 54 counts a birth; pairing is index | DESTROYER_TACIT §7 | demo BLAST 54 holds; pairing story is the lie |
| beck: fd is where the process wrote | only a **trailing** `2>&1` token is peeled; mid-command `2>&1` is stdout and agrees with tee | DESTROYER_BECK §3 | transcript |
| beck: JSON pieces are the same object | greedy cover of `kizu@0.7.0` steals `@0.7.0` from `notify-debouncer-full@0.7.0` | DESTROYER_BECK intro / facet hole | transcript |
| maiden: never-red = this test has never been red | fold over parsed dialects keyed by string id; `<flakyFailure>` maidens; bun/go/nextest `{}` | DESTROYER_MAIDEN primitive + §8 | **reproduced** flaky maiden vs badge scar |
| maiden: `--census` is a roster | sitbone 0∩213; kizu 0∩489 | DESTROYER_MAIDEN §9 | transcript |
| maiden: `--latest --skeptic` is the anti-`rg` | `--latest` is `rg PASS`; composing them is `rg` | DESTROYER_MAIDEN | transcript |
| lien: `git diff \| lien` gates leftovers of *this* change | two `version` keys are one natal; kizu plugin.json 0.3.0 is a homonym; CI green | DESTROYER_LIEN §6 | **reproduced** `lien_rc=0` |
| weft: `--only docs` means no code ply leaked | docs is a path glob; README fence is one backtick-string | DESTROYER_WEFT §1 | transcript |
| woof: fence interiors are number ply (v0.2 close of WEFT) | a *new* bash sample is 114 ident inserts; SHA is digit prefix + leftover text | DESTROYER_WOOF §1 | transcript |
| zanei/nagori: `10 → 30` leftover is timeout 10 | ISO `2024-10-01` hits `(?<![\d.])10(?![\d.])` | DESTROYER_ZANEI §1 | transcript |
| zanei: JSON-only fact is a fact | quoted `"version":` is invisible; nagori sees JSON then drops the prose leftover of that fact | DESTROYER_ZANEI complementary holes | nagori demo includes JSON-key checks 27/27 |
| held: timeout is unknown | `--timeout 0` on `exec -- true` is never-held FALSE | DESTROYER_OCCUPANCY §7 | transcript |
| held: `--full` is the lattice | list order invents FALSE gaps across merge diamonds | DESTROYER_OCCUPANCY; DESTROYER_FORD | transcript |
| plait: inverted clock `same-tree` is the fold | reports `same-tree` on the wrong image | DESTROYER_PLAIT §2 (cited, not re-run) | UNVERIFIED-by-this-judge |
| gist: `character` is dest UTF-16 | Python `len` / source column | DESTROYER_GIST | UNVERIFIED-by-this-judge |
| vow: comments are not oaths | same-line `# ran on` is the expected slot | DESTROYER_VOW §1 | UNVERIFIED-by-this-judge |
| smolder: dest locus invert names the falsifying commit | dest rename / leftover-name of dest text; 2 MB dest omit reports live dest `missing` | DESTROYER_SMOLDER | UNVERIFIED-by-this-judge |
| ford: join is parent trees | `--boolean` never computes the lattice; octopus cannot tell 1-of-3 from 2-of-3 | DESTROYER_FORD | UNVERIFIED-by-this-judge |
| braid: occupancy of the composed after-image | three-round STACK cannot occupy; covering is of a live-gap canvas | DESTROYER_BRAID | UNVERIFIED-by-this-judge |
| peal: stdin locators recover the file | first-locator / `pins[:16]` / substring containment | DESTROYER_PEAL | UNVERIFIED-by-this-judge |

Lies that **do not kill** the primitive: the object is still visible on
the gold path (cinch wheat, dwelt eras, nagori CLAUDE.md, beck stderr,
cleat kizu split, weld expr-first, tacit 27 TACIT, scarp SLEEP, xref
not-strings). Lies that **do** kill a *product claim*: lien-as-release-CI,
maiden-as-never-red, berth-either-name, invert-ranking, xref-DUE-as-proof,
scarp-ntp, weft-docs-path.

---

## Reimpls — which survived

Survival = independent source (hash ≠ ancestor) + this-session demo 0 +
reproduced ancestor gold on kizu/sitbone **or** destroyer fixtures.
All five named reimpls survived. None is a copy.

| reimpl | ancestor | loc | sha vs ancestor | demo | gold reproduced this session | inherited DESTROYER lie |
| --- | --- | --- | --- | --- | --- | --- |
| **dwelt** | held | 994 vs 1026 lines | `bfb0efc0` ≠ `e874d20f` | **39/39** | sitbone FocusRiverView FTF 11/100; `git log -- PATH` empty | occupancy timeout→FALSE, `--full` ≠ lattice (DESTROYER_OCCUPANCY) — not dwelt-specific, still the object |
| **nagori** | zanei | 1490 vs 1549 | `057b265b` ≠ `3c35359d` | **27/27** | sitbone `e9b0f75` CLAUDE.md:329/:332 | ISO month 10; complementary JSON/prose (DESTROYER_ZANEI). Primitive proof, not a patch. |
| **prove** | xref / DESTROYER_ASSAY | 2057 vs 3732 | `668a5ee4` ≠ `3a6aeb65` | **78/78** | git `GIT_DIR`; not `ARRAY_SIZE`; kizu `KIZU_CONFIG` source⋈image | **`FALSE_DUE_NAME` still DUE** (this session). Closed 12k flood / `COLOR_FORCE`. Did not close `*getenv` suffix. |
| **solder** | weld / DESTROYER_WELD | 3601 vs 3401 | `a3239790` ≠ `873c4ae4` | **84/84** | tenaoshi `{response}\nDone.` + fence `json\n` in demo | leftover `\n` hydrate flood on kizu `teardown.rs` **same as weld** this session. Clean-room of the proving-string verb, not of DESTROYER_WELD §1. |
| **cleat** | pin v0.5 / DESTROYER_PIN_V5 | 2226 vs 2268 | `d181253f` ≠ `7b4eba80` | **all checks** | kizu `app.rs:529@b4e6a5d → layout.rs:17`; voidtrace identity; tenaoshi line 12 `same 1.000` | not re-attacked as pin. Demo includes relative `.ops` extract and basename-bait skip. That is the destroyer mutation, rebuilt. |

**Verdict:** keep all five as **primitive-strength proofs**. Do not
collapse dwelt into held, nagori into zanei, prove into xref, solder
into weld, cleat into pin. The night asked “is the object an accident
of one file?” The hashes plus matching gold say no.

Caveat an empiricist will not swallow: solder’s 84/84 is the **same
battery count and same last five PASS lines** as weld. That is the
clean-room-from-behavior contract, not plagiarism (hashes differ;
solder is 200 lines longer). prove’s 78/78 is the same shape versus
xref, and prove is *smaller* (2057 vs 3732) — stronger independence.

snug (reimpl-06, cinch) and stencil/whence/roost/brood/scree were not
in the assigned reimpl list and were not re-run.

---

## Per-candidate scores (named lineages)

`Σ` is unweighted and is not the ranking. **Keep follows Empirical ∩
surviving gold meaning.** Mutate when DESTROYER named a hole and the
object still stands. Kill vapor only.

Legend: **K** = survive / object real. **M** = mutate (Gen3 already
did some of these). **P** = park spare. **KILL** = stop.

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement | evidence of run |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-15 | invert | 4 | 4 | 5 | 5 | **5** | 4 | 27 | **K / M** | instance → template + named holes + span leftover; ranking still prefers no-hole prefix | this-session 46/46; prefix lie reproduced; DESTROYER_PIN_INVERT |
| hyb-03 | cinch | 3 | 5 | 5 | 4 | **5** | 4 | 26 | **K / M** | 1-minimal production hunks current tests veto; tests never wheat | this-session demo OK; DESTROYER_CINCH 4087-line transcript; units 10/10 |
| mut-46 | scarp | 4 | 3 | 4 | 5 | **5** | 4 | 25 | **K / M** | two cuts, which clock owns the gap; `ntp=` is misnamed slew | this-session demo 0 + live SLEEP 1d05h03m / ntp=-7.354s; DESTROYER_SCARP |
| mut-69 | xref | 4 | 3 | 4 | 4 | **5** | 4 | 24 | **K / M** | DUE as getenv-shaped *use* vs LATENT docs; suffix is not libc | this-session 78/78; FALSE_DUE_NAME reproduced; DESTROYER_XREF |
| mut-59 | weld | 4 | 4 | 5 | 5 | **5** | 3 | 26 | **K / M** | concat may start at an expression; later string proves it | this-session 84/84 tenaoshi; leftover `\n` flood reproduced; DESTROYER_WELD |
| mut-52 | berth | 4 | 3 | 4 | 5 | **5** | 3 | 24 | **K / M** | file-identity occupancy; `--full` R100 is real; default either-name is not | this-session 79/79; dead-name lie reproduced; DESTROYER_BERTH |
| cand-40 | tacit | 5 | 4 | 5 | 4 | **5** | 4 | 27 | **K / M** | omitted vs restated vs overridden vs bound default | this-session 32/32 + sitbone 27/0; DESTROYER_TACIT |
| cand-41 | beck | 4 | 4 | 5 | 5 | **5** | 4 | 27 | **K / M** | first pipeline stage that produced this byte; unpiped stderr | this-session 33/33; DESTROYER_BECK gold holds |
| cand-42 | maiden | 4 | 3 | 3 | 4 | **5** | 3 | 22 | **M** (badge) | never-red fold over *parsed* observations × string id — not “never been red” | this-session 27/27; flakyFailure maidens; DESTROYER_MAIDEN |
| reimpl-02 | dwelt | 2 | 3 | 5 | 5 | **5** | 2 | 22 | **K** proof | held is real; rebuilt from behavior | this-session 39/39 + FocusRiverView probe |
| reimpl-03 | nagori | 3 | 3 | 4 | 5 | **5** | 2 | 22 | **K** proof | leftover *claims*; complementary holes vs zanei | this-session 27/27 + e9b0f75 probe; DESTROYER_ZANEI |
| reimpl-09 | prove | 4 | 3 | 4 | 4 | **5** | 3 | 23 | **K / M** | DUE is a call-site column; 12k flood closed; `*getenv` not closed | this-session 78/78; FALSE_DUE_NAME still DUE |
| reimpl-10 | cleat | 4 | 3 | 4 | 4 | **5** | 3 | 23 | **K** | leftover is an import relative to the leftover file | this-session full demo including kizu split |
| reimpl-11 | solder | 4 | 4 | 5 | 5 | **5** | 3 | 26 | **K** proof | weld’s proving-string-backward verb is not an accident of weld.py | this-session 84/84; leftover `\n` still weld’s |
| mut-103 | lurch | 3 | 3 | 4 | 5 | **5** | 3 | 23 | **K** | scarp names on adjacent pairs | this-session demo 0 ok; closes DESTROYER_SCARP two-cut window |
| mut-104 | holt | 3 | 3 | 4 | 5 | **5** | 3 | 23 | **K** | berth identity from all-reachable R; tip occupant is the seed | this-session 112/112; dead-name TRUE 187/244 |
| mut-105 | noun | 3 | 4 | 4 | 5 | **5** | 3 | 24 | **K** | (package, noun) natal; plugin.json is not a Cargo homonym | this-session 51/51; `lien_rc=0`/`noun_rc=1` reproduced |
| cand-43 | badge | 4 | 3 | 4 | 4 | **5** | 3 | 23 | **K** | never-red keyed by (suite, class, method); `<flakyFailure>` is red | this-session 32/32; flaky SCARRED vs maiden MAIDEN |

Suggested mutations (only where keep/mutate): invert ranking must not
let a no-hole prefix beat a binding; xref/prove DUE allowlist libc
`getenv` / rust `__var` (not suffix); scarp rename `ntp` → slew and
stop 0-filling porcelain; weld leftover `\n` stays a different filter
(rime/caulk already peeled); maiden dialect-refuse empty parse (badge
owns identity); cinch EMPTY is the banner, not exit 5.

---

## Gen3 closures that are empirically real

Not “Keep” because the CANDIDATE says Keep. Because this session
showed the ancestor lie and the descendant not-lie on the **same
operand**.

| ancestor lie | Gen3 close | operand |
| --- | --- | --- |
| DESTROYER_BERTH either-name first-parent never-held | **holt** dead-name `true=187/244` / `--first-parent` `true=21/24` | kizu `deep-research-ai-agent-hooks.md` |
| DESTROYER_LIEN §6 plugin.json homonym, CI green | **noun** `plugin/plugin.json:4` rc=1 | kizu `9349dc5` |
| DESTROYER_SCARP `cuts[0], cuts[1]` | **lurch** dilate-then-sleep is two names (author demo 0 this session) | fixtures + live Darwin SLEEP |
| DESTROYER_MAIDEN `<flakyFailure>` maidens | **badge** SCARRED | destroyer `flaky-then-green.xml` |
| DESTROYER_PIN_V5 leftover not a pointer | **cleat** relative `.ops` → `src/math/ops.py` in demo | synthetic + kizu split |
| DESTROYER_ASSAY 12k DUE | **xref** already; **prove** rebuilt | rustc tens; this-session 78/78 |
| DESTROYER_WELD expr-first is real | **solder** rebuilt | tenaoshi 84/84 |

Gen3 that I did **not** run: preen, innard, shim, stile, shoal, rune,
proxy, binom, hydra, tilde, seed. Their CANDIDATE.md files have
`demo.sh` in harvest and live worktrees (`missing=0`). **UNVERIFIED**
as binaries this session. Not vapor.

---

## Vapor / UNVERIFIED

Vapor = no runnable demo in the live worktree. Named vehicles above
are not vapor.

- Incomplete harvest `lab/lineages/subagent-*` without `demo.sh`:
  coordinator copies, not candidates.
- Destroyer lineages without `demo.sh`: reports. Their `/tmp/destroy-*`
  transcripts **are** evidence.
- Ghost cluster (haunt / wraith-as-product / folk): first selection
  already killed/parked. Not re-animated. No new demo evidence to
  reverse that.
- Author-only claims I did not re-run (peal, gist, vow, smolder, ford,
  braid, plait, assay, pin v0.5 itself, weft/woof binaries):
  **UNVERIFIED-by-this-judge**, DESTROYER-VERIFIED. I will not promote
  them on README counts.

A 4+ on Empirical for those last tools would require my run. They stay
E=4 **only** because DESTROYER recorded `./demo.sh` 0 after the battery
*and* left a transcript I can still `wc`. That is one step below a
this-session run, not README vapor.

---

## Survivors (several)

Do not collapse to invert. Do not collapse to cinch. The empiricist
carry set is **orthogonal objects whose gold meaning survived**:

1. **cinch** — lockset (not winnow fingerprint, not alibi file).
2. **dwelt / held** — occupancy eras (`git log -- PATH` is the lie).
3. **nagori / zanei** — leftover *claims* (CLAUDE.md:329/332).
4. **beck** — first producer of an unpiped byte.
5. **cleat** — leftover-relative pin (kizu split).
6. **weld / solder** — expr-first concat filter (tenaoshi).
7. **tacit** — omitted vs restated default (27 TACIT).
8. **noun** — package-scoped natal (plugin.json).
9. **holt** — file identity from all-reachable R (closes berth’s lie).
10. **lurch** — scarp-as-stream (closes two-cut window).
11. **badge** — never-red with flakyFailure (closes maiden’s lie).
12. **prove / xref** — call-site DUE column (closes assay flood; suffix still open).
13. **invert** — named-hole filter (ranking still open; 7-hole gold holds).
14. **scarp** — which clock (SLEEP gold holds; `ntp=` name is a lie).

Park as proofs, not extra PATH entries: dwelt, nagori, solder, prove
(until `*getenv` dies), stencil, snug.

Kill as products (object absorbed or Unix): haunt, folk, unfmt-08/13
walkers, weft’s `--only docs` path glob (woof is the remaining ply
gate, and DESTROYER_WOOF still mutates it).

---

## What this judge will not do

- Rank by LOC, README length, or `passed=84`.
- Treat DESTROYER “mutate, do not kill” as a keep on the *claim*.
- Treat a Gen3 CANDIDATE “Keep” as evidence. holt/noun/badge/lurch
  earned Keep by closing a lie I could still reproduce.
- Collapse five surviving reimpls into their ancestors. The hashes
  forbid it.

Evidence roots: live worktrees under
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/`, destroyer reports
in `lab/judges/DESTROYER_*.md`, transcripts in `/tmp/destroy-*/`,
this-session logs in `/tmp/judge05-empiricist/`.
