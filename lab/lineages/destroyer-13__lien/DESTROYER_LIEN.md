# DESTROYER — lien

Adversarial pass on the CI gate `git diff | lien`. No rewrites. Failures are conceptual except occupancy that is already fail-closed (binary stdin, garbage stdin, FILE:LINE).

- **lien** (mutation-57, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b73-d86c-77e1-9302-7593e3f5ed08`
- Transcript: `/tmp/destroy-lien/transcript.txt`
- Follow-up: `/tmp/destroy-lien/followup.txt`
- Fixtures: `/tmp/destroy-lien/fixtures/`
- Attack driver: `/tmp/destroy-lien/attack.py` (copy: `lab/judges/destroy-lien/attack.py`)
- `./lien self-test` → 55 ok, rc=0 after the attacks. `./lien --version` → `lien 0.2.0`. Victim not patched.

Attacks: empty diff, binary, rename-only, generated dest, Japanese bindings, workspace two packages named version, blame vs natal, stdin vs path, huge diffs. Dogfood sitbone `e9b0f75` and kizu `9349dc5` / `04adde1` / `c1d9da9`.

Verdict: **mutate, do not kill.** The object is still “this change left dest lines that still speak the natal as current.” `t1 = 15` → `driftDelay = 15` still fails `T1 is 15 seconds` as `via=both` rc=1. sitbone `e9b0f75` still fails `CLAUDE.md:329` / `:332` as both-rows, 12 current liens, no `v0.4`, no kin. A kizu *release* that left `plugin.json` at `0.3.0` is a green CI because two packages named `version` are one noun and the stale manifest is a homonym.

---

## Primitive restated

A unified diff on stdin mints a **natal record** (typed old→new + inflected names). Default output is a **CI check**: one dest-line lien (`path:line: via: …`), silent on success, exit 1 if the dest tree still speaks that record as *current*. `--explain` is the human natal dump. Kin-only and migration prose are not the default gate.

`FILE:LINE` is refused (exit 2). That invert is sire, not this battery.

---

## 1. Empty diff — vacuous OK; occupancy of nothing (survived / conceptual)

```
$ printf '' | ./lien --no-color -C $EMPTY
# silent  rc=0  0.049s

$ printf '\n' | ./lien …          # rc=0
$ printf '  \n\t\n' | ./lien …    # rc=0
$ git -C $EMPTY diff | ./lien …   # clean tree, rc=0
$ git diff HEAD^ HEAD | ./lien …  # trailing-space-only hunk, rc=0
$ git diff HEAD^ HEAD | ./lien …  # add empty notes.txt, rc=0

$ printf 'commit deadbeef\nAuthor: x\n' | ./lien …
lien: stdin is not a unified diff (first line: 'commit deadbeef')
# rc=2
```

Empty / newline / whitespace / clean tree / empty-file add: honest zero. Same class as weft/zanei empty diffs. A CI job that pipes `git diff` after the change is already committed (no `--cached`, no `origin/main...HEAD`) is green. Advertised. Not a walk.

Garbage stdin is fail-closed. Keep.

---

## 2. Binary — skip is fail-open on dest; stdin is fail-closed (conceptual + operational)

Binary *plus* a JSON version hunk still mints the natal. The gate is not “binary poisons the pipe”:

```
$ git diff HEAD^ HEAD | ./lien --no-color -C $BINARY
README.md:1: both: VERSION  0.3.0 → 0.7.0: plugin version 0.3.0
# rc=1

$ git diff HEAD^ HEAD | ./lien --facts-only …
lien: 1 natal record(s)  diff → worktree
  value    VERSION  0.3.0 → 0.7.0  (plugin.json:2)
```

**Binary-only is occupancy of nothing.** `git diff` of a replaced blob is a legal unified diff with no hunks:

```
diff --git a/blob.bin b/blob.bin
index 5aa987c..665b388 100644
Binary files a/blob.bin and b/blob.bin differ
```

```
$ git diff HEAD^ HEAD | ./lien --no-color -C $BINARY_ONLY
# silent  rc=0
```

Dest README still says `plugin version 0.3.0`. No natal, so no leftover. A “CI gate on this change” that also replaced `icon.png` / `secret.bin` / wasm is green even if the only dest copy of the old fact lives in the blob.

Leftover *only* inside a dest binary (`secret.bin` contains `version=0.3.0\0`, source paid `0.3.0 → 0.7.0`):

```
$ git diff HEAD^ HEAD | ./lien --facts-only -C $BIN_DEST
  value    VERSION  0.3.0 → 0.7.0  (src.py:1)
$ git diff HEAD^ HEAD | ./lien -C $BIN_DEST
# silent  rc=0
```

`read_tree_file` returns `None` on NUL in the first 4k. Size-cap cousin. Silent omit.

Stdin with NUL / `0xff` is fail-closed exit 2 (`lien: binary diff (stdin)`). That is the right direction for a crash. It does not make dest-binary skip visible.

---

## 3. Rename-only — 100% `git mv` mints no natal (conceptual, load-bearing)

```
diff --git a/src/t1.py b/src/drift_delay.py
similarity index 100%
rename from src/t1.py
rename to src/drift_delay.py
```

```
$ git diff HEAD^ HEAD | ./lien --facts-only -C $RENAME
lien: 0 natal record(s)  diff → worktree

$ git diff HEAD^ HEAD | ./lien --no-color -C $RENAME
# silent  rc=0

$ git diff HEAD^ HEAD | ./lien --explain …
lien: 0 leftovers  diff → worktree  both=0 claim=0 kin=0
  no natal records in this change.
```

Dest README still says `Import t1 from src/t1.py. T1 is 15 seconds.` Path natal does not exist. `extract_natals` only walks hunks; a 100% rename has none. The CI verb “did this change leave dest speaking the old name” cannot see a file rename.

**Binding rename in place still holds.** Same README, `t1 = 15` → `driftDelay = 15`:

```
$ git diff HEAD^ HEAD | ./lien --no-color -C $RENAME_PLUS
README.md:1: both: t1↔driftDelay  15: T1 is 15 seconds.
# rc=1
```

That is the product. Kill the tool for rename-only and you throw this away.

---

## 4. Generated dest — `dist/`/`build`/`target` are skip-blind; `generated/` is hungry (conceptual, load-bearing)

Source paid `TIMEOUT 10 → 30` and `VERSION 0.3.0 → 0.7.0`. Dest still has copies in:

| path | SKIP_DIRS? | default check |
| --- | --- | --- |
| `src/config.py` (paid) | no | skip_lines (new hunk) |
| `README.md` | no | **FAIL** both |
| `generated/schema.json` | **no** | **FAIL** both |
| `docs/generated/lib.rs` | **no** | **FAIL** both |
| `dist/bundle.js` | yes | **absent** |
| `build/out.js` | yes | **absent** |
| `target/gen.rs` | yes | **absent** |

```
$ git diff HEAD^ HEAD | ./lien --no-color -C $GENERATED
generated/schema.json:3: both: VERSION  0.3.0 → 0.7.0: "version": "0.3.0"
generated/schema.json:2: both: TIMEOUT  10 → 30: "timeout": 10,
README.md:1: both: TIMEOUT  10 → 30; VERSION  0.3.0 → 0.7.0: timeout is 10, version 0.3.0
docs/generated/lib.rs:1: both: TIMEOUT  10 → 30: pub const TIMEOUT: u64 = 10;
# rc=1
```

`dist/bundle.js` still says `const TIMEOUT = 10`. CI does not. Directory name is the policy, and it is two policies at once: codegen under `target/` is invisible; codegen under `generated/` or `docs/generated/` fails the build as if it were a current claim.

A “source paid, ship the bundle” PR is green if webpack wrote `dist/` and red if it wrote `generated/`. Not a generated-dest verb.

---

## 5. Japanese bindings — CJK is not a pair; unnamed `value` 10→30 is min-score gated; alias is one-way (conceptual, load-bearing)

CANDIDATE already said `タイムアウト = 10` is not a fact. Confirmed as a *gate*:

```
# src/config.py
-タイムアウト = 10
-リトライ = 3
-閾値 = 0.4
+タイムアウト = 30
+リトライ = 8
+閾値 = 0.45
```

```
$ git diff HEAD^ HEAD | ./lien --facts-only -C $JP
lien: 1 natal record(s)  diff → worktree
  value    VALUE  10 → 30  (src/config.py:1)

$ git diff HEAD^ HEAD | ./lien --no-color -C $JP
# silent  rc=0

$ git diff HEAD^ HEAD | ./lien --explain …
lien: 0 leftovers  diff → worktree  both=0 claim=0 kin=0
  1 natal record(s); none still speaking (min-score gated).
```

`IDENT_RE` / `PAIR_RE` are Latin (`[A-Za-zÀ-ÖØ-öø-ÿ_]`). The hunk falls through to “lone number on the line,” named `value`. `merge_natals` then folds every unnamed number change on the same stem `value` into **one** natal: `10 → 30` wins, `0.4 → 0.45` is discarded. Dest `タイムアウトは 10 秒` / `threshold is 0.4` / fullwidth `１０` never leftover-match a natal named `value` hard enough to clear `--min-score 55` (docs claim without ident is ~44).

**The other direction still works.** English `timeout = 10` / `threshold = 0.4` bumped, dest Japanese:

```
$ git diff HEAD^ HEAD | ./lien --no-color -C $JP_ALIAS
docs/ja.md:1: both: TIMEOUT  10 → 30; THRESHOLD  0.4 → 0.45: タイムアウトは 10 秒。閾値は 0.4。
# rc=1
```

`--explain` why: `name-alias, old-value, via-both`. `docs/fw.md` `タイムアウトは １０ 秒` is absent. Fullwidth `１０` is not `10`. Alias table leftover-matches Japanese *of an English fact*. Japanese *as the natal* is a green CI.

---

## 6. Two packages named `version` — one noun; kizu `plugin.json` is a homonym (conceptual, load-bearing)

### Fixture: bump only `cli`, `core` stays `0.3.0`

```
$ git diff HEAD^ HEAD | ./lien --facts-only -C $WS_SAME
lien: 1 natal record(s)  diff → worktree
  value    VERSION  0.3.0 → 0.7.0  (crates/cli/Cargo.toml:3)

$ git diff HEAD^ HEAD | ./lien --no-color -C $WS_SAME
crates/core/Cargo.toml:3: both: VERSION  0.3.0 → 0.7.0: version = "0.3.0"
README.md:1: claim: VERSION  0.3.0 → 0.7.0: cli 0.3.0 and core 0.3.0 ship together.
# rc=1
```

Independent crate `core` still at `0.3.0` fails CI as leftover of `cli`'s bump. Same key, same old token, no package identity.

### Fixture: bump both, different versions

`cli 0.3.0 → 0.7.0` and `core 1.2.0 → 1.3.0` in one commit:

```
$ git diff HEAD^ HEAD | ./lien --facts-only -C $WS_TWO
lien: 1 natal record(s)  diff → worktree
  value    VERSION  0.3.0 → 0.7.0  (crates/cli/Cargo.toml:3)
```

`merge_natals` groups by `ident_parts(names[0])` → `("version",)`. First valued natal wins. `1.2.0 → 1.3.0` is gone.

```
$ git diff HEAD^ HEAD | ./lien --no-color -C $WS_TWO
README.md:1: both: VERSION  0.3.0 → 0.7.0: cli version 0.3.0. core crate version 1.2.0.
README.md:2: both: VERSION  0.3.0 → 0.7.0: plugin version 0.3.0
# rc=1
```

`docs/core.md` `core version 1.2.0 is the library API` is **kin-only** (name `version`, value is not `0.3.0`) so default check drops it. The core crate's leftover is not a current lien of the cli natal. Two packages, one noun, the second bump never existed.

### Dogfood kizu `9349dc5` release v0.7.0

```
$ git -C kizu diff 9349dc5^ 9349dc5 --stat
 Cargo.lock | 2 +-
 Cargo.toml | 2 +-
```

```
$ git diff 9349dc5^ 9349dc5 | ./lien --facts-only -C kizu
lien: 1 natal record(s)  diff → worktree
  value    VERSION  0.6.0 → 0.7.0  (Cargo.lock:920)

$ git diff 9349dc5^ 9349dc5 | ./lien --no-color -C kizu
# silent  rc=0   0.292s
```

HEAD still has:

```
plugin/plugin.json  "version": "0.3.0"
Cargo.toml          version = "0.7.0"
```

`--explain` / `--all` print **28 kin** rows of the *word* `version` (`"version": 1` in Cursor hooks docs, `clap = { version = "4.6.0" }`, historical `0.3.1 → 0.3.2` plans). **`plugin/plugin.json` is in neither the default check nor `--all`.** Config-path + generic name + bound value `0.3.0 ≠ 0.6.0` is `is_homonym` → `decide_via` returns `None`. The stale plugin manifest is not leftover of *this* natal; it is a different package's `version` that the gate cannot name.

kizu `87a54a4` (`0.2.0 → 0.3.0`) is the same shape: default check rc=0 against today's tree (plugin.json *is* 0.3.0 now, so the old natal is paid-or-homonym); `--explain` is the same 28 kin flood.

A release CI job `git diff origin/main...HEAD | lien` on a Cargo.toml bump is green while the Claude plugin still advertises 0.3.0. That is the workspace hole on a real tree.

---

## 7. Blame vs natal — dest occupancy is not authorship (survived, with a hungry ADR)

Not sire. The CI question is “does dest still speak this change's natal?”, not “who last wrote the leftover line?”

```
$ git -C sitbone blame -L 329,329 -- CLAUDE.md
^a2512fe (Annenpolka 2026-03-31 …) @Test("… threshold 0.4）")

$ git -C sitbone blame -L 76,76 -- docs/adr/0019-presence-hysteresis.md
98a80094 (Annenpolka 2026-04-10 11:25:08 +0900) 既存の `threshold: Double = 0.4` …

$ git log -1 --format='%h %ci %s' e9b0f75
e9b0f75 2026-04-10 11:28:37 +0900 Implement dual-threshold hysteresis in PresenceArbiter

$ git log -1 --format='%h %ci %s' 98a8009
98a8009 2026-04-10 11:25:08 +0900 Add ADR-0019 presence hysteresis design
```

`git blame` of the money-shot leftover is **a2512fe** (root docs), not **e9b0f75**. ADR-0019 landed **three minutes before** the implementation and already quotes `threshold: Double = 0.4`. The gate still fails both:

```
$ git diff e9b0f75^ e9b0f75 | ./lien --no-color -C sitbone
CLAUDE.md:329: both: threshold↔presentThreshold  0.4 → 0.45: @Test("… threshold 0.4）")
CLAUDE.md:332: both: …
docs/adr/0019-presence-hysteresis.md:76: both: … 既存の `threshold: Double = 0.4`
docs/adr/0019-presence-hysteresis.md:9: both: … 単一閾値(0.4)
docs/adr/0001-…:19: claim: … normalized score > 0.4
docs/adr/0019-…:25: claim: … ema値が0.4の境界
SPEC.md:145: claim: … `normalized > 0.4`
Tests/…/PresenceArbiterTests.swift:40,55,133,177,216: claim: … 0.4
# rc=1  12 liens  both=4  (json: leftovers 16 with --explain union; natal=1)
```

`--at e9b0f75` vs worktree vs `./lien -C sitbone e9b0f75` (SHA form): **same 12 lines**. ADR already exists at the natal commit, so `--at` does not drop it. That is dest occupancy, and it is the product: CLAUDE.md:329 is still a current leftover of `0.4 → 0.45` no matter who blamed the line.

Hungry side, already in CANDIDATE: ADR-0019:25 (`ema値が0.4の境界`) and ADR-0001's `normalized score > 0.4` fail default check. A PR that implements an already-merged ADR fails CI on the ADR. `is_ci_lien` drops kin-only quotes (`:12`, `:77`) and migration lines that also name `0.45` (`:176–177` only appear under `--all`). The remaining ADR both-rows are the spec quoting the old binding on purpose.

Do not invert this into sire. The mutate is “docs that already narrate the move are not current,” which v0.2 started and did not finish.

---

## 8. Stdin vs path — pipe and `--diff FILE` match; wrong `-C` is fail-open; FILE:LINE is refused (conceptual)

Gold JSON hunk is identical three ways:

```
$ cat plugin.diff | ./lien --no-color -C $DEST
$ ./lien --no-color -C $DEST --diff plugin.diff
$ cat plugin.diff | ./lien --no-color -C $DEST --diff -
README.md:1: both: VERSION  0.3.0 → 0.7.0: plugin version 0.3.0, hook timeout 10 seconds.
# rc=1 all three
```

Cwd without `-C` matches. Path-limited `git diff -- crates/cli/Cargo.toml` mints the same cli natal.

**Wrong dest is silent pass.** Sitbone hysteresis diff piped at kizu:

```
$ git -C sitbone diff e9b0f75^ e9b0f75 | ./lien --facts-only -C kizu
lien: 1 natal record(s)  diff → worktree
  record   threshold↔presentThreshold  0.4 → 0.45  (Sources/SitboneCore/PresenceArbiter.swift:30)

$ git -C sitbone diff e9b0f75^ e9b0f75 | ./lien --no-color -C kizu
# silent  rc=0  0.579s
```

Natal is parsed from stdin (dest-independent). Scan walks *kizu*'s tree. No leftover of `0.4`/`threshold` there. CI green. `git diff | lien` without `-C` at the repo that owns the dest is occupancy of a different tree.

FILE:LINE is not a locator (lien's object, not a destroyer hole to “fix” into sire):

```
$ ./lien --no-color -C $DEST README.md:1
lien: pass a unified diff on stdin or a commit, not FILE:LINE
      (lien starts from a change; leftovers are the natal record speaking)
# rc=2
```

---

## 9. Huge diffs / size-cap — omit is silent; add-heavy rewrites mint zero natals (conceptual, load-bearing)

CANDIDATE: “Size-cap omit is silent.” Confirmed.

Dest `generated/huge.json` is **1,600,224 bytes** of `"version": "0.3.0"` (cap `1_500_000`). Source paid `0.3.0 → 0.7.0`:

```
$ git diff HEAD^ HEAD | ./lien --facts-only -C $HUGE
lien: 1 natal record(s)  diff → worktree
  value    VERSION  0.3.0 → 0.7.0  (src/config.py:1)

$ git diff HEAD^ HEAD | ./lien --no-color -C $HUGE
# silent  rc=0

$ git diff HEAD^ HEAD | ./lien --explain …
lien: 0 leftovers  …  1 natal record(s); none still speaking (min-score gated).
```

`read_tree_file` returns `None`. No skip line, no warning, no `omitted=`. CI green. Same shape as dest-binary NUL skip.

kizu large commits are a different omit — **no natal at all**:

| commit | stat | facts | default check |
| --- | --- | --- | --- |
| `04adde1` jsx/tsx | 25 files, +1918/−63, 115,563-byte diff | `0 natal record(s)` | rc=0, 0.087s |
| `c1d9da9` ui facade split | +1995/−1972, 153,140-byte diff | `0 natal record(s)` | rc=0, 0.090s |

`extract_natals` skips `status=="add"` and unpaired deletions. A rewrite that is new files, or delete+add not aligned as a value/rename pair, is occupancy of nothing. The CI gate cannot fail leftovers of a change it did not name. Speed is fine (~90ms). The object is missing, not slow.

---

## What survived

- Gold binding rename: `t1 = 15` → `driftDelay = 15` still `README.md:1: both: t1↔driftDelay  15: T1 is 15 seconds.` rc=1.
- Gold sitbone `e9b0f75`: 12 current liens, 4 `via=both`, CLAUDE.md:329/332 both-rows, live test `0.4` claims, no `v0.4`, no `: kin:` on default. `--all` restores 16 (kin + migration). json: 1 natal, leftovers 16, via `{claim:10, both:4, kin:2}`.
- Gold JSON hunk pipe / `--diff FILE` / `--diff -`: same dest-line lien.
- Garbage stdin rc=2, names unified diff. Empty stdin rc=0 silent. FILE:LINE rc=2.
- Japanese leftover of an *English* timeout/threshold natal is via=both (alias table).
- Binary+version hunk still extracts `VERSION 0.3.0 → 0.7.0` and liens dest prose.
- `self-test` 55/55 after the battery. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

Nothing here turned `git diff | lien` into `git diff --stat` or into sire (`FILE:LINE` → natal SHA). The both-row on `T1 is 15` and sitbone `CLAUDE.md:329` still fail the gate. Do not kill because a 100% rename, a CJK assignment, or kizu's plugin.json homonym is invisible. Those are mutations. Killing them would throw away a real natal-record gate to hide a Latin pair-regex and a single `version` noun.

| do not kill because | mutate toward |
| --- | --- |
| `t1↔driftDelay` both-row rc=1; sitbone `e9b0f75` 12 current liens, 4 both, no `v0.4`; pipe=`--diff FILE`; FILE:LINE stays refused | **Path natal.** `git mv src/t1.py src/drift_delay.py` must mint a rename record so dest `t1.py` / `T1` can fail CI. Binding-in-place already works. |
| | **CJK is an ident.** `タイムアウト = 10` is a named fact, not `VALUE 10→30` merged with `0.4→0.45`. Keep alias leftover-match of English natals. Fullwidth digits are the same token or they are not — pick one and print it. |
| | **`version` is per package, not one noun.** `merge_natals` on `ident_parts("version")` is why cli+core collapse and why kizu `plugin.json` `0.3.0` is a homonym of Cargo `0.6.0→0.7.0`. Origin path (or crate name) is part of the record. |
| | **Skip/omit is a line, not silence.** `dist/` / `target/` leftover, dest NUL, dest `>1.5MB` must say `omitted=` (or fail closed). `generated/` / `docs/generated/` should not fail CI as “current” unless that is the stated generated-dest policy. |
| | **Wrong `-C` / stdin dest.** Natal from stdin + scan of a foreign tree is fail-open rc=0. Default dest should be the diff's new side (or refuse if cwd is not that repo), not “whatever `-C` points at.” |
| | **Adds and unpaired deletes can be natal.** kizu `04adde1` / `c1d9da9` mint 0 records. A rewrite is not occupancy of nothing. |
| | **Release bump vs sibling manifests.** kizu `9349dc5` default check rc=0 while `plugin.json` is `0.3.0` is the workspace hole on a real tree — fix via package-scoped version, not by failing every docs hit of the word `version` (`--all` already does that, 28 kin). |

Binary stdin / garbage / FILE:LINE stay fail-closed. Empty diff stays vacuous OK.

Do not grow a leftover-name walker. The next mutation is *one natal per origin package* plus a path/CJK fact, not `--explain` prettier and not sire's locator.
