# DESTROYER — cinch × hasp

Adversarial pass on 1-minimal *locksets*. Failures are conceptual except one crash.

- **cinch** (dirty-tree lockset, whole suite at NEW) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-03-cinch`
- **hasp** (PR-range lockset, only tests born in the range) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/hybrid-06-hasp`
- Transcript: `/tmp/destroy-cinch-hasp/transcript.txt`
- Follow-up: `/tmp/destroy-cinch-hasp/followup.txt`
- Fixtures: `/tmp/destroy-cinch-hasp/fixtures/`
- Attack driver: `/tmp/destroy-cinch-hasp/attack.py`
- cinch 0.2.0 units 10/10; hasp 0.2.0 units 14/14. `./demo.sh` both `demo OK` after the attacks.

Attacks: empty test suite, failing tests, generated files as tests, huge dirty trees, timeouts, nested git, unicode paths, tests that always pass.

One fail-closed one-liner applied (binary stdout). Everything else left.

Verdict: **mutate both, do not kill.** The object is still “drop this production hunk and the tests go red.” cinch and hasp still disagree on the *same* tree (MUTE vs LOCKED) the way the hybrid pitch said they would. The attacks show where empty/timeout/codegen/nested-git are reported as that object.

---

## cinch

Primitive restated: dirty tree vs `--base`. Tests stay at NEW. Wheat is the 1-minimal production subset the *current* command requires.

## hasp

Primitive restated: two revisions (`A...B`). Lock is only named tests that *appear* in the range. Updated old tests are background. Production with no new names is MUTE.

---

## 1. Empty suite — EMPTY is honest; exit 5 is a magic number (conceptual)

Dirty `app.py` (`return 0` → `return a + b`), `tests/` exists, no test files. Default `unittest discover -s tests`:

```
$ ./cinch -C $EMPTY_SUITE --json
status EMPTY  trials=1  prod=1  wheat=[]  chaff=['app.py#1']
new_run exit_code=5  "Ran 0 tests" / "NO TESTS RAN"
# rc=5  elapsed=0.105s
```

Same with no `tests/` dir at all (`discover -q`, rc=5, 0.103s). v2’s EMPTY ≠ BROKEN holds.

hasp on the same dirty tree (`HEAD...worktree`) never runs the command:

```
$ ./hasp -C $EMPTY_SUITE --json HEAD
status MUTE  trials=0  prod=1  new_tests=[]
note: no new tests in the range; production is unhasped
# rc=6  elapsed=0.075s
```

**Test-only red is CLEAN.** Dirty `test.py` (`assert add(2,3)==99`), production unchanged:

```
$ ./cinch -C $TEST_ONLY_RED --json -- python3 test.py
status CLEAN  trials=0  prod=0  held_tests=['test.py']
note: no production source units differ from base; skipped test runs
# rc=0  elapsed=0.064s
```

CANDIDATE already named this. Confirmed: a red suite with zero production units is occupancy of nothing, reported as clean. The tests are not run.

**Exit 5 is not “no tests.”** Custom runner prints `actually failed 5 assertions` and `sys.exit(5)`:

```
$ ./cinch -C $EXIT5 --json -- python3 fail5.py
status EMPTY  new_run.output_tail=["actually failed 5 assertions"]
chaff: app.py#1 AND fail5.py#1 (new file, classified production)
# rc=5  elapsed=0.090s
```

`empty_suite()` is `exit_code == 5` first, banner second. pytest-empty and a runner that uses 5 for “failed” are the same status. `fail5.py` itself is wheat-candidate production (`.py` not `test_*`).

Default discover on nested-git (assert-scripts, no TestCase) is the same EMPTY (`Ran 0 tests`, rc=5, follow-up). `test.py` is held; it is not collected.

---

## 2. Failing tests — BROKEN is closed; NEW-red is unaskable (operational, load-bearing)

Assertion fail / `assert False` / `from missing_mod import nope` on NEW:

```
status BROKEN  trials=1  note: refusing to isolate while the new tree is already red
# rc=3  elapsed≈0.10s
```

hasp with dirty `add()` returning 0 against new `test_add`: BROKEN rc=3. Restored committed PR: LOCKED `app.py#1` (`return a + b`), chaff `extra()` + `DEBUG`, 4 trials, 0.236s. Demo case 1 still holds.

This is the right refuse. Isolation is pass/fail of NEW. A suite that is already red has no lockset.

---

