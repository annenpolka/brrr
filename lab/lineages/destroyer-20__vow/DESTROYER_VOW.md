# DESTROYER — vow

Adversarial pass on the **two-oath object** (expected×actual). No rewrites: the failures are conceptual except a same-line comment that is parsed as the expected slot (operational), left unpatched so the pair/path holes stay visible.

- **vow** (mutation-68, v0.2) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb888759e773`
- Peels: **troth** (mutation-89), **onset** (mutation-102), **writ** (hybrid-16)
- Transcript: `/tmp/destroy-vow/transcript.txt`
- Follow-up: `/tmp/destroy-vow/followup/`
- Fixtures: `/tmp/destroy-vow/fixtures/`
- Attack driver: `/tmp/destroy-vow/attack.py`
- `./vow --self-test` still ok after the attacks. Gold `pytest_fail` stays `EXPECTED-BOUND vs ACTUAL-BOUND`. Gold `xctest_fail` stays `EXPECTED-OPEN vs ACTUAL-BOUND`.

Attacks: `# ran on` comments, HOST soft, Swift `#expect` generics, wrap-across-message asserts, `expected=home; assert got==expected`, sitbone FIXTURE vs TAINTED, portable OPEN expected skipped wrongly, quoting asserts vs comments about John Doe.

Verdict: **mutate, do not kill.** The pair is still two unary skip/apply machines on the gold dumps. Nothing in this battery turned `--from-fail` into lees `--par` or visa-of-the-file. Do not kill because HOST is soft, because Swift Testing prints one side, or because `--apply` is still expected-polarity. Those are mutations. Killing them would throw away XCTest polarity (actual-first) to hide a soft axis.

---

## Primitive restated

A failing assertion implies **two** oaths. Pair the expected-literal machine with the actual-side machine. The object is `EXPECTED-BOUND vs ACTUAL-BOUND` (or OPEN), not lees residue. Comments are not oaths. v0.2 names this host's role (`EXPECTED` | `ACTUAL` | `BOTH` | `NEITHER`) but `--apply` still talks to the expected side.

---

## 1. `# ran on` — own-line is silent; same-line is the expected slot (operational + conceptual)

Gold holds. Own-line `# ran on alice` / `# HOME=/Users/alice` is OPEN, silent `USER=alice`, require empty. Inside a fail dump the comment is skipped and does not bind; `E - /tmp/x` / `E + /Users/alice/Library` is still `EXPECTED-OPEN vs ACTUAL-BOUND`.

```
$ ./vow --json fixtures/comment_only.py
status OPEN  require {}  silent USER=['alice']

$ ./vow --from-fail < fixtures/comment_in_fail.txt
vow  pair  pytest  EXPECTED-OPEN vs ACTUAL-OPEN
# # ran on alice does not bind

$ ./vow --from-fail < ran_on + E-minus/plus paths
vow  pair  pytest  EXPECTED-OPEN vs ACTUAL-BOUND
# exp USER empty; act HOME=/Users/alice
```

**Same-line comment is an oath.** Python's assert window runs to NEWLINE, so the trailing comment is the expected literal:

```
# followup/ran_on_sameline.py
def test_spec():
    assert 1 + 1 == 2  # ran on annenpolka HOME=/Users/annenpolka

$ ./vow --json followup/ran_on_sameline.py
status BOUND
require {'HOME': '/Users/annenpolka', 'USER': 'annenpolka', 'layout': 'macos-home', 'platform': 'Darwin'}
window expected= 2  # ran on annenpolka HOME=/Users/annenpolka
silent []
```

`--apply` on that file is MATCH on this laptop and MISS everywhere else. The comment is not in `silent`. `alice` on the same line is textbook payload → SPEC (status SPEC, require empty) — still not "comment is silent."

A Swift `# ran on alice` is not a comment (`#` is not `//`); it is dropped, not silent. `#expect this was alice` as the first line of a dump is kept as `pending_assert` because it starts with `#expect`, then ignored because the E +/- pair wins.

onset on the same-line file is `OPEN` (`expected-bound 0`). The peel does not inherit vow's comment-pollute. That is not a rescue of the unary window: vow `--scan` of a test that wrote `# ran on $USER` on the assert line would BOUND this host.

---

## 2. HOST is soft — hostname cannot name a machine or a host role (conceptual, load-bearing)

`HOST` is in `SOFT_AXES` with `CWD`/`TMPDIR`. `live_axes()` collects `platform.node()`. `match_oath` never reads `soft`. A HOST-only oath is OPEN, MATCH everywhere, `--apply` 0.

