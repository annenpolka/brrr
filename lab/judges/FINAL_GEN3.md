# FINAL_GEN3 — Gen3-holes Judge (judge-12)

Independent jury on whether Generation 3 closed DESTROYER conceptual holes, or papered over them.

Clock: 2026-08-20 final jury. This worktree is isolated. No merge to main. Scores are not the question; **the named lie** is.

Gold is DESTROYER, not CANDIDATE.md. A Keep harvest is occupancy of a report, not a closed hole. A one-line rename, an extra flag, or a display sticker that leaves `now=` / default seed / KIND the same is paper.

## Method

Read DESTROYER mutate-toward tables in `lab/judges/DESTROYER_*.md`. Read Gen3 CANDIDATE.md. Then **run the tools** against DESTROYER gold, not the README:

| probe | result |
| --- | --- |
| `lurch < stream-dilate-then-sleep.jsonl` | DILATE then SLEEP (`ntp=` still printed) |
| `lurch < slew-noproper.txt` | SLEEP `sleep=1d00h00m ntp=-7.500s` |
| `lurch < wait61.txt` | DILATE (not `kind=host`) |
| `noun self-test` | 0; plugin.json leftover of kizu cargo bump |
| `git -C kizu diff 9349dc5^ 9349dc5 \| noun` | `plugin/plugin.json:4: claim: crate:kizu VERSION 0.6.0 → 0.7.0` |
| `binom -C kizu plugin/plugin.json:4` | **none**; homonym `53cbd1a` Cargo.toml |
| `binom -C sitbone CLAUDE.md:329` | leftover `e9b0f75` `0.4 → 0.45` |
| `holt exists` either kizu name | `true=187/244` same roost |
| `holt --first-parent exists` dead name | dest roost `true=21/24` origin `321a830` |
| `innard` `$()` / mid `2>&1` / unpiped git | inner `tr`; stderr mint; tee MISS |
| `shim --app` false.c / empty.c / `--no-follow python3` | only `REAL_GETENV_NAME`; `(no owed names)`; `shim xcselect` |
| `stile` `{body}abcd` / incomplete fence / `\nDone.` | miss / miss / bind |
| `solder` same three | **hit** / **truncated-success** / bind |
| `shoal --selftest` | ok |
| `rune ./demo.sh` | kizu `528 → 16` + origin `diagnostics: []`; SARIF 529 stays; sitbone `44 → 74` |
| `proxy --from-fail` name-follow dumps | **one** pair; HOST still soft |
| `hydra -C kizu exists CLAUDE.md` | hydra `1-of-2` at `0ea3916` and `21ae074`; TRUE 17-commit continue |
| `tilde` NFC NFD-tree / stack-mid | PENDING `exact-before`; SUPERSEDED of `beta→beta3` |
| `seed` `rg return None;` / `rg let b_side` | bag rc=2 (9 stacks); gold three spans |
| `badge` flaky / 2019+2024 / `--latest --skeptic` / go-fail | SCARRED / gold alpha SCARRED / rc=2 / **empty `{}` rc=0** |
| `preen --selftest` + sitbone `presentThreshold` | PinProfile OVERRIDE 20; **27 TACIT** |

Worktrees: `lab/lineages/{mutation-103..114,hybrid-18,hybrid-19,candidate-43,reimpl-11}__*/WORKTREE.txt`.

## Scoreboard

| pair | verdict | named hole | paper? |
| --- | --- | --- | --- |
| DESTROYER_SCARP vs lurch | **partial** | `cuts[0], cuts[1]` + missing-proper DILATE | no — window flipped; `ntp=` still adjtime |
| DESTROYER_BERTH vs holt | **partial** | all-reachable R + tip-occupant seed | no — identity flipped; lattice still list-order |
| DESTROYER_LIEN vs noun | **partial** | `(package, noun)`; plugin leftover of crate bump | no — CI hole closed; path/CJK/omit still silent |
| DESTROYER_TACIT vs preen | **partial** | constructed unfold + clap invocation | no — PinProfile 20 vs 15; `*args` still steals |
| DESTROYER_BECK vs innard | **partial** | `$()` inner + mid-command `2>&1` | no — inner ≠ wrap; JSON field-cover still facet |
| DESTROYER_XREF vs shim | **partial** | `*getenv` suffix + shim role | no — allowlist + `shim` porcelain; wrappers/inlined still |
| DESTROYER_WELD vs stile / solder | **partial** | distinctive proving string + incomplete fence | **split** — stile closed; solder reimpls the ancestor including the holes |
| DESTROYER_KEEL vs shoal | **closed** | origin cannot be typed into `git remote add` | no — remotes ∩ and `object_exists` no longer identity |
| DESTROYER_GIST vs rune | **partial** | UTF-16 `character` + origin `diagnostics: []` | no — dest-owns the unit; rustc gutter carry still `old+k` |
| DESTROYER_VOW vs proxy | **partial** | follow `expected=name`; one pair per assertion | no — n=1 after follow; HOST still soft |
| DESTROYER_SMOLDER vs binom | **partial** | workspace `version` without killing kizu gold | **gold inverted** — `53cbd1a` is now “homonym, not this package” |
| DESTROYER_FORD vs hydra | **partial** | 1-of-3 ≠ 2-of-3; recursive occupancy | no — arity displayed; `now=` still the folded meet |
| DESTROYER_BRAID vs tilde | **partial** | NFC line images + covering of the nits | no — café PENDING; three-round STACK still SPLIT |
| DESTROYER_PEAL vs seed | **closed** | first locator is not the seed | no — bag refuses; gold `let b_side` still three spans |
| DESTROYER_MAIDEN vs badge | **partial** | never-red is not a string id / `<flakyFailure>` | no — flaky is red + rename unifies; go/bun/nextest still empty |

