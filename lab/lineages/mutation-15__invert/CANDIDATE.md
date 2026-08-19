# mutation-15 — invert

## Primitive

Inverse printf as a **filter that binds names**: runtime string(s) on argv or stdin, templates on the other channel (`--templates -` / a file / `--files`). No implicit repository walk. Each hit unpacks `{rest}`, `\(oldPhase.rawValue)`, `${snapshot.id}` into named bindings, and a timestamp wrapper is a reported **span**, not a discarded prefix.

## Why this might not exist

sluice (mutation-02) flipped unfmt's buried walker: templates arrive on a stream. That is the right object. What it still threw away was the **payload**. Holes printed as `{}`. A 7-hole sitbone Logger line matched, but you could not tell `idle` from `deserted`. A kizu paste `2026-08-19T23:50:01Z ERROR failed to spawn…` "worked" only because the filter silently stripped the wrapper — `--exact` had nothing to refuse, and the leftover was gone. Sitbone's camera line `"camera presence \(self.isCameraEnabled ? "enabled" : "disabled", privacy: .public)"` never extracted: a language-blind quote scanner dies at the nested `"`.

unfmt-13 (candidate-13) independently hit those three misses on a walker. The conventional mutation is "copy its scanner into sluice." The missing verb is still a **stream filter**, just one that keeps the names and treats a prefix as a span.

Discarded (more conventional): add `--names` to sluice and keep timestamp stripping. That hides the wrapper the user actually pasted.

## How to run

```bash
chmod +x invert
./invert --selftest
./demo.sh
rg -n --type rust 'format!|anyhow!' /path | ./invert '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
rg -n --type swift 'awayRecovered' /path | ./invert 'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0'
rg -n --type swift 'camera presence' /path | ./invert 'camera presence enabled'
git -C /path grep -n -e 'format!' -- '*.rs' | ./invert --chdir /path 'filled-in error'
git log -p -S 'failed:' -- src | ./invert 'filled-in error'
./invert --templates extracted.txt --any < build.log
./invert --exact --templates extracted.txt 'must be the entire formatted string'
```

Exit 0 = every argument matched (stdin / `--any`: any line). Exit 1 = miss. Exit 2 = usage. Directories on `--templates`/`--files` exit 2; the tool will not walk. `-C` / `--chdir` only resolves relative stream paths.

## Empirical transcript

### v0.1 working prototype

Took sluice's stream ingest (grep / rg-json / patch / `--files` / `--open auto` / `--chdir`). Changed the kernel: tokenize keeps names; match emits bindings.

`./invert --selftest` → `selftest: ok`

`./demo.sh` → `passed=42 failed=0`

Named holes on fixtures:

```
$ rg -n -g '*.py' 'f"' fixtures | ./invert 'user 42 not found'
fixtures/src/user.py:2:20: … tmpl:  user {uid} not found
  {uid} = 42

$ rg -n -g '*.rs' 'format!' fixtures | ./invert 'unparseable `diff --git` header: a/foo b/foo'
  tmpl:  unparseable `diff --git` header: {rest}
  {rest} = a/foo b/foo
```

Real trees, v0.1:

```
$ rg -n -g '*.swift' 'awayRecovered' ~/…/sitbone \
    | ./invert 'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0'
…/SitboneCore.swift:554:35: score=0.94 holes=7
  tmpl:  transition {oldPhase.rawValue} → {newPhase.rawValue} reason={reason.name} …
  {oldPhase.rawValue} = focused
  {idle} = 12
  {counters.awayRecovered.value} = 0

$ rg -n -g '*.rs' 'failed to spawn' ~/…/kizu \
    | ./invert '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
…/revert.rs:46:18: score=1.00 holes=0 via=full
  query: failed to spawn `git apply --reverse`
  tmpl:  failed to spawn `git apply --reverse`
```

7-hole already bound. kizu "survived" by **stripping** the timestamp — the query printed was already the inner string. No `prefix:`.

### Failures that drive the first improvement

```
$ rg -n -g '*.swift' 'camera presence' ~/…/sitbone \
    | ./invert 'camera presence enabled'
— no template for: camera presence enabled
# source is: "camera presence \(self.isCameraEnabled ? "enabled" : "disabled", privacy: .public)"
# scanner terminated the string at the nested quote
```

kizu prefix was a lie of success: sluice-shaped `normalize_query` ate `2026-08-19T23:50:01Z ERROR` before match. unfmt-13's lesson was span, not strip — leftover reported, `--exact` can refuse it.

A first ranking draft that applied the short-static infix floor to **holed** templates then rejected `user {uid} not found` under `ERROR [worker] user 7 not found` (static=15 < 16). Hole templates already have `MIN_STATIC_HOLE`; that floor is only for static decoys.

### After the improvement (v0.2)

Swift-aware `"` / `"""` readers: `\(` is one interpolation, quotes inside it are not the closer. Match the original paste; leftover before the first literal is a **span**. Score by how much of the query is consumed plus literal uniqueness; **reward** holes (`0.03 * min(N, 7)`), do not tax them. `--exact` refuses prefix/suffix. Grep line is a proximity hint after `--open` hydrates the file.