```
$ ./vow --json host_getenv.py     # assert os.environ['HOSTNAME'] == 'ci-mac-7'
status OPEN  match MATCH  require {}  soft {'HOST': 'ci-mac-7'}
# --apply rc=0 on this laptop (HOST=Mac)

$ ./vow --from-fail --apply < host_fail.txt
# source: assert os.environ['HOSTNAME'] == 'ci-mac-7'
# E - ci-mac-7 / E + Mac
pair EXPECTED-OPEN vs ACTUAL-OPEN  host NEITHER
esoft {'HOST': 'ci-mac-7'}  asoft {'HOST': 'Mac'}
ematch MATCH  amatch MATCH
# --apply rc=0
```

A dump whose expected is *this* hostname and actual is `other-box` is still `host NEITHER`. v0.2's new object ("which recorded machine is this host") cannot see HOST. `socket.gethostname()` and a `host: ci-mac-7` snap are the same OPEN.

onset agrees: `host_getenv.py` is `OPEN`, `expected-bound 0`. troth `--apply` on a HOST dump is the same vacuous APPLY. The axis exists so it can be printed; it cannot skip.

---

## 3. Swift `#expect` — `<>` is parsed; `contains(where:)` is not; Swift Testing is unary (conceptual)

CANDIDATE said "Swift `#expect` with `<>` generic noise is not" parsed. Empirically the compare-parens window **is** built. `<>` is not a depth token and does not have to be: `==` is still at depth 0.

```
#expect(home as Optional<String> == "/Users/annenpolka")
#expect(User<Host>.home == "/Users/annenpolka/Library")

$ ./vow --json expect_generic_me.swift
status BOUND
require HOME=/Users/annenpolka USER=annenpolka platform=Darwin
windows 2
```

Textbook `/Users/alice` in the same shapes is SPEC (payload), not a parse miss. onset calls those windows `EXPECTED-BOUND` even for alice — peel disagreement on textbook, not on `<>`.

**The real miss is a trailing-closure compare:**

```
#expect(items.contains(where: { $0.path == "/Users/annenpolka" }))
status OPEN  windows 0
```

`split_compare` sees `==` inside `{…}` and emits no window.

**Swift Testing `--from-fail` is not a pair.** `SWIFT_TESTING_RE` takes only the right-hand side of `Expectation failed: … == …`. Actual is `""`.

```
$ ./vow --from-fail < 'Expectation failed: (home → "/Users/alice/Library") == "/tmp/x"'
vow  pair  swift-testing  EXPECTED-OPEN vs ACTUAL-OPEN
  expected /tmp/x
  actual
  host     NEITHER
```

XCTest `("actual") is not equal to ("expected")` still pairs. The two-oath object stops at Apple's XCTest grammar. `#expect` source is unary-expected; the Swift Testing dump is unary-expected with an empty actual.

---

## 4. Wrap-across-message — source call-args hold; dump line-at-a-time does not (conceptual)

A multiline `XCTAssertEqual(got, "/Users/annenpolka/Library", "home should be \(NSHomeDirectory())")` is BOUND. Third-arg path is not the expected slot (`XCTAssertEqual(got, want, "/Users/alice/Library is required")` is OPEN). That is call-arg split working.

`--from-fail` walks `splitlines()`. A wrap kills the pair:

```
XCTAssertEqual failed: ("/Users/alice/Library") is not equal to
("/tmp/x")

$ ./vow --from-fail < wrap_multiline.txt
vow  -  OPEN
  (portable — no assertion named a machine)
```

A trailing same-line message survives (`EXPECTED-OPEN vs ACTUAL-BOUND`) but dirties `expected_raw` to `("/tmp/x") - home should match`. A value with `)` is worse: `[^)]+` stops early, leftover `("home (/Users/alice)")` derives `HOME=/Users/alice)` `USER=alice)`. The pair exists; the actual machine is garbage.

---

## 5. `expected = home; assert got == expected` — no name follow; two inverted pairs (conceptual, load-bearing)

Unary source does not chain `home = os.environ['HOME']` → `expected = home` → `assert got == expected`:

```
status OPEN  require {}
windows [('expected=', 'home', 'expected'), ('assert', 'expected', 'got')]
```

`--from-fail` of the pytest dump without a repr is not two machines:

```
assert got == expected
E   AssertionError: assert '/tmp/x' == expected

pair EXPECTED-OPEN vs ACTUAL-OPEN
exp_raw /tmp/x
act_raw expected
src     assert got == expected
```

`src_exp` is refused when the source expected is an identifier. Left of `assert '/tmp/x' == expected` becomes the expected oath.

With `-vv` (`where got = '/tmp/x'` / `and expected = home`) **both** pairs survive — the vv replace only drops an unlabeled pair of the *same two values*, and `{home, /tmp/x} ≠ {/tmp/x, /Users/annenpolka}`:

```
n 2
pytest     EXPECTED-OPEN vs ACTUAL-BOUND   exp /tmp/x              act /Users/annenpolka
pytest-vv  EXPECTED-OPEN vs ACTUAL-OPEN    exp home                act /tmp/x
```