**2 closed, 13 partial, 0 still-open as a pair.** No pair left the DESTROYER object extinct. Two pairs actually killed the *named* next-mutation lie. One pair (binom) closed a workspace hole by throwing away DESTROYER gold. One pair (stile/solder) is two tools: only stile is a hole-closer.

Coordinator harvest said “Gen3; all Keep.” Keep is not closed.

---

## 1. DESTROYER_SCARP vs lurch — partial

**Gold that must survive** ([DESTROYER_SCARP.md](DESTROYER_SCARP.md) What survived): `{cut; sleep 0.35; cut} | scarp` is DILATE without spawn. `fixtures/slew.txt` is SLEEP, not STEP. Folklore `wall + python.monotonic` since boot is SLEEP, not a 29-hour NTP step. Two unlabeled timestamps are REST.

**Named lie:** `classify_text` parses every cut then uses `cuts[0], cuts[1]`. Three JSONL cuts that dilate then sleep print only DILATE. Unlabeled numbers are a duration bag or the first eight fields. Missing proper lets 22 days of awake beat 1 day of lid-close. `ntp=` is adjtime (`CLOCK_MONOTONIC − RAW`), not NTP.

**What lurch did:** adjacent pairs. Independent:

```
$ ./lurch < fixtures/stream-dilate-then-sleep.jsonl
DILATE  1000→1002  sleep=0s     ntp=0s
SLEEP   1002→1012  sleep=9.000s ntp=0s
```

Unlabeled `1000 1001 1005 1010` → three REST (scarp: STEP duration bag). `slew-noproper.txt` → SLEEP `1d00h00m` (scarp: DILATE of 22d awake). `wait61.txt` → DILATE (scarp: REST `kind=host`).

**Still open (DESTROYER mutate-toward, not parked):** `ntp=` is still the field name for −7.5s adjtime. Suggested mutation “Name Darwin CLOCK_MONOTONIC vs RAW as SLEW, not `ntp=`” was not taken — DESTROYER warned a one-line `ntp`→`slew` rename would hide Darwin leftover without touching the two-cut window. lurch kept the name and closed the window. Repeated `key=value` still splits. ISO-8601 still scavenges REST ticks.

Not paper. The load-bearing window hole is gone. The load-bearing *name* hole is not.

---

## 2. DESTROYER_BERTH vs holt — partial

**Gold:** kizu `--full` R100 `deep-research-ai-agent-hooks.md → docs/…` is one roost `true=187` from either name. C056 leftover blob is not a follow. sitbone first-parent FocusRiverView hints `--full`; `--full` is the 11-commit island. skills `preact-zero-mock` is README-only ghost. Copy stays copy.

**Named lie:** “query the old name or the new name; occupancy stays TRUE” is false on the default first-parent walk. `follow_names` seeds from first existence of the query path, so a leftover at `old.txt` occupies the twin. `--now exists DEST` of uncommitted `git mv` is never-held.

**What holt did:** identity from all-reachable R; occupancy default is every reachable commit (`--first-parent` opt-in); seed from the occupant at the walk tip.

Independent, live kizu:

- `exists docs/deep-research-ai-agent-hooks.md` and `exists deep-research-ai-agent-hooks.md` → same identity, `true=187/244`.
- `--first-parent exists` on the **dead** name → dest roost `true=21/24`, origin `321a830 as deep-research-ai-agent-hooks.md`. berth’s default dead-name was never-held + hint `--full`.

**Still open:** occupancy eras are still `git log --reverse`, not the merge lattice (DESTROYER: “`--full` must not invent FALSE gaps”). NFC/NFD. `git mv` + rewrite below similarity is still D+A. Same-commit name swap is still M/M.

Not paper. The identity walk DESTROYER named as the next mutation (rove’s all-reachable R for `exists` + tip-occupant seed) landed. The occupancy lattice did not.