```
$ rg -n -g '*.rs' 'failed to spawn' ~/…/kizu \
    | ./invert '2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`'
…/revert.rs:46:18: score=0.66 lang=rust holes=0 via=span from=file
  query: 2026-08-19T23:50:01Z ERROR failed to spawn `git apply --reverse`
  tmpl:  failed to spawn `git apply --reverse`
  prefix: 2026-08-19T23:50:01Z ERROR
  span=27-64

$ ./invert --exact --templates -  <<same stream>> '2026-08-19T23:50:01Z ERROR …'
# exit 1 — prefix refused

$ rg -n -g '*.swift' 'camera presence' ~/…/sitbone \
    | ./invert 'camera presence enabled'
…/SitboneCore.swift:361:17: score=0.90 holes=1
  tmpl:  camera presence {self.isCameraEnabled}
  {self.isCameraEnabled} = enabled

$ rg -n -g '*.swift' 'awayRecovered' ~/…/sitbone \
    | ./invert 'transition focused → idle reason=timeout idle=12s deserted=0 driftRecovered=0 awayRecovered=0'
…/SitboneCore.swift:554:35: score=1.10 holes=7
  {oldPhase.rawValue} = focused
  {newPhase.rawValue} = idle
  {reason.name} = timeout
  {idle} = 12
  {counters.deserted.value} = 0
  {counters.driftRecovered.value} = 0
  {counters.awayRecovered.value} = 0
```

voidtrace coverage ranking: production two-hole (`score=1.05`) beats the test-file static prefix (`score=0.86`, suffix leftover). tenaoshi Japanese binds `{http.statusCode}=429`, `{detail}=rate limited`.

`./demo.sh` → `passed=46 failed=0`.

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/` | `rg -g`, `--templates` file, `--files` | rust/js/py/swift/go, nested quotes, 7-hole, spaces in path |
| `…/kizu` | `rg 'failed to spawn'`, `git grep format!` | timestamp prefix span, anyhow sibling hydrate |
| `…/sitbone` | `rg -n` / `rg -l` | 7-hole Logger `"""` `\`, camera ternary quotes |
| `…/voidtrace` | `rg` | two-hole `${this.#processedTimeMs}`, test-prefix ranking |
| `…/tenaoshi` | `rg` vs `git grep` | untracked Swift, Japanese interpolations |

## Surprises

- sluice already "survived" the 7-hole line. The failure was **anonymity**, not ranking. Once names stay on the tokens, the same alignment prints `{idle}=12`.
- Silently stripping log prefixes makes `--exact` meaningless and hides the thing unfmt-13 called a span. A stripped-then-exact match outranked the span (score 0.92 vs ~0.5) until the strip variant was deleted.
- `\(x, privacy: .public)` is one hole. The leading identifier path is enough to read.
- Nested quotes only exist because Swift interpolations can contain string literals. A generic escape skip (`i += 2` on `\(`) lands on the inner `"` and ends the template.
- Query-coverage ranking, not a hole tax, is what keeps the 7-hole above a short static substring and above a test-file prefix.

## Failures

- Interpolated tail only (`fatal: not a git repository…`) still does not find `git diff single file failed: {1}`.
- Adjacent concatenation (`"open " + path + ": " + err`) is not one template.
- Abridged pastes of the 7-hole line (user omits `deserted=…`) miss; the query is not a prefix of a template instance.
- Dynamic format strings (format stored in a variable) are invisible.
- `--open auto` re-reads working-tree files. Wrong for `git log -p` unless `--open always`.
- Relative `git -C` paths still need `--chdir`. We will not guess the repo.

## Suggested mutations

- Reconstruct an error as an ordered *chain* of templates (`context` + inner), using the span leftover as the next query.
- Treat adjacent literals with an expression between them as one template (`"statting " + path`).
- Invert a whole log (`--batch`) and emit `line → file:line + bindings` as a map.
- Optional tree-sitter extraction for raw strings / implicit format args.

## Kill / keep

**Keep.** The flipped assumption is still sluice's (stream, no walker). The harvested wins are real and local: names, span, no hole tax, Swift interpolations. It already hits kizu prefix, sitbone 7-hole, sitbone camera, tenaoshi Japanese, voidtrace two-hole *without* owning ignore policy. Do not grow the walker back.

## What the flipped assumption bought and lost

**Bought**

- Composability of sluice, plus the bindings unfmt-13 had on a walker.
- Prefix is evidence, not noise. `--exact` is a real switch.
- 7-hole Logger lines are the *best* match, not a tax victim.
- Policy still lives in the producer.

**Lost**

- One-shot `tool -C repo 'message'`. You must know how to produce templates.
- Completeness still depends on the producer naming the file.
- Span mode can still surface a long static comment that is a substring of the query; `--exact` opts out.
