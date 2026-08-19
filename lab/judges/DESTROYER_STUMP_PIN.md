# DESTROYER — stump × pin

Adversarial pass on the hardened invert/pin mutations. No rewrites: the failures are conceptual, not one-line bugs.

- **stump** (hardened invert, v0.2) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01afa-49e6-7b70-a5b5-bd59389b559b`
- **pin** (hardened pin, v0.3) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01afa-49e6-7b70-a5b5-bd46235631d2`
- Transcripts: `/tmp/destroy-stump-pin/transcript.txt`, `/tmp/destroy-stump-pin/transcript2.txt`
- Fixtures: `/tmp/destroy-stump-pin/`
- `stump --selftest` → `selftest: ok`. `pin selftest` → `selftest: ok`.
- `stump` `./demo.sh` → `passed=59 failed=0` (destroyer regressions included).
- `pin` `./demo.sh` → all checks passed, including leftover-stub / ambiguous / 1.2MB / NFD / missing `--to` / truncated token / foreign repo / kizu / voidtrace / tenaoshi.

Verdict: **mutate, do not kill.** The previous DESTROYER_PIN_INVERT list is actually closed. The new holes are where each mutation overcorrected, or where the refuse-rule is narrower than the pitch.

---

## Previous DESTROYER bugs — verified fixed

Re-ran the old attacks against the new binaries (demo.sh + `/tmp/destroy-stump-pin/attack.sh`).

### stump (was invert)

| old bug | now |
| --- | --- |
| abridged 7-hole paste miss | `transition focused → idle reason=timeout idle=12s` → `holes=7 via=truncated` `{from}=focused` `{idle}=12` `truncated: deserted={0}…` rc=0 |
| `user 42 not` miss | `{uid}=42` `truncated: found` rc=0 |
| truncated spawn miss | `{cmd}=git ap` `prefix: 2026-08-19T23:50:01Z ERROR` rc=0 |
| `--> src/git/revert.rs:46:18` bound `src/{i}.rs` | `— rustc locator, not a template query` (no `{i}=`) |
| no-hole decoy outranked holed spawn | full spawn paste hits `failed to spawn `{cmd}`` score=0.48; decoy absent from ranking |
| `--any` printed 98 MB | 3000 identical lines → 1 hit, 312 bytes; producer that sleeps 6s inverted in 0.04s |
| binary stdin `UnicodeDecodeError` | `stump: binary stdin: NUL byte` / `not UTF-8`, demo rc=2, no traceback |

Concat (`"open " + path`) is still not a template. That was already a sibling mutation, not a claimed fix.

### pin

| old bug | now (demo.sh) |
| --- | --- |
| leftover stub `shifted 1.000` on `src/calc.py` | `moved … src/calc/ops.py:5 0.998` `skipped leftover stub src/calc.py:1; basename bait src/legacy/calc.py:1` |
| identical helpers `moved z/calc.py 1.000` | `ambiguous … a/ops.py:1,z/calc.py:1 0.946`; `--strict` fails |
| 1.2 MB godfile omitted | minted + `same src/godfile.py:1 1.000` |
| NFD `cafe\u0301.py` not in snapshot | NFD mint → NFC `src/café.py:1` |
| `--to this-ref-does-not-exist` → `deleted` rc=0 | rc=2 `pin: unknown ref:` stdout empty |
| truncated `pin1.…` porcelain `unresolved` rc=0 | rc=1 `corrupt pin: Error -5…` stdout empty |
| foreign helper `moved 1.000` | rc=1 `pin belongs to a different repository (git:… vs git:…)`; `--any-repo` still 1.000 (the override) |

kizu `src/app.rs:529@b4e6a5d` still lands `src/app/layout.rs:17` with no path:line on resolve. Unique pins still do not hallucinate onto voidtrace/tenaoshi.

---

## stump

Primitive restated: inverse printf as a **filter that binds names**, including when the runtime string is a **prefix of an instance**. rustc locators refused. `--any` stops. Binary fails closed. A no-hole prefix of the paste cannot beat a holed source.

The kernel is still leftmost `query.find(literal)` plus “if the next literal is missing, the rest of the query is the last hole / a truncated prefix.” That is not the same object as “prefix of an instance.”

### 1. Truncation stuffs a non-prefix tail into the last hole (conceptual, lethal to the pitch)

The pitch is syslog/terminal/human **prefix** truncation. Alignment does not require the query to be a prefix. It requires the static literals that *are* present to appear in order; everything between them is a hole.

Middle-drop paste (start + end, no middle):

