# FINAL_TOMORROW — tomorrow-test jury (judge-07)

Source: isolated worktree `subagent-01a01c4f-d862-7dc1-94b1-fce24f958494`, branch `judge-07/final-tomorrow`. Clock window: 2026-08-20 08:20 JST final jury. **Do not merge to main.**

Axis of record is the **tomorrow-test**: which tools should a human actually *install and type* tomorrow morning *instead of* `git` / `rg` / `jq`? Default **no**. Shortlist **≤6**. This session: **4**. Empty slots 5–6 are load-bearing.

FIRST_SKEPTIC (`lab/judges/FIRST_SKEPTIC.md`) kept four *objects*: winnow / cinch / invert / zanei. This judge keeps those four objects and **swaps three binaries** after destroyer peels and bakeoffs. Coordinator `lab/STATUS.md` shortlist of eleven families is a breeding board, not an install list.

Other judges (FIRST_TOOLSMITH, FIRST_HERETIC, FIRST_UNIX, bakeoffs, DESTROYER_*, Gen3 Keep peels) are evidence, not a ranking to rubber-stamp.

---

## The question

A tomorrow-test keeps a verb only when the Unix one-liner is the *wrong object*, not the uglier spelling — **and** the binary on disk does not lie about that object.

`rg` the static prefix. `git add -p` plus rerun. `git apply --check --reverse`. `git log --full-history -- path`. `git log -S`. Those are what I will type at 10:00 unless the tool names a question those commands cannot ask, *and* I will not get a confident wrong answer (CLEAN on a red suite, `{to} = idle awayRecovered=0`, October as leftover timeout 10, `generated/` as a believer).

Ghost-name search, occupancy dashboards, env-ABI dumps, pin tokens, path-condition reprints, and Gen3 peels of a parked object are not tomorrow-morning PATH entries.

---

## Install (would type instead of git/rg/jq)

Four verbs. Not eleven. Not sixteen. Not the coordinator's STATUS table.

| # | install this binary | object | not this ancestor | why Unix loses |
| --- | --- | --- | --- | --- |
| 1 | **winnow** | smallest *uncommitted hunks* that reproduce a command fingerprint | glean (`--grain file`) | `git add -p` + rerun is a 20-minute loop. `git bisect` has no dirty-hunk object. |
| 2 | **cinch 0.3** | 1-minimal *production* hunks the current tests veto; timeout is unknown | cinch 0.2, snug, tock, hasp | Same loop, different predicate. winnow wheat includes `print("debug")`. I want the lockset. 0.2 reports test-only red as CLEAN. |
| 3 | **lede** | instance → template + **named holes**; truncation is a **prefix of an instance** | invert, stump, splice, weld | `rg 'user 42 not found'` is 0 hits on `user {uid} not found`. invert/stump stuff a middle-drop tail into the last hole. |
| 4 | **cinder** | leftover *claims* a diff just made false; regenerated dest is **ash**, not a believer | zanei, nagori, ember | After a 40-hunk rename/value PR I will not remember every old literal. zanei flags `2024-10-01` and `generated/`. |

