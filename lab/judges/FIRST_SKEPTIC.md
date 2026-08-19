# FIRST_SKEPTIC — first selection

Source: first-selection skeptic on 2026-08-20. Axis of record is the **tomorrow-test**: would I actually type this tomorrow *instead of* `git` / `rg` / `jq`? Default **no**.

Other judges (FIRST_TOOLSMITH, FIRST_HERETIC, FIRST_UNIX, DISTINCT, GHOST_CLUSTER, UNFMT_BAKEOFF, DESTROYER_*) are evidence, not a ranking to rubber-stamp. FIRST_SELECTION's intersection is a hypothesis this judge is allowed to reject.

Scores 0–5 integers: Novelty / Utility / Primitive / Composability / Empirical / Evolution. **Utility is the veto.** U≥4 only if this judge would type the verb instead of a 15-second Unix pipeline. A 4+ on Empirical requires a run, not a README. This session did **not** re-run `./demo.sh` batteries (those prove the binary works; they do not prove the verb is necessary). It ran targeted Unix-first probes on dogfood trees, then the candidate only if `git`/`rg` missed.

Several survivors. Not one winner. Haunt stays dead. Folk stays parked.

---

## The question

A skeptic keeps a verb only when the Unix one-liner is the wrong object, not merely the uglier spelling.

`rg` the static prefix. `git log --full-history -- path`. `git apply --check --reverse`. `git log -S`. `rg` the old constant. Those are not "prior art footnotes." They are what I will type at 10:00 tomorrow unless the tool names a question those commands cannot ask.

Ghost-name search, occupancy dashboards, env-ABI dumps, wait-for graphs, and token minting are unnecessary until a dirty tree, a log paste, or a leftover *claim* forces them.

---

## Survivors (would type instead of git/rg/jq)

Four verbs. Not twelve. Not sixteen.

| # | tool | id | primitive | why the Unix one-liner loses |
| --- | --- | --- | --- | --- |
| 1 | **winnow** | candidate-15 | smallest *uncommitted hunks* that reproduce a command fingerprint | `git add -p` + rerun is a 20-minute loop. `git bisect` has no dirty-hunk object. |
| 2 | **cinch** | hybrid-03 | 1-minimal *production* hunks the current tests veto | Same loop, different predicate. winnow wheat includes `print("debug")`. I want the lockset. |
| 3 | **invert** | mutation-15 | instance → template + **named holes** as a filter | `rg 'user 42 not found'` is 0 hits on `user {uid} not found`. `rg 'not found'` is a guess. |
| 4 | **zanei** | candidate-07 | leftover *claims* a diff just made false | Barely. After a 40-hunk rename/value PR I will not remember every old literal. After `0.3.0 → 0.7.0` I will `rg 0.3.0`. |

Lineage spares, not extra PATH entries: **glean** (`winnow --grain file`), **sluice** (anonymous invert kernel), **stencil** (walker spare; do not ship).

stump (mutation-23) is invert after DESTROYER. DESTROYER_STUMP_PIN: non-prefix tails stuffed into the last hole; a 10-char static prefix is a confident hit. Do not promote stump over invert this wave.

---

## Unix clones (kill the product)

If the honest object is an existing command plus flags, the product dies. Harvest at most one fact.

