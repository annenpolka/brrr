# mutation-44 — oath

## Primitive

Parse assertion literals (not comments) so an oracle's implied machine is a skip/apply predicate. A comment containing HOME or a username is not an oath; `assertEqual` / `XCTAssertEqual` / `#expect` second arguments, snapshot goldens, and pytest expected= are.

## Why this might not exist

visa (mutation-27) is unary: one recording in, the visa it demands. It still *read the whole file*. v0.1 lied on kizu textbook paths; v0.2 invented payload heuristics because comments about `/Users/John Doe` and `macOS PollWatcher` looked like recordings. lees (candidate-31) named the leftover mutation: "Parse only assertion literals (not comments)."

The daily loop is: a red CI log, a test file with `# ran on alice` in a comment and `assert os.environ['USER'] == 'alice'` in the body. Developers already know which one is the machine demand. Nobody parses that distinction. Snapshot serializers normalize going forward; `diff` does not know HOME; pytest `skipif` is written by hand after someone already decided.

Flip: the window is the assertion, not the file. Empty oath ⇒ portable.

Discarded as conventional: wrapping `uname`, generating a Dockerfile, becoming clutch/sinter. `--emit gha` is a coarse projection, not the product.

## How to run

From this worktree root:

```bash
./demo.sh
./oath --help
./oath --self-test
python3 -m unittest discover -s tests -q
./oath fixtures/comment_only.py
./oath fixtures/env_assert.py
./oath --apply --match fixtures/local.snap
./oath --emit pytest fixtures/env_assert.py
./oath --scan -C /path/to/repo --porcelain
pytest -q | ./oath --from-fail
```

## Empirical transcript

### v0.1 — assertion window works; relative paths lie as fixtures

`./oath --self-test` 44/44. Unittest 29/29. Gold:

```
# ran on alice          → OPEN, silent comment USER=alice, apply true
assert os.environ['USER'] == 'alice'  → BOUND require USER=alice
both in one file        → require from the assert; comment still silent
fixtures/local.snap     → BOUND HOME=/Users/alice platform=Darwin
fixtures/spec_only.snap → OPEN
fixtures/conflict.snap  → UNSAT
WindowTitleParserTests  → FIXTURE USER=annenpolka, require empty
```

lees `--par` alice vs CI is MACHINE / empty residue. oath is unary: `local.snap` and `ci.snap` are two machines, not a substitution.

Dogfood `--scan` (this host, 2026-08-20, v0.1):

| repo      | BOUND | OPEN | SPEC | UNSAT | FIXTURE | note |
| --------- | ----- | ---- | ---- | ----- | ------- | ---- |
| sitbone   | 0     | 21   | 0    | 0     | 4       | title fixture correct; extra slash-paths |
| kizu      | 0     | 3    | 2    | 0     | **13**  | `src/auth.rs` treated as owner/repo |
| voidtrace | 0     | 67   | 0    | 0     | 0       | goldens are numbers |
| tenaoshi  | 0     | 12   | 0    | 0     | 5       | `application/json`, `contracts/testcases` |

kizu e2e `waitForText("src/auth.rs")` became FIXTURE USER=src. The fixture detector inherited visa's "any slash is owner/repo".

### v0.2 — fixture is GitHub identity, not a slash

Relative paths, MIME types, `https://example.invalid`, and `async/await` in a Chrome title are not owner/repo. GitHub titles and `github.com/owner/repo` still are.

After:

```
$ ./oath fixtures/comment_only.py
oath  fixtures/comment_only.py  OPEN
  silent   comment L1:1  USER=alice  ran on alice
  apply    true

$ ./oath fixtures/env_assert.py
oath  fixtures/env_assert.py  BOUND
  require  USER=alice
  window   assert  L6:5  expected="alice"
  silent   comment L5:5  USER=alice  ran on alice
  apply    [ "${USER}" = alice ]

$ ./oath sitbone/…/WindowTitleParserTests.swift
oath  …/WindowTitleParserTests.swift  FIXTURE
  window   string  L10  GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome
  window   XCTAssertEqual  L13  expected="GitHub"
  witness  fixture USER=annenpolka
  apply    true

$ ./oath kizu/src/init/tests.rs
oath  …/init/tests.rs  SPEC
  window   assert_eq!  L472  expected="'/Users/John Doe/kizu'"
  silent   comment L424  HOME=/Users/John Doe   ← the doc, not an oath
  witness  payload HOME=/Users/John Doe         ← the assertion, spec of a quoter
```