---

## 3. DESTROYER_LIEN vs noun — partial

**Gold:** `t1 = 15` → `driftDelay = 15` still `via=both` on `T1 is 15 seconds`. sitbone `e9b0f75`: 12 current liens, 4 `via=both`, CLAUDE.md:329/332, no `v0.4`. FILE:LINE stays refused.

**Named lie** (§6, load-bearing): `merge_natals` on `ident_parts("version")`. cli+core collapse. kizu `9349dc5` crate `0.6.0→0.7.0` is **silent rc=0** while `plugin.json` still says `0.3.0` because bound `0.3.0 ≠ 0.6.0` was `is_homonym`. Mutate toward: “`version` is per package, not one noun.” “Release bump vs sibling manifests.”

**What noun did:** natal identity `(package, noun)`. Independent:

- self-test: `cli+core version bumps are two nouns`; `plugin.json 0.3.0 is leftover of kizu cargo bump (not a homonym)`.
- live: `git diff 9349dc5^ 9349dc5 | noun -C kizu` → `plugin/plugin.json:4: claim: crate:kizu VERSION  0.6.0 → 0.7.0`.
- sitbone `e9b0f75` still CLAUDE.md:329/332 `via=both`.

They kept `crate:kizu` / `plugin:kizu` as **one product noun** so the release CI fails. That is DESTROYER’s intended gate, not leftover-name of the word `version`. cli vs core is the other direction.

**Still open:** path natal (`git mv t1.py`). CJK ident. Size-cap omit silent. Wrong `-C` fail-open. Add-heavy rewrites mint 0 natals (`04adde1` / `c1d9da9`).

Not paper. The §6 CI hole is closed. The rest of DESTROYER_LIEN is still the ancestor.

---

## 4. DESTROYER_TACIT vs preen — partial

**Gold:** sitbone `presentThreshold` **27 TACIT, 0 SHADOW**. `e9b0f75` BLAST 54, `--check` rc=1. `makeDefault` SHADOW `colorHue 0.45`.

**Named next mutation:** unfold the **constructed** default, not `Foo`’s init signature. `PinProfile(..., thresholds: Thresholds(driftDelay: 20))` omitted is OVERRIDE 20, not TACIT 15. Clap TACIT is an invocation that omitted `--flag`, not a command-shaped line. kizu TACIT=6 (comments / `contains`) should become 0.

**What preen did:** Independent self-test: `PinProfile constructed Thresholds(driftDelay: 20) is OVERRIDE 20` / `is not TACIT 15 of the type signature`. Nested `Thresholds(driftDelay: 15)` is SHADOW. Clap `contains`/prose kebab is not TACIT; shebang `{} hook-post-tool --agent cline` is OVERRIDE. Live sitbone `--summary presentThreshold` still **27 TACIT**.

**Still open (parked in Failures, DESTROYER named):** `*args` still steal positionals. TS `name = value` still a keyword. Unlabeled first `paint("red")` still drops the call. tenaoshi wrapper `func reopenUnit(id: String)` still TACIT. Pairing still by index.

Not paper. The two DESTROYER “next mutation” items landed. The rest of omission is still tacit’s holes.

---

## 5. DESTROYER_BECK vs innard — partial

**Gold:** `git -C /tmp status | cat` is MINT stage 0 **stderr**, `piped_bytes=0`, tee MISS. sed prefix wrap disagrees with tee. Trailing `2>&1` / `|&` keep origin fd stderr. kizu `git log | rg | head` mints at git.

**Named lie:** `$()` is one outer stage (`echo $(printf kizu | tr k K)` mints at echo). Mid-command `2>&1` is stdout because only a trailing token is peeled.

**What innard did:** Independent:

```
$ innard --needle 'Kizu' --sh 'echo $(printf kizu | tr k K) | cat'
INNARD  WRAP  stage 0.1  stdout  tr k K    # inner, not echo wrap
$ innard --needle 'fatal: …' --sh 'git -C /tmp 2>&1 status | cat'
INNARD  MINT  stage 0  stderr  git -C /tmp status
$ innard --needle 'fatal: …' --sh 'git -C /tmp status | cat'
INNARD  MINT  stage 0  stderr   tee MISS
```

v0.2: `$()` stderr leak is `leak`, not remint (command substitution does not capture stderr). Gold unpiped git holds.

**Still open:** greedy JSON coincidence `kizu@0.7.0` vs `notify-debouncer-full@0.7.0` (facet’s hole, DESTROYER’s first mutate-toward). `printf hi | echo hi` still occupancy-carry. `--run +` still `" ".join`. `{ }` walks as parser honesty, not the product.

Not paper. Inner first-producer is a real descent, not a `{`/`}` depth counter.

---

## 6. DESTROYER_XREF vs shim — partial