## 3. Generated files as tests — `dist`/`build` vanish; `generated/` is the lock (conceptual)

`--list` on a tree that adds identical tests in five places plus a snapshot:

```
$ ./cinch -C $GENERATED --list --json
production: app.py#1
held_tests: generated/test_gen.py, snapshots/add.snap, vendor/pkg/test_vendor.py
# dist/test_dist.py, build/test_build.py, __pycache__/test_pyc.py absent
```

`SKIP_DIR_NAMES` has `dist`, `build`, `__pycache__`. It does not have `generated/` or `vendor/` (vendor is only `LINK_DIR_NAMES`). `*.snap` is a test path. Directory name is the policy.

`-- python3 generated/test_gen.py` on that tree: **LOCKED** `app.py#1`, 2 trials, 0.115s. Real tests still assert the *old* `add==0` (BROKEN if you pass `test.py`). The codegen file is a believer the tool will treat as the suite.

hasp on a committed codegen test:

```
$ ./hasp --list main...HEAD
new-test    generated/test_gen.py::G.test_add
$ ./hasp --json main...HEAD
status LOCKED  wheat=['app.py#1']  cmd=["hasp-run","generated/test_gen.py::G.test_add"]
# rc=0  elapsed=0.160s
```

v2 demoted goldens/fixtures. It did not demote `generated/test_*.py`. A regenerated oracle is a lock, not a leftover *build*. Same class as zanei’s `generated/` believer.

---

## 4. Huge dirty trees — 1-wheat is cheap; all-required is a trial budget (operational)

80 chaff modules + one real `add()` hunk. Test only imports `app`:

```
$ ./cinch -C $HUGE_CHAFF --json -- python3 test.py
status LOCKED  trials=9  prod=80  wheat=['app.py#1']
# rc=0  elapsed=1.050s
```

ddmin finds the one hunk. The primitive works at this size.

48 modules, test asserts `N==1` in every file (all required):

```
status LOCKED  trials=188  prod=48  wheat=all 48  elapsed=6.450s
```

Default `--max-trials 200` survived. Cap it:

```
$ ./cinch -C $HUGE_ALL --max-trials 20 -- python3 test.py
cinch: exceeded --max-trials 20
# rc=2  elapsed=1.261s
```

All-required isolation is O(n) complements plus leave-one-out. ~64 independent hunks would blow the default 200 and look like a tool error, not “the tests require everything.” No warning that the budget is the object.

Godfile (~40k comment lines, two hunks): LOCKED `app.py#2` (the `VALUE` line), header-comment chaff, 4 trials, 0.183s. Size is not omit.

hasp `HEAD~1...HEAD` on the 40-file chaff commit: **MUTE** in 0.632s. The range rewrote `test.py` (`assert add==0` → `==5`) but that file has no `test_*` names and already existed, so it is not `<module>` and not a new test. An updated assert-script is invisible to hasp. cinch on the dirty form of the same tree locked `app.py#1`. Complementary holes: cinch will isolate a tautology-free assert-script; hasp will not see it as a lock.

---

## 5. Timeouts — timeout is fail, so a speed hunk is wheat (conceptual)

NEW sleeps 8s, `--timeout 0.4`:

```
status BROKEN  new_run exit_code=124 timed_out=true
output_tail: [cinch: timed out after 0.4s]
# rc=3  elapsed=0.502s
```

Honest refuse (NEW never went green).

The load-bearing case: production has `FAST=False` / `VALUE=0` → `FAST=True` / `VALUE=1`. Tests sleep 8s unless `FAST`, then `assert VALUE==1`. `--timeout 0.5`:

```
$ ./cinch -C $TIMEOUT_LOCK --timeout 0.5 -- python3 test.py
status LOCKED  trials=4  wheat=['app.py#1','app.py#2']
new_run pass 0.015s
splice_run timeout 0.504s  [cinch: timed out after 0.5s]
# rc=0  elapsed=1.164s
```

Drop `FAST` and the assertion would still pass in 8s. Timeout maps to fail, so *both* hunks veto. Wheat is “the tests finish before the budget,” not “the tests require VALUE.” Witnesses on both hunks are `[]` (no FAIL line; the child was killed).

`--timeout 0`: NEW times out in 0.001s, BROKEN. A predicate that is actually green is occupancy-dead.

hasp, same story, adjacent lines collapsed to one hunk:

```
$ ./hasp --timeout 0.5 main...HEAD
status LOCKED  wheat=['app.py#1']  added=["FAST = True","VALUE = 1"]
new: T.test_new  background: T.test_old
splice exit_code=124 timed_out=true
# rc=0  elapsed=0.655s
```