| kill | honest object | Unix I will type |
| --- | --- | --- |
| **haunt** | worse leftover-name join | already dead (GHOST). `rg` the name. |
| **wraith** / **wisp remnants** | inverted knip / dead defs in docs | `rg` + compiler. One leftover-*name* search is already too many. |
| **reverb** | preimage of this diff as a search | `git diff` minus lines → `rg`. tenaoshi `Content-Type` is that pipeline. |
| **unfmt-08 / unfmt-13** | inverse-printf *walker* | `rg` the static prefix, then invert if holes remain. UNFMT_BAKEOFF closed two walkers. |
| **sluice as product** | invert without names | invert is the filter. |
| **moor** | slip × unfmt in one trenchcoat | composition. Kill. |
| **due / lode / orbit** | env ABI / `ldd` of getenv / guise vs payload | `rg getenv` / `rg std::env` / `strings` / `otool -L` / `which`. |
| **aka / sic** | inflection pact / exact wire key | `rg -i has_more`. A `--check` on a patch is a linter. |
| **nigh** | string-edit distance to cuts | `ENOENT` ≈ `event`. Dead. |
| **akin** similarity | invented merge-bases | clone-detect + `merge-file`. **once** exact-blob is still git. Park `--port` only. |
| **pinch / hitch / knot** | wait-for graph | `pstree`, `strace`, `offcputime`. |
| **spoor** | spawn-wrap wake | `time` + leftovers. |
| **coast** | post-waitpid interval | I write `sleep 2`. `wait` exists. AUTHOR-only; I did not run it. |
| **cleave** | test vs prod inhabitance *report* | dashboard. |
| **yoke** | spec-clause polarity | spec-check with more words. |
| **veil** | LIVE/VEIL/BARE | coverage + `rg vi.mock`. |
| **skew** | file clock vs callee | `stat` / commit date. |
| **deja** | RELAPSE / UNDOFIX | `git log -S` plus "was this a fix." |
| **folk** | unwritten handshakes | 0 keepers after honesty filter. Park, do not spend slots. |
| **kiln / clutch** as products | generation lots | sinter is the fused assay if anyone needs a spec-gen CI. I will not type it tomorrow. |

---

## Park (object may be real; I will not type it tomorrow)

| park | Unix I will type instead | leftover fact (do not evolve unless a new condition) |
| --- | --- | --- |
| **when / under / chime** | open the file; `git diff -W` | `given` fallthrough is a real noun. Live `layout.rs:17` is depth=0. This session: `parse.rs:60` is four early returns I already read. |
| **held / dwelt** | `git log --full-history -- path`; `git log --all -- '*FocusRiver*'` | Poster `git log -- path` empty is a known simplification footgun, not a missing verb. Era compression is pretty. |
| **perch / stint / tell** | `git log -S` + `rg`; `git diff --stat` | README-only tenure is `rg` after the definition left. tell inverts a question I already have. |
| **pin / slip / flume** | `rg` the function name | kizu `src/app.rs:529` → `layout.rs:17` is real. `rg seen_hunk_fingerprint` lands `:17` without a token. I will not mint `pin1.eNpt…` into a ticket. |
| **sate / lodge** | `git apply --check --reverse` | This session: reverse-check of `HEAD^..HEAD` on HEAD is rc=0. sate says APPLIED. The boolean is not a lie here. SUPERSEDED in `--log` is archaeology. |
| **erst / also / owe** | `git show $SHA` + `rg` natal keys | `t1`↔`driftDelay` is the only miss. Review companion, not a daily filter. |
| **sow** | `rg` call sites vs tests | Missing *value* is real. Quarterly audit, not tomorrow. |
| **alibi** | `git stash -k` is the wrong splice — agreed | No cargo/swift splice on dogfood. E=3. |
| **lees** | `diff` + sed `$HOME` | MACHINE vs SPEC is a real verdict. I compare snapshots rarely. |
| **sinter / clutch / kiln** | `just spec-gen` / mtime | relico eight-day split is real and still a spec-gen niche. |
| **doze / unseen** | `git blame` the call + look at the signature | CI-shaped remainder. Not a tomorrow verb. |
| **cusp / kerf** | read the comparison | Cut values (401/400) beat nigh. Still static analysis. |
| **zure / rift** | `rg` the deleted identifier | Useful pre-commit. Not unseen. Daily form is "I know what I deleted." |
| **wraith** | one leftover-name spare | Archaeology. zanei is the post-diff verb if anything. |

---

## Per-candidate scores

`Σ` is unweighted and is not a ranking. **Keep follows Utility**, then "can Unix phrase this." Novelty does not save a clone. Utility does not save a clone either — `winnow` is the exception because the *object* (uncommitted hunks) is not `git bisect`.

Legend: **K** = survive / I would type it. **P** = preserve the object, no PATH. **PARK**. **KILL**.