```
$ rg -n -g '*.swift' awayRecovered fixtures | ./stump --templates - \
    'transition focused → idle awayRecovered=0'
fixtures/src/log.swift:20:27: score=0.73 holes=7 via=truncated
  tmpl:  transition {from} → {to} reason={reason} idle={idle}s deserted={0} …
  {from} = focused
  {to} = idle awayRecovered=0
  truncated:  reason={reason} idle={idle}s deserted={0} driftRecovered={0} awayRecovered={0}
```

`awayRecovered=0` is not a prefix remainder. It is a later fragment swallowed by `{to}` because ` → ` matched and ` reason=` did not. The tool reports a 7-hole truncated success. A human who copied the start and the end of a log line gets a **wrong binding**, not a miss.

Newline wrap (terminal wrap inside the instance) does the same to `{reason}`:

```
query: transition focused → idle reason=timeout
idle=12s deserted=0 driftRecovered=0 awayRecovered=0
  {reason} = timeout
idle=12s deserted=0 driftRecovered=0 awayRecovered=0
  truncated:  idle={idle}s deserted={0} …
```

The wrapped tail is not unmatched; it is bound. `--exact` would refuse both, and also refuses ordinary log prefixes (see §5). There is no “prefix-of-instance only” mode.

Suffix-only (`fatal: not a git repository` vs `git diff single file failed: {1}`) still misses. CANDIDATE already listed that. The new lie is the opposite: **non-prefix queries still hit, with names.**

### 2. Prefix of the first literal is a confident hit with no bindings (conceptual)

`MIN_STATIC_PREFIX = 10`. A paste that is only the leading static of a holed template now scores like a truncated instance:

```
$ ./stump --templates fixtures/src/user.py 'cannot reach'
user.py:6:27: score=0.86 lang=py holes=2 via=truncated
  tmpl:  cannot reach {host}:{port} after 3 retries
  truncated:  {host}:{port} after 3 retries
  # no {host} / {port} bindings

$ ./stump --templates fixtures/src/prefix.rs 'failed to spawn'
prefix.rs:7:13: score=0.87 lang=rust holes=1 via=truncated
  tmpl:  failed to spawn `{cmd}`
  truncated:  `{cmd}`
```

`holes=2` / `holes=1` in the header is the template’s hole count, not bindings produced. Score 0.86 is above the 7-hole abridged sitbone line’s neighborhood and well above `--min-score 0.34`. Truncation was added so `idle=12s` still binds `{idle}`; it also made **any 10-character prefix of a log template a hit.**

Slightly longer is worse, not better: `cannot reach db` binds `{host}=db` and claims truncated at `:{port}`. A hostname fragment is enough.

### 3. Exact match of the documentation decoy still beats the holed source (conceptual)

v0.2 closed “no-hole template that is a *prefix of the query*.” It did not close “query that is the decoy, or a prefix of the decoy.”

```
$ ./stump --templates fixtures/src/prefix.rs \
    '2026-08-19T23:50:01Z ERROR failed to spawn'
prefix.rs:3:21: score=1.00 holes=0 via=full
  tmpl:  2026-08-19T23:50:01Z ERROR failed to spawn
  # decoy. holed `{cmd}` does not appear

$ ./stump --templates fixtures/src/prefix.rs \
    '2026-08-19T23:50:01Z ERROR failed'
prefix.rs:3:21: score=0.91 holes=0 via=truncated
  tmpl:  2026-08-19T23:50:01Z ERROR failed to spawn
  truncated:  to spawn
```

A truncated spawn line that lost `` `{cmd}` `` is **identical** to the documentation sample. Accepting truncated instances and rejecting documentation prefixes of those instances cannot both hold when truncation lands on the prefix. The old ranking bug is closed for leftover suffix on the query; it is open for leftover suffix eaten by truncation.

Full paste with the command still ranks the holed source first (previous bug stays fixed).

### 4. rustc *messages* still bind; only locators are refused (conceptual)

`COMPILER_LOCATOR_RE` is `--> file:line`, `error[E\d+]`, caret/`= note:` lines. Compiler diagnostics that are printf-shaped are inverse-printfed.

Against a local `format!("error: {e}")` / `format!("error: expected {t}")` / `format!("src/{i}.rs")`:

```
$ ./stump --templates err.rs -e 'error: mismatched types'
err.rs:2:13: score=0.69 holes=1 via=full
  tmpl:  error: {e}
  {e} = mismatched types

$ ./stump --templates err.rs -e 'error: expected i32, found String'
err.rs:8:13: score=0.78
  tmpl:  error: expected {t}
  {t} = i32, found String          # greedy hole, not a type name

$ ./stump --templates fixtures/src/prefix.rs 'src/git/revert.rs'
prefix.rs:11:13: score=0.73 holes=1 via=full
  tmpl:  src/{i}.rs
  {i} = git/revert
```

