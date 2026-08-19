# reimpl-01 — stencil

## Primitive

Paste a runtime string (error, log line, assertion); locate the source format template that can produce it, including `{}` / `{name}` / `${…}` / `\(...)` / `%s` holes.

## Why this might not exist

`grep` and livegrep go pattern → text. The daily move is the opposite: you have the *instance* (`git diff single file failed: fatal: not a git repository`) and need the *template* (`"git diff single file failed: {}"`). Format holes, wrapped `error:` / anyhow prefixes, and Swift `\(…, privacy:)` interpolations make literal search fail. The missing Unix verb is inverse printf against a tree.

This is a from-behavior reimplementation of `unfmt` (candidate-08). The original Python file was never opened. CLI shape, fixtures, and dogfood queries were recovered by running the original binary and reading its README / CANDIDATE / demo.

## How to run

```bash
chmod +x stencil
./stencil --selftest
./demo.sh
./stencil -C /path/to/repo 'some filled-in error'
./stencil -C /path/to/repo --index          # dump templates
cargo test 2>&1 | ./stencil -C . --any      # hunt a log
./stencil -C . -e '--looks-like-a-flag'
```

Exit 0 = every argument matched (stdin / `--any`: any line). Exit 1 = miss. Exit 2 = usage.

## Empirical transcript

### v0.1 working prototype (commit eaf3c01)

`./stencil --selftest` → `selftest: ok`

`./demo.sh` → `passed=28 failed=0` (same 28 cases as original unfmt, including kizu / voidtrace / sitbone / tenaoshi).

Fixture (ugly names, nested dir, skipped `node_modules` / `*.min.js`):

```
$ ./stencil --walk -C fixtures/ugly 'user 42 not found'
src/user.py:2:20: score=0.81 lang=py holes=1 via=full
  query: user 42 not found
  tmpl:  user {} not found

$ ./stencil --walk -C fixtures/ugly 'Duplicate event ID: evt-99'
src/events.ts:5:19: … tmpl: Duplicate event ID: {}

$ ./stencil --walk -C fixtures/ugly 'session started profile=Focus'
src/log.swift:2:29: … tmpl: session started profile={}
```

Same queries against original `unfmt` recovered the same paths; scores differed in the second decimal (independent scorer, same ranking).

Real trees, first try:

```
$ ./stencil -C kizu 'git diff single file failed: fatal: not a git repository (or any of the parent directories): /tmp/nope'
src/git/diff.rs:34:28: score=0.74 lang=rust holes=1 via=full
  tmpl:  git diff single file failed: {}
src/git/diff.rs:31:18: score=0.55 lang=rust holes=0 via=full
  tmpl:  git diff single file          # .context() prefix, also found by original

$ ./stencil -C voidtrace 'Duplicate event ID: evt-abc'
packages/kernel/src/event-queue.ts:61:23: … tmpl: Duplicate event ID: {}

$ ./stencil -C sitbone 'session started profile=DeepWork'
Sources/SitboneCore/SitboneCore.swift:423:33: … tmpl: session started profile={}

$ ./stencil -C tenaoshi 'has_more cannot be true when units is empty'
Engine/Sources/TenaoshiEngine/EditPlan.swift:260:43: score=1.00  # untracked file
$ ./stencil --cached-only -C tenaoshi 'has_more cannot be true when units is empty'
— no template for: …                 # after v0.2; v0.1 leaked identifier fragments
```

### Failures that drove v0.2

Side-by-side with original `unfmt` on the same argv (never reading its source):

**Short no-hole fragments ranked.** Original does not. v0.1 treated any 4+ char literal as a span:

```
$ ./stencil -C kizu 'failed to spawn `git apply --reverse`'
src/git/revert.rs:46:18: score=1.00 tmpl: failed to spawn `git apply --reverse`
src/git.rs:922:26: score=0.47 tmpl: git apply          # noise
src/git/revert.rs:40:25: score=0.47 tmpl: --reverse    # noise

$ unfmt -C kizu 'failed to spawn `git apply --reverse`'
src/git/revert.rs:46:18: score=1.00                    # only this
```

Same leak on tenaoshi (`has_more` as a prefix of the real message) and sitbone (`cumulative.json`, `sessions`). Probe of original: no-hole *exact* match at static≥4; *prefix of query* at static≥10; leftover prefix / middle span only at static≥16.

**Swift nested quotes.** Original cannot invert sitbone's camera log. v0.1 accidentally matched via a truncated `\(` but also indexed the broken prefix:

```
$ unfmt -C sitbone 'camera presence enabled'
— no template for: camera presence enabled

# source is:
# "camera presence \(self.isCameraEnabled ? "enabled" : "disabled", privacy: .public)"
$ unfmt --index -C sitbone | rg 'camera presence'
… holes=0 static=41 camera presence \(self.isCameraEnabled ?
```

### After the improvement (v0.2)

No-hole alignment/length rules. Swift `"…"` scans through quotes that live inside `\(...)`.

```
$ ./stencil -C sitbone 'camera presence enabled'
Sources/SitboneCore/SitboneCore.swift:361:17: score=0.77 lang=swift holes=1 via=full
  tmpl:  camera presence {}

$ ./stencil --index -C sitbone | rg 'camera presence'
Sources/SitboneCore/SitboneCore.swift:361:17: lang=swift holes=1 static=16 camera presence {}

$ ./stencil -C kizu 'failed to spawn `git apply --reverse`'
src/git/revert.rs:46:18: score=1.00
  tmpl:  failed to spawn `git apply --reverse`
# no git apply / --reverse fragments

$ ./stencil --cached-only -C tenaoshi 'has_more cannot be true when units is empty'
— no template for: has_more cannot be true when units is empty   # exit 1, same as original
```

`./demo.sh` after the change: `passed=29 failed=0` (adds the sitbone camera case original still misses).

Head-to-head on the original demo queries: same producing path in every case. Voidtrace `predicate.event-kind-mismatch` ranking identical (production `.ts` before `.test.ts`). Wall time on voidtrace ~0.27s original vs ~0.30s stencil.

## Dogfood targets

| Target | What we threw at it |
| --- | --- |
| `fixtures/ugly` | weird filename, nested path, `node_modules`, `*.min.js`, rust/js/py/swift/go |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | anyhow / format! / `.context`, backticks, `--attach` via `-e` |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | JS templates, two-hole RangeError, problem codes, test-vs-prod rank |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | Swift `\(` + `privacy:`, multiline `"""` logs, nested quotes in ternary |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | untracked Swift sources vs `--cached-only` |
| `/Users/annenpolka/ghq/github.com/annenpolka/skills` | Python f-string `File not found: {file_path}` |

## Surprises

- The original's no-hole policy is not "substring search"; it is three different floors (exact / prefix / span). Copying "index every 4-char literal" without those floors looks like a ranking bug.
- Sitbone's camera line is one hole whose fill is the *result* of a ternary with nested quotes. A language-blind quote scanner never sees the producing template; a paren-aware one collapses to `camera presence {}` and that is enough.
- `.context("git diff single file")` is a no-hole prefix of the wrapped anyhow error. Inverse printf usefully returns *both* the hole template and the context literal.
- Working-tree vs HEAD is load-bearing: tenaoshi's `EditPlan.swift` is untracked (`??`) and `--cached-only` correctly misses.

## Failures

- Interpolated *tail* only (`fatal: not a git repository…`) does not find `git diff single file failed: {}`. Correct for the primitive; still a human disappointment.
- Adjacent concatenation (`"open " + path + ": " + err`) is not a template.
- `git {} failed` in kizu still ranks third on the long git-diff query (score 0.36, above `--min-score 0.34`). Original does not show it. Hole templates have a weaker uniqueness filter than no-hole spans.
- `--attach` alone is a flag; even with `-e` there is no template equal to `--attach`.
- No stitching of anyhow *chains* into one explanation (`context` + `inner` as a path).
- Indexes stay large (voidtrace ~12k rows): test titles, date formats, short identifiers.
- Markdown / prose claims are out of scope.
- Score numbers are not identical to original (independent formula). Ranking of the intended hit was.

## Suggested mutations

- Reconstruct an error as an ordered *chain* of templates (`context: inner`).
- `--contains` mode: treat the query as a needle inside no-hole templates (for `--attach`).
- Adjacent concatenation as one template (`"statting " + path` → `statting {path}`).
- Language-aware public-surface only (skip test titles, skip `yyyy-MM-dd`).
- History: if HEAD misses, search `git log -G` / dangling blobs for the template.
- Cache the template index keyed by `git ls-files -s`.

## Kill / keep

**Keep.** The primitive survived a from-scratch rebuild: same demo, same real-tree hits, and the first improvement (nested Swift quotes + no-hole floors) came from comparing the two CLIs on sitbone/kizu rather than from reading the original. Inverse printf is the verb; the scanners are just enough machinery. Not an LSP.