### Inverse printf

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-15 | invert | 4 | 4 | 5 | 5 | 5 | 4 | 27 | **K** | runtime instance on one channel, templates on the other; named holes; leftover prefix is a span |
| mut-23 | stump | 4 | 3 | 4 | 5 | 5 | 3 | 24 | PARK | invert after DESTROYER; truncation lies on non-prefix tails (DESTROYER_STUMP) |
| reimpl-01 | stencil | 3 | 2 | 5 | 3 | 5 | 2 | 20 | PARK spare | walker. `rg` is the producer |
| hyb-01 | moor | 2 | 2 | 3 | 4 | 4 | 2 | 17 | KILL | two objects in a trenchcoat |
| cand-08 | unfmt | 3 | 2 | 4 | 3 | 5 | 2 | 19 | KILL | walker; camera miss; `rg` the static |
| cand-13 | unfmt | 3 | 2 | 4 | 3 | 5 | 2 | 19 | KILL | named holes already in invert |
| mut-02 | sluice | 3 | 3 | 4 | 5 | 5 | 2 | 22 | PARK kernel | stream assumption; invert adds names |

Mutate invert: DESTROYER_PIN_INVERT (no-hole prefix must not beat a binding; refuse rustc; binary fail closed). Do not grow a walker. Do not ship stump as a second filter until prefix-of-instance is honest.

### Dirty tree / tests as lock

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-15 | winnow | 2 | 5 | 4 | 5 | 4 | 3 | 23 | **K** | smallest hunk set that reproduces a command fingerprint |
| hyb-03 | cinch | 3 | 5 | 5 | 4 | 4 | 4 | 25 | **K** | smallest *production* hunks the current tests veto; tests never wheat |
| mut-07 | glean | 2 | 4 | 4 | 5 | 4 | 2 | 21 | PARK→flag | file grain + untracked; `winnow --grain file` |
| cand-24 | alibi | 4 | 2 | 4 | 3 | 3 | 4 | 20 | PARK | tests@NEW × prod@OLD; no cargo/swift splice |

Novelty of winnow is 2 (ddmin, 1970s). Heretic kills it for that. Skeptic keeps it because the *substrate* is the dirty tree, and I will type it. cinch is the one I type when the command is a test suite.

### Leftover claims (not leftover names)

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-07 | zanei | 4 | 3 | 4 | 5 | 4 | 3 | 23 | **K** thin | facts from a diff; afterimages in the dest tree |
| reimpl-03 | nagori | 3 | 3 | 4 | 5 | 4 | 2 | 21 | PARK proof | clean-room zanei; complementary JSON/prose holes (DESTROYER_ZANEI) |
| cand-04 | reverb | 2 | 2 | 2 | 4 | 4 | 1 | 15 | KILL | `git grep` of the minus lines |
| cand-06 | deja | 3 | 2 | 3 | 4 | 4 | 2 | 18 | PARK | `git log -S` + fix-memory |
| cand-12 | wraith | 2 | 2 | 2 | 3 | 3 | 1 | 13 | KILL | leftover names; knip inverted |
| cand-05 | haunt | 1 | 1 | 2 | 2 | 4 | 1 | 11 | KILL | worse wraith; lost `preact-zero-mock` |
| cand-03 | wisp | 2 | 1 | 2 | 2 | 3 | 1 | 11 | KILL remnants | occupancy half is stint |

zanei U=3: this session `rg 0.3.0` reproduced the kizu poster exactly (`plugin.json` + two `plans/v0.3.md` lines). The keep is the *large-diff* case, not the version bump. Stay a filter (`git diff \| zanei --diff -`). DESTROYER: ISO-date `10`, `generated/` not skipped, JSON-only facts missed, binary stdin exit 1.

### Relocatable locus

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-16 | slip | 3 | 3 | 4 | 4 | 5 | 2 | 21 | PARK | rewrite `file:line` by fingerprint |
| mut-04 | flume | 3 | 3 | 4 | 5 | 2 | 3 | 20 | PARK | log in, log out, gitless |
| mut-14/22 | pin | 4 | 2 | 4 | 3 | 5 | 4 | 22 | PARK | token is the address; I will not mint one |