On kizu, the original destroyer query without `-->` still lands on the test-fixture format string:

```
$ rg -n -g '*.rs' -g '!target/**' 'format!|anyhow!' kizu \
    | ./stump --templates - 'src/git/revert.rs'
kizu/src/app.rs:5778:52: score=0.73 holes=1 via=full
  tmpl:  src/{i}.rs
  {i} = git/revert
```

`error[E0308]: …` and `--> file:line:col` still refuse. gcc/clang `file:line:col: error:` and Python `File "…", line N` missed on prefix.rs (honest). The refuse-list is a regex of rustc gutter grammar, not “compiler output is a different tool.”

### 5. `--any` stops on the first truncated hit; `--exact` cannot save a real log stream (conceptual)

```
$ { echo 'user 42 not'; echo 'ERROR [worker] user 7 not found'; } \
    | ./stump --templates fixtures/src/user.py --any
user.py:2:20: score=0.82 via=truncated
  {uid} = 42
  truncated:  found
  # second line never read
```

`--any --exact` on the same pipe: truncated first line misses (good), then the complete worker line also misses, because `--exact` refuses leftover prefix:

```
$ echo 'ERROR [worker] user 7 not found' | ./stump --templates user.py --exact
— no template for: ERROR [worker] user 7 not found   # rc=1

$ echo 'ERROR [worker] user 7 not found' | ./stump --templates user.py
user.py:2:20: score=0.51 via=span
  {uid} = 7
  prefix: ERROR [worker]
```

Span leftover (the invert harvest) and truncation (the stump harvest) share one `--exact` bit. A stream probe that wants “first complete instance” cannot use `--any` (truncated prefix wins) and cannot use `--exact` (real logs have timestamps/levels). `--any` is now a probe that stops, as promised; it stops on the new false-positive class.

### 6. Holed leftover is silent; empty holes score 0.94 (conceptual)

No-hole templates reject a substantial suffix (`Event id must not be empty` vs `… or null when enqueueing evt-99` is a miss — previous fix). Holed templates accept extra trailing text up to `max(24, static)` and do not print it:

```
$ ./stump --templates fixtures/src/user.py 'user 42 not found today'
user.py:2:20: score=0.68 holes=1 via=full
  tmpl:  user {uid} not found
  {uid} = 42
  # no suffix= note; via=full

$ ./stump --templates fixtures/src/user.py 'user  not found'
user.py:2:20: score=0.94 via=full
  {uid} =
```

JSON wrap `{"msg":"user 42 not found"}` is a span (`prefix: {"msg":"`) — that one is the leftover-prefix feature, not a new lie.

### 7. 2.1 MB `--templates` file is a silent empty stream (same class as old pin 1 MB omit)

`MAX_FILE_BYTES = 2_000_000`. `extract_from_file` returns `[]` with no warning.

```
godfile_bytes 2100073
$ ./stump --templates godfile.py --extract
# no lines
$ ./stump --templates godfile.py 'user 42 not found'
stump: 0 templates ingested
— no template for: user 42 not found
```

Pin raised this ceiling and added a mint-target fallback. Stump still omits. A `--templates` of kizu-scale generated source, or a concatenated extract, goes quiet.

### Acknowledged, still true

- `"open " + path` extracts as holes=0 static=5 `open `; query `open /tmp/x: permission denied` misses. Sibling mutation.
- Concat Go still only hits if a sibling `fmt.Errorf` lives in the same slurp.

---

## pin

Primitive restated: mint a self-contained fingerprint once; the token is **allowed to refuse**. Leftover stubs are not identity; uniqueness is uniqueness in both snapshots; missing `--to` is an error; clipped tokens fail closed; a foreign repo is refused unless `--any-repo`.

The leftover-stub scorer and the origin string each pretend to be more than they are.

### 1. Stem-split beats identity — leftover-stub overcorrection (conceptual, lethal to “the token is the locus”)

v1 `src/calc.py` still has `def helper_keep():` / `return "stable helper"`. v2 **copies** it to `src/calc/ops.py` and leaves the original file untouched.

```
$ PIN=$(./pin mint --repo $KEEP --from $V1 src/calc.py:4)
$ ./pin resolve --repo $KEEP --to $V2 --porcelain "$PIN"
moved	-	src/calc.py:4	src/calc/ops.py:4	0.998	path or surrounding file changed; skipped basename bait src/calc.py:4
```

