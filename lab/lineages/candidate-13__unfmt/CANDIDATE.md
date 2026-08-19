# candidate-13 — unfmt

## Primitive

The observed runtime string is the query language: paste an error, log line, or assertion message, and invert it against source format/template literals to recover the producing site and the hole bindings.

## Why this might not exist

Developers already `rg` a distinctive word from a log line and hope the format string is close enough. That fails when the unique part is interpolated (`failed: {stderr}`), when the paste includes a timestamp or log level, when Swift hides extra quotes inside `\(...)`, and when a multiline template was joined with `\`. Observability stacks invert *their* grok patterns against logs; nobody ships a local Unix verb that inverts an arbitrary observed string against a working tree. The missing verb is "where could this value have been printed?"

Privately listed four primitives, discarded the two most conventional (`thaw`: files whose imports moved; `blame-why`: `git log -L` as a decision stack). The other remaining idea was `gone` (discover retired names from diffs and hunt residue). Implemented `unfmt` because it is a new query primitive, not a git hygiene report.

## How to run

```bash
cd /Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01a85-7970-76f3-9304-ba3259b5566f
./demo.sh
./unfmt -C /path/to/repo 'observed string'
echo 'observed string' | ./unfmt -C /path/to/repo --json
./unfmt --exact -C /path/to/repo 'must be the entire formatted string'
```

## Empirical transcript

### v0.1 (commit 16cc644) — working prototype

Fixture suite (`./demo.sh`) passed: static, Rust `{}` / `{rest}`, Swift `\()`, Python `{name!r}`, Go `%s`, JS `` `${path}` ``, shell `$HOST`/`${STAGE}`, path with spaces, JSON, miss→exit 1.

Real repos, v0.1:

```
$ ./unfmt -C kizu 'failed to spawn `git apply --reverse`'
src/git/revert.rs:46:18: static  score=2.000
  template: failed to spawn `git apply --reverse`

$ ./unfmt -C kizu '`git apply --reverse` failed: patch does not apply'
src/git/revert.rs:63:28: brace  score=0.450
  template: `git apply --reverse` failed: {1}
  {1} = patch does not apply

$ ./unfmt -C kizu 'unparseable `diff --git` header: a/foo b/bar'
src/git/parse.rs:171:40: brace  score=0.705
  template: unparseable `diff --git` header: {rest}
  {rest} = a/foo b/bar

$ ./unfmt -C sitbone 'presentThreshold must be greater than absentThreshold (got 0.3 vs 0.9)'
Sources/SitboneCore/PresenceArbiter.swift:40:13: swift  score=0.916
  template: presentThreshold must be greater than absentThreshold (got \(presentThreshold) vs \(absentThreshold))
  {presentThreshold} = 0.3
  {absentThreshold} = 0.9

$ ./unfmt -C tenaoshi 'Anthropic APIがHTTP 429を返した: rate limited'
Engine/Sources/TenaoshiEngine/Adapters/AnthropicMessagesClient.swift:86:34: swift  score=0.369
  template: Anthropic APIがHTTP \(http.statusCode)を返した: \(detail)
  {http.statusCode} = 429
  {detail} = rate limited

