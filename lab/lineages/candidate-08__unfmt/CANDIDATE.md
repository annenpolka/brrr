# candidate-08 — unfmt

## Primitive

Paste a runtime string (error, log line, assertion); locate the source format template that can produce it, including `{}` / `{name}` / `${…}` / `\(...)` / `%s` holes.

## Why this might not exist

`grep` and livegrep go pattern → text. The daily move is the opposite: you have the *instance* (`git diff single file failed: fatal: not a git repository`) and need the *template* (`"git diff single file failed: {}"`). Format holes, wrapped `error:` / anyhow prefixes, and Swift `\(…, privacy:)` interpolations make literal search fail. IDEs do not index format strings as reverse templates. The missing Unix verb is inverse printf against a tree.

Discarded (more conventional): identifier-level tree diff; forgotten co-change partners from git history. The other remaining idea, coarse file-delete mutation (`spite`), is listed under mutations.

## How to run

```bash
chmod +x unfmt
./unfmt --selftest
./demo.sh
./unfmt -C /path/to/repo 'some filled-in error'
./unfmt -C /path/to/repo --index          # dump templates
cargo test 2>&1 | ./unfmt -C . --any      # hunt a log
./unfmt -C . -e '--looks-like-a-flag'
```

Exit 0 = every argument matched (stdin / `--any`: any line). Exit 1 = miss. Exit 2 = usage.

## Empirical transcript

### v0.1 working prototype

`./unfmt --selftest` → `selftest: ok`

Fixture (ugly names, nested dir, skipped `node_modules` / `*.min.js`):

```
$ ./unfmt --walk -C fixtures/ugly 'user 42 not found'
src/user.py:2:20: score=0.70 lang=py holes=1 via=full
  query: user 42 not found
  tmpl:  user {} not found

$ ./unfmt --walk -C fixtures/ugly 'Duplicate event ID: evt-99'
src/events.ts:5:19: … tmpl: Duplicate event ID: {}

$ ./unfmt --walk -C fixtures/ugly 'session started profile=Focus'
src/log.swift:2:29: … tmpl: session started profile={}
```

Real trees, first try (already useful):

```
$ ./unfmt -C ~/…/kizu 'git diff single file failed: fatal: not a git repository (or any of the parent directories): /tmp/nope'
src/git/diff.rs:34:28: score=0.78 lang=rust holes=1 via=full
  tmpl:  git diff single file failed: {}

$ ./unfmt -C ~/…/voidtrace 'Duplicate event ID: evt-abc'
packages/kernel/src/event-queue.ts:61:23: … tmpl: Duplicate event ID: {}

$ ./unfmt -C ~/…/sitbone 'session started profile=DeepWork'
Sources/SitboneCore/SitboneCore.swift:423:33: … tmpl: session started profile={}
```

### Failures that drove v0.2

tenaoshi message lives in an **untracked** file; default `git ls-files --cached` missed it:

```
$ ./unfmt -C ~/…/tenaoshi 'has_more cannot be true when units is empty'
— no template for: has_more cannot be true when units is empty

$ git -C ~/…/tenaoshi status --short -- Engine/Sources/TenaoshiEngine/EditPlan.swift
?? Engine/Sources/TenaoshiEngine/EditPlan.swift
```

sitbone os_log is a **multiline Swift string** with `\` line continuation. The index stored indent + newlines, so a flattened console line missed:

```
$ ./unfmt -C ~/…/sitbone --index | rg 'JSONSessionStore.swift:45'
Sources/SitboneData/JSONSessionStore.swift:45:36: holes=2 static=86 \n                cumulative save failed path={} \n                error={}\n