Human format rounds that to `moved 1.00`. The line at the minted path is **byte-identical**. `_pick_exact` prefers a unique stem-split (`src/calc.py` → `src/calc/`) over same-path with high neighbor score. The skip note names the identity `basename bait`.

The leftover-stub mutation assumed same-path + low neighbors is a re-export. When same-path neighbors are the original body, stem-split still wins first. **Extract-and-keep is reported as a move.** The file-split story now fires when the old path is *not* gone.

### 2. Leftover stub + extract to a renamed package is ambiguous with basename bait (conceptual)

Demo leftover lands because dest is `src/calc/ops.py` (`is_stem_split`). Real module extraction often goes to `src/math/ops.py`.

v2: leftover wrapper at `src/calc.py`, body at `src/math/ops.py`, clone at `src/legacy/calc.py`.

```
$ ./pin resolve --repo $MATH --to $V2 --porcelain "$PIN"
ambiguous	-	src/calc.py:4	src/legacy/calc.py:1,src/math/ops.py:4	0.952	2 copies: src/legacy/calc.py:1; src/math/ops.py:4
```

The stub did **not** steal (old bug stays fixed). The body ties with basename bait. Neighbors are equal (`return "stable helper"`). Without stem-split, there is no vote. The file-split story still only holds if the new path is `oldstem/…`.

### 3. Origin is “sorted root SHAs” — same repo becomes foreign (conceptual)

`repo_origin` = `git:` + up to four `rev-list --max-parents=0 --all` prefixes. Any extra root changes the string. Pins minted before the extra root refuse the same commit.

Orphan branch added, then checkout back to `main`. Resolve `--to` the **original commit**:

```
origin before: git:8c17586764fdde04
roots after:   1c022ed73bd6f9a3… and 8c17586764fdde04…

$ ./pin resolve --repo $ORPH --to $ORPH_V1 --porcelain "$PIN"
pin resolve: pin belongs to a different repository
(git:8c17586764fdde04 vs git:1c022ed73bd6f9a3,8c17586764fdde04)
# rc=1
```

Same tree, same file, same SHA. A subtree merge, `git checkout --orphan`, or a grafted second history invalidates every pin in the ticket.

Shallow clone of the same repo:

```
full origin:    git:103bf704f71e3836   # true root
shallow roots:  dc6273c75c68f320…      # depth-1 HEAD, parents grafted away

$ ./pin resolve --repo $SHALLOW --to HEAD --porcelain "$FULLPIN"
pin resolve: pin belongs to a different repository
(git:103bf704f71e3836 vs git:dc6273c75c68f320)
```

CI `--depth 1` checkouts cannot resolve pins minted on a full clone. The origin check stopped the helper-keep/unrelated-repo 1.000. It also treats **history shape** as repo identity.

### 4. Origin check is git-root only; missing origin still lands 1.000 (conceptual)

`origins_match(None, dest)` is True. `--to-dir` sets origin only when `discover_repo(directory) == directory`.

Foreign repo **root** refuses (old bug stays fixed). The same foreign repo’s **subdirectory** does not:

```
$ ./pin resolve --repo $UNREL --to HEAD --porcelain "$MATHPIN"
pin resolve: pin belongs to a different repository (git:86e1ea25… vs git:2e7befc2…)  # rc=1

$ ./pin resolve --to-dir $UNREL/pkg --porcelain "$MATHPIN"
moved	-	src/calc.py:4	util.py:1	1.000	path or surrounding file changed

$ ./pin resolve --to-dir $GITLESS --porcelain "$MATHPIN"    # copied util.py, no .git
moved	-	src/calc.py:4	util.py:1	1.000
```

`--from-dir` pins carry no `origin:` and land on any git repo at 1.000. A forged v1 payload (`{"v":1,…}` no `o`) does the same — `Fingerprint.from_payload` still accepts v1, and encode never rewrites it:

```
$ ./pin show "$V1PIN"
  minted: src/calc.py:1
  text:   def helper_keep():
  # no origin line

$ ./pin resolve --repo $UNREL --to HEAD --porcelain "$V1PIN"
moved	-	src/calc.py:1	pkg/util.py:1	1.000
```

The token is allowed to refuse only when both sides bothered to mint a v2 origin and the dest path is a git root. `--any-repo` is no longer the only 1.000 footgun.

### 5. `vendor/` mint succeeds, resolve on the same tree reports deleted (conceptual)

`SKIP_DIRS` includes `vendor`. `load_snapshot` omits those paths. Mint of the skipped path still works via `load_one_into` (the mint-target fallback added for godfiles).

