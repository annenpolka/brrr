# mutation-43 — scribe

## Primitive

A SARIF / clang / Swift diagnostic stream is a document of *nested* locators: rewrite stale addresses from directory A onto B by content fingerprint; emit valid JSON of the same schema. The path is not cargo's sibling `file_name` + `line_start`. It is `physicalLocation.artifactLocation.uri` + `region.startLine` (clang `caret`, Swift `key.filepath` / serialized `filename`).

## Why this might not exist

`flume` (mutation-04) relocates `file:line` in a stdin→stdout log. `inlay` (mutation-26) walks cargo/rustc JSON where the path and the line are siblings. inlay itself suggested the next flip: SARIF / clang JSON / Swift serialized diagnostics as first-class schemas. A SARIF locator is *not* a sibling pair. `uri` lives under `artifactLocation`; `startLine` is an integer under `region`. A text splice misses the integer or unseals the document when the dest path contains `"`. `jq` does not know locators. `inlay` does not know `physicalLocation`. Source maps are for minifiers.

## How to run

From the worktree root:

```bash
chmod +x ./scribe
./scribe --help
./demo.sh
cat results.sarif | ./scribe --from-dir oldtree --to-dir newtree
clang -fdiagnostics-format=json src.c 2>/dev/null | ./scribe --from-dir oldtree --to-dir newtree --trace
```

Exit 0 on success. `--strict` exits 1 if a locator cannot be read from `--from-dir`. Confirmed deletions pass through on stdout (they are answers, not errors); `--trace` reports them on stderr. The binary never calls git — a stub `git` on PATH dies if it is touched. Non-JSON chatter passes through. Concatenated JSON values (NDJSON, pretty-printed objects, one array) are the ingest. Pretty input stays pretty (`indent=2`); compact NDJSON stays one object per line (`--compact` / `--indent` override).

## The assumption that was flipped

Killed: “the schema is cargo's `file_name` + `line_start` (or a `file:line` substring).”

New: scribe is a **schema-shaped JSON rewriter**. `--from-dir` and `--to-dir` only. stdin is SARIF / clang `-fdiagnostics-format=json` / Swift SourceKit or serialized-diag JSON; stdout is the same stream with locators rewritten *inside nested values*. A SARIF `physicalLocation` is one locator. A clang `caret` is one locator. A Swift `key.filepath` + `key.line` is one locator. Cargo `file_name` + `line_start` is left stale on purpose.

### Bought

- Unix-composable on the streams GitHub code scanning, clang, and SourceKit already emit. No `jq` reconstruction into `file:line` for flume.
- Nested pairs move together: `uri` + `startLine` + `endLine`; clang `file` + `line` + `offset`; Swift `key.filepath` + `key.line` + `key.offset`. Line fields stay JSON numbers.
- Re-serialization: dest paths with quotes, spaces, unicode stay valid JSON.
- Dest-owned `byteOffset` / `charOffset` / `offset` / `snippet.text` / rustc gutters inside `message.text`.
- Pretty vs NDJSON: a pretty SARIF file is still a SARIF file; a clang array on one line stays one line.
- ANSI-wrapped locators inside rendered/message strings still bind; wrapping resets survive.
- Path-only SARIF `runs[].artifacts[].location.uri` is not a locator (no region). Same rule as inlay's `target.src_path`.

### Lost

