# mutation-04 — flume

## Primitive

A compiler/test log is a stream of locators plus noise: rewrite every stale `file:line` in that stream from one directory snapshot onto another, by content fingerprint, without git and without the user naming a single address.

## Why this might not exist

`slip` (candidate-16) already relocates a `file:line` by fingerprint. Its interaction still assumes the user names two git refs and, usually, the locators themselves (`--from SHA --to HEAD src/app.rs:529`). That is the wrong object. The thing in your hand is a *log*: rustc, pytest, swiftc, a CI transcript, mixed, full of timestamps and URLs and gutter lines. You want `cat old.log | flume --from-dir oldtree --to-dir newtree`, the way you want `sed`. Nobody shipped that filter. `sed` does not know locators. `git blame --reverse` does not read rustc. Source maps are for minifiers.

## How to run

From the worktree root:

```bash
chmod +x ./flume
./flume --help
./demo.sh
cat compiler.log | ./flume --from-dir oldtree --to-dir newtree
./flume --from-dir oldtree --to-dir newtree rustc.log pytest.log --trace
```

Exit 0 on success. `--strict` exits 1 if a locator cannot be read from `--from-dir`. Confirmed deletions pass through on stdout (they are answers, not errors); `--trace` reports them on stderr. The binary never calls git — a stub `git` on PATH dies if it is touched.

## The assumption that was flipped

Killed: “the user names two git refs and individual locators.”

New: flume is a **pure stream rewriter**. `--from-dir` and `--to-dir` only. stdin is an arbitrary log; stdout is the same log with locators rewritten. Mixed Python / Rust / Swift grammars plus noise lines are the job, not an add-on.

### Bought

- Unix-composable without a repository: tarball vs tarball, CI artifact vs checkout, Python tree vs rewrite.
- A total stdin→stdout contract. Same line count, same noise, only addresses move. Mappings live on stderr (`--trace`).
- Positional arguments are extra log files, never locators — the `ref:path:line` colon pile-up is gone.
- Compiler-dialect locators (rustc `-->`, Python `File ", line`, Swift `file.swift:12:5: error:`, unique basename) because the stream is the object.
- Absolute CI prefixes stay (`/home/runner/work/kizu/kizu/` + new relative path).
- `shifted` as a first-class status (same file, line number drifted).

### Lost

- Cannot name two SHAs; someone else must materialize trees (`git archive` in `demo.sh`, a cache, a checkout).
- Cannot ask `flume src/app.rs:529` as a one-shot. Everything is a stream.
- No git rename-map hint. Split-directory path affinity has to do that work alone.
- No per-locator ref overlay (`V1:src/calc.py:3`).
- Lazy `git show` of one file is gone: both snapshots are walked.

## Empirical transcript

### Working software (v0.1)

Synthetic mixed stream (Python traceback, rustc arrow, Swift basename, colon filename, spaces, unicode, URL, timestamp, `error:1` chatter) with a stub `git` on PATH:

```
$ cat mixed.log | ./flume --from-dir from --to-dir to
12:34:56 INFO starting build
error[E0599]: no method named seen_hunk_fingerprint
  --> src/app/layout.rs:4:1
   |
 4 | pub fn seen_hunk_fingerprint(
  File "src/math/ops.py", line 3, in add
pytest src/math/ops.py:8: in test_helper
note: also see src/math/sauce.py:3
http://localhost:8080/health
error: src/calc.py:11: doomed is gone
LICENSE:1: copyright
PresenceArbiter.swift:23:20: error: cannot find 'threshold' in scope
KinsokuEngine.swift:12:5: error: type 'TransformRequest' is not a member
  --> /home/runner/work/ugly/ugly/src/app/navigation.rs:1:5
not a locator, just chatting about foo:bar and error:1
```

Real copies (`git archive` into temp dirs; flume itself never talks to git):

```
$ cat kizu.log | ./flume --from-dir kizu-b4e6a5d --to-dir kizu-HEAD --trace
# stdout:
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
   |
529 | pub fn seen_hunk_fingerprint(
  File "src/app/navigation.rs", line 22, in nearest_landing_forward
LICENSE:1: copyright
12:34:56 INFO cargo test
http://localhost:8080/health
# stderr:
moved	src/app.rs:529:5	src/app/layout.rs:17:5	0.939	path or surrounding file changed
moved	src/app.rs:543	src/app/navigation.rs:22	0.939	path or surrounding file changed
same	LICENSE:1	LICENSE:1	1.000
```

```
$ cat sitbone.log | ./flume --from-dir sitbone-a95da43 --to-dir sitbone-HEAD --trace
# stderr:
shifted	Sources/SitboneCore/PresenceArbiter.swift:45:17	Sources/SitboneCore/PresenceArbiter.swift:75:17	1.000	same file, line number drifted
# stdout:
Sources/SitboneCore/PresenceArbiter.swift:75:17: error: cannot find 'threshold' in scope
PresenceArbiter.swift:75:17: error: cannot find 'threshold' in scope
```

