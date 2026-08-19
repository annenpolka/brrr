# DESTROYER — maiden

Adversarial pass on **never-red**. No rewrite of maiden. Failures are conceptual except one documented CLI argparse miss (operational), left unpatched so the dialect/identity holes stay visible.

- **maiden** (candidate-42, v0.2) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1`
- Transcript: `/tmp/destroy-maiden/transcript.txt`
- Follow-up: `/tmp/destroy-maiden/followup.txt`
- Fixtures: `/tmp/destroy-maiden/fixtures/`
- Attack driver: `/tmp/destroy-maiden/attack.py`
- `./maiden --selftest` → `28 passed, 0 failed` after the attacks. maiden 0.2. Victim not touched.

Attacks: no-records UNKNOWN vs never-red, SKIP-only, `--skeptic` vs `--latest --skeptic`, renamed ids, ledger format, junit flaky then green, xcresult missing, CI log of the wrong suite, `rg PASS`.

Verdict: **mutate, do not kill.** The object is still “this id’s recorded `<failure>`/`... FAILED` history is empty.” Gold 2019-fail + 2024-green still names `pkg.T::alpha` **SCARRED** and `--skeptic`; `--latest` still maidens it. sitbone `swift test list` is **213 UNKNOWN**, kizu `cargo --list` is **489 UNKNOWN**. SKIP-only is not maiden. That is not `rg PASS` and not alibi. The attacks show where never-red is a **parser × string id**, not “this test has never been red.”

---

## Primitive restated

The never-red set is a fold over **observations maiden actually parsed**, keyed by **canonical string id**:

| verdict | claimed meaning | actual harvest |
| --- | --- | --- |
| **MAIDEN** | ≥1 pass, 0 fail | ≥1 mapped-pass, 0 mapped-fail (`<failure>`/`<error>` child, `... FAILED`, pytest `FAILED`/`XFAIL`) |
| **SCARRED** | ≥1 fail (error counts) | same, plus `status=fail/failure/error` in jsonl/`--format json` |
| **SKIPPED** | only skip/ignored | junit `<skipped/>`, cargo `ignored`, pytest `SKIPPED` |
| **UNKNOWN** | in the roster, never an outcome | `SEEN` from `--list` / `--census`, or no parse |
| **ORPHAN** | outcomes, not in current roster | identity split (census vs specifier) produces this on a green run |

`--skeptic` is latest PASS ∩ history FAIL. `--latest` is the `rg PASS` snapshot. `--check MAIDEN` is the TDD gate on the maiden column.

---

## 1. no-records UNKNOWN vs never-red — roster is honest; unparsed red is not UNKNOWN (conceptual, load-bearing)

Empty stdin / garbage / markdown “All tests PASS”:

```
$ ./maiden --no-ledger --counts
# SCARRED 0  MAIDEN 0  SKIPPED 0  UNKNOWN 0  ORPHAN 0
```

A roster without outcomes is the named empty set CANDIDATE claimed:

```
$ swift test list --skip-build | ./maiden --no-ledger --roster --counts
# SCARRED 0  MAIDEN 0  SKIPPED 0  UNKNOWN 213  ORPHAN 0
# --check MAIDEN  rc=0

$ cargo test --all-targets --all-features -- --list | ./maiden --no-ledger --roster --counts
# SCARRED 0  MAIDEN 0  SKIPPED 0  UNKNOWN 489  ORPHAN 0
```

`--census` is a **different 489 / different 135**, intersection with the runner list is **0**:

| tree | census ids | runner ids | ∩ |
| --- | --- | --- | --- |
| kizu | 489 bare `fn` names (`compute_operation_diff_empty_when_identical`) | 489 `mod::tests::fn` | **0** |
| sitbone | 135 `@Test("display")` + `func test*` | 213 `Module.Type[/Nested]/func` | **0** |

A real fail in a dialect maiden does not parse is **not UNKNOWN**. It is occupancy of nothing:

```
$ ./maiden --no-ledger --json fixtures/ci/go-fail.txt
{}          # --- FAIL: TestAlpha  vanished

$ ./maiden --no-ledger --json fixtures/ci/bun-fail.txt
{}          # bun test  ✗  1 fail  vanished