PRIOR_ART named "durable pin." That is a gap in the literature, not a gap in tomorrow's fingers. This session: `rg seen_hunk_fingerprint` hits `src/app/layout.rs:17`. slip `--from b4e6a5d src/app.rs:529` also lands `:17` score 0.919. Both work. I still `rg`.

### Occupancy / path-condition

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-09 | held | 4 | 2 | 5 | 5 | 5 | 3 | 24 | PARK | eras a predicate held; Unix is `--full-history` + `-S` |
| reimpl-02 | dwelt | 2 | 2 | 5 | 5 | 5 | 2 | 21 | PARK | proof held is real |
| mut-17 | perch | 4 | 2 | 5 | 4 | 4 | 3 | 22 | PARK | split when the holder set changes |
| mut-03 | tell | 4 | 2 | 5 | 5 | 4 | 3 | 23 | PARK | two trees → shortest predicate; I have `git diff --stat` |
| mut-18 | stint | 3 | 2 | 4 | 3 | 3 | 2 | 17 | PARK | interval ghosts + `--pick` |
| cand-20 | when | 4 | 2 | 5 | 4 | 5 | 3 | 23 | PARK | condition stack at a locus; I open the file |
| mut-10 | under | 3 | 2 | 4 | 4 | 3 | 2 | 18 | PARK→flag | name a predicate, emit lines |
| mut-16 | chime | 4 | 2 | 5 | 4 | 3 | 2 | 20 | PARK→flag | other loci with the same stack |

held poster this session: `git log -- Sources/SitboneUI/FocusRiverView.swift` empty; `git log --full-history --` prints `14b1d6e` add and `70ec7df` delete; `git log --all -- '*FocusRiver*'` same. held `--full exists` adds `TRUE 11 / FALSE 78` compression. Pretty. Not a new question.

when poster this session: `when --explain kizu/src/git/parse.rs:60` reprints the four early-return guards I already had on screen at lines 43–57. Heretic object. Not a tomorrow keystroke.

### Wire / env / birth / worlds / occupancy of patches

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mut-01 | sic | 2 | 2 | 3 | 5 | 4 | 2 | 18 | PARK | exact wire key `--check`; linter |
| cand-02 | aka | 2 | 2 | 3 | 5 | 5 | 2 | 19 | PARK | inflection identity; `rg -i` |
| cand-28 | due | 2 | 2 | 2 | 3 | 4 | 2 | 15 | KILL | `rg getenv` |
| mut-21 | lode | 2 | 2 | 3 | 4 | 3 | 2 | 16 | KILL | `ldd` + getenv names |
| cand-30 | orbit | 3 | 2 | 3 | 3 | 3 | 2 | 16 | PARK | which binary will run; `which` + rustup |
| mut-19 | erst | 4 | 3 | 4 | 4 | 3 | 3 | 21 | PARK | natal cohort + inflection; `git show` + `rg` |
| cand-10 | also | 3 | 2 | 4 | 4 | 4 | 2 | 19 | PARK | FILE:LINE spelling of erst |
| mut-06 | owe | 3 | 2 | 4 | 4 | 3 | 2 | 18 | PARK | exact-key erst |
| mut-13 | sow | 4 | 2 | 4 | 4 | 3 | 3 | 20 | PARK | untested production worlds as fixtures |
| cand-18 | cleave | 3 | 1 | 3 | 3 | 2 | 2 | 14 | KILL | the report |
| cand-34 | sate | 4 | 2 | 5 | 4 | 4 | 3 | 22 | PARK | hunk occupancy vs `git apply --check` boolean |
| cand-31 | lees | 4 | 2 | 5 | 4 | 3 | 4 | 22 | PARK | oracle modulo substitution |
| hyb-04 | sinter | 3 | 2 | 4 | 3 | 3 | 2 | 17 | PARK | RAGGED/STALE/CLEAN lot |
| cand-27 | clutch | 3 | 2 | 3 | 3 | 3 | 2 | 16 | PARK | receipts |
| cand-26 | kiln | 3 | 2 | 3 | 3 | 3 | 2 | 16 | PARK | claims |