```
$ cat tenaoshi.log | ./flume --from-dir tenaoshi-a41089c --to-dir tenaoshi-HEAD --trace
# stderr:
same	Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12:17	Engine/Sources/TenaoshiEngine/KinsokuEngine.swift:12:17	1.000
# stdout keeps KinsokuEngine.swift:12 (full path and basename forms)
```

Read-only working trees also work as `--to-dir` (kizu, sitbone, tenaoshi).

### Failures recorded against v0.1

kizu's rustc *block* is only half-rewritten. The `-->` locator moved 529 → 17; the snippet gutter did not:

```
  --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
   |
529 | pub fn seen_hunk_fingerprint(
```

slip would not see this: it relocates addresses, not diagnostic *blocks*. A stream rewriter that remembers the last rewrite can carry the line number onto the following `NNN |` gutters.

### After the improvement (v0.2)

Carry the last diagnostic rewrite onto rustc/clang `NNN |` gutters for the next 16 lines. Python `File ", line` does not own the gutter. Same kizu log:

```
$ cat kizu.log | ./flume --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
error[E0599]: no method named seen_hunk_fingerprint
  --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5
   |
 17 | pub fn seen_hunk_fingerprint(
  File "src/app/navigation.rs", line 22, in nearest_landing_forward
LICENSE:1: copyright
12:34:56 INFO cargo test
http://localhost:8080/health
```

Synthetic rustc block `src/app.rs:14` → `src/app/navigation.rs:1` now takes its gutter with it (`14 | fn nearest_landing…` → ` 1 | fn nearest_landing…`). sitbone/tenaoshi streams unchanged (Swift has no numbered gutter). `./demo.sh` still exits 0.

## Dogfood targets

- Synthetic two-directory fixture in `./demo.sh`: Python split/rename/delete, Rust file-split, Swift shift + identity, unicode, `src/weird:colon.py`, `notes/file with spaces.txt`, extensionless Makefile/LICENSE, URL/timestamp/`error:1` noise. Stub git on PATH.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` and `HEAD` (9480-line `src/app.rs` split), plus the live working tree as `--to-dir`.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` at `a95da43` and `HEAD` (`detect()` 45 → 75), plus live tree.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` at `a41089c` and `HEAD` (`KinsokuEngine.transform` still line 12, score 1.000), plus live tree.

## Surprises

- File-split into a directory of the same stem (`src/app.rs` → `src/app/*.rs`) still falls out of path affinity with no git rename map. The lost rename hint was cheaper than expected.
- Unique-basename binding is what makes Swift usable: `PresenceArbiter.swift:45` never contains the tree-relative prefix swiftc omits.
- Silent pass-through of deletions is the right stream default. `src/calc.py:11` (doomed) staying in the log is honest; inventing a destination would be a lie.
- `shifted` vs `same` matters once stdout is a log: sitbone `detect()` is the same file and the same text, but line 45 in yesterday's log is a lie.
- rustc's `529 |` gutter is not a locator. v0.1 "worked" (exit 0) and left it stale. The first real-log dogfood was the only way to see it; the fix is stream state, which slip's per-address CLI cannot grow.

## Failures

- rustc multi-hunk snippets whose later gutter numbers are *not* old_line+k (a split function) will follow the first locator's offset and can land wrong.
- Common/`}`-only lines refuse to fingerprint (`unresolved`) and pass through.
- Two identical helpers in dest can still confuse the scorer; path affinity usually wins.
- A log that already mixes old *and* new paths will rewrite only what binds against `--from-dir`. New-only paths (added after the snapshot) are noise, by design.
- Whole-tree walk of a dirty kizu working tree (~2700 e2e fixtures) is acceptable but not free; copies via `git archive` are the intended dogfood.

## Suggested mutations

- ANSI-aware matching (`\x1b[31msrc/app.rs\x1b[0m:529`) so colorized CI logs still flume.
- `--watch` a pinfile of logs, rewrite on tree change (scar-review companion).
- JSON compiler streams (`cargo --message-format=json`, Swift structured diagnostics) as another grammar.
- `soul`: rare-token file identity across a language rewrite, same stream contract.

## Kill / keep

**Keep.** The flipped assumption is the primitive: a log in, a log out, two directories, no git. Empirically hits kizu's `app.rs` split (locator *and* rustc gutter), sitbone's shifted `detect()`, tenaoshi's identity `transform`, and a mixed dialect stream with a stub git that never fires. The v0.2 gutter carry is evidence the stream object is real: slip could not have grown that feature without first becoming a filter. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just a backend.