**Gold:** direct `getenv("DIRECT_ENV_NAME")` is DUE. Orphan cstrings are not. Homebrew `PYTHON_GIL` DUE / `PYTHONHOME` LATENT. Sysroot rustc tens of names, not 12,596 LLVM opcodes. `/bin/ls` is `CLICOLOR_FORCE`, not `COLOR_FORCE`.

**Named lie:** DUE is `endswith("getenv")`. `not_a_getenv("FALSE_DUE_NAME")` is DUE. `/usr/bin/python3` and PATH `rustc` print the same `(no owed names)` as `int main(){return 0;}`. Mutate toward: allowlist libc `getenv` / rust `__var`; shims are a role.

**What shim did:** Independent:

```
$ cc -O0 -fno-inline -o /tmp/judge-false fixtures/shim/false.c
$ ./shim --app /tmp/judge-false
DUE  REAL_GETENV_NAME  call  getenv     # FALSE_DUE_NAME absent
$ ./shim --app /tmp/judge-empty
(no owed names)
$ ./shim --no-follow --app /usr/bin/python3
shim  xcselect  /usr/bin/python3
```

self-test: `suffix not_a_getenv is not getenv`; `no-follow trampoline not harvested`.

**Still open:** one-hop wrappers (lash) — Homebrew 3.14 `PYTHONHOME` still LATENT. Inlined Rust `env::var` (wad). `kind_of` has no neither. Fat slices, `blr`/GOT, false LATENT `STACK_SIZE`. One hop only; pyenv scripts are not this object.

Not paper. The two DESTROYER sentences that defined the pair (`*getenv` is not getenv; trampoline is not empty) are gone. The rest of DUE-as-proof is still xref.

---

## 7. DESTROYER_WELD vs stile / solder — partial (split)

**Gold:** `response() + "\nDone."` is `{response}\nDone.` on concat.js and tenaoshi :318. Full fence keeps `\n`. 4-hole wrap. 3-hole middle-drop still misses. rustc `-->` refused. Directories exit 2.

**Named lie:** `{body}abcd` matches every log line ending `abcd` (4-char floor). Incomplete fence leftover `"```json\n{"ok":true}"` truncated-succeeds. Unclosed `"```json\n" + response()` stuffs the closer into the hole. Mutate toward: proving string must be **distinctive**; truncation is a prefix of an instance, not leftover-into-the-last-hole. Do not lower `visible < 4` so `{cleaned}\n` matches every log line. Do not grow a walker.

### stile — hole closer

Independent, same fixtures:

```
$ ./stile --templates thin.go 'ERROR worker crashed abcd'
— no template     # rc=1     weld/solder: hit
$ ./stile --templates concat.swift $'```json\n{"ok":true}'
— no template     # rc=1
$ ./stile --templates concat.js $'{"ok":true}\nDone.'
{response} = {"ok":true}
```

`cleaned + "\n"` stays a miss (newline-only is not distinctive). That is DESTROYER’s instruction, not a raise of 4 to 6.

**Still open on stile:** `{a}:{b}` still matches URLs (assignment exception for ≥2 holes). `{path}: {err}` as suffix of a longer splice still hits when the longer template is not in this stream. Sprint spaces, `Join`/`push_str`, `MAX_FILE_BYTES` silent omit.

### solder — reimpl, not a closer

Clean-room of **weld’s primitive** (expr-first concat from a proving string). Independent: `\nDone.` binds. **thin.go still hits** `{body}abcd` rc=0. **Incomplete fence still truncated-succeeds** (`truncated: \n````). DESTROYER_WELD holes are the ancestor, rebuilt.

Do not treat solder as closing DESTROYER_WELD. It proves the primitive survives a rewrite. stile is the mutation.

---

## 8. DESTROYER_KEEL vs shoal — closed

**Gold:** kizu `src/app.rs:529@b4e6a5d → src/app/layout.rs:17` on a full clone and on `file:// --depth 1`. Foreign git root rc=1. `--to-dir` of a subdirectory still inside that foreign `.git` inherit-refuses. Orphan extra root is not a different repository.

**Named lie (lethal):** `keels_match` is remotes ∩ **or** 16-char tip ∩ **or** `object_exists(dest, pin.witness)`. `git remote add extra git@github.com:victim.git` lands. Fetch one witness SHA lands. `origins_match`: if either side has no origin, return True. Missing `o` is a silent global locator. Mutate toward: **origin that cannot be typed into `git remote add`**, plus missing-`o` fail-closed. A one-line “refuse dest remotes superset” would hide extra-remote and not touch fetch/alternates.

