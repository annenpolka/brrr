# oath

Parse **assertion literals**, not comments. Emit the machine condition those assertions imply as a skip/apply predicate.

A comment containing `HOME` or a username is not an oath. `assertEqual` / `XCTAssertEqual` / `#expect` second arguments, snapshot goldens, and pytest `expected=` are. Empty require means portable.

visa scanned a whole recording (comments included). oath flips the window.

## Install / run

Python 3.10+, stdlib only.

```bash
chmod +x ./oath
./oath --help
./demo.sh
./oath --self-test
```

## Three examples

### 1. A comment is not an oath. An env assert is.

```bash
./oath fixtures/comment_only.py
# oath  fixtures/comment_only.py  OPEN
#   silent   comment L1  USER=alice  ran on alice
#   apply    true

./oath fixtures/env_assert.py
# oath  fixtures/env_assert.py  BOUND
#   require  USER=alice
#   window   assert  L6  expected="alice"
#   silent   comment L5  USER=alice  ran on alice   ← seen, not required
#   apply    [ "${USER}" = alice ]
```

`--emit pytest` prints skipif polarity (true → skip):

```bash
./oath --emit pytest fixtures/env_assert.py
# not (getpass.getuser() == 'alice')
```

### 2. Sitbone window titles are identity-as-data, not USER=

```bash
./oath Tests/SitboneCoreTests/WindowTitleParserTests.swift
# oath  …/WindowTitleParserTests.swift  FIXTURE
#   window   string  L10  GitHub - annenpolka/sitbone · Pull Request #3 …
#   window   XCTAssertEqual  L13  expected="GitHub"
#   witness  fixture  USER=annenpolka
#   apply    true
```

`--apply` exits 0 (FIXTURE/OPEN/SPEC always match). A recording leak `assert_eq!(home, "/Users/annenpolka/proj")` is BOUND.

### 3. Pipe a red test, or scan a repo

```bash
pytest -q | ./oath --from-fail
# oaths the expected side (pytest / cargo / XCTest / Jest / Go / JUnit / …)

./oath --scan -C /path/to/repo --porcelain
./oath --apply --match fixtures/local.snap; echo $?
# 1  on this host (you are not alice)
```

`--emit gha` is a coarse `runs-on` projection of the oath, not the product.

## Why this is not visa

visa asked "what machine does this file demand?" and had to invent textbook/payload rules because comments and quoting fixtures looked like recordings. oath never opens that window: comments are silent, assertion expecteds name the axis, the literal names the machine. `assert os.environ['USER'] == 'alice'` is an oath even though alice is a textbook name. `# ran on alice` is not.