Dogfood `--scan` after the fixture tighten:

| repo      | BOUND | OPEN | SPEC | UNSAT | FIXTURE | note |
| --------- | ----- | ---- | ---- | ----- | ------- | ---- |
| sitbone   | **0** | 21   | 0    | 0     | 4       | all four USER=annenpolka, kind=fixture |
| kizu      | 0     | 13   | 2    | 0     | 0       | textbook asserts SPEC; comments silent |
| voidtrace | 0     | 67   | 0    | 0     | 0       | portable goldens |
| tenaoshi  | 0     | 17   | 0    | 0     | 0       | MIME/paths no longer fixtures |

sitbone v0.1 false TAINTED on `annenpolka` in a window-title fixture stays 0 BOUND (kind=fixture). `--from-fail` now also reads pytest / cargo / XCTest / Jest / Go / JUnit / RSpec / Vitest / PHPUnit, and keeps the source `assert os.environ['USER'] == 'alice'` so a dump of that failure is still USER=alice.

`./demo.sh` → passed=42 failed=0. Unittest 31/31.

## Dogfood targets

- `fixtures/` — comment vs env-assert, alice/CI snaps, sitbone-shaped title, kizu quoting payload, `#expect`, ugly unicode/spaces, pytest/cargo/jest/go/junit/xctest dumps
- This host's live `$HOME`/`$USER` written into `demo-tmp/live.snap` (MATCH) vs alice (MISS)
- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,voidtrace,tenaoshi}` `--scan`

## Surprises

- The flip is visible on one file: `env_assert.py` has `# ran on alice` *and* `assert os.environ['USER'] == 'alice'`. visa would have bound both; oath requires only the assert and prints the comment as `silent`.
- sitbone needed no live-USER stain (visa's flip) *and* no whole-file scan: `XCTAssertEqual(result, "GitHub")` expected is `"GitHub"`; `annenpolka` lives in the `from:` fixture string and stays kind=fixture.
- kizu `init/tests.rs` is the object lesson for the assertion window: the comment about `/Users/John Doe` is silent; the `assert_eq!(shell_single_quote("/Users/John Doe/kizu"), …)` expected is payload SPEC (quoting spec, not a skip). visa v0.1 would have been UNSAT from two layouts; oath never asks the comment.
- voidtrace `.expected.json` goldens are the empty case: numbers, no host. OPEN is a result.
- `--from-fail` on `assert got == want` must not treat the *names* `got`/`want` as expected literals; the E +/- dump is the oracle.

## Failures

- Assertion strings that wrap across lines with a message as a third argument are parsed as call-args (usually fine); Swift `#expect` with `<>` generic noise is not.
- `skills` was not in this dogfood set. `--scan` still says `no oracle-like files` on trees without test/golden names.
- HOST is reported soft and is not part of `--apply`. A laptop rename would otherwise skip a still-valid USER oath.
- `--emit gha` cannot express `USER=alice`. The shell/pytest predicate is the real oath; runs-on is a coarsening.
- Python `tokenize` fallback on a broken file uses the generic scanner, which can miss a statement after a syntax error.

## Suggested mutations

- Infer an oath from the *actual* side of `--from-fail` as well, and pair them: two oaths, not lees residue.
- `--held`-style: given an oath, walk history for the commit where an assertion newly acquired it (when the test became machine-tied).
- Join with alibi: splice tests onto old production, then oath the failure (LOCKED-and-BOUND vs LOCKED-and-OPEN).
- Resolve `expected = home; assert got == expected` by following the name inside the function.

## Kill / keep

**Keep.** The object is new: a skip/apply predicate implied by assertion literals, with comments explicitly not in the window. sitbone stays FIXTURE (not TAINTED, not BOUND). kizu comments about John Doe are silent; quoting asserts are SPEC. `# ran on alice` is not an oath; `assert os.environ['USER'] == 'alice'` is. Not `uname`, not visa's whole-file scan, not lees `--par`.