- Cannot name two SHAs; someone else must materialize trees (`git archive` in `demo.sh`).
- Cannot ask `scribe src/app.rs:529` as a one-shot. Everything is a JSON stream.
- Cargo / rustc `--error-format=json` sibling spans are not rewritten (inlay's job). String values inside them still move if they contain `file:line`.
- Insignificant JSON whitespace of compact input is not preserved (validity and pretty-vs-NDJSON, not byte identity).
- Binary Swift `.dia` bitstreams are not JSON; we take the JSON dumps (SourceKit `key.*`, serialized-diag records).

## Empirical transcript

### Working software (v0.1)

Synthetic SARIF + clang array + Swift SourceKit + serialized-diag + cargo-negative + chatter, stub `git` on PATH:

```
$ cat mixed.jsonl | ./scribe --from-dir from --to-dir to
   Compiling ugly v0.1.0
{"$schema":"…sarif-2.1.0.json","version":"2.1.0","runs":[{…,
  "results":[{"locations":[{"physicalLocation":{"artifactLocation":{"uri":"src/app/layout.rs"},
    "region":{"startLine":4,"byteOffset":65,"snippet":{"text":"pub fn seen_hunk_fingerprint("}}}}],
   "fixes":[{"artifactChanges":[{"artifactLocation":{"uri":"src/app/layout.rs"},…}]}]},
  {… "uri":"file:///home/runner/work/ugly/ugly/src/app/navigation.rs","startLine":1 …},
  {… doomed src/calc.py startLine 11 unchanged}]}]}
[{"kind":"error","locations":[{"caret":{"file":"src/app/layout.rs","line":4,"offset":65}}]}]
{"key.diagnostics":[{"key.line":23,"key.filepath":"Sources/SitboneCore/PresenceArbiter.swift",…}]}
{"diagnostics":[{"filename":"…/KinsokuEngine.swift","line":12,…}]}
{"reason":"compiler-message","message":{"spans":[{"file_name":"src/app.rs","line_start":4}]}}
not a locator, just chatting about foo:bar and error:1
```

`startLine` is still an integer. Dest path `src/quo"te.py` dumps as `src/quo\"te.py` and `json.loads`. Cargo `file_name`+`line_start` is still `src/app.rs:4` — the flip is visible in a type. Path-only `artifacts[0].location.uri` stayed `src/app.rs`.

Real copies (`git archive` into temp dirs; scribe itself never talks to git):

```
$ cat kizu.sarif | ./scribe --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# uri   file:///home/runner/work/kizu/kizu/src/app.rs
#    →  file:///home/runner/work/kizu/kizu/src/app/layout.rs
# startLine 529 → 17   (integer)
# byteOffset 18000 → 791 (dest-owned, col 5)
# snippet    pub fn seen_hunk_fingerprint(     (dest-owned)
# message    --> …/src/app/layout.rs:17:5
# gutter     17 | pub fn seen_hunk_fingerprint(
# second result  src/app.rs:543 → src/app/navigation.rs:22
```

```
$ cat sit.json | ./scribe --from-dir sitbone-a95da43 --to-dir sitbone-HEAD
# key.filepath PresenceArbiter.swift  key.line 45 → 75
# key.offset dest-owned
# serialized-diag filename line 45 → 75; url / timeout:5 chatter untouched
```

```
$ cat vt.sarif | ./scribe --from-dir voidtrace-HEAD --to-dir voidtrace-HEAD
# evaluate.ts:40 KERNEL_ENGINE_VERSION identity
# evaluate.ts:1  import { stays; does not jump to cli.ts clones
```

### Failures recorded against v0.1

Colorized `message.text` bound (strip-ANSI map) but ate wrapping resets:

```
# input   ESC[1msrc/app.rsESC[0m:4:1
# v0.1    ESC[1msrc/app/layout.rs:4:1     ← reset gone; colon stays bold
# gutter  ESC[32m 4ESC[0m |  →  ESC[32m 4 |   ← reset after the number gone
```

Pretty vs NDJSON already preserved in v0.1 (`looks_pretty` on the original slice). The remaining lie was ANSI-inside-rendered, the gap inlay named.

### After the improvement (v0.2)

Re-insert a reset that sat between path and `:line`. Gutter splice ends after the last digit, not at the next visible char.

```
$ cat ansi.sarif | ./scribe --from-dir from --to-dir to
# message.text contains ESC[1msrc/app/layout.rsESC[0m:4:1
# gutter            ESC[32m 4ESC[0m |
```

Same kizu / sitbone / voidtrace streams unchanged. `./demo.sh` exits 0.

## Dogfood targets

- Synthetic two-directory fixture in `./demo.sh`: SARIF physicalLocation + artifactChanges.replacements, clang caret/ranges/offset, Swift SourceKit `key.*`, serialized-diag `filename`/`line`/`offset`, cargo-negative, deletion, unique-token trees with no shared history, unicode, dest path containing `"`, pretty vs NDJSON, ANSI-wrapped rendered, `--strict` missing path vs confirmed deletion. Stub git on PATH.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` and `HEAD` (9480-line `src/app.rs` split → `layout.rs:17` / `navigation.rs:22`), plus the live working tree as `--to-dir`. Gold is a SARIF file constructed from that locator, not cargo JSON.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` at `a95da43` and `HEAD` (`detect()` 45 → 75) as SourceKit + serialized-diag JSON, plus live tree.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` at HEAD: `evaluate.ts:40` identity and `evaluate.ts:1` `import {` must not jump to other files. Not pin: no leftover-name, no token mint.

## Surprises

- The flip is visible in a type: inlay can never rewrite `region.startLine` because it is not a sibling of `uri`. The first SARIF object in the fixture is the proof. The cargo object in the same stream staying stale is the other half of the proof.
- SARIF `fixes[].artifactChanges` is the same nested shape (`uri` on one object, `startLine` on `deletedRegion`). Treating `physicalLocation` only would leave the fix pointing at yesterday.
- Path-only `run.artifacts[].location.uri` looks like a path and is not a locator. Leaving it stale is correct — the catalog names the original artifact, not a diagnostic span. After a file-split, two results that shared `index: 0` must not keep sharing it; we write dest `uri` onto each location instead of mutating the catalog.
- Unique-basename binding still makes Swift SourceKit usable: `key.filepath: "PresenceArbiter.swift"` has no tree prefix.
- Silent pass-through of deletions is the right JSON default. `src/calc.py` startLine 11 (doomed) staying in the object is honest.
- Pretty-printed SARIF falling out of NDJSON line splitting is why ingest is `raw_decode` *and* why emit inspects the original slice. That is the JSON object, not an add-on flag.
- ANSI wrap is not a locator *and* not a field. v0.1 rewrote the visible path and still shipped a contradictory color run. The first colorized dogfood was the only way to see it.

## Failures

- rustc multi-hunk snippets whose later gutter numbers are *not* old_line+k (a split function) will follow the first locator's offset and can land wrong.
- Common/`}`-only lines refuse to fingerprint (`unresolved`) and pass through.
- `byteOffset` assumes `\n` UTF-8. SARIF `charOffset` uses Python code points, not UTF-16. Wide chars and `\r\n` files can be off by a few.
- A log that already mixes old *and* new paths will rewrite only what binds against `--from-dir`.
- Concatenated pretty-printed objects with leading commentary on the same line as `{` can fail `raw_decode` and pass through as raw.
- Binary `.dia` files are out of scope.
- Whole-tree walk of a dirty kizu working tree (~2700 e2e fixtures) is acceptable but not free; copies via `git archive` are the intended dogfood.

## Suggested mutations

- LSP `textDocument/publishDiagnostics` (0-based `range.start.line` + `uri`) as another first-class schema — different off-by-one, same nested shape.
- `scribe --index` to dest-own SARIF `runs[].artifacts` when every location sharing an `index` moved to the *same* dest file, and to drop `index` when they split.
- Inverse: emit SARIF *from* a flume text log / inlay cargo stream, so the three filters meet in the middle.
- `--watch` a pinfile of SARIF logs, rewrite on tree change (scar-review companion). Do not become pin.

## Kill / keep

**Keep.** The flipped assumption is the primitive: nested schema locators in, same schema out, two directories, no git. Empirically hits kizu's `app.rs` split through a SARIF file (uri *and* startLine *and* dest `byteOffset` *and* snippet *and* gutter), sitbone's shifted `detect()` through SourceKit JSON, voidtrace identity without leftover-name, and a mixed SARIF/clang/Swift stream with a stub git that never fires and a cargo span that stays stale. The v0.2 ANSI wrap is evidence the string value is real: a text splice cannot keep `ESC[0m` between path and colon while still emitting valid JSON with a quote in the dest uri. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just a backend.