### Wait / brink / kinship / other

| id | tool | N | U | P | C | E | V | Σ | verdict | primitive restatement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cand-25 | coast | 3 | 2 | 4 | 4 | 3 | 3 | 19 | PARK | interval after waitpid; I type `sleep 2` |
| mut-12 | cling | 3 | 2 | 3 | 3 | 3 | 2 | 16 | PARK | attach-pid |
| hyb-02 | knot | 2 | 2 | 3 | 4 | 3 | 2 | 16 | KILL product | wait-for graph |
| cand-22 | pinch | 2 | 1 | 3 | 3 | 2 | 1 | 12 | KILL | absorbed |
| cand-23 | hitch | 2 | 1 | 3 | 3 | 2 | 1 | 12 | KILL | absorbed |
| cand-21 | spoor | 3 | 1 | 3 | 3 | 2 | 2 | 14 | KILL | spawn-wrap |
| mut-11 | cusp | 3 | 2 | 4 | 4 | 3 | 3 | 19 | PARK | constructed values on a cut |
| cand-17 | nigh | 1 | 1 | 2 | 2 | 2 | 1 | 9 | KILL | string distance |
| cand-01 | akin | 2 | 1 | 2 | 3 | 4 | 1 | 13 | KILL | similarity merge-base |
| mut-09 | once | 2 | 1 | 3 | 4 | 2 | 2 | 14 | PARK | exact blob kin; 0 on dogfood trees |
| cand-19 | folk | 2 | 1 | 3 | 2 | 2 | 1 | 11 | PARK | 0 real orphans |
| cand-32 | veil | 3 | 1 | 3 | 3 | 3 | 2 | 15 | KILL | cover-type |
| cand-11 | rift | 2 | 2 | 3 | 4 | 4 | 2 | 17 | PARK | identifier conflicts a clean merge accepts |
| mut-05 | zure | 2 | 3 | 3 | 4 | 2 | 2 | 16 | PARK | dirty-tree rift; I `rg` what I deleted |
| cand-14 | unseen | 3 | 2 | 3 | 3 | 3 | 2 | 16 | PARK | definition as last seen by this use-site |
| mut-20 | doze | 3 | 3 | 4 | 4 | 3 | 2 | 19 | PARK | `--check` signature lag; CI, not tomorrow |
| mut-08 | skew | 2 | 1 | 3 | 3 | 2 | 2 | 13 | KILL | file clocks |
| cand-29 | yoke | 2 | 1 | 2 | 3 | 3 | 2 | 13 | KILL | spec-check polarities |

---

## Disagreements

### vs Toolsmith (PATH twelve)

Toolsmith would run invert, slip, winnow, when, zanei, reverb, sic, due, sate, zure, held, cinch tomorrow.

Skeptic keeps **winnow, cinch, invert, zanei**. Parks slip, when, sate, held. Kills reverb, due. Parks sic, zure.

Toolsmith's U=5 on slip/when/sate/held/due is "a developer could." This judge's U is "I will." Those are different numbers.

### vs Heretic (unseen objects)

Heretic kills winnow as ddmin and keeps when / perch / tell / pin / erst / alibi / lees / sate / clutch / sow / coast.

Skeptic **keeps the corpse heretic buried** (winnow/cinch) and **parks the museum heretic loves**. An unseen question-word I will not type is not a survivor. Novelty is not a defense here; it is how we got a lab full of walkers.

Agree: haunt dead, folk parked, one leftover-name search is enough (and even that is too many), invert is the inverse-printf vehicle, unfmt walkers die, kiln∥clutch collapse.

### vs Unix (sixteen mutate vehicles)

Unix wants invert, pin, flume, tell, perch, sate, erst, sic, sow, zanei, lode, lees, cinch, under, cusp, doze as Gen-3 vehicles.

Skeptic mutate list is **winnow, cinch, invert, zanei**. Everything else is a parked object or a Unix clone. Do not spend Gen-3 inventing a thirteenth leftover-name search, a second walker, or a pinfile product I will not mint.

Agree: haunt dead, folk parked, invert is a filter not "the winner," do not merge the survivors.

