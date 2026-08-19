# mutation-102 — onset

## Primitive

`onset` emits the commit where an assertion window newly acquired an **actual-bound machine** (this host's `$HOME`, `/Users/alice` as the *actual* side). held occupies a boolean; mint occupies production clearance; troth names the legal apply set of one dump. onset's object is the **era of ACTUAL-BOUND**, and it is distinct from first-assertion, first-expected, first-fixture, and first-spec.

## Why this might not exist

troth `--apply` is `OPEN expected ∪ ACTUAL-BOUND-if-this-host`. The leftover question is *when* the actual-bound machine appeared. `git log -S /Users/` fires on comments (`# ran on alice`), GitHub titles (`annenpolka/sitbone`), expected goldens (`assert USER == 'alice'`), and nested quoting args (`quote("/Users/John Doe")`). `held grep /Users/` occupies a string. mint births production visas. Nobody walks assertion windows and asks: *when did the actual side become a machine?*

Discarded: lees `--par` clone. Discarded: visa-of-the-whole-file. Discarded: leftover-name. Discarded: treating `# ran on alice` as an oath. Discarded: treating sitbone titles as TAINTED.

## How to run

From this worktree root:

```bash
./demo.sh
./onset --help
./onset --self-test
python3 -m unittest discover -s tests -q
./onset fixtures/comment_only.py
./onset fixtures/env_assert.py
./onset fixtures/actual_literal.swift
./onset fixtures/title.swift
./onset fixtures/payload.rs
./onset --from-fail < fixtures/xctest_fail.txt
./onset -C /path/to/repo
./onset -C /path/to/repo --eras
./onset -C /path/to/repo --full --porcelain
```

## Empirical transcript

### v0.1 (`5ac8dd9`) — first-actual ≠ first-assertion; first-parent names the merge

`./onset --self-test` ok. Unittest 7/7. `./demo.sh` passed=28 failed=0.

```
$ ./onset fixtures/env_assert.py
onset  fixtures/env_assert.py  EXPECTED-BOUND
  expected   L6 assert BOUND alice  USER=alice
  comment    L5 comment SILENT  USER=alice  ran on alice
  # actual-bound 0

$ ./onset fixtures/actual_literal.swift
onset  …/actual_literal.swift  ACTUAL-BOUND
  actual     L2 XCTAssertEqual BOUND alice  HOME=/Users/alice

$ ./onset fixtures/title.swift
onset  …/title.swift  FIXTURE
  fixture    L3 string FIXTURE  USER=annenpolka
  note: FIXTURE is identity-as-data, not TAINTED

$ ./onset fixtures/payload.rs
onset  …/payload.rs  SPEC
  expected   L7 assert_eq! SPEC  HOME=/Users/John Doe
  expected   L8 assert_eq! SPEC  HOME=/home/user
  # actual-bound 0  (nested quote() is not the actual)
```

Synthetic history (t0 OPEN assertion → t1 comment → t2 EXPECTED-BOUND alice → t3 FIXTURE title → t4 ACTUAL-BOUND this `$HOME`): four distinct SHAs. `distinct yes`. `git log -S /Users/` on t1's comment is not an onset.

Dogfood `--walk` first-parent (this host, 2026-08-20):

```
$ ./onset -C sitbone --eras
onset  sitbone  31 of 100 commits  first-parent
  first-assertion  d3737ea  2026-03-31  Tests/SitboneCoreTests/SitboneCoreTests.swift
                    Implement v0.1: state machine + MenuBarExtra + Notch overlay
  first-expected   (none)
  first-actual     (none)
  first-fixture    343dba6  2026-04-01  Tests/SitboneCoreTests/SiteResolutionTests.swift  USER=annenpolka
                    Merge pull request #1 from annenpolka/feat/v0.1-polish
  now              assertions=300  actual-bound=0  fixture=10
  now-status       FIXTURE
  distinct         yes  first-actual is none (never ACTUAL-BOUND)
  note             FIXTURE is not TAINTED; comments are not oaths
  eras of ACTUAL-BOUND:
    FALSE  31 commits  a2512fe..094769d  2026-03-31 → 2026-04-17

$ ./onset -C kizu --eras
onset  kizu  24 of 244 commits  first-parent
  first-assertion  21ae074  2026-04-15  src/app.rs
                    Merge pull request #2 from annenpolka/feat/v0.1-mvp
  first-actual     (none)
  now              assertions=646  actual-bound=0  spec=2  silent=5
  now-status       SPEC
  distinct         yes
```

**v0.1 holes on real queries:**

- Header already printed `24 of 244` / `31 of 100`, but did not hint `--full`. first-assertion / first-fixture were **merges**, not the feature commits (`1f32f50 feat(git)`, `f45ca8c WindowTitleParserTests`).
- kizu HEAD is SPEC (`/home/user`, John Doe) and v0.1 did not name `first-spec`. SPEC birth is a different object from ACTUAL-BOUND; hiding it makes `/home/user` look like a miss rather than a classified onset.
- `--full` of a same-second merge diamond could steal first-assertion (git log order, not parent-before-child).

### v0.2 — `--full` hint; first-spec; topo-order

After: a first-* that is a merge prints `rerun with --full to name the feature commit`. `first-spec` is a first-class stamp. Walks are `--topo-order --reverse` so parents precede children when timestamps collide.

```
$ ./onset -C sitbone
  first-assertion  d3737ea  SitboneCoreTests.swift
  first-actual     (none)
  first-fixture    343dba6  Merge PR #1  SiteResolutionTests  USER=annenpolka
hint: 31 of 100 commits on first-parent
hint: first-fixture is a merge (343dba6). rerun with --full to name the feature commit

$ ./onset -C sitbone --full --porcelain
  first-assertion  d3737ea  SitboneCoreTests.swift
  first-fixture    f45ca8c  WindowTitleParserTests.swift  USER=annenpolka
  first-actual     (none)
  # fixture birth is the TDD commit, not the merge — still not ACTUAL-BOUND

$ ./onset -C kizu
  first-assertion  21ae074  Merge PR #2  src/app.rs
  first-spec       ca0577a  Merge PR #3  src/hook.rs  HOME=/home/user
  first-actual     (none)
hint: 24 of 244 commits on first-parent
hint: first-assertion is a merge (21ae074). rerun with --full …
hint: first-spec is a merge (ca0577a). rerun with --full …

$ ./onset -C kizu --full --porcelain
  first-assertion  1f32f50  src/git.rs     feat(git): implement diff parser…
  first-spec       3d4b543  src/hook.rs    HOME=/home/user
  first-actual     (none)
```

kizu `--full` first-spec `3d4b543` is the hook commit (`feat(hook): hook-post-tool…`), a day after first-assertion. Textbook `/home/user` is SPEC, not this host, not alice, not ACTUAL-BOUND. Comments (`silent=5`) stay silent.

`./demo.sh` → passed=33 failed=0. Self-test includes a `--no-ff` merge: first-parent first-actual is `Merge topic`; `--full` names `topic: ACTUAL-BOUND`, distinct from `main: assertion`.

## Dogfood targets

- `fixtures/` — comment vs env-assert vs actual-literal vs sitbone-shaped title vs kizu quoting vs nested `shell_single_quote("/Users/alice")` vs XCTest fail dump
- Synthetic git in `./demo.sh` / `--self-test` (OPEN → comment → EXPECTED-BOUND → FIXTURE → ACTUAL-BOUND this `$HOME`; plus a merge diamond)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` first-parent 31 / full 100 (read-only)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` first-parent 24 / full 244 (read-only)

## Surprises

- sitbone first-assertion `d3737ea` is on first-parent. The annenpolka title is **not**. first-parent fixture is Merge PR #1; `--full` names `f45ca8c` `WindowTitleParserTests` the same day as the assertion, a different commit. `git log -S annenpolka` would call that identity-birth. onset calls it FIXTURE.
- kizu tests live in `src/*.rs`, not `Tests/`. An oracle-path filter would have reported no assertions. The window is the `assert_eq!`, not the path.
- `assert_eq!(shell_single_quote("/Users/alice/kizu"), …)` has `/Users/alice` in the *actual expression* as a call argument. That is not ACTUAL-BOUND. `XCTAssertEqual("/Users/alice/Library", "/tmp/x")` is. Surface literal vs nested arg is the whole polarity.
- `--full` without `--topo-order` on equal-timestamp merges listed the topic commit first, so first-assertion coincided with first-actual. That is how the stop condition fails by accident.

## Failures

- HOST (hostname) is still soft and not an onset.
- Swift `#expect` with `<>` generic noise is not parsed; XCTest `XCTAssertEqual` is.
- Production `assert!` / `assert_eq!` in non-test modules still count as assertion windows (kizu `src/git.rs` is a `#[cfg(test)]` module; a true production assert would also count).
- `skills` / voidtrace / tenaoshi were not walked this generation (sitbone/kizu were the gold).
- Eras are `--topo-order --reverse`, not a merge-diamond lattice. Adjacent in the list is not always adjacent in wall time.

## Suggested mutations

- Join with alibi: splice tests onto old production, then onset the failure (LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND).
- Per-window identity: the *same* assertion acquiring ACTUAL-BOUND, not repo-global firsts (line drift, rename).
- `--follow` so a test file rename is one era.
- Cache probe results in `.git/onset-cache/` keyed by blob sha (the in-process cache already is).

## Kill / keep

**Keep.** The object is new: occupancy of ACTUAL-BOUND on the actual side of an assertion window, not a string pickaxe and not mint's production visa-birth. first-actual-bound is distinct from first-assertion on the synthetic history (t0 vs t4 this `$HOME`) and on sitbone/kizu (actual is *none* while assertions exist; fixture/spec are other firsts). sitbone stays FIXTURE, not TAINTED. kizu `/home/user` and `John Doe` stay SPEC; comments silent. Nested `quote("/Users/alice")` is not the actual. `# ran on` does not bind. Not lees `--par`, not visa's whole file, not leftover-name.