$ ./unfmt -C voidtrace 'Cannot enqueue event before processed time 1200: 800'
packages/kernel/src/event-queue.ts:65:9: dollar  score=0.812
  template: Cannot enqueue event before processed time ${this.#processedTimeMs}: ${snapshot.timeMs}
  {this._processedTimeMs} = 1200
  {snapshot.timeMs} = 800

$ ./unfmt -C skills 'File not found: /tmp/foo.md'
execplan-manager/scripts/validate_execplan.py:55:48: brace  score=0.439
  template: File not found: {file_path}
  {file_path} = /tmp/foo.md
```

### Failures recorded on first dogfood (v0.1)

```
$ ./unfmt -C kizu '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
unfmt: no template produced '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'

$ ./unfmt -C sitbone 'camera presence enabled'
unfmt: no template produced 'camera presence enabled'
# source is: "camera presence \(self.isCameraEnabled ? "enabled" : "disabled", privacy: .public)"
# scanner terminated the string at the nested quote

$ ./unfmt -C sitbone 'transition focused → idle reason=timeout idle=12s'
unfmt: no template produced '...'
# source is a Swift """ ... \ newline-joined Logger string
```

Also: a 7-hole sitbone transition that *could* be extracted after the scanner fix still scored 0.06 < `--min-score 0.12` (hole tax of `0.12 * N` punished the exact templates we want). Span matching without a length floor then ranked `"git apply"` and `"--reverse"` and whitespace-only strings above the real message.

### After improvement (v0.2)

Span/prefix match; Swift-aware strings (quotes inside `\(...)`); `\` line-join + dedent; scoring that rewards literal uniqueness instead of taxing holes; drop space-only templates and short static fragments as substrings; rank by how much of the query is consumed so a test-file prefix loses to the real template.

```
$ ./unfmt -C kizu '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
src/git/revert.rs:46:18: static  score=1.381  span  span=27-64
  template: failed to spawn `git apply --reverse`
  prefix: 2026-08-19T23:50:01Z ERROR

$ ./unfmt -C sitbone 'camera presence enabled'
Sources/SitboneCore/SitboneCore.swift:361:17: swift  score=0.775  full
  template: camera presence \(self.isCameraEnabled)
  {self.isCameraEnabled} = enabled

$ ./unfmt -C sitbone 'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0'
Sources/SitboneCore/SitboneCore.swift:554:35: swift  score=1.001  full
  template: transition \(oldPhase.rawValue) → \(newPhase.rawValue) reason=\(reason.name) idle=\(idle)s deserted=\(counters.deserted.value) driftRecovered=\(counters.driftRecovered.value) awayRecovered=\(counters.awayRecovered.value)
  {oldPhase.rawValue} = focused
  {newPhase.rawValue} = idle
  {reason.name} = timeout
  {idle} = 12
  {counters.deserted.value} = 0
  {counters.driftRecovered.value} = 0
  {counters.awayRecovered.value} = 0

$ echo 'failed to spawn `git apply --reverse`' | ./unfmt -C kizu
src/git/revert.rs:46:18: static  score=2.000  full
  template: failed to spawn `git apply --reverse`

$ ./unfmt --exact -C fixtures '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
# exit 1 — prefix refused
```

`./demo.sh` still exits 0, now including prefixed / nested-quote / multiline-join / `--exact` cases.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — Rust `anyhow!` / `format!` / static context strings
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — Swift interpolations, nested quotes, Logger `"""` + `\`
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — Japanese Swift errors, empty `\(hint)` holes, `detail.prefix(300)`
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — TS template literals; test-file static prefix vs real template
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` — Python f-string `File not found: {file_path}`
- `fixtures/` — mixed languages, `dir with spaces/t.rs`, nested `git-ish/note.sh`

## Surprises

- Sitbone's "simple" camera log is a ternary with nested quotes inside the interpolation. A language-blind quote scanner cannot see it.
- A 7-hole Logger line is a *better* match than a 1-hole `error: {}`, but a naive per-hole tax ranked it to zero.
- The test file often contains the template's literal prefix as a static string. Coverage-of-query ranking is required or the assertion outranks the producer.
- Swift `\(` + `privacy: .public` is one hole. Taking the leading identifier as the binding name is enough to be readable.

## Failures

- **String concatenation** (`"foo " + x + " bar"`, `format!(concat!(...))`) is still several templates, not one.
- **Abridged pastes** of a long Logger line (user omits `deserted=…`) miss; we do not yet match a query that is a prefix of a template instance.
- **Dynamic format strings** (format stored in a variable) are invisible.
- **i18n catalogs** / gettext `msgid` not indexed unless they look like source strings.
- Span mode can still surface a long static comment that happens to be a substring of the query; `--exact` opts out.

## Suggested mutations

- Treat adjacent literals with an expression between them as one template (`"statting " + path` → `statting {path}`).
- Invert a whole log file (`unfmt --batch`) and emit `line → file:line` as a map.
- Optional tree-sitter extraction for raw strings / implicit format args.
- Cache the template index keyed by `git ls-files -s` for large trees.
- Hybrid with `gone`: if inversion fails, search git history for a template that used to produce this string.

## Kill / keep

**Keep.** It is a small verb, it ran on five real trees, the first dogfood failures were specific and the second pass fixed them without turning the tool into a platform. The interaction (paste what you saw) is the thing that did not exist; the scanners are just enough machinery to make that verb true.