Lineage spares, not extra PATH entries: **glean** (`winnow --grain file`), **invert** (lede's ancestor), **stump** (lied on non-prefix tails), **ember** (typed facts; still treats `generated/` as a claim), **snug** (reimpl transcript of the lockset).

### 1. winnow — dirty-tree fingerprint

- Lineage: `lab/lineages/candidate-15__winnow/`
- WORKTREE: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-bf36-7370-8d54-8bed7c40c0c8`
- HEAD: `42b127e418058023775946cc832914a2a7d1d70e`
- Binary: `./winnow` (Python 3.9+, `git`. No other deps.)
- How to run: `./winnow -- pytest tests/test_foo.py` · `./winnow --format patch -- python3 test.py > guilty.patch`
- **1-command smoke:** `cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-bf36-7370-8d54-8bed7c40c0c8 && ./demo.sh`
- This session: **PASS** (`all demo cases passed` — hunk split, pycache, nested git, working tree restored).

winnow is 1970s ddmin. Heretic kills it for that. This judge keeps it because the *substrate* is the dirty tree, and I have typed the `git add -p` + test loop. I will type this tomorrow when the command is a CLI fingerprint (stdout/exit), not when it is a test suite (that is cinch).

### 2. cinch 0.3 — production lockset

- Lineage: `lab/lineages/mutation-48__cinch/`
- WORKTREE: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27`
- HEAD: `25d833b469905f2d0b0efe039a00901365c99796`
- Binary: `./cinch` (Python 3.10+, `git`. No third-party packages.)
- How to run: `./cinch -- python3 test.py` · `./cinch --format patch -- pytest > locked.patch`
- **1-command smoke:** `cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27 && ./demo.sh`
- This session: **PASS** (`demo OK` — lockset wheat is `return a + b`; debug print is chaff; test-only red is BROKEN rc=3; FAST is `budget`, VALUE is wheat).

Do **not** install hybrid-03 cinch 0.2 (`lab/lineages/hybrid-03__cinch/`, `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-03-cinch`). DESTROYER_CINCH: dirty `test.py` `assert add(2,3)==99`, production unchanged → `status CLEAN trials=0`. Occupancy of nothing, exit 0. LOCKSET_BAKEOFF carried 0.3 (honest 4/4). LOCKSET_TOCK: tock ties honesty, does not unseat; do not put tock on PATH; no fourth cinch.

v0.3 still has shared holes (exit-5 ≠ empty, `generated/`/`vendor/`, nested git, `--max-trials`). Those are mutate notes, not a reason to skip the install. The founding split survived a clean-room rebuild (snug).

### 3. lede — inverse printf, honest truncation

- Lineage: `lab/lineages/mutation-33__lede/`
- WORKTREE: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b45-0fff-7093-ac6a-fc9ee6728a41`
- HEAD: `83c450aa4cf6e78f46b67598a36dced36d4e31d4`
- Binary: `./lede` (single Python 3 file. No deps. Filter: `rg | lede`. Will not walk.)
- How to run: `rg -n --type rust 'format!|anyhow!' ~/src | ./lede '2026-08-19T23:50:01Z ERROR failed to spawn \`git apply --reverse\`'`
- **1-command smoke:** `cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b45-0fff-7093-ac6a-fc9ee6728a41 && ./demo.sh`
- This session: **PASS** (`passed=63 failed=0` — named holes, refuse-walk, DESTROYER regressions: middle-drop is a miss, rustc locator refused, binary stdin rc=2, `--any` stops).

FIRST_SKEPTIC kept **invert** and parked stump: DESTROYER_STUMP_PIN stuffed `awayRecovered=0` into `{to}`. lede flipped that kernel: truncation is prefix-of-instance; later holes stay unbound; a middle-drop paste is a miss. Same stream contract as invert. Install **lede**, not invert, not stump.

Daily paste is a log line. Format strings (Rust/Python/Swift interpolation) are the common case. Concat (`"open " + path`) is a *different* object (splice/weld). Do not put a second inverse-printf on PATH. If lede misses on `+` / `<>` / `fmt.Sprint`, the spare is weld — see skip.

### 4. cinder — leftover claims, ash ≠ believer

- Lineage: `lab/lineages/mutation-37__cinder/`
- WORKTREE: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b59-bd03-7f81-b375-7b1b1f81ed30`
- HEAD: `38d33580de3aeeee1c6dd4bb1888c65ecc976b2e`
- Binary: `./cinder` (Python 3.10+, `git`. No other deps.)
- How to run: `./cinder` (HEAD → worktree) · `git diff main | ./cinder --diff - -C .`
- **1-command smoke:** `cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b59-bd03-7f81-b375-7b1b1f81ed30 && ./demo.sh`
- This session: **PASS** (`passed=86 failed=0` — JSON quoted version is a fact; `2024-10-01` is not timeout 10; `generated/` / `oracle/` / lockfiles are CINDER not exit-1 claims; kizu `plugin.json` 0.3.0 leftover; sitbone `threshold 0.4`).

FIRST_SKEPTIC kept **zanei** thin (U=3): version bump `0.3.0 → 0.7.0` is `rg 0.3.0`; keep is the *large-diff* case. DESTROYER_ZANEI: month 10 inside ISO dates, `generated/` is a believer, JSON-only facts missed. ember typed the fact. cinder types regenerated dest as **ash** (visible with `--include-generated`, does not flip exit 1). Install **cinder**. Stay `diff in → claims out`. Do not install smolder (the invert: leftover locus → falsifying commit) as a second PATH entry; that is archaeology.

This is the thinnest keep. After `timeout 10 → 30` I will type `cinder`. After a one-line version bump I will still `rg`. The install is for the PR I have not named.

---

## Skip (do not install as products)

### Killed (Unix clone or worse join)

| skip | honest object | Unix I will type |
| --- | --- | --- |
| **haunt** | worse leftover-name join | already dead (GHOST). `rg` the name. |
| **folk** | unwritten handshakes | 0 keepers. Parked, not a slot. |
| **nigh** | string-edit distance to cuts | `ENOENT` ≈ `event`. Use `cusp` as a parked fact, not a product. |
| **unfmt-08 / unfmt-13** | inverse-printf *walker* | `rg` the static prefix, then lede if holes remain. UNFMT_BAKEOFF closed two walkers. |
| **pinch / hitch** | wait-for graph | `pstree`, `strace`. Use `knot` as absorbed fact. |
| **kiln / clutch** | generation lots | use `sinter` as fused assay if anyone needs spec-gen CI. I will not type it tomorrow. |
| **amid** | under-as-stream spare | ambit won the bakeoff; I still will not type ambit tomorrow. |
| **cinch 0.2** | lockset with occupancy lies | test-only red as CLEAN. Install 0.3. |

### Same-object peels — one PATH slot already filled

Do not install a second kernel of an object you already have.

| skip | why not PATH | if you need the peel |
| --- | --- | --- |
| invert, stump | lede is invert after DESTROYER_STUMP prefix-of-instance | lineage history |
| splice, weld, rime, caulk, stile, solder | concat inverse-printf; second filter for the same paste | weld worktree `lab/lineages/mutation-59__weld/` only if lede misses on `"lit" + expr` |
| zanei, nagori, ember | cinder is typed facts + ash | — |
| smolder, tinder, binom | leftover → falsifying *commit*; invert of cinder | `git blame` the leftover, then `git log -S` |
| glean | `winnow --grain file` | — |
| tock, snug, hasp, scree, gage | lockset bakeoff carried cinch 0.3; tock ties, does not unseat | snug is the reimpl transcript |
| sluice, stencil, moor | invert kernel / walker spare / two objects in a trenchcoat | — |

### STATUS "install these first" this judge drops

Coordinator table in `lab/STATUS.md`. Demos paid rent. They did not beat a Unix one-liner I will type at 10:00.

| skip | Unix I will type instead | leftover fact (do not evolve unless a new condition) |
| --- | --- | --- |
| **when / whence / graft / ambit / peal / seed** | open the file; `git diff -W` | `given` fallthrough is a real noun. `when --explain kizu/src/git/parse.rs:60` reprints the four early returns I already had on screen. ambit is `rg \|` of that reprint. |
| **pin v0.5 / slip / flume / keel / shoal** | `rg` the function name | kizu `src/app.rs:529` → `layout.rs:17` is real. `rg seen_hunk_fingerprint` lands `:17` without minting `pin1.eNpt…` into a ticket. DESTROYER_PIN_V5: leftover is not a pointer. I still will not mint. |
| **held / perch / tenure / stead / berth / holt / hydra** | `git log --full-history -- path`; `git log --all -- '*FocusRiver*'` | Poster `git log -- path` empty is a known footgun. Era compression is pretty. berth `--full` 187-commit roost is `--follow` with extra words. |
| **erst / brood / also / owe / kith / sire** | `git show $SHA` + `rg` natal keys | Review companion, not a daily filter. |
| **sate / lodge / dreg / braid / tilde** | `git apply --check --reverse` | reverse-check of `HEAD^..HEAD` on HEAD is rc=0. SUPERSEDED is archaeology. |
| **sow / hatch / till / seep / loam** | `rg` call sites vs tests | Missing *value* is real. Quarterly audit. |
| **plait / spar / wale / hank / quire** | read the suggestion thread | COMMUTE/STACK/JAM is a real GitHub-nit algebra. I will not install a review platform tomorrow morning. |
| **assay / xref / lash / shim / wad / prove** | `rg getenv` / `rg std::env` / `strings` | KIND split is real (DESTROYER_ASSAY mutate). rustc DUE was a strings flood; xref closed 12k opcodes. Still not a 10:00 verb. |
| **lien / noun** | CI on stdin diff | Natal-record gate. CI, not tomorrow morning. |
| **weft / woof / snag / tally** | `git diff --stat` + a docs path filter | Comment-only leak gate. CI. |

### Gen3 Keep peels — object survived destroyer; I still will not type it tomorrow

STATE: Gen3 harvested lurch / holt / noun / preen / innard / shim / stile / shoal / rune / proxy / binom / hydra / tilde / seed / badge / solder. All **Keep**. Keep ≠ install.

| skip | parked object |
| --- | --- |
| lurch | scarp as a stream of cuts. I do not have two clock readings at 10:00. |
| holt | berth all-reachable R default. `git log --follow`. |
| noun | lien workspace version identity. CI. |
| preen | tacit unfold of a constructed default. Review. |
| innard | beck `$()` / `2>&1` first-producer. Rare pipeline debug. |
| shim | xref rustup/xcselect hop. `which rustc`. |
| stile / solder | weld proving-string floor / clean-room weld. Concat spare, not a fifth inverse-printf. |
| shoal | keel remotes are not `--any-repo`. Pin family. I will not mint. |
| rune | gist dest-own UTF-16 `character`. LSP rewriter. |
| proxy | vow follow `expected=name`. Test-dump grammar. |
| binom | smolder package-scoped version. Leftover invert. |
| hydra | ford octopus + first-parent join. Occupancy lattice. |
| tilde | braid NFC path+line image. Suggestion occupancy. |
| seed | peal seed is not first locator. Path-condition stream. |
| badge | maiden identity ≠ string id. Tests that have never been red — CI audit. |

### Other parked objects (FIRST_SKEPTIC + later)

alibi, lees, sinter, coast, cling, cusp, kerf, zure, rift, doze, unseen, sic, aka, due, lode, orbit, veil, yoke, skew, deja, reverb, wraith, wisp, akin, once, folk, tacit, maiden, beck, facet, scarp, twixt, yaw, gist, blot, flare, vow, troth, writ, ford, weir, ditto, crib, pup, kit, thatch, wane, neap, dirge, visa, mint, stain, admit, brand, sear, canto, reel, ply, twain, lapse, coast.

Interesting nouns. Not tomorrow keystrokes.

---

## Empty slots 5 and 6

≤6 allowed two more. This judge refuses to fill them.

Candidates that came closest and still lost:

| almost | why not |
| --- | --- |
| **weld** | DESTROYER_WELD: splice misses `response() + "\nDone."`; weld binds. Real hole. A human pasting a log line will not know to type `weld` vs `lede`. Two inverse-printf verbs is a product failure. Spare, not PATH. |
| **when** | Toolsmith PATH, Heretic keep, Skeptic park. I open the file. The stack is a reprint. |
| **pin v0.5** | Durable address is a literature gap (PRIOR_ART). I still `rg` the name. I will not mint a token into a ticket. |
| **sate** | `git apply --check --reverse` already says applied. SUPERSEDED is `--log` archaeology. |
| **tacit** | Omitted vs restated default is a new object (sitbone 27 TACIT). Review, not morning. |
| **plait** | Suggestion algebra. I read the thread. |
| **maiden / badge** | Tests that have never been red. Quarterly / CI. |

If a later jury needs a fifth, the only honest candidate is **weld** for a concat-heavy (JS/Go) tree, run *after* lede misses — not beside it on PATH.

---

## Disagreements

### vs FIRST_SKEPTIC (winnow / cinch / invert / zanei)

Agree on the four *objects*. Disagree on three *binaries*.

Skeptic filed at 03:52, before lede / cinder / cinch 0.3. DESTROYER_STUMP_PIN parked stump over invert; lede closed prefix-of-instance (`passed=63`, middle-drop miss). DESTROYER_ZANEI parked generated-as-believer; cinder classifies ash (`passed=86`, October is not timeout 10, lockfiles are CINDER). DESTROYER_CINCH + LOCKSET_BAKEOFF retired 0.2. Installing invert / zanei / cinch 0.2 tomorrow would re-teach those lies.

Agree: haunt dead, folk parked, do not install the coordinator's twelve, do not mint pin, do not type when instead of opening the file.

### vs lab/STATUS.md "Tomorrow-test shortlist"

Coordinator listed eleven families. This judge installs four binaries. STATUS is a breeding board. An install list that includes pin, when, held, sate, erst, sow, plait, assay, and kith is how a human installs nothing because they installed everything.

### vs Toolsmith (PATH twelve)

Toolsmith would run invert, slip, winnow, when, zanei, reverb, sic, due, sate, zure, held, cinch.

This judge keeps **winnow, cinch 0.3**. Replaces invert with lede, zanei with cinder. Parks slip, when, sate, held, sic, zure. Kills reverb, due.

Toolsmith U=5 is "a developer could." This judge's U is "I will, tomorrow morning, instead of git/rg."

### vs Heretic (unseen objects)

Heretic kills winnow as ddmin and keeps when / perch / tell / pin / erst / alibi / lees / sate / clutch / sow / coast.

This judge **keeps the corpse heretic buried** (winnow/cinch) and **skips the museum heretic loves**. An unseen question-word I will not type is not an install.

Agree: haunt dead, folk parked, invert-lineage is the inverse-printf vehicle (this judge: lede), unfmt walkers die.

### vs Unix (sixteen mutate vehicles)

Unix mutate list is orthogonal primitives to *breed*, not to install. This judge's install list is a subset: cinch, lede (invert lineage), cinder (zanei lineage). winnow was Unix "keep, do not evolve this wave." Correct: still candidate-15.

Do not spend a morning installing pin, flume, tell, perch, sate, erst, sic, sow, lode, lees, under, cusp, doze.

### vs DESTROYER mutate lists

Every dedicated destroyer this night said **mutate, do not kill**. That is a breeding instruction. It is not an install instruction. Mutate-not-kill on scarp / berth / lien / tacit / beck / xref / weld / keel / gist / vow / smolder / ford / braid / peal / maiden / woof means the *object is real*. Real ≠ I will type it at 10:00.

Agree mutate-not-kill on cinch, invert/stump, zanei, pin. Then pick the peel that stopped lying: cinch 0.3, lede, cinder. Pin still fails the tomorrow-test after v0.5.

### vs Gen3 Keep peels

Sixteen Keep. Zero installs. A Keep peel of a parked object is still parked.

---

## Evidence of this session

Did not re-run FIRST_SKEPTIC's Unix-first dogfood probes (`rg` then the tool on kizu/sitbone). Those already showed when/held/sate/pin lose to git/rg. This session **ran the four install `./demo.sh` batteries** (2026-08-20, this worktree):

| binary | smoke | result |
| --- | --- | --- |
| winnow | `./demo.sh` in candidate-15 worktree | exit 0, all cases |
| cinch 0.3 | `./demo.sh` in mutation-48 worktree | exit 0, `demo OK` including DESTROYER cases 14–18 |
| lede | `./demo.sh` in mutation-33 worktree | exit 0, 63/63 including DESTROYER regressions + kizu/sitbone/tenaoshi/voidtrace rg pipes |
| cinder | `./demo.sh` in mutation-37 worktree | exit 0, 86/86 including DESTROYER JSON/date/ash + kizu/sitbone gold |

Cited, not re-run: DESTROYER_CINCH, DESTROYER_STUMP_PIN, DESTROYER_ZANEI, DESTROYER_PIN_V5, DESTROYER_WELD, LOCKSET_BAKEOFF, LOCKSET_TOCK, UNFMT_BAKEOFF, AMBIT_AMID_BAKEOFF, FIRST_SKEPTIC Unix-first transcripts, STATE vehicle carry list, Gen3 CANDIDATE Keep lines.

---

## Copy-paste morning

```bash
# 1. dirty-tree fingerprint
cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-bf36-7370-8d54-8bed7c40c0c8 && ./demo.sh

# 2. production lockset (not cinch 0.2)
cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27 && ./demo.sh

# 3. inverse printf (not invert, not stump)
cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b45-0fff-7093-ac6a-fc9ee6728a41 && ./demo.sh

# 4. leftover claims (not zanei)
cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b59-bd03-7f81-b375-7b1b1f81ed30 && ./demo.sh
```

Then, on a real dirty tree:

```bash
WINNOW=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-bf36-7370-8d54-8bed7c40c0c8/winnow
CINCH=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b64-f63d-7ec0-b76f-cb9797ff4a27/cinch
LEDE=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b45-0fff-7093-ac6a-fc9ee6728a41/lede
CINDER=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b59-bd03-7f81-b375-7b1b1f81ed30/cinder

$WINNOW -C "$REPO" -- pytest
$CINCH  -C "$REPO" -- pytest
rg -n --type rust 'format!|anyhow!' "$REPO" | $LEDE 'paste a log line here'
git -C "$REPO" diff | $CINDER --diff - -C "$REPO"
```

Do not symlink all four plus STATUS's eleven into `~/bin`. Four is already a morning.

---

## What this judge is not doing

- Not picking a single winner. winnow is not "the" tool. lede is not "the" tool.
- Not grading polish, LOC, or demo counts.
- Not keeping two walkers, two leftover-name miners, two wait-graph CLIs, two generation-lot CLIs, two inverse-printf filters, or a pin token I will not mint.
- Not killing winnow because Heretic said "1970s." The object is uncommitted hunks. I will type it.
- Not installing when / pin / perch / sate / erst / sow / coast / plait / assay / tacit / maiden because they are strange and the dogfood transcript is pretty. Strange and unused is still unused.
- Not treating DESTROYER "mutate, do not kill" or Gen3 "Keep" as install.
- Not merging to `main`.

If a later jury needs a short list: **winnow, cinch 0.3, lede, cinder**.