**What shoal did:** remotes signed at mint; dest extras not walked, not stored, not printed by `shoal id`. Fetch of a pin witness is occupancy, not identity. Missing origin / unsigned v1–v3 `o` / gitless `--to-dir` fail-closes unless `--any-repo`. `--selftest` ok after those cases (remote-add, fetch SHA, set-url, file:// depth-1, remotes-less hop, orphan `--to` original, missing `o`, kizu land + kizu steal). v0.2: FOLLOW_HOPS=16 with cycle detection (3-hop file:// of mint-at-V1 lands); `www.github.com` / `ssh.github.com` fold to `github.com`; gitlab same-path still refuses.

They did not paper with `--any-repo`. DESTROYER said `--any-repo` would also land a helper on an unrelated repo at 1.000.

**Residual (different verb, not the named hole):** `--any-repo` is still both the fork verb and the stranger verb. Mint-at-V1 + GHA later tip (hop gone, dest HEAD not a stored witness) still fail-closes — remotes ∩ without lineage would re-open `git remote set-url`. `Host gh` SSH aliases unread. Path `git clone --depth 1 $REPO` is still a silent full copy.

The lethal conceptual hole is gone. Fork identity is a leftover DESTROYER named as a separate mutation.

---

## 9. DESTROYER_GIST vs rune — partial

**Gold:** kizu `range.start.line` **528 → 16**, not 17. `character` 4 kept. fission `layout.rs` + `navigation.rs`. SARIF `startLine` 529 stays 529. sitbone `44 → 74`, **no** extra empty. voidtrace `evaluate.ts` line 0 identity, `cli.ts` does not appear. Dest-owned `Content-Length`. `data` keep.

**Named next mutation:** dest-own `character` as UTF-16 (not Python `len()`). Origin-clear: when every bound locator leaves a uri, emit `diagnostics: []` for the origin. Same-file shift and confirmed deletion must not grow an extra empty. Gutter carry is not `old+k` across a split.

**What rune did:** Independent `./demo.sh` all passed:

- kizu LSP copies: `app.rs#528 → layout.rs#16` **and** third notification `uri …/src/app.rs  diagnostics: []`.
- SARIF 529 stays 529.
- sitbone `44 → 74`.
- voidtrace identity at line 0.
- demo.sh asserts UTF-16 clamp (17, not codepoints 16, not source 22) and remap (insert 😀 moves column 15 → 18, clamp-only would keep 15 inside the surrogate).

**Still open:** rustc multi-hunk one-`-->` still follows the first locator’s offset inside `message` (CANDIDATE Failures). `}`-only still unresolved. Mixed dest uris. SARIF keys sitting on an LSP object. Pretty `{` after commentary.

Not paper. The two blot peels DESTROYER named as gist’s next mutation landed next to `528 → 16`. Gutter carry is still gist.

---

## 10. DESTROYER_VOW vs proxy — partial

**Gold:** pytest `EXPECTED-BOUND vs ACTUAL-BOUND` alice vs runner. XCTest `EXPECTED-OPEN vs ACTUAL-BOUND` `/tmp` vs Alice (actual-first). Own-line `# ran on` silent. sitbone 0 BOUND / 4 FIXTURE. kizu John Doe comments silent; quoting asserts SPEC.

**Named lie:** `expected = home; assert got == expected` emits **two** inverted pairs (pytest PM takes left as expected, plus E +/-). rustc `left:` treated as expected. Mutate toward: one pair per assertion; follow `expected = home`; rustc `left:` is actual.

**What proxy did:** Independent:

```
$ ./proxy --from-fail < name_follow_fail_diff.txt
proxy  pair  pytest  EXPECTED-BOUND vs ACTUAL-OPEN   # n=1
$ ./proxy --from-fail < name_follow_fail_src.txt
proxy  pair  pytest-src  …  proxy os.environ['HOME']→/Users/annenpolka   # n=1
```

vow on the src dump was n=2 with no top-level pair. Gold XCTest/pytest self-tests still pass. Own-line `# ran on` still silent.

**Still open:** HOST is still soft (`self-test: HOST getenv is not a hard visa` / `OPEN + soft`). Same-line `# ran on` on the assert is still an oath (not this mutation). Swift Testing dumps still unary-expected. Wrap-across-newline XCTest still one-line. `--apply` from host role is troth, not proxy.

Not paper. The dump-as-two-pairs lie is gone. HOST-as-oath is still occupancy of nothing.

---

## 11. DESTROYER_SMOLDER vs binom — partial (gold inverted)

**Gold that DESTROYER said is the product:** kizu `plugin/plugin.json:4` → **`53cbd1a` Cargo.toml `0.3.0 → 0.3.1`**, not `git blame` `bff820fb`, not Cargo.lock. “That is still the why-doesn’t-this-exist moment.” sitbone `CLAUDE.md:329` → `e9b0f75` `0.4 → 0.45`. Named lockfile dest regenerate.

**Named workspace hole** (§4): `pkg_a` 0.3.0→0.7.0 falsifies `pkg_b` leftover of 0.3.0. Mutate toward, quoted:

> **Workspace identity.** `pkg_a` 0.3.0→0.7.0 does not falsify `pkg_b` 0.3.0. **Gold kizu plugin.json is one product, not two packages.**

**What binom did:** leftover identity `(crate/package, noun, dest)`. Independent:

```
$ ./binom -C kizu plugin/plugin.json:4
binom: none  plugin/plugin.json:4  package plugin:kizu
  homonym cargo:kizu version 0.3.0 → 0.3.1   Cargo.toml:3   53cbd1a055f5 is not this package
# rc=1
$ ./binom -C sitbone CLAUDE.md:329
binom: leftover  CLAUDE.md:329
FALSIFIED e9b0f75 … threshold: 0.4 → 0.45
```

self-test: `pkg_a bump does not falsify pkg_b`; `plugin.json dest is not leftover of Cargo.toml homonym version`.

**The inversion:** DESTROYER said kizu plugin.json **is** the workspace story *without* identity, and that invert is the intended win — one product. binom treated plugin vs cargo as two packages and returned **none**. CANDIDATE: “Gold kizu plugin.json is no longer Cargo.toml — that was the hole, not the product.” That sentence argues with gold.

lien-lineage **noun** did the opposite: `crate:kizu` / `plugin:kizu` stay one product so `9349dc5` fails CI. smolder-lineage **binom** splits them so `53cbd1a` is not the falsifier. Same kizu tree, opposite product identity. That is a load-bearing split, not two peels of one object.

pkg_a/pkg_b is closed. kizu gold is inverted. dest:84 leftover-name, dest-rename R, Japanese bindings, size-cap `missing`, ash-as-table: still open.

This is the night’s clearest conceptual paper: they closed the fixture by throwing away the dogfood gold DESTROYER ordered them to keep.

---

## 12. DESTROYER_FORD vs hydra — partial

**Gold:** kizu `CLAUDE.md` at `0ea3916` is `FALSE ⊓ TRUE`, origin `e1098c8`, not a boolean birth. `--any` is a TRUE ford, not a 23-commit birth. sitbone FocusRiverView first-parent never-held; `--full` island **11**. Timeout `⊓ UNKNOWN` is UNKNOWN rc=3. Depth-1 is SHALLOW.

**Named lie:** octopus 1-of-3 and 2-of-3 are the same meet (`FALSE` as soon as any parent is FALSE), same `--any` join, same exit, same `never_held`. Origin is the first TRUE parent. Join inputs are parent **trees**, so kizu `21ae074` is `T⊓T` preserve (weir already peeled recursive occupancy). Mutate toward: 1-of-3 and 2-of-3 are different introductions; display k-of-n; recursive occupancy at merge-of-merges.

**What hydra did:** Independent live kizu `exists CLAUDE.md`:

```
FALSE  0ea3916   hydra  1-of-2  FALSE ⊓ TRUE
FALSE  21ae074   hydra  1-of-2  FALSE ⊓ TRUE   # recursive; ford would fold trees
FALSE  ca0577a..ad6de10  inherited 1-of-2
TRUE   d9b9645..9349dc5  17 commits  continue after hydra 21ae074
```

sitbone `--full exists FocusRiverView.swift` → TRUE **11** commits `14b1d6e..1fefafb`. demo.sh asserts octopus `held=1-of-3` ≠ `held=2-of-3`, and **both** `now=FALSE`.

**Still open:** `now=` is still the folded meet. DESTROYER’s occupancy flag does not distinguish 1-of-3 from 2-of-3; only `held=` does. `never_held` at a merge HEAD whose tree has the file is still occupancy-never ≠ path-never. Rename is still path death. `--boolean` is still a labelled lie.

Not paper. Arity is a crossing identity (v1 putting k-of-n on preserve merges re-split the 17-commit continue — they backed that out). The boolean that CI would read is still the fold.

---

## 13. DESTROYER_BRAID vs tilde — partial

**Gold:** stack-mid is SUPERSEDED of `beta→beta3`; plea is APPLIED+PENDING of the rounds. Demo case 6. JAM rc=2 `occupy=—`. Inverted-clock fold is still `beta3`. Empty-before disjoint markdown is PARALLEL, not DESTROYER_PLAIT’s SPLIT.

**Named lie:** path keys collapse NFC/NFD while **line images stay raw** — `café` vs `café` SUPERSEDES a still-open nit. Covering paints unclaimed gaps from HEAD so a one-line pad mints chimera `alpha|alpha|gamma`. `--ignore-space` applies to pair_verdict, not occupy. Three-round STACK is SPLIT (non-adjacent same-span afters). Mutate toward: NFC-normalize **line** images; covering occupancy is of the nits; occupy honors `--ignore-space`.

**What tilde did:** Independent:

- NFC claim vs NFD tree: `occupy=PENDING method=exact-before` (not SUPERSEDED).
- stack-mid: `compose=SERIES occupy=SUPERSEDED` of `beta→beta3`.
- selftest: `nfc-line-image`, `covering-is-nits-not-live-gap`, `occupy-honors-ignore-space`. JAM still refuses.

**Still open:** three-round `v1→v4` still SPLIT (CANDIDATE Failures; DESTROYER’s first mutate-toward). SERIES covering stays the 1-line fold; `stack-both` PENDING still hides live `beta2`. `--remarks` CONNECTING can still COVER-label.

Not paper. A one-line NFC on `before`/`after` would have hidden café and left the chimera — DESTROYER said so, and they did not do only that. They still did not occupy the series fold when N>2.

---

## 14. DESTROYER_PEAL vs seed — closed

**Gold:** `cd kizu && rg -n 'let b_side' src/git/parse.rs | peal --explain` is the same three spans as `chime parse.rs:60`, including `Some(bytes_to_path(a_side))` which rg never printed. `--hits --same-as :60` is chime’s filter (`:62` only). No cwd walk.

**Named lie (three sentences, one object):** first locator is the seed. `rg 'return None;'` chimed quoted-form `:34`, not the unquoted survivor. Uniqueness is substring `in`. `pins[:16]` throws away the 17th pin that distinguishes twins. Mutate toward: refuse a bag of `cond_keys`; pin match is the stripped line; do not cap pins at 16.

**What seed did:** Independent live kizu:

```
$ rg -n 'let b_side' src/git/parse.rs | seed --explain
seed    parse.rs:60
deeper  :61-62  return None
deeper  :64     Some(bytes_to_path(a_side))     # gold three spans

$ rg -n 'return None;' src/git/parse.rs | seed --explain
seed: locators name 9 stacks; pass --same-as FILE:LINE or :LINE or --first
  :34  quoted-form
  :62  unquoted gold arm
  …
# rc=2   first locator is not the seed
```

`--same-as :60` binds to the recovered file (v0.2). `--first` still chimed `:33-34` as peal’s default, **opt-in**. Substring decoy does not recover. 16 shared pins refuse; 17th `UNIQUE_REAL` recovers.

**Residual (not the named lie):** `rg -nH` basename from a nested cwd still joins to git toplevel. `--column` is still LINE:COL:text. Binary stdin traceback still rc=1 not 2. Inherited chime engine holes (`if let` dropping `let`).

The advertised pipe for a pattern that hits more than one arm no longer silently seeds the first. That was DESTROYER_PEAL’s load-bearing object. Closed.

---

## 15. DESTROYER_MAIDEN vs badge — partial

**Gold:** 2019-fail + 2024-green → `pkg.T::alpha` **SCARRED**, `--skeptic`; `--latest` maidens it. SKIP-only is not maiden. sitbone `swift test list` **213 UNKNOWN**. kizu cargo `--list` **489 UNKNOWN**. Empty/garbage/markdown: honest zero.

**Named lie:** never-red is **parser × string id**. Surefire `<flakyFailure>` maidened a test the file said had failed. `pkg.T::compute_diff` → `pkg.T::compute_operation_diff` is a new maiden column. go/bun/nextest logs parse to `{}` — a later cargo `... ok` of the same string launders the fail. `--latest --skeptic` composes the anti-`rg` into `rg`. Mutate toward: junit outcome is the recorded status (`<flakyFailure>`, `<rerunFailure>`, `status="failed"`); identity is still the runner specifier but `--skeptic`/`why` should name the scar beside a rename; unrecognized dialect fail-closed when the user thought they ingested a run.

**What badge did:** Independent:

- flaky-then-green.xml → **SCARRED** `pkg.T::alpha` (maiden: MAIDEN).
- 2019+2024 → alpha SCARRED, beta/delta MAIDEN, gamma SKIPPED.
- `--latest --skeptic` → `badge: --skeptic cannot compose with --latest (that is rg PASS)` **rc=2**.
- self-test: rename `compute_diff`+`compute_operation_diff` is one SCARRED identity, SKEPTIC 1; gold 4-id fold does not collapse; sitbone roster 213 UNKNOWN.

**Still open (DESTROYER §8, load-bearing):** live DESTROYER fixtures:

```
$ badge --no-ledger --json /tmp/destroy-maiden/fixtures/ci/go-fail.txt
{"version":"0.2","summary":{},"tests":[]}    # rc=0
```

Same empty for bun-fail and nextest-fail. Occupancy of nothing. A later cargo-looking pass of `TestAlpha` can still maiden a go fail. Class+method both changing still splits. `alpha` → `alpha_v2` does not join. xcresult missing bundle still empty.

Not paper on flaky/rename/`--latest --skeptic`. The dialect-refuse DESTROYER named as occupancy of nothing is still the default.

---

## Cross-cuts

### noun vs binom — one kizu, two products

DESTROYER_LIEN wanted plugin leftover of a crate bump to **fail CI**. noun: `crate:kizu`/`plugin:kizu` = one product → `9349dc5` rc=1 on `plugin.json:4`.

DESTROYER_SMOLDER wanted plugin leftover of a crate bump to **name `53cbd1a`**. mutate-toward: “Gold kizu plugin.json is one product, not two packages.” binom: two packages → none + homonym print.

Gen3 did not reconcile this. A release CI job and an invert of the same leftover now disagree about whether the Claude plugin is the crate.

### stile vs solder — mutation vs reimpl

The pair is “WELD vs stile/solder.” Only stile closed DESTROYER_WELD’s 4-char floor and incomplete-fence leftover. solder rebuilt weld, including `{body}abcd` and truncated fence. Clean-room survival of expr-first concat is a primitive-strength result, not a hole close.

### Display vs occupancy flag

hydra’s `held=1-of-3` ≠ `held=2-of-3` while `now=` is FALSE for both. DESTROYER’s occupancy object is the flag CI would branch on. A sticker is not the lattice.

### First locator / first pair / first existence

scarp `cuts[0], cuts[1]`, peal first locator, berth first-existence seed: three “the stream had N, we classified 1” lies. lurch, seed, holt each flipped that shape. That is the night’s real Gen3 pattern, not Keep counts.

---

## What would still be a one-line hide (DESTROYER’s test)

DESTROYER said: if a one-line patch would hide the transcript without touching the object, do not apply it in the destroyer pass — leave it for the mutation.

| pair | one-line hide DESTROYER refused | did Gen3 do that? |
| --- | --- | --- |
| scarp | rename `ntp`→`slew` | no — kept `ntp=`, closed the window |
| berth | point first-parent never-held at dest | no — all-reachable R + tip seed |
| lien | fail every docs hit of `version` | no — default check is one dest-line |
| tacit | skip `#` in `split_top` | no — constructed unfold + clap invocations |
| beck | `{`/`}` depth counter | no — `$()` descent |
| xref | — | allowlist + shim role, not a suffix invert |
| weld | raise `visible < 4` to 6; print skipped huge file | stile: distinctive, not a higher floor |
| keel | refuse dest remotes superset; drop `object_exists` only | shoal: signed remotes + required witnesses |
| gist | — | UTF-16 dest-own + origin-clear, not a clamp-to-`len()` |
| vow | comment-mask inside Python assert slice | no — name follow |
| smolder | consult `SKIP_DIRS` | no — but they inverted kizu gold instead |
| ford | refuse `--boolean` unless T/F | no — k-of-n on crossings |
| braid | NFC on `before`/`after` only | no — nits covering + NFC lines |
| peal | stdin decode-or-die | no — bag refuse |
| maiden | `status=` attribute reader | no — but go/bun/nextest still empty |

Gen3 mostly did not take the one-line hide. The exception is binom: they took the workspace fixture and refused DESTROYER’s “one product” instruction on kizu.

---

## Carry / do not carry

**Carry as closed enough to stop spending DESTROYER slots on that sentence:** shoal (origin-as-config), seed (ambiguous-seed refuse).

**Carry as partial — next mutation is still the DESTROYER sentence, not polish:**

- lurch: name SLEW, not `ntp=`
- holt: occupancy on the merge lattice
- noun: path natal + omit-visible; do not fight binom by accident
- preen: `*args` / unlabeled first / wrap signature
- innard: field-cover handoff to facet; remint vs occupancy
- shim: wrappers on the *payload*; `kind_of` neither
- stile: `{a}:{b}` URL; ranking of suffix splices. solder is not this mutation
- rune: gutter re-fingerprint; `}` neighbor
- proxy: HOST hard or not an oath; same-line comments
- binom: **restore kizu gold as one product** or rewrite DESTROYER_SMOLDER — do not ship both
- hydra: `now=` is k-of-n, or refuse to call 2-of-3 `never_held`
- tilde: transitive STACK N>2
- badge: unrecognized dialect fail-closed (go/bun/nextest)

**Do not:** grow a fourth cinch, a third ambit, a leftover-name search, a second inverse-printf walker, or a test-intel platform. DESTROYER already named those as the kill.

---

## Evidence of run (this jury)

Commands in Method, executed 2026-08-20 on this Darwin host against live kizu/sitbone and DESTROYER fixtures under `/tmp/destroy-maiden/`. Tools from Gen3 worktrees `01a01c27-4df0-7683-956b-a7bef4531e96` … `a8a24a7d1c61`. Not UNVERIFIED.

Judge: **judge-12**. File: `lab/judges/FINAL_GEN3.md`. Isolated worktree. Do not merge.
