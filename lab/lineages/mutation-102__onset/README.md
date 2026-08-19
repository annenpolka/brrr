# onset

When did an assertion newly acquire an **actual-bound machine**?

`held` occupies a boolean. `mint` occupies production clearance. `troth` names the legal apply set of one fail dump. `onset` walks git history of **assertion windows** and emits the commit where the *actual side* first names a machine (this host's `$HOME`, `/Users/alice`, …).

Comments are not oaths. GitHub titles stay FIXTURE, not TAINTED. Expected-side BOUND is a different first. Nested call arguments (`quote("/Users/alice")`) are not the actual.

## Install / run

Python 3.9+, stdlib only, `git`.

```bash
chmod +x ./onset
./onset --help
./demo.sh
./onset --self-test
./onset -C /path/to/repo
./onset --from-fail < fail.txt
```

Exit 0 if first-actual-bound is distinct from first-assertion (including "never ACTUAL-BOUND"). Exit 1 if they coincide. Exit 2 on usage / not a repo.

## Three examples

### 1. OPEN expected is not ACTUAL-BOUND

```bash
./onset fixtures/env_assert.py
# EXPECTED-BOUND  USER=alice  actual-bound 0
# the comment `# ran on alice` is silent

./onset fixtures/actual_literal.swift
# ACTUAL-BOUND  HOME=/Users/alice  (the first argument of XCTAssertEqual)
```

`assert os.environ['USER'] == 'alice'` binds the *expected* side. `XCTAssertEqual("/Users/alice/Library", "/tmp/x")` binds the *actual* side. Those are two onsets.

### 2. A title is FIXTURE, not TAINTED

```bash
./onset fixtures/title.swift
# FIXTURE  USER=annenpolka  identity-as-data
# XCTAssertEqual(result, "GitHub") does not bind a machine
```

sitbone's `WindowTitleParserTests` contains `annenpolka/sitbone`. That is not `$HOME` as the actual. `--scan` / `--walk` keep it FIXTURE.

### 3. History: first-actual ≠ first-assertion

```bash
./onset -C /path/to/repo --eras
```

```
onset  demo  5 commits  first-parent
  first-assertion  …  t0  tests/test_open.py     OPEN
  first-expected   …  t2  tests/test_user.py     USER=alice
  first-actual     …  t4  tests/test_actual.swift this-host HOME=$HOME
  first-fixture    …  t3  tests/test_title.swift  USER=annenpolka
  distinct         yes  first-actual ≠ first-assertion
```

`git log -S /Users/` fires on comments, titles, and expected goldens. onset does not.

Default walk is **first-parent**. The header prints `24 of 244 commits` when that walk hides reachable history. If a first-* is a merge, onset hints `rerun with --full` — kizu's assertion birth is `feat(git)` (`1f32f50`), not Merge PR #2; sitbone's FIXTURE birth is `WindowTitleParserTests`, not Merge PR #1.

`--full` walks every reachable commit. `first-spec` is the quoting/textbook onset (`/home/user`, `John Doe`) and is not ACTUAL-BOUND.
