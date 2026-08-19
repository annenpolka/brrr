# mutation-41 — till

## Primitive

Production argument worlds as a **runnable test file**, with **rename-follow**: the subject name at HEAD is not the identity. If `isBrowser` was `isWebApp` last week, production callers of the old name still define worlds tests owe.

## Why this might not exist

`sow` (mutation-13) made production argument worlds into fixture records. `hatch` (mutation-30) flipped the object: default stdout is XCTest/pytest. Both still key the subject by the **token living at HEAD**. Coverage, `grep fn(`, and `git log -S` also key by a name. None of them answer: *production used to call `isWebApp("Brave Browser")`; the function is now `isBrowser`; tests never pass Brave — here is the XCTest method.*

The missing Unix verb is **identity across a rename**, not another coverage number.

Flipped assumption: `git log --follow` / def-line hops in the range. `--no-follow` is hatch. `--report` is sow. `--check` still exits 1 if any due world exists.

## How to run

```bash
./till --help
./demo.sh
./till --self-test
./till -C fixtures/ugly isBrowser
./till --report -C /path/to/repo isBrowser
./till --check -C /path/to/repo isBrowser
./fixtures/rename/build.sh /tmp/till-rename
./till --no-follow -C /tmp/till-rename/leftover isBrowser   # misses Brave
./till             -C /tmp/till-rename/leftover isBrowser   # emits Brave as isBrowser(...)
./till             -C /tmp/till-rename/leftover isWebApp    # query by the dead name
./till --aka-map -C /path/to/repo
```

Exit 0 on success. `--check` exits 1 if any due fixture. Errors exit 2.

## Empirical transcript

### Before the improvement (v0.1)

Self-test + rename fixture already proved the flip:

```
./till --no-follow --emit pytest -C leftover isBrowser
# no generable due fixtures

./till --emit pytest -C leftover isBrowser
# def test_isBrowser_name_Brave_Browser():
#     isBrowser(name="Brave Browser")

./till --emit pytest -C leftover isWebApp
# same file — dead name follows to HEAD name
```

Sibling `hatch` and `sow` on the same leftover tree: `# no generable due fixtures`.

sitbone `isBrowser` still emitted six `XCTAssertTrue` methods. Overlay `swift test --filter WindowTitleParserHatchTests`: **Executed 6 tests, with 0 failures**. `--check` exits 1. `extractSiteName` silent. `record(duration: 1)` is `XCTSkip`, no Swift `...`.

Census (analysis unchanged from hatch v0.2; identity is the new axis):

```
sitbone    files=49  defs=409  calls=3072  prod_fns=133  due_fns=65  due=80  generable=24  aka_fns=4
kizu       files=70  defs=1022 calls=10555 prod_fns=382  due_fns=242 due=335 generable=111 aka_fns=4
tenaoshi   files=25  defs=170  calls=1599  prod_fns=107  due_fns=64  due=94  generable=36  aka_fns=0
```

### After the improvement (v0.2)

Dogfood showed four real sitbone identities (`stopSession` → `stopCapture`) that `--report` hid because they were sown. Named `--report` now keeps sown aka chains. `--aka-map` prints the table. Test-path hunks no longer steal a production hop (hist fixture went silent until hunks flushed on `diff --git`). Concrete `is*`/`has*` worlds get `XCTAssertTrue` / `assert`, so leftover Swift is an assert, not a bare call.

```
./till --report -C sitbone stopSession
# AVCameraFrameProvider.stopCapture  …  sown
#   aka  stopSession → stopCapture
#   follow  stopSession → stopCapture  CameraFrameProvider.swift  38caadc6

./till --no-follow --report -C kizu install_claude_code
# no due fixtures  prod_fns=0 due=0          ← hatch/sow

./till --report -C kizu install_claude_code
# install_settings_hook_agent  src/init/install.rs:193  4 due
#   aka  install_claude_code → install_settings_hook_agent
#   follow  install_claude_code → install_settings_hook_agent  src/init.rs  98870f20
```

## Dogfood targets

- `fixtures/ugly` — Python, JS, Rust (lifetimes), Swift; unicode path; colon filename; spaces; comments; nested git
- `fixtures/rename` — leftover old-name callers + historical-only literals
- sitbone `isBrowser` / `record` / `extractSiteName` / `stopSession` (read-only; overlay `swift test`)
- kizu `run_split_command` / `install_claude_code` (read-only)
- tenaoshi `PromptStore.validate` (read-only; no renames in range)

## Surprises

- sitbone never renamed `isBrowser`. The six Brave/Chromium/Edge/Opera/Orion/Vivaldi members are still the hatch gold — rename-follow is a no-op on that subject and must stay one.
- sitbone *did* rename `stopSession` → `stopCapture` (38caadc). Tests already inhabit every production world, so the identity is sown. The useful output is the aka line, not a test file. `--report` that drops sown functions hides the primitive.
- kizu `install_claude_code` is a dead HEAD token. Querying it with hatch/sow/`--no-follow` is silence (`prod_fns=0`). till follows it onto `install_settings_hook_agent` and the four agent-kind worlds (`claude-code` / `codex` / `qwen` + dyn). That is the real-repo rename fixture.
- A hunk attributed to the *next* file (`+++ b/tests/...`) made v0.1 drop the only hop in the hist fixture once test-path hops were filtered. Flush on `diff --git` / `+++` before changing path.

## Failures

- Same-named methods across types still share unprefixed calls.
- Instance methods have no `self` construction (`record` cannot be a real call without a `SiteObserver()`).
- `is_hunk_seen` → `hunk_fingerprint` (via `seen_hunk_fingerprint`) is a real evolution but two live successors exist; newest hop wins.
- JS/TS options-bag worlds remain coarse.
- Whole-tree `--check` is noisy; the useful invocation names a function (or an old name).
- tenaoshi had `aka_fns=0` in the scanned range — not every dogfood tree has a rename.

## Suggested mutations

- Construct `Type()` / use existing test fixtures when the subject is an instance method.
- Append into an existing XCTestCase instead of a sibling `*HatchTests` class.
- Rank / hide display-wrapper functions before emitting a whole-tree file.
- Join with `seep`: emit the timeout=0 world first because it does IO.
- Walk `git log -L` / tree-sitter for hops that are not on adjacent def lines.

## Kill / keep

**Keep.** The flip is real: sow/hatch on the leftover rename fixture emit nothing; till emits `isBrowser("Brave Browser")` (and `XCTAssertTrue` for the Swift twin). sitbone still runs 6/6. kizu `install_claude_code` is silence for the parents and four due worlds for till. Kill only if a later generation proves the real object is a patch against the existing test file, not a new file on stdout.