### vs FIRST_SELECTION intersection

Coordinator kept invert, when, zanei, sate, held/perch, pin, erst, sow, coast (plus cinch as disagreement).

Skeptic **drops when, sate, held/perch, pin, erst, sow, coast** from the install-first list. They paid rent as *demos*. They did not survive "instead of git/rg/jq."

Keep the disagreement on cinch: Toolsmith PATH, Heretic kill, Skeptic **keep**. Lockset ≠ fingerprint is why I type cinch rather than winnow when the command is a test.

### vs DESTROYER

Mutate invert and zanei; do not kill. Agree. pin v0.3 closed the first destroyer list and still fails the tomorrow-test (I will not mint). stump's new lies are a reason to hold invert, not to elect stump.

---

## Evidence of this session (Unix first, then the tool)

Worktrees under `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/`. Dogfood: `~/ghq/github.com/annenpolka/{kizu,sitbone,skills}`.

### invert — spawn poster is `rg`; hole poster is not

```
$ rg -n 'failed to spawn' kizu -g '*.rs' | head -1
kizu/src/git/revert.rs:46:        .context("failed to spawn `git apply --reverse`")?;
# first hit is already the invert landing. unique static `git apply --reverse`.

$ rg -n --no-heading 'failed to spawn' kizu | invert --templates - \
    '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
…/revert.rs:46:18  score=0.66  holes=0  prefix: 2026-08-19T23:50:01Z ERROR  span=27-64
# invert adds a span report. I already had the file.

$ rg -n 'user 42 not found' invert/fixtures
# 0 hits

$ rg -n -g '*.py' 'f"' invert/fixtures | invert --templates - 'user 42 not found'
fixtures/src/user.py:2:20  tmpl: user {uid} not found  {uid}=42
# this is the keep. instance digits are not in the source.

$ rg -n -g '*.swift' 'awayRecovered' sitbone | invert --templates - \
    'transition focused → idle reason=timeout idle=12s … awayRecovered=0'
…/SitboneCore.swift:554:35  holes=7  {idle}=12  {oldPhase.rawValue}=focused …
# rg awayRecovered also finds the line. invert unpacks names. unpacker, not search.
```

### zanei — version bump is `rg 0.3.0`

```
$ rg -n '0\.3\.0' kizu -g '!target/**' -g '!*.lock'
plugin/plugin.json:4:  "version": "0.3.0",
plans/v0.3.md:103: - [ ] version bump to 0.3.0
plans/v0.3.md:451: "version": "0.3.0"

$ git -C kizu diff v0.3.0 v0.7.0 -- Cargo.toml | zanei --diff - -C kizu --min-score 70
FACT version: 0.3.0 → 0.7.0
  103 config  plugin/plugin.json:4   "version": "0.3.0",
   84 docs    plans/v0.3.md:103
   84 docs    plans/v0.3.md:451
# same three hits. scoring is extra. keep is for the diff I have not named.
```

sitbone `rg 'threshold 0.4'` already hits CLAUDE.md:329/332 (zanei/erst poster leftovers) plus hysteresis tests.

### held — `--full-history` already names birth and death

```
$ git -C sitbone log --oneline -- Sources/SitboneUI/FocusRiverView.swift
# empty  — the known footgun

$ git -C sitbone log --oneline --full-history -- Sources/SitboneUI/FocusRiverView.swift
70ec7df Clean up: remove unused FocusRiverView + SettingsWindowController
14b1d6e Focus River settings UI + dropdown settings button

$ git -C sitbone log --oneline --all -- '*FocusRiver*'
# same two commits

$ held -C sitbone --full exists Sources/SitboneUI/FocusRiverView.swift
FALSE 11  TRUE 11 (14b1d6e..1fefafb)  FALSE 78
# compression of the interval. I already had add + delete.
```

### perch — `git log -S` + `rg`