$ ./maiden --no-ledger --json fixtures/ci/nextest-fail.txt
{}          # nextest FAIL [0.010s] kizu app::tests::alpha  vanished
```

kizu’s other suite is bun (`tests/e2e/*.test.ts`, **37** `test(` calls). `cargo --list` never names them. A red e2e run cannot scar.

Then a cargo-looking pass of the same string launders the go fail:

```
$ ./maiden --no-ledger --header go-only.txt cargo-same-id.txt
MAIDEN  TestAlpha     # --- FAIL: TestAlpha dropped; `test TestAlpha ... ok` maidens
```

No-records is UNKNOWN **only if a roster was supplied**. An unrecognized fail log is the empty fold. The next recognized pass of that string is maiden. That is not “never-red.” It is “never-parsed-red.”

---

## 2. SKIP-only claimed maiden — holds; skip-then-pass is maiden (survived)

```
$ ./maiden --no-ledger --header fixtures/junit/skip-only.xml
SKIPPED  0 0 1  …  pkg.T::never
# --check MAIDEN  rc=0
```

Skip then a later pass is **MAIDEN** (`n_pass=1 n_skip=1`). The primitive said skip-only is not maiden, not “skip forever.” Honest. pytest `SKIPPED` is skip. cargo `ignored` is skip (gold selftest).

XFAIL/XPASS is a mapping, not skip:

```
tests/test_old.py::test_known_bug  XFAIL  → SCARRED   # expected fail scars forever
tests/test_old.py::test_flaky      XPASS  → MAIDEN    # unexpected pass of a known flake
```

An xfailed test has been red (on purpose). An xpassed flake has been the opposite of never-red. STATUS_MAP is the policy.

---

## 3. latest-green ∩ historical-fail (`--skeptic`) — gold holds; `--latest --skeptic` is `rg PASS` (conceptual)

Gold junit 2019-fail + 2024-green:

| id | history | `--latest` | `--skeptic` |
| --- | --- | --- | --- |
| pkg.T::alpha | SCARRED (fail 2019, pass 2024) | MAIDEN | yes |
| pkg.T::beta | MAIDEN (2 pass) | MAIDEN | no |
| pkg.T::gamma | SKIPPED | SKIPPED | no |
| pkg.T::delta | MAIDEN (born 2024) | MAIDEN | no |

```
$ ./maiden --no-ledger --latest --counts 2019 2024
# SCARRED 0  MAIDEN 3  SKIPPED 1

$ ./maiden --no-ledger --skeptic --header 2019 2024
SCARRED  1 1 0  …  pass  pkg.T::alpha
# --check SKEPTIC  rc=1
```

`--latest` is applied **before** `skeptic_rows`. Combining the lie-mode with the anti-lie flag deletes the fail:

```
$ ./maiden --no-ledger --latest --skeptic --counts 2019 2024
# SKEPTIC 0  (latest PASS ∩ history FAIL)  SCARRED=0 MAIDEN=3 SKIPPED=1
```

Same-timestamp fail-then-pass in one junit (retry in one suite timestamp): fail wins the latest tie → **SCARRED**, not skeptic. never-red still holds. `--latest` does not maiden it.

Timestamp-less junit uses **mtime as the clock**. Fail file newer than green → latest=FAIL, SKEPTIC 0 (still SCARRED). Green newer → SKEPTIC 1. A git checkout that touches mtimes can invert “currently green.” The scar stays.

`rg PASS` on the 2024 file is 4 `testcase` tags (repaired alpha + skip gamma + beta + delta). History MAIDEN is 2. The named set survives. The composition `--latest --skeptic` does not.

---

## 4. renamed tests — string id is the whole object (conceptual, load-bearing)

```
$ ./maiden --no-ledger --header rename-fail.xml rename-pass.xml
SCARRED  pkg.T::compute_diff              # failed 2019
MAIDEN   pkg.T::compute_operation_diff    # born green 2024
# --skeptic  SKEPTIC 0
```

Classname move is the same split: `pkg.Old::alpha` SCARRED, `pkg.New::alpha` MAIDEN. Skeptic is empty. The test was red. The new string has never been red. never-red is not a test. It is a spelling.

kizu’s live identity `app::tests::compute_operation_diff_empty_when_identical` is this spelling. A module split (`app.rs` → `app/stream.rs`) is a new maiden column unless the ledger is rewritten.

---

## 5. ledger format lies — `status: red` maidens; `{id}` swallows cargo (conceptual)

Honest jsonl (`"status":"fail"` then `"pass"`) is SCARRED / skeptic. `"status":"failure"` maps. `"status":"FAIL"` maps. Then:

```
{"id":"pkg.T::alpha","status":"red","t":"2019-06-01T12:00:00Z"}
{"id":"pkg.T::alpha","status":"pass","t":"2024-08-01T12:00:00Z"}
```

```
$ ./maiden --no-ledger --json status-red.jsonl
MAIDEN  pkg.T::alpha   n_fail=0 n_pass=1
```

`red` / `flaky` are not in STATUS_MAP. The fail line is dropped. The pass remains. never-red of the ledger **as written** is a lie.

A file whose first non-empty line is `{..."id"...}` is a ledger for the whole file (`looks_like_ledger`). Cargo lines after it are ignored:

```
{"id":"note","status":"seen"}
test kizu::scar::undo ... FAILED
test kizu::hook::parse ... ok
```

```
UNKNOWN  note     # undo never scars
```

Documented ingest is argparse-broken (operational):

```
$ ./maiden ingest --run ci-2024 fixtures/junit/run-2024-green.xml
# rc=2  unrecognized arguments: …/run-2024-green.xml
```

`ingest FILE --run ci-2024` and `--run ci-2024 ingest FILE` work. SHA skip of identical bytes works (`ingested 0`). The README order is the one that fails.

---

## 6. junit flaky then green — `<flakyFailure>` is MAIDEN (conceptual, load-bearing)

Surefire / Jenkins retry XML records the red attempt as a child that is not `<failure>`:

```xml
<testcase classname="pkg.T" name="alpha">
  <flakyFailure message="boom">…</flakyFailure>
</testcase>
```

```
$ ./maiden --no-ledger --json flaky-then-green.xml
MAIDEN  pkg.T::alpha   n_fail=0 n_pass=1
# --check MAIDEN  rc=1
```

`<rerunFailure>` is the same MAIDEN. The file says the test failed, then passed. The TDD gate `--check MAIDEN` fires as if it had never been red.

`status="failed"` / `status="error"` with no child (Android / some Gradle / some xunit):

```xml
<testcase classname="pkg.T" name="alpha" status="failed"/>
```

```
MAIDEN  pkg.T::alpha   latest=pass
```

`<error>` **child** still scars (gold). The walker is “child tag ∈ {failure, error} or skip,” not “recorded outcome.” never-red on junit is `rg '<failure>|<error>'` plus empty-body = pass. A flaky-then-green CI artifact is a maiden column.

---

## 7. xcresult missing — Info.plist dir is empty rc=0 (conceptual)

```
$ ./maiden --no-ledger --json Missing.xcresult     # dir + Info.plist, xcresulttool errors
{}

$ ./maiden --no-ledger --counts sitbone/.build/Sitbone.app
# rc=1  Is a directory   # no Info.plist at the bundle root

$ ./maiden --no-ledger --counts sitbone/.build/Sitbone.app/Contents
# SCARRED 0  MAIDEN 0  …  # Info.plist present → parse_xcresult → []
```

xcresulttool on both: `Failed to create a new result bundle reader`. maiden swallows that as zero observations. sitbone has **no `.xcresult` on disk**. CANDIDATE named this.

Even a dumped JSON file is not walked. Apple boxes strings as `{"_value": "Failure"}`; the walker requires `name` and `status` to be `str`. Boxed schema → empty. Flat `{"name":"alpha","result":"failed"}` as a **file** is not an xcresult dir, so the walker never runs; `parse_bytes` sees `{` and no `"type":"test"` → empty.

xcresult is a claimed ingest. It is a silent empty. A failed Xcode run pointed at the app bundle or a missing bundle does not scar.

---

## 8. CI log parse of the wrong suite — bun/lint vanish; cargo `... ok` maidens (conceptual, load-bearing)

Synthetic GHA matrix: e2e bun fail + unit cargo pass + a captured `test kizu::scar::undo ... FAILED` prefixed with `captured:`:

```
$ ./maiden --no-ledger --json wrong-suite-gha.txt
MAIDEN  kizu::hook::parse
MAIDEN  kizu::scar::undo     # unit `... ok`; bun ✗ dropped; `captured: test … FAILED` does not match ^test
# --skeptic  SKEPTIC 0
```

Real sitbone `gh run view 23830489453 --log` (Verify / “Add CI and make lint pass”, **failure**, 167 lines) **did download** (not 410). The failing step is `swiftlint: command not found` exit 127. Zero test lines.

```
$ ./maiden --no-ledger --counts sitbone-fail-gha.log
# SCARRED 0  MAIDEN 0  SKIPPED 0  UNKNOWN 0  ORPHAN 0

$ ./maiden -C sitbone --no-ledger --roster --counts sitbone-list.txt sitbone-fail-gha.log sitbone-one.log
# SCARRED 0  MAIDEN 1  SKIPPED 0  UNKNOWN 212
```

A failed CI log plus one green `formatTime: ゼロ` maidens `SitboneUITests.UILogicTests/formatTimeZero`. The “failed run” never touched the suite.

Newer sitbone/kizu logs are **HTTP 410**. kizu `24923167384` (“Split large modules”, failure): `macos-latest / stable` **success**, `ubuntu-latest / stable` **failure**, job logs 410. Cannot scar kizu from the job that actually failed.

---

## 9. `rg PASS` skeptic pipeline — the anti-`rg` is real; census is a second `rg` (survived / conceptual)

`rg PASS` / `--latest` on 2024 junit keeps repaired alpha. Full fold does not. `--skeptic` names alpha. That is the product.

`--census` plus a live green log is a second identity `rg`:

```
# sitbone one green formatTime: ゼロ  + --census
ORPHAN  SitboneUITests.UILogicTests/formatTimeZero     # alias rewrote the log
UNKNOWN formatTime: ゼロ                               # census id never joins
# MAIDEN 0

# kizu one green cargo --exact  + --census
ORPHAN  app::tests::compute_operation_diff_empty_when_identical
# 489 census fn names stay UNKNOWN. MAIDEN 0
```

v0.2 alias + `--roster` is the honest join (MAIDEN 1 / UNKNOWN 212, MAIDEN 1 / UNKNOWN 488). `--census` is advertised as “approximate roster” and produces **zero** never-red of the runner specifier. The green run maidens an ORPHAN. Same shape as v0.1 display/specifier split, which CANDIDATE already killed once.

Japanese-first list lines are dropped (`RE_SWIFT_LIST` wants ASCII `[A-Za-z_]` on the first segment). `ウェイク処理/cameraRestartsAfterWake()` vanished; `SitboneCoreTests.SystemSleepTests/ウェイク処理/…` stayed. sitbone’s real list is ASCII-prefixed, so dogfood 213/213 holds.

---

## What survived

- Gold 2019+2024: alpha SCARRED, beta/delta MAIDEN, gamma SKIPPED. `--latest` MAIDEN 3. `--skeptic` is alpha only. `--check SKEPTIC` rc=1.
- SKIP-only `--check MAIDEN` rc=0. sitbone/kizu roster `--check MAIDEN` rc=0 (213 / 489 UNKNOWN).
- Empty / garbage / markdown: honest zero.
- sitbone live `UILogicTests/formatTimeZero` + list + `-C Tests/`: **MAIDEN** specifier, ORPHAN 0, UNKNOWN 212.
- kizu live `app::tests::compute_operation_diff_empty_when_identical` + `--list`: **MAIDEN**, UNKNOWN 488. Cargo id = list id.
- `<error>` child scars. libtest json `event=failed` scars. GHA prefix strip + `kizu::scar::undo` fail then pass is SCARRED / skeptic (fixture).
- Honest jsonl ledger + `ingest FILE` (flags after the path) + SHA skip + 2019 re-ingest: alpha SCARRED.
- `--selftest` 28/28. No rewrite.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “this spelling has no parsed fail in the fold.” 2019 `<failure>` + 2024 green is still skeptic. sitbone/kizu with no junit still refuse to call 213/489 tests maiden. Nothing in this battery turned that into `rg PASS latest.xml` or into alibi-on-HEAD. Do not kill because `<flakyFailure>`, rename, or bun. Those are mutations. Killing them would throw away a real history fold to hide a junit dialect and a string key.

| do not kill because | mutate toward |
| --- | --- |
| Gold alpha SCARRED / `--skeptic`; `--latest` is the named lie; SKIP-only not maiden; sitbone 213 UNKNOWN; kizu 489 UNKNOWN; one green run maidens the **runner** specifier | **junit outcome is the recorded status, not the child-tag set.** `<flakyFailure>`, `<rerunFailure>`, `status="failed"`/`error` are fails. Empty body stays pass. |
| | **Identity is still the runner specifier** (v0.2). Do not advertise `--census` as a roster: 0∩489 / 0∩213. Join cargo `--list` paths, not `fn` names. |
| | **`--latest --skeptic` must refuse or ignore `--latest`.** The anti-`rg` cannot be composed into `rg`. |
| | **Unrecognized dialect is fail-closed when the user thought they ingested a run** (non-empty log, zero obs → exit 2 / UNKNOWN-with-src), not a silent empty that a later cargo pass can maiden. bun / go / nextest / TAP are first-class or explicitly refused. |
| | **Ledger status outside STATUS_MAP is refuse, not drop.** `red`/`flaky` cannot launder a pass. A `{id}` first line must not hide subsequent `test … FAILED` lines (or ingest is jsonl-only by flag). |
| | **xcresult is refuse-or-walk, not empty OK.** Info.plist is not a test run. Unbox `_value`. Missing bundle ≠ maiden. |
| | **Rename is a new id** — keep that axiom, but `--skeptic` / `why` should be able to name “ORPHAN scar beside a maiden of the same leaf.” Do not pretend the new spelling is a different test without saying so. |
| | **Documented `ingest --run ID FILE`** is argparse `words`/`--run` order. Fix the CLI or the README; do not leave rc=2 on the advertised command. |
| | Persist `gh run view --log` before 410 (CANDIDATE). The one sitbone fail log that still exists is **lint**, not tests. |

A one-line `status=` attribute reader would hide Android junit and would not touch rename, bun, or `--census`. Not applied.

Do not grow a test-intel platform. The next mutation is **dialect-honest fold** (junit retries + refuse-empty-parse) plus **census off the roster**, not a prettier TSV.
