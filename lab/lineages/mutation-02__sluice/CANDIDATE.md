# mutation-02 — sluice

## Primitive

Inverse printf as a filter: runtime string(s) on argv or stdin, templates on the other channel (`--templates -` / a file / `--files`). No implicit repository walk.

## Why this might not exist

`unfmt` (candidate-08) already inverts `{}` / `${}` / `\(` / `%s` against a tree. The buried assumption is that *discovery* belongs to the matcher: git ls-files, a walker, skip lists, cached-vs-untracked. That is the part that does not compose. You cannot `git log -p | unfmt`. You cannot ask git grep (tracked only) one minute and `rg --no-ignore` (untracked) the next without the tool growing flags for each policy. The missing verb is the other half of inverse printf: **consume a template stream**.

Discarded (more conventional): add `--stdin-templates` to unfmt and keep `-C`. That leaves the walker in charge.

## How to run

```bash
chmod +x sluice
./sluice --selftest
./demo.sh
rg -n --type rust 'format!|anyhow!' /path | ./sluice 'filled-in error'
rg -l --type swift 'Logger' /path | ./sluice --files - 'filled-in log'
git -C /path grep -n -e 'format!' -- '*.rs' | ./sluice --chdir /path 'filled-in error'
git log -p -S 'failed:' -- src | ./sluice 'filled-in error'
./sluice --templates extracted.txt --any < build.log
```

Exit 0 = every argument matched (stdin / `--any`: any line). Exit 1 = miss. Exit 2 = usage. Directories on `--templates`/`--files` exit 2; the tool will not walk.

## Empirical transcript

### v0.1 working prototype

`./sluice --selftest` → `selftest: ok`

`./demo.sh` → `passed=36 failed=0`

Fixture stream (policy is the producer):

```
$ rg -n --no-heading -g '*.py' 'f"' fixtures | ./sluice 'user 42 not found'
fixtures/src/user.py:2:20: score=0.70 lang=py holes=1 via=full from=grep
  tmpl:  user {} not found

$ ./sluice --templates fixtures/streams/raw.txt --from raw 'open /tmp/x: permission denied'
fixtures/streams/raw.txt:1:1: … tmpl:  open {}: {}
```

Default `rg` hides gitignored `node_modules/`; `rg --no-ignore` admits it. `*.min.js` is *not* ignored unless the caller writes `-g '!*.min.js'`. sluice never had a skip list.

### Real trees, first try (templates via rg / git)

```
$ rg -n -g '*.rs' -g '!target/**' 'format!|anyhow!|bail!' ~/…/kizu \
    | ./sluice 'git diff single file failed: fatal: not a git repository (or any of the parent directories): /tmp/nope'
…/kizu/src/git/diff.rs:34:28: score=0.68 lang=rust holes=1 via=full from=grep
  tmpl:  git diff single file failed: {}

$ rg -n -g '*.ts' -g '!node_modules/**' 'Duplicate event ID|throw new' ~/…/voidtrace \
    | ./sluice 'Duplicate event ID: evt-abc'
…/event-queue.ts:61:23: … tmpl:  Duplicate event ID: {}

$ rg -n -g '*.swift' 'session started profile' ~/…/sitbone \
    | ./sluice 'session started profile=DeepWork'
…/SitboneCore.swift:423:33: … tmpl:  session started profile={}

$ rg -n -g '*.swift' 'has_more cannot be true' ~/…/tenaoshi \
    | ./sluice 'has_more cannot be true when units is empty'
…/EditPlan.swift:260:43: score=1.00 … tmpl:  has_more cannot be true when units is empty
```

tenaoshi's engine source is **untracked**. That is no longer sluice's problem:

```
$ git -C ~/…/tenaoshi grep -n -e 'has_more cannot be true' -- '*.swift'
# (empty)

$ rg -n -g '*.swift' 'has_more cannot be true' ~/…/tenaoshi | ./sluice -q -e 'has_more cannot be true when units is empty'
# exit 0
```

History works because a patch is a stream:

```
$ git -C ~/…/kizu log -p -S 'git diff single file failed' -- src/git/diff.rs \
    | ./sluice 'git diff single file failed: boom'
src/git/diff.rs:34:28: score=0.93 lang=rust holes=1 via=full from=patch
  tmpl:  git diff single file failed: {}
```

### Failures that drive the first improvement

`git -C kizu grep -n -e 'format!' -- '*.rs' | ./sluice 'git diff single file failed: boom'` → **miss**. The template lives in `anyhow!(…)`, not `format!`. unfmt-the-walker would have extracted both. A stream is only as complete as the producer. (Broader `rg 'format!|anyhow!'` hits.)

sitbone multiline via `rg -n` (the default instinct) is a **degraded** 1-hole fragment. The next hole is on the next line, behind a `\`:

```
$ rg -n -g '*.swift' 'session saved key' ~/…/sitbone \
    | ./sluice 'session saved key=2026-08-19 sessionsInDay=3 path=/tmp/x.json'
…/JSONSessionStore.swift:89:1: score=0.63 holes=1 from=fragment
  tmpl:  session saved key={}

$ rg -l -g '*.swift' 'session saved key' ~/…/sitbone \
    | ./sluice --files - 'session saved key=2026-08-19 sessionsInDay=3 path=/tmp/x.json'
…/JSONSessionStore.swift:88:35: score=0.88 holes=3 from=file
  tmpl:  session saved key={} sessionsInDay={} path={}