`pgrep time.sleep` empty after the battery. No process-group leak cited. The mapping timeout→fail is the miss either way.

---

## 6. Nested git — inner worktree is outer production (conceptual)

Untracked `nested/` with its own `.git`, dirty `inner.py` / `test_inner.py`. Outer `git status`: `M app.py`, `M test.py`, `?? nested/`.

```
$ ./cinch -C $NESTED --list
prod   2 production unit(s)
  production  modify app.py  #1
  production  add    nested/inner.py  #1 (new file)
  test        nested/test_inner.py  (held)
  test        test.py  (held)
```

`.git` inside nested is skipped. The *files* are not. `-- python3 test.py` correctly chaffs `nested/inner.py` (3 trials, LOCKED `app.py#1` only). Default discover is EMPTY (assert-scripts). `-C nested` isolates the inner repo honestly (`inner.py#1` wheat).

hasp `main...HEAD` on a committed PR with an untracked inner repo: `--list` does not see `vendor_src/` (committed range, `git archive`). `-C vendor_src --list HEAD` is CLEAN (inner HEAD vs its worktree). Nested dirt is a *worktree* object. cinch’s dirty-tree walk is the one that swallows it.

---

## 7. Unicode paths — names work; unittest collection is the EMPTY (survived / operational)

NFC `café.py`, `日本語/app.py`, `tests/test_日本語.py` (`def test_カフェ`, not a TestCase), NFD `src/café_nfd.py`, emoji markdown:

```
$ ./cinch -C $UNICODE --list
  production  modify café.py
  production  add    src/café_nfd.py    # listed NFC; APFS inode-collapses NFD
  production  modify 日本語/app.py
  test        tests/test_日本語.py  (held)
  ignored     docs/emoji 🌀.md
```

`-- unittest discover -s tests` → EMPTY (`Ran 0 tests`). The file is held; discover wants TestCase, not `def test_*`. Not a path codec bug.

Same names as unittest.TestCase (follow-up `unicode-case`):

```
status LOCKED  wheat=['café.py#1']  chaff=['日本語/app.py#1']
witnesses: test_値
# rc=0  elapsed=0.182s
```

hasp `tests/test_日本語.py::カフェ.test_値` LOCKED `café.py#1` in 2 trials, 0.157s. Japanese class/method ids round-trip through the runner (`_hasp_tests_test_日本語_py.カフェ.test_値`).

APFS: NFC and NFD `café.py` are ino 120771921. Last write wins. One production add. Paths are not the hole.

---

## 8. Tests that always pass — LOOSE is honest; skip is pass; `<module>` is a fake lock (conceptual)

`def test_ok(): assert True` plus a rewrite of `app.py` and a new `lib.py`:

```
$ ./cinch --json -- python3 test.py
status LOOSE  trials=2  prod=2  wheat=[]  chaff=[app.py#1, lib.py#1]
note: tests pass with every production hunk reverted
# rc=2  elapsed=0.105s
```

hasp new `N.test_always`: same LOOSE, rc=2. unittest `@skip` on the only test: LOOSE (`OK (skipped=1)` on NEW *and* splice). A skipped suite is occupancy of the constant True.

**hasp empty new test file** (`tests/test_new.py` is a comment, no `test_*`):

```
$ ./hasp --list main...HEAD
new-test    tests/test_new.py::<module>
$ ./hasp --json main...HEAD
status LOOSE  cmd=["hasp-run","tests/test_new.py::<module>"]
new_run: "tests/test_new.py ... ok"
```

v2 still mints `<module>` for a *new* Python test path with zero names, then `exec`s it. Empty `exec` succeeds. MUTE would match the pitch (“no new tests”). LOOSE says there *was* a lock that locked nothing. The runner printed `... ok` for a comment.

Rename `test_add` → `test_addition` (same body) + `DEBUG = True`: hasp lists `T.test_addition` as new, background empty, LOOSE (the body still passes on old `add()`). Identity is the name. A reworded `it("…")` analogue in Python.

MUTE vs cinch on the dedicated fixture (updated `test_extra`, no new name): hasp MUTE rc=6; cinch `--base main` LOCKED `app.py#1` in 2 trials. That contrast is the hybrid’s object. It survived.

---

## 9. Binary stdout — was a crash; fail-closed one-liner applied

Before:

```
$ ./cinch -C $BINARY --json -- python3 test.py
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 1
# rc=1  traceback from run_cmd subprocess.run(text=True)
```

`run_cmd` already special-cased `FileNotFoundError` and `TimeoutExpired`. Binary child stdout was uncaught. Exit 1 is not a cinch status.

Applied in both worktrees (the only rewrite):

```python
except UnicodeDecodeError as e:
    raise CinchError(f"binary test output: {e}", 2) from e
```

After:

```
cinch: binary test output: 'utf-8' codec can't decode byte 0xff in position 1: invalid start byte
# rc=2  elapsed=0.111s
```

hasp’s default runner never hits it: `unittest.TextTestRunner(buffer=True)` makes `sys.stdout` a StringIO, so `sys.stdout.buffer.write(b'\x00\xff')` is `AttributeError` → BROKEN rc=3 (`ERROR: test_bin`). Different object (buffered test error), already refused. The one-liner is for `--cmd` / raw scripts. Units 10/10 and 14/14, both `./demo.sh` still 0.

Not a primitive fix. Left as the one allowed closed crash.

---

## 10. Index / empty / not-git — sandbox is not a git repo (documented, confirmed)

Staged `app.py` (`git add`), test asserts `'X = 1' in git diff --cached`:

User tree: the staged hunk is real. Sandbox: no `.git`, so git picks `diff --no-index` and dies `unknown option cached` (rc=129). cinch BROKEN rc=3. CANDIDATE said “commands that consult the git index see a lie.” They see *no repository*. Stronger than a lie.

Empty repo (init, dirty `app.py`, no commits): `cinch: unknown revision 'HEAD'` / `hasp: unknown revision 'HEAD'`, rc=2, no traceback. Not-a-git: `not a git repository: …`, rc=2. Closed. Occupancy of a commit-less dirty tree is unaskable (same class as held `--now` on empty).

---

## What survived

- Demo money shots: cinch drops `print("debug")`, keeps `return a + b`; hasp locks `test_add` / chaffs updated `test_extra`+`DEBUG`; MUTE vs cinch LOCKED on the no-new-name PR. Both `./demo.sh` exit 0.
- BROKEN on NEW-red (assert / import / hasp dirty `add()`).
- EMPTY on real unittest-zero (the tenaoshi v2 story).
- 80-file chaff → 1 wheat in 9 trials / 1.05s. Godfile header vs `VALUE` split. Unicode TestCase / hasp `カフェ.test_値` lock `café.py`.
- Ugly paths already in demo (spaces/parens). NFC listing of an NFD twin (APFS one inode).
- Nested `-C nested` isolates the inner repo. hasp committed range does not ingest untracked inners.
- FOREIGN still refuses Swift (demo case 14). Isolation still Python-only.
- User worktree never rewritten (sandbox `/tmp/cinch-*` / `/tmp/hasp-*`).
- `--help` / `--version`. Units green after the binary one-liner.

---

## Kill / keep

**Keep both. Mutate both.**

The lockset is still not `alibi | winnow`. Case 1 on both demos is the proof. Generated/`<module>`/timeout/exit-5 are where the predicate pretends to be “tests require this hunk.”

| tool | do not kill because | mutate toward |
| --- | --- | --- |
| cinch | Dirty-tree 1-minimal still splits debug-print from return; 80-chaff and godfile still 1-wheat. EMPTY on real zero-collect. | Always run NEW (test-only red is BROKEN, not CLEAN). Exit 5 is pytest-empty, not a universal “no tests” (banner without 5, or require the banner). Timeout is unknown, not fail — a speed hunk must not be wheat. `generated/` / `vendor/` are not a suite. Nested untracked git is not outer production (or a dedicated note). `--max-trials` on all-required should say “every hunk is required” instead of dying. |
| hasp | Range object still MUTE when cinch LOCKED; named new tests still lock one hunk. Unicode names and FOREIGN survive. | Empty/`# comment` new files are MUTE, not `<module>` LOOSE. Updated assert-scripts without `test_*` are either a lock or they are not — pick one. Codegen `generated/test_*.py` is a fixture unless `--keep`. Timeout same as cinch. Isolation still Python-only (FOREIGN is honest; `--cmd` that runs the *whole* suite is cinch’s object). |

A one-line `generated` add to `SKIP_DIR_NAMES` would hide the codegen lock and would not touch timeout-as-wheat, exit-5, or test-only CLEAN. Not applied. Binary stdout was a crash and is closed.