With E +/- (minus oracle, plus actual) the labeled DIFF is correct **and** the PM pair is inverted:

```
n 2
pytest  EXPECTED-OPEN vs ACTUAL-BOUND   exp /tmp/x                 act /Users/annenpolka
pytest  EXPECTED-BOUND vs ACTUAL-OPEN   exp /Users/annenpolka      act /tmp/x
```

JSON with `len(pairs)!=1` has no top-level `pair`. The object is "two oaths"; the dump emits two *pairs*.

**Cargo polarity is rustc-inverted.** `assert_eq!(got, expected)` prints `left: got` / `right: expected`. vow `add("cargo", left, right)` takes left as expected:

```
left: "/home/runner/work/proj"
right: "/Users/alice/proj"

EXPECTED-BOUND vs ACTUAL-BOUND
  expected /home/runner/work/proj    # runner, as if the golden were CI
  actual   /Users/alice/proj
```

Gold `fixtures/cargo_fail.txt` puts alice on the left, so self-test agrees with the fixture and not with rustc. XCTest polarity was the whole flip in CANDIDATE; cargo was not flipped.

Bare pytest `E   AssertionError: assert 'runner' == 'alice'` with no source line and no +/- is `EXPECTED-OPEN vs ACTUAL-OPEN` (`exp_raw=runner act_raw=alice`) — textbook names without `axis_hint` from source do not bind, and PM still took left as expected.

---

## 6. sitbone FIXTURE vs TAINTED — holds (survived)

```
$ ./vow --scan -C sitbone --porcelain
OPEN 21  FIXTURE 4  BOUND 0

FIXTURE:
  Tests/SitboneCoreTests/WindowTitleParserTests.swift
  Tests/SitboneCoreTests/BrowserSiteKeyUnificationTests.swift
  Tests/SitboneCoreTests/SessionEngineExtendedTests.swift
  Tests/SitboneCoreTests/SiteResolutionTests.swift

$ ./vow --json WindowTitleParserTests.swift
status FIXTURE  USER not in require
witness fixture annenpolka
```

Bare `XCTAssertEqual(result, "annenpolka")` / `score("annenpolka/sitbone")` is not BOUND. GitHub title identity-as-data is fixture, not a skip.

onset first-parent sitbone: `first-actual (none)`, `now-status FIXTURE`, `fixture=10`, `distinct yes`. `FIXTURE is not TAINTED`. first-fixture is still the merge (`343dba6`); `--full` is onset's object, not vow's.

writ `--list -C sitbone`: 0 production paths (tests-only tree). No splice pair. The peel does not occupy sitbone.

---

## 7. Portable OPEN expected skipped wrongly — `--side both` and expected-only `--apply` (conceptual)

Default `--apply` on gold XCTest (`/tmp/x` vs Alice, host NEITHER) is rc=0. OPEN expected still applies here. That is the oracle polarity CANDIDATE kept.

```
$ ./vow --from-fail --apply < xctest_fail.txt          # rc=0
$ ./vow --from-fail --apply --side both < xctest_fail.txt
# expected MATCH OPEN ∧ actual MISS Alice  →  rc=1
```

`--side both` ANDs Alice's MISS into a portable `/tmp` golden and skips. troth names that trap (`side both SKIP  AND actual MISS into OPEN expected`) and still exits 1; troth's *host-role* `--apply` stays 0 (`legal OPEN`).

This host as the actual machine:

```
$ printf 'E   - /Users/alice/proj\nE   + %s/proj\n' "$HOME" | ./vow --from-fail --apply
vow  pair  pytest  EXPECTED-BOUND vs ACTUAL-BOUND
  host     ACTUAL  this host produced the fail
  expected MISS    HOME want=/Users/alice have=/Users/annenpolka
  actual   MATCH   HOME=/Users/annenpolka
# rc=1   --side actual would be 0
```

Host role is named, not an exit code. troth `--apply` is rc=0 (`legal ACTUAL`). The peel is the mutation CANDIDATE suggested (`--apply` from host role without breaking OPEN expected). vow still has the hole.

`--apply` on `E - /tmp/x` / `E + $HOME/proj` is rc=0 (OPEN expected). Portable golden is not skipped just because host is ACTUAL. The skip is `--side both`, not default.

---

## 8. Quoting asserts vs comments about John Doe — holds; this-home quote is BOUND (survived / conceptual)

kizu `--scan`: `OPEN 13  SPEC 2  BOUND 0`. SPEC files are `src/init/tests.rs` and `src/hook/tests.rs`.

