# candidate-35 — twain

## Primitive

A unified diff is two patches (oracle-half vs production-half). `twain` occupies each half against a tree and reports whether the oracle-half *binds* the production-half. The mixed patch's APPLIED hides MUTE / HOLLOW / LOOSE / ORACLE_AHEAD.

## Four primitives considered

1. **twain** — typed split of a patch + occupancy of each half + bind. **Implemented.**
2. **spar** — review suggestions as a patch algebra (COMMUTE / CONFLICT / ABSORB / ORDERED), not occupancy against a tree. Not implemented; suggested mutation. Needs a suggestion corpus; `twain --emit` already produces the patches spar would compose.
3. **gage** — 1-minimal *oracle* set that still locks a production delta (dual of cinch). **Discarded:** same experiment as cinch/hasp/alibi with the axis flipped; judges will collapse it to concatenation.
4. **ban** — a rejected patch as a negative oracle (HEAD must not occupy the forbidden after-image). **Discarded:** sate occupancy with a sign flip; deja already names RELAPSE.

`spar` is real (reviewers never compose two ` ```suggestion ` blocks). It is a mutation of *emitted halves*, not a second object for v0.

## Why this might not exist

`git apply --check` is a boolean on the mixed patch. sate/plea/lodge occupy before→after *images* without typing hunks as tests vs production. alibi/cinch/hasp *run* tests. Reviewers ask a static question about the patch itself: *did the tests in this commit land without the code, the code without tests, or tests that never mention the change?*

Coverage says a line ran. alibi says the suite fails on old production. Neither will say "this PR's oracle-half already occupies main" (HOLLOW ratchet) or "the new tests do not share a token with the production cores" (LOOSE).

## How to run

From the worktree root:

```bash
chmod +x ./twain ./demo.sh
./twain --help
./twain --selftest
./demo.sh
./twain HEAD
./twain HEAD --against HEAD^
./twain --emit oracle HEAD
./twain --json main...HEAD
```

Python 3.10+, stdlib, git. Default occupy `--against HEAD`. `--worktree` reads the filesystem. Stdin: `--patch -`.

## Empirical transcript

### v0.1 (path roles + cfg(test)-to-EOF + DUPLEX leftover-befores)

`./twain --selftest` → 25 passed (after unicode/tests.rs path fixes). Fixture LOCKED/MUTE/HOLLOW/LOOSE/SEAM/sandwich/emit all matched.

Dogfood (`./demo.sh` first run): **19 passed, 2 failed.**

| tree | commit | v0.1 |
| --- | --- | --- |
| kizu HEAD | `9349dc5` release | MUTE (Cargo.toml) — correct |
| sitbone `094769d` | notch controls | MUTE — correct, ADR ignored |
| tenaoshi `4878b75` | contract tests all green | **HOLLOW** — 14 oracle hunks, 0 production. The finding. |
| kizu `04adde1` | jsx/tsx feat | **SEAM** — `src/language/js_ts.rs` create hunk `@@ -0,0 +1,252 @@` contains `#[cfg(test)] mod tests` at line 202 |
| voidtrace `bb4c16d` | shield layer | **SPLIT** prod=MIXED(110) oracle=APPLIED(100). Two production hunks DUPLEX against the commit that introduced them (`evaluate.ts` #11, `scenario-domain.ts` #10). 60+ experiment/fixture JSON hunks classified as prod. Bind was hashes. |

v0.1 SEAM treated any mixed hunk as inseparable. The js_ts.rs module is a *suffix cut*. Occupancy inherited sate's leftover-before DUPLEX, which is the wrong question for "did this half land?"

### v0.2 (one improvement, three dogfood findings)

Forced by that run, not a feature list:

1. **Contiguous mixed hunks split.** A single prod→oracle (or oracle→prod) cut becomes two virtual hunks. Interleaved prod/oracle/prod stays SEAM. Rust `mod tests { }` is brace-matched, not painted to EOF.
2. **After-image present ⇒ APPLIED.** Leftover befores do not MIXED a landed half. twain occupy is "does this half's after-image sit in the tree?", not sate DUPLEX.
3. **Fixtures/experiments/scenario JSON are oracles; `*.generated.*` is ignore.** voidtrace's shield goldens were drowning production.

After v0.2: `./twain --selftest` **31 passed**. `./demo.sh` **22 passed, 0 failed**.

kizu `04adde1 --against 04adde1`: **LOCKED** prod=50 oracle=8 seam=0 bind=`JSX TSX JsTsDialect JsxBlockComment Highlighter …`. Sandwich `--against 04adde1^`: **PENDING** both halves. `--emit oracle` lists `src/hook/tests.rs`, `src/ui/tests.rs`, `tests/e2e/jsx-tsx.test.ts`, *and the test module of* `src/language/js_ts.rs`. `--emit prod` lists the other half of the same file. The split paid rent on a real create hunk.

voidtrace `bb4c16d --against bb4c16d`: **LOCKED** prod=50 oracle=141. Bind includes `resolvedShield`, `Absorb`, `DEF-003`, `Armor`. Generated spec-artifacts dropped to ignore.

tenaoshi `4878b75`: still **HOLLOW**. Oracle-only contract tightening. sitbone `#9`: still **MUTE**.

Emit of a tests-first apply of the LOCKED fixture: mixed patch against that tree is **ORACLE_AHEAD**.

## Dogfood targets

- `./twain --selftest` (31): LOCKED/MUTE/HOLLOW/LOOSE, suffix cut vs interleaved SEAM, sandwich, emit, addition prefix, spaces+unicode `加算`, path roles.
- `./demo.sh` fixtures + emit apply + ugly `--patch`.
- `/Users/annenpolka/ghq/github.com/annenpolka/{kizu,sitbone,voidtrace,tenaoshi,skills}`.

## Surprises

- A tests-all-green commit (tenaoshi `4878b75`) is HOLLOW, not LOCKED. The suite got stricter; production did not move.
- kizu's jsx feat *looks* like one new file. It is two patches glued at `#[cfg(test)]`.
- Bind on cores only: a unicode function name in *context* does not lock. The first ugly fixture was honestly LOOSE until `加算` appeared on a `+` line.
- `src/hook/tests.rs` is not a `tests/` directory; it is a file named `tests.rs`. Path role missed it until the stem `tests?` rule.

## Failures

- `--emit` of a split create file's oracle half is a suffix hunk, not a standalone create; `git apply` of that half alone may not compile. Occupancy of the virtual hunk still holds.
- Combined merge diffs are not parsed; `git diff REV^ REV` is first-parent.
- Bind is token intersection, not execution. LOOSE can be a false alarm when tests call a renamed wrapper. LOCKED can be a hash/`$schema` collision on JSON oracles (voidtrace still binds versions).
- Python `class Test` / `def test_` in a production module are tagged; JS in-file `describe(` is not (too greedy).

## Suggested mutations

- **spar** — compose `twain --emit` halves or review suggestions: COMMUTE / CONFLICT / ABSORB.
- Bind on string literals and call-names only (drop JSON hashes and semver).
- `--lock`: run the oracle-half against production-less tree (alibi at patch grain, no dirty worktree).
- Brace-match Python test classes the way v0.2 brace-matches `mod tests`.

## Kill / keep

**Keep.** The object is the typed split of a patch, not occupancy of a mixed image and not a test runner. MUTE/HOLLOW/LOCKED on four real repositories is a reviewer verb `git show --stat` does not have. v0.2's suffix-cut is the difference between "this file is a seam" and "this file is two patches."