```
$ git -C skills log --oneline -S 'preact-zero-mock' --name-only
127df9c remove preact-zero-mock    preact-zero-mock/SKILL.md
5b1c907 add README …              README.md
007292a add preact-zero-mock      preact-zero-mock/SKILL.md

$ perch -C skills grep preact-zero-mock
TRUE 21 SKILL.md / TRUE 10 README+SKILL / TRUE 16 README only  ghost: definition left
# nicer report of what `rg preact-zero-mock` already shows at HEAD (README).
```

### when — I read the function

```
$ when --explain kizu/src/git/parse.rs:60
in     parse_diff_git_header
given  ¬(len<5+ 2)            # source L43
given  inner.is_multiple_of(2) # L47
given  bytes.starts_with(b"a/") # L51
given  … == Some(b" b/")       # L57
here   let b_side = …
# I had L22–65 open. the stack is a reprint.
```

### sate — `git apply --check --reverse` already says applied

```
$ git -C kizu diff HEAD^ HEAD | git -C kizu apply --check --reverse ; echo rc=$?
rc=0

$ sate --git HEAD -C kizu --against HEAD --report-only
unanimous=APPLIED  APPLIED=2   # Cargo.toml + Cargo.lock

$ sate --git HEAD -C kizu --against HEAD^ --report-only
unanimous=PENDING  PENDING=2

$ sate --log 8 -C kizu --report-only
SPLIT  88362116  release: v0.6.0   PENDING=1 SUPERSEDED=1
# SUPERSEDED is the extra column. archaeology. not tomorrow.
```

Forward `git apply --check` of an already-applied HEAD patch fails (rc=1). That is the boolean working, not lying.

### pin / slip — I `rg` the name

```
$ slip --repo kizu --from b4e6a5d --to HEAD --porcelain src/app.rs:529
moved  src/app.rs:529  src/app/layout.rs:17  0.919

$ rg -n 'seen_hunk_fingerprint' kizu -g '*.rs'
src/app/layout.rs:17:pub fn seen_hunk_fingerprint(

$ pin mint --repo kizu src/app/layout.rs:17
pin1.eNptkN1KxDAQhV9lyIXs…     # I will not paste this into a ticket
```

`git log -L 17,17:src/app/layout.rs` shows the split as a new file and stops. That is the PRIOR_ART gap. It is not a reason I will mint.

### winnow / cinch — UNVERIFIED this session as binaries

Did not run `./demo.sh`. Cite Toolsmith + parent: winnow PASS (hunk split, pycache, nested git); cinch PASS (lockset wheat is the return hunk; winnow wheat includes the debug print). The tomorrow-test here is conceptual and sufficient: I have typed the `git add -p` + test loop. I will type these.

---

## Suggested mutations (only K)

Do not spend Gen-2/3 slots on when-flags, pinfile registries, occupancy TUIs, leftover-name ignore lists, or a second inverse-printf walker.

1. **winnow** — default fingerprint that does not need `PYTHONDONTWRITEBYTECODE`. `--grain file` eats glean.
2. **cinch** — `--base origin/main` as the PR verb. EMPTY≠BROKEN already; keep it. Do not become a coverage dashboard.
3. **invert** — DESTROYER list. Prefix-of-a-holed-template. No-hole prefix cannot beat a binding. Refuse rustc. Binary stdin fail closed. Optional `rg |` wrap, not a walker. Hold stump until non-prefix tails miss.
4. **zanei** — stay `diff in → claims out`. Tighten small integers inside ISO dates. `generated/` is a leftover *build*, not a leftover *claim*. Binary `--diff -` must be exit 2, not linter-positive 1.

---

## What this judge is not doing

- Not picking a single winner. winnow is not "the" tool. invert is not "the" tool.
- Not grading polish, LOC, or demo counts.
- Not keeping two walkers, two leftover-name miners, two wait-graph CLIs, two generation-lot CLIs, or a pin token I will not mint.
- Not killing winnow because Heretic said "1970s." The object is uncommitted hunks. I will type it.
- Not keeping when / pin / perch / sate / erst / sow / coast because they are strange and the dogfood transcript is pretty. Strange and unused is still unused.

Next hour: mutate the four. Do not invent a fifth leftover-name search. Do not install the coordinator's twelve.

If a later jury needs a short list: **winnow, cinch, invert, zanei**.