$ ./unfmt -C ~/…/sitbone 'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
— no template for: cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved
```

voidtrace exact codes ranked **tests above production** (lexicographic path):

```
$ ./unfmt -C ~/…/voidtrace -n 5 'predicate.event-kind-mismatch'
packages/kernel/src/rejected-rule-trace.test.ts:57:11: score=1.00
packages/rules/src/execution.test.ts:133:15: score=1.00
packages/rules/src/execution.test.ts:161:21: score=1.00
packages/rules/src/execution.ts:191:24: score=1.00
```

`--attach` as a query was eaten by argparse:

```
$ ./unfmt -C ~/…/kizu --attach
usage: unfmt [-h] …
unfmt: error: unrecognized arguments: --attach
```

Short Go `open %s: %v` (7 static chars) and `format!("…\\n")` vs a stripped log line also missed in the first fixture pass.

### After the improvement

Default index is the **working tree** (cached + untracked, still gitignored-excluded). Swift `"""` strings apply `\` join + indent strip. Tests sort after production on a score tie. `-e` takes flag-like messages. JSON-looking literals are dropped from the index.

```
$ ./unfmt -C ~/…/tenaoshi 'has_more cannot be true when units is empty'
Engine/Sources/TenaoshiEngine/EditPlan.swift:260:43: score=1.00 lang=swift holes=0 via=full
  tmpl:  has_more cannot be true when units is empty

$ ./unfmt --cached-only -C ~/…/tenaoshi 'has_more cannot be true when units is empty'
— no template for: has_more cannot be true when units is empty

$ ./unfmt -C ~/…/sitbone 'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
Sources/SitboneData/JSONSessionStore.swift:45:36: score=0.75 lang=swift holes=2 via=full
  tmpl:  cumulative save failed path={} error={}

$ ./unfmt -C ~/…/sitbone 'session saved key=2026-08-19 sessionsInDay=3 path=/tmp/x.json'
Sources/SitboneData/JSONSessionStore.swift:88:35: score=0.88 lang=swift holes=3
  tmpl:  session saved key={} sessionsInDay={} path={}

$ ./unfmt -C ~/…/voidtrace -n 5 'predicate.event-kind-mismatch'
packages/rules/src/execution.ts:191:24: score=1.00    # production first
packages/rules/src/execution.ts:203:9: score=1.00
packages/kernel/src/rejected-rule-trace.test.ts:57:11: score=1.00
…

$ ./unfmt -C ~/…/kizu -e 'Ghostty --attach is only supported on macOS (requires AppleScript)'
src/attach.rs:80:21: score=1.00
```

`./demo.sh` after the change: `passed=28 failed=0` (includes the tenaoshi + sitbone multiline dogfood cases).

## Dogfood targets

| Target | What we threw at it |
| --- | --- |
| `fixtures/ugly` | weird filename, nested path, `node_modules`, `*.min.js`, rust/js/py/swift/go |
| `/Users/annenpolka/ghq/github.com/annenpolka/kizu` | anyhow / format! / `.context`, backticks inside templates |
| `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` | JS templates, two-hole RangeError, problem codes |
| `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` | Swift `\(` + `privacy:`, multiline `"""` logs |
| `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` | untracked Swift sources |
| `/Users/annenpolka/ghq/github.com/annenpolka/skills` | almost no runtime strings (shell/py scripts only) |

## Surprises

- kizu `.context("git diff single file")` is a no-hole string that usefully matches as a *prefix* of the wrapped error, next to the `failed: {}` template.
- sitbone logs are not the source text. `"""` + `\` continuation is a hidden pretty-printer; flattening it is the whole game.
- A large fraction of a “source index” is tests repeating the same literal. Ranking is not optional.
- tenaoshi’s real engine sources can sit untracked beside a partial git tree. “Search the repo” must mean the working tree.
- skills is a markdown garden; inverse printf is the wrong primitive there (428 hits, all from helper scripts).

## Failures

- Interpolated *tail* only (`fatal: not a git repository…`) does not find `git diff single file failed: {}`. Correct for the primitive; still a human disappointment.
- rustc diagnostics (`error[E0425]: …`) are not in the project. unfmt is not a compiler database.
- `--attach` alone is a flag, not a message; even with `-e` there is no template equal to `--attach`.
- No stitching of anyhow *chains* into one explanation (`context` + `inner` as a path). Both appear independently.
- Adjacent concatenation (`"open " + path + ": " + err`) is not a template.
- Indexes stay large (voidtrace ~11k rows): test titles, date formats, short identifiers.
- Markdown / prose claims are out of scope.

## Suggested mutations

- Reconstruct an error as an ordered *chain* of templates (`context: inner`).
- `--contains` mode: treat the query as a needle inside no-hole templates (for `--attach`).
- Language-aware public-surface only (skip test titles, skip `yyyy-MM-dd`).
- History: if HEAD misses, search `git log -G` / dangling blobs for the template (the error is from an older build).
- `spite`: delete a source file and report which tests still pass.
- stdin block mode for multi-line Rust panics.

## Kill / keep

**Keep.** It is a one-verb filter, it already hits real kizu/voidtrace/sitbone/tenaoshi messages, and the first improvement came from those trees rather than from the fixtures. Not a platform. Worth mutating the chain-reconstructor and the working-tree vs HEAD distinction; not worth turning into an LSP.