```

`--files` already has the right answer. Requiring the caller to remember `rg -l` + `--files` for every continued string is the v0 tax.

Relative paths from `git -C repo grep` cannot be opened from another cwd. Line-mode still works when the line is complete; hydration would need a chdir.

### After the improvement (v0.2)

Default `--open auto`: a grep/path record that names a file we can open is a **file selector**. The line is a hint; the file is the template source. `--open never` is the old line-only filter. `--chdir DIR` (`-C`) resolves relative stream paths and **does not scan DIR**.

sitbone `rg -n` now yields the real multiline template:

```
$ rg -n -g '*.swift' 'session saved key' ~/…/sitbone \
    | ./sluice 'session saved key=2026-08-19 sessionsInDay=3 path=/tmp/x.json'
…/JSONSessionStore.swift:88:35: score=0.88 holes=3 from=file
  tmpl:  session saved key={} sessionsInDay={} path={}

$ rg -n -g '*.swift' 'cumulative save failed' ~/…/sitbone \
    | ./sluice 'cumulative save failed path=/Users/x/Library/cumulative.json error=The file could not be saved'
…/JSONSessionStore.swift:45:36: score=0.75 holes=2 from=file
  tmpl:  cumulative save failed path={} error={}
```

`git grep format!` still does not contain the `anyhow!` *line*, but it does name `diff.rs` (other `format!` calls). `--chdir` makes that path openable:

```
$ git -C ~/…/kizu grep -n -e 'format!' -- '*.rs' \
    | ./sluice --templates - --open never 'git diff single file failed: boom'
— no template for: git diff single file failed: boom

$ git -C ~/…/kizu grep -n -e 'format!' -- '*.rs' \
    | ./sluice --chdir ~/…/kizu 'git diff single file failed: boom'
src/git/diff.rs:34:28: score=0.93 holes=1 from=file
  tmpl:  git diff single file failed: {}
```

`./demo.sh` → `passed=40 failed=0`.

Patches stay stream-pure (`git log -p` is history, not the working tree) unless `--open always`.

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/` | `rg -g`, `--templates` file, `--files` | rust/js/py/swift/go, spaces in path, nested, skip policy |
| `…/kizu` | `rg 'format!\|anyhow!'`, `git grep`, `git log -p` | anyhow / format! / `--attach` |
| `…/voidtrace` | `rg` + optional `-g '!*test*'` | JS templates, two-hole RangeError, problem codes |
| `…/sitbone` | `rg -n` vs `rg -l \| --files` | Swift `\(` + multiline `"""` |
| `…/tenaoshi` | `git grep` vs `rg` | untracked Swift sources |

## Surprises

- The skip-list fight (`node_modules`, `*.min.js`, untracked) evaporates. It was never a matcher problem.
- `git log -p` is the first thing unfmt could not do and sluice can. History is a stream for free.
- A narrow producer is a new class of miss (`format!` vs `anyhow!`). Walking hid that.
- Grep-line fragments of Swift `""" \` logs still *match*, just with the wrong hole count. Easy to mistake for success.
- voidtrace production-before-test ranking still matters when the caller does *not* glob tests out; when they do, the stream is already clean.

## Failures

- Interpolated tail only (`fatal: not a git repository…`) still does not find `git diff single file failed: {}`.
- Adjacent concatenation (`"open " + path + ": " + err`) is not a template (bundle.min.js is a quote plus `+x`).
- `git -C repo grep` relative paths still need `--chdir`; v0.2 added that prefix without growing a walker.
- No stitching of anyhow chains.
- Markdown / JSON fixture hits appear if the producer selected them (voidtrace golden files). That is now correct, and a `-g '*.ts'` away.

## Suggested mutations

- Reconstruct an error as an ordered *chain* of templates (`context` + inner).
- `--from blame` / `git log -G` wrapper that still only emits a stream.
- Prefer templates whose span covers the grepped line when a hydrated file has many strings.
- Language-aware public-surface filter as a *producer* (`rg` types), not a walker flag.

## Kill / keep

**Keep.** The flipped assumption is real: one command is gone (`-C` scan; `-C` now only resolves paths), a family of pipelines appeared (`rg`, `git grep`, `git log -p`, extract files). It already hits kizu / voidtrace / sitbone / tenaoshi *without* owning their ignore policies. v0.2 hydrated files the producer named; do not grow the walker back.

## What the flipped assumption bought and lost

**Bought**

- Composability: any tool that emits grep lines, paths, patches, or JSONL is an indexer.
- Policy lives in the producer. Tracked-only (`git grep`) vs working tree (`rg`) vs ignored (`rg --no-ignore`) vs tests-out (`-g '!*test*'`) vs history (`git log -p`) are not flags on sluice.
- tenaoshi untracked sources work the moment `rg` sees them; unfmt had to invent `--cached-only` vs working-tree.
- A saved `--extract` file is a reusable index. Match a log later without touching the tree.

**Lost**

- One-shot `tool -C repo 'message'`. You must know *how* to produce templates.
- Completeness. A walker extracts every string; `rg 'format!'` will not see `anyhow!` on the next line.
- Completeness still depends on the producer naming the *file*. A `git grep` that never touches `diff.rs` cannot hydrate the anyhow! there.
- `--open auto` re-reads working-tree files. That is wrong for `git log -p` (hence patch stays stream-pure) and for a blob that no longer matches disk.
- Relative paths still need an explicit `--chdir`. We will not guess the repo.