```
$ ./vow --json kizu/src/init/tests.rs
status SPEC  require {}
silent HOME=/Users/John Doe  USER=John Doe   # comments

$ ./vow --json quote_assert.rs     # assert_eq!(quote("/Users/John Doe/…"), "'…'")
status SPEC  require {}

$ ./vow --json quote_comment.rs    # // binary lives at `/Users/John Doe/.cargo/bin/kizu`
status OPEN  require {}
silent HOME=/Users/John Doe USER=John Doe USER=alice
```

Space / textbook keeps John Doe and `/home/user` as payload SPEC. Comments stay silent.

`assert_eq!(shell_single_quote("/Users/annenpolka/kizu"), "'/Users/annenpolka/kizu'")` is **BOUND** this host. The expected *literal* is this HOME; textbook alice in the same call-arg shape is SPEC. onset calls the alice nested quote `EXPECTED-BOUND` (peel is stricter). Nested `quote(path)` is not ACTUAL-BOUND on either tool — the actual expression is the call, not the machine that produced a fail.

---

## What survived

- Gold pytest: `EXPECTED-BOUND vs ACTUAL-BOUND` alice vs runner, `host NEITHER` on this laptop.
- Gold XCTest: `EXPECTED-OPEN vs ACTUAL-BOUND` `/tmp/x` vs Alice. Apple's actual-first order still holds.
- Own-line `# ran on` / `# HOME=` is not an oath. Dump comments do not bind.
- sitbone `--scan` 0 BOUND / 4 FIXTURE / 21 OPEN. `WindowTitleParserTests` USER empty. Not TAINTED.
- kizu `--scan` 0 BOUND / 2 SPEC / 13 OPEN. John Doe comments silent; quoting asserts SPEC.
- Default `--apply` on OPEN expected is 0. A portable `/tmp` golden is not skipped because host is NEITHER.
- Dump `actual=$HOME` still names `host ACTUAL`.
- `./vow --self-test` ok. No rewrite.

---

## Peels (troth, onset, writ)

| peel | what it occupies | vs this battery |
| --- | --- | --- |
| **troth** | `--apply` = `OPEN expected ∪ ACTUAL-BOUND-if-this-host` | Closes §7 host-role apply. Does not close HOST soft, same-line comments, Swift Testing actual="", cargo polarity, name-follow double pairs. |
| **onset** | era of ACTUAL-BOUND | sitbone/kizu `first-actual (none)` — agrees the gold trees never bound an actual machine. Same-line `# ran on` is OPEN here (does not inherit vow's comment-pollute). HOST is not an onset. |
| **writ** | splice then pair (`LOCKED-and-EXPECTED-BOUND vs LOCKED-and-ACTUAL-BOUND`) | `--list` sitbone/kizu: 0 production. No `swift test` / `cargo test`. The joint occupancy was not run on the gold repos. |

Concatenation `alibi && troth --from-fail` still needs a dump. writ's object is not a destroyer of vow's pair; it is a later join.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still "one failing assertion → two unary skip/apply machines." Gold XCTest `/tmp` vs Alice, gold pytest alice vs runner, sitbone FIXTURE, kizu John Doe SPEC — all still hold. Host role is still named when the axis is HOME. Nothing here is lees residue or visa-of-the-file.

| do not kill because | mutate toward |
| --- | --- |
| Gold pair XCTest `EXPECTED-OPEN vs ACTUAL-BOUND`; pytest two BOUND; sitbone 0 BOUND / 4 FIXTURE; kizu comments silent + quoting SPEC; own-line `# ran on` silent; default `--apply` on `/tmp` expected is 0 | **`--apply` from host role ∪ OPEN expected** (troth). `--side both` must not skip a portable golden. Host `ACTUAL` must be a legal apply set, not a flag. |
| | **Same-line comments are comments.** Strip COMMENT tokens from the assert expected slice. `# ran on $HOME` on `assert 1+1==2` must stay OPEN/silent. |
| | **HOST is a hard axis or it is not an oath.** A HOSTNAME assert that failed on this box must be able to name `host ACTUAL` / skip. Soft-print-only is occupancy of nothing. |
| | **Swift Testing dump is a pair.** Parse `Expectation failed: (actual) == expected` (and the `got →` form). `#expect` closures that contain `==` are windows. `<>` already works — do not invent a generic parser. |
| | **One pair per assertion.** pytest PM (`assert left == right` → left is *actual*) must not coexist with E +/- as a second inverted pair. Follow `expected = home`. rustc `left:` is actual. |
| | **Wrap-across-newline is one XCTAssert.** Do not `$`-anchor a single line. `[^)]+` cannot tokenize a value that contains `)`. Corrupted `USER=alice)` is worse than OPEN. |

Do not grow a splice platform (that is writ). Do not walk git eras (that is onset). The next mutation is *apply-from-role without AND* plus *one polarity per dump grammar* — not a prettier pair banner.

A one-line comment-mask inside the Python assert slice would hide §1 and would not touch HOST, Swift Testing, cargo left/right, or `--side both`. Not applied.