```
$ git -C $VEND ls-files
src/app.py
vendor/lib/x.py

$ ./pin mint --repo $VEND --from HEAD vendor/lib/x.py:1
pin1.…          # ok; show: minted vendor/lib/x.py:1 unique vendor_fn

$ ./pin resolve --repo $VEND --to HEAD --porcelain "$VPIN"
deleted	-	vendor/lib/x.py:1	-	0.000	no candidates
# rc=0
```

The file is in git HEAD. The pin was minted from it. Resolve on the same ref is a successful delete. Moving a locus *into* `vendor/` is the same `deleted / no candidates` with no skip warning.

`node_modules`, `target`, `dist`, `build`, `coverage` share the omit. Dest skip is a delete oracle.

### 6. 48 MB dest omit is still silent deletion (ceiling moved, not the mutation)

DESTROYER asked for “mint from a single file, do not index the world.” v0.3 set `HARD_MAX_BYTES = 48_000_000` and injects the *mint* target if the source snapshot skipped it. Dest still indexes the world and omits over-ceiling files.

Empty dest of only the huge file: `pin: skipping huge file src/god.py (48000051 bytes)` then `destination snapshot is empty` rc=2 (honest-ish). Dest with a tiny sibling:

```
$ ls -l dest/src
god.py   48M
other.py 6B
$ ./pin resolve --to-dir dest --porcelain "$GODPIN"
pin: skipping huge file src/god.py (48000051 bytes)
deleted	-	src/god.py:1	-	0.000	no candidates
# rc=0
```

Unique locus on line 1 of the godfile, still in the tree, reported gone. Same lie as the 1 MB cutoff; the number changed.

---

## What survived

- stump 7-hole full and abridged pastes still bind names; sitbone/kizu dogfood in demo.sh still pass.
- stump rustc `-->` / `error[E0308]` refuse; the documentation decoy no longer beats a holed spawn when the query still has leftover suffix.
- stump `--any` really stops reading; binary stdin fails closed; directories still refused.
- pin leftover **wrapper** no longer scores `shifted 1.000` when dest is `oldstem/ops.py`.
- pin identical dest copies emit `ambiguous`, never two hidden 1.000 landings.
- pin unique kizu tokens still land the godfile split and still refuse voidtrace/tenaoshi.
- pin missing `--to`, truncated tokens, NFD locators, 1.2 MB mint: as advertised.
- pin `--repo foreign` (git root) refuses without `--any-repo`.
- src vs tests: when dest still has `src/calc.py` identity, pin keeps it (`same 1.000 skipped tests/test_calc.py:1`). The overcorrection is stem-split, not “any second copy.”

Both CLIs still `--help` / selftest clean after the attacks (`stump --selftest`, `pin selftest`).

---

## Kill / keep

**Keep both. Mutate both. Do not rewrite in this pass.**

| tool | do not kill because | mutate toward |
| --- | --- | --- |
| stump | Stream + names + span is still invert’s harvest. Prefix-of-instance on a *real* truncated 7-hole/spawn still binds. Locator gutter no longer hallucinates `{i}=git/revert`. | Truncation must be a prefix of an instance, not leftover-into-the-last-hole. A first-literal prefix with **no bindings** is not a hit. Exact decoy-prefix vs truncated-hole is still open. Compiler *messages* / path format strings are still a different grammar. `--any` must not stop on truncated if the probe is “first complete instance”; `--exact` cannot be the only knob for that (it kills span). Warn (or slurp) `MAX_FILE_BYTES`. Concat stays a sibling. |
| pin | The object is still the token. Unique pins + kizu split still work. The seven DESTROYER refuses are real. | Same-path identity with high neighbors beats stem-split (extract-and-keep is not a move; do not call it basename bait). Stem-split is a tie-break against leftover stubs, not against the original body. File-split to a *renamed* package must not tie with basename bait. Origin should be a stable repo id, not the set of roots (orphan / shallow / graft are not “foreign”). `--to-dir` inside a git repo must inherit origin; missing origin / v1 must fail closed unless `--any-repo`. Mint-target fallback on dest, or refuse to mint `SKIP_DIRS` paths. Huge dest omit with a sibling is still `deleted`. |

A one-line stump `if truncated and not bindings: return None` would hide §2 and would not touch middle-drop hole stuffing, decoy-prefix identity, or rustc messages. Not applied.

A one-line pin “prefer same-path if `ns >= 0.5` before stem-split” would hide §1 and would re-open leftover stubs that happen to keep a docstring neighbor. The leftover-stub vs extract-and-keep trade is the mutation, not a patch.
