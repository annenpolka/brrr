# mutation-67 — gist

## Primitive

An LSP `textDocument/publishDiagnostics` stream is a document of *nested* locators: rewrite stale addresses from directory A onto B by content fingerprint; emit valid JSON of the same schema. The path is `uri` (often on the parent params object). The line is 0-based `range.start.line`. Off-by-one is load-bearing.

## Why this might not exist

`flume` relocates `file:line` in a stdin→stdout log. `inlay` walks cargo/rustc JSON where path and line are siblings. `scribe` walks SARIF / clang / Swift: `physicalLocation.artifactLocation.uri` + 1-based `region.startLine`. inlay itself suggested the next flip: LSP as another first-class schema — different off-by-one, same nested shape. An LSP locator is *not* a SARIF region. `range.start.line` is 0-based. `uri` may not even be a sibling of `range` (it lives on `PublishDiagnosticsParams`). A text splice misses the integer, treats 528 as 529, or unseals the document when the dest path contains `"`. `scribe --lsp` would be a flag on the wrong object. `jq` does not know locators.

## How to run

From the worktree root:

```bash
chmod +x ./gist
./gist --help
./demo.sh
cat publish.json | ./gist --from-dir oldtree --to-dir newtree
cat publish.json | ./gist --from-dir oldtree --to-dir newtree --trace
```

Exit 0 when locators rewritten (confirmed deletions are answers). Exit 1 if some locators cannot be read from `--from-dir`. Exit 2 on usage. The binary never calls git — a stub `git` on PATH dies if it is touched. Non-JSON chatter passes through. Concatenated JSON values (NDJSON, pretty-printed objects, JSON-RPC notifications) are the ingest. Pretty input stays pretty (`indent=2`); compact NDJSON stays one object per line.

## The assumption that was flipped

Killed: “the schema is SARIF `uri` + 1-based `startLine` (or cargo's `file_name` + `line_start`).”

New: gist is a **0-based LSP rewriter**. `--from-dir` and `--to-dir` only. stdin is `textDocument/publishDiagnostics` / `Location` / `LocationLink` / `Diagnostic`; stdout is the same stream with locators rewritten *inside nested values*. A `PublishDiagnosticsParams` is one document of locators (one uri, many ranges) and may *fission* when those ranges land in different dest files after a split. A SARIF `physicalLocation` is left stale on purpose. A 1-based `startLine` is rejected with an explicit `ignored	sarif` trace, never silently shifted.

### Bought

- Unix-composable on the stream rust-analyzer / pyright / tsserver already emit. No `jq` reconstruction into SARIF for scribe.
- Nested pairs move together: `uri` + `range.start.line` + `range.end.line`; `relatedInformation[].location`; `LocationLink.targetUri` + `targetRange`. Line fields stay JSON numbers, including `0`.
- Re-serialization: dest paths with quotes, spaces, unicode, `file://` stay valid JSON.
- `data` is kept (walked for nested locators, never dropped).
- Dest-dropped `version` when the uri moved (a stale document version would make a client discard the notification).
- Dest-owned `Content-Length` on the LSP byte frame (UTF-8 length of the rewritten body).
- File-split fission: one notification becomes N of the same schema.
- Pretty vs NDJSON: a pretty JSON-RPC file is still JSON-RPC; compact NDJSON stays one object per line.
- 1-based compiler `file:line` inside `message` still binds (human locators are not LSP); wrapping ANSI survives.
- Path-only / missing-range diagnostics are not locators. Overlapping ranges rewrite independently.

### Lost

- Cannot name two SHAs; someone else must materialize trees (`git archive` in `demo.sh`).
- Cannot ask `gist src/app.rs:528` as a one-shot. Everything is a JSON stream.
- Cargo / rustc `--error-format=json` sibling spans are not rewritten (inlay's job). SARIF `startLine` is not rewritten (scribe's job).
- Insignificant JSON whitespace of compact input is not preserved (validity and pretty-vs-NDJSON, not byte identity).
- Does not become pin (no durable token). Does not walk a git repo.

## Empirical transcript

### Working software (v0.1)

Synthetic JSON-RPC publishDiagnostics + Location + overlapping ranges + missing range + cargo-negative + SARIF-negative + chatter, stub `git` on PATH:

```
$ cat mixed.jsonl | ./gist --from-dir from --to-dir to
   Compiling ugly v0.1.0
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///home/runner/work/ugly/ugly/src/app/layout.rs",
  "diagnostics":[{"range":{"start":{"line":3,"character":0},"end":{"line":3,"character":24}},
    "data":{"rendered":"keep me",…},
    "relatedInformation":[{"location":{"uri":"src/app/navigation.rs",
      "range":{"start":{"line":0,…}}}}]}]}}
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///…/src/app/navigation.rs",
  "diagnostics":[{"range":{"start":{"line":0,…},"end":{"line":7,…}},"data":{"id":99}}]}}
{"uri":"src/math/ops.py","diagnostics":[… overlapping add() both still two diagnostics, line 2 …]}
{"uri":"src/calc.py","diagnostics":[{"message":"no range at all"},{"range":{"start":{"character":0},…}}]}
{"reason":"compiler-message","message":{"spans":[{"file_name":"src/app.rs","line_start":4}]}}
{"version":"2.1.0","runs":[{… "uri":"src/app.rs","startLine":4,"byteOffset":120 …}]}
{"params":{"uri":"src/calc.py","diagnostics":[{"range":{"start":{"line":10,…}}}]}}
not a locator, just chatting about foo:bar and error:1
```

`range.start.line` is still an integer, including `0`. Dest path `src/quo"te.py` dumps as `src/quo\"te.py` and `json.loads`. Cargo `file_name`+`line_start` is still `src/app.rs:4`. SARIF `startLine` is still `4` / `byteOffset` 120. `--trace` prints `ignored	sarif`. One app.rs notification *fissioned* into layout.rs + navigation.rs (version dropped on the moved uri). Missing-range diagnostics stayed on `src/calc.py`.

Real copies (`git archive` into temp dirs; gist itself never talks to git):

```
$ cat kizu.publish.json | ./gist --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# uri   file:///home/runner/work/kizu/kizu/src/app.rs
#    →  file:///home/runner/work/kizu/kizu/src/app/layout.rs
# range.start.line  528 → 16   (integer, 0-based; not 17)
# character 4 kept
# message    --> …/src/app/layout.rs:17:5     (1-based inside the string)
# gutter     17 | pub fn seen_hunk_fingerprint(
# data       {"check":"keep"}
# second notification  src/app.rs → src/app/navigation.rs, line 542 → 21
```

```
$ cat kizu.sarif | ./gist --from-dir kizu-b4e6a5d --to-dir kizu-HEAD --trace
# startLine 529 unchanged; byteOffset 18000 unchanged
# stderr: ignored	sarif	-	-	1-based region.startLine is not LSP range.start.line; use scribe
```

```
$ cat sit.json | ./gist --from-dir sitbone-a95da43 --to-dir sitbone-HEAD
# uri PresenceArbiter.swift  range.start.line 44 → 74
# message PresenceArbiter.swift:75:17
```

```
$ cat vt.json | ./gist --from-dir voidtrace-HEAD --to-dir voidtrace-HEAD
# evaluate.ts line 39 KERNEL_ENGINE_VERSION identity
# evaluate.ts line 0  import { stays; does not jump to cli.ts clones
```

Exit 2 with no `--from-dir`. Exit 1 on `src/does-not-exist.rs`. Exit 0 on confirmed deletion (`calc.py` 0-based 10).

### Failures recorded against v0.1

A real LSP wire stream is byte-framed:

```
Content-Length: 312\r\n
\r\n
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{…src/app.rs…}}
```

v0.1 treats the header as chatter and rewrites only the JSON body. After `app.rs` → `layout.rs` the body is longer; `Content-Length: 312` is now a lie. An LSP client would truncate the notification. Same class of bug as inlay leaving `byte_start` stale and scribe leaving `byteOffset` stale — the dest snapshot owns the payload, so it must own the frame length.

### After the improvement (v0.2)

Parse `Content-Length` / `Content-Type` as a byte frame, rewrite the JSON body, emit a dest-owned `Content-Length` (UTF-8 byte length). File-split fission emits **two** frames. `Content-Type` survives. Chatter before the frame is still chatter.

```
$ cat framed.bin | ./gist --from-dir from --to-dir to
   Compiling ugly v0.1.0
Content-Length: 259\r\n
Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n
\r\n
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{"uri":"…/layout.rs",…}}
Content-Length: 265\r\n
…
{"jsonrpc":"2.0",…,"uri":"…/navigation.rs",…}
```

The source `Content-Length` is not the dest length. Same kizu / sitbone / voidtrace streams unchanged. `./demo.sh` exits 0.

## Dogfood targets

- Synthetic two-directory fixture in `./demo.sh`: JSON-RPC publishDiagnostics, Location, overlapping ranges, missing range, file://, unicode, dest path containing `"`, pretty vs NDJSON, cargo-negative, SARIF-negative (1-based not shifted), deletion, unique-token trees with no shared history. Stub git on PATH. Exit 0/1/2.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` and `HEAD` (9480-line `src/app.rs` split → `layout.rs` 0-based 16 / `navigation.rs` 0-based 21), plus the live working tree as `--to-dir`. Gold is a publishDiagnostics file constructed from that locator, not SARIF. A parallel SARIF file with `startLine: 529` must stay 529.
- Copies of sitbone (`detect()` 0-based 44 → 74) and voidtrace (`evaluate.ts` identity, `import {` at line 0 must not jump).

## Surprises

- The flip is visible in a type *and* in a number: scribe can never emit `range.start.line: 16` because it only knows 1-based `startLine`. kizu's gold is `528 → 16`, not `529 → 17`. Feeding SARIF `startLine: 529` through gist leaves 529. Stuffing the 1-based integer `4` into an LSP `range.start.line` does *not* land on dest line 3 (the 0-based dest of 1-based line 4). Off-by-one is the object.
- `uri` is often not a sibling of `range`. publishDiagnostics has one uri and many ranges. After kizu's godfile split those ranges do not share a dest file, so **one notification becomes two**. Treating `params.uri` like SARIF's per-result `artifactLocation.uri` would pin navigation.rs's diagnostic on layout.rs.
- `range.start.line: 0` is a valid locator (first line of navigation.rs, first line of evaluate.ts). scribe's `as_lineno` rejects `<= 0`. That rejection would have dropped the landing-function diagnostic.
- Path-only / missing-range diagnostics are not locators, same rule as SARIF `runs[].artifacts[].location.uri`. Overlapping ranges on `add()` both moved to `ops.py` and stayed two diagnostics.
- Silent pass-through of deletions is the right JSON default. `src/calc.py` 0-based 10 (doomed) staying in the object is honest.
- `data` must be kept even when it is opaque. Dropping it would be schema-valid JSON and a lie to rust-analyzer.
- Pretty-printed JSON-RPC falling out of NDJSON line splitting is why ingest is `raw_decode`. LSP `Content-Length` falling out of line splitting is why v0.2 scans bytes. That is the LSP object, not an add-on flag.

## Failures

- rustc multi-hunk snippets whose later gutter numbers are *not* old_line+k (a split function) will follow the first locator's offset inside `message` and can land wrong.
- Common/`}`-only lines refuse to fingerprint (`unresolved`) and pass through; exit 1.
- LSP `character` is kept, not dest-owned as UTF-16. Wide chars and a dest line shorter than the original column can be off.
- A log that already mixes old *and* new paths will rewrite only what binds against `--from-dir`.
- When every diagnostic moves off a uri, v0.2 does not emit `diagnostics: []` for the origin document. A client that already applied the old notification will keep stale squiggles on `app.rs`.
- Concatenated pretty-printed objects with leading commentary on the same line as `{` can fail `raw_decode` and pass through as raw.
- Whole-tree walk of a dirty kizu working tree (~2700 e2e fixtures) is acceptable but not free; copies via `git archive` are the intended dogfood.

## Suggested mutations

- Emit an empty `diagnostics: []` notification for the origin uri when every locator moved away (client-clear).
- Dest-own `character` as UTF-16 (the LSP spec unit), not Python code points.
- Inverse: emit publishDiagnostics *from* a flume text log / scribe SARIF, so the four filters meet in the middle.
- `--watch` a pinfile of LSP logs, rewrite on tree change (scar-review companion). Do not become pin.

## Kill / keep

**Keep.** The flipped assumption is the primitive: nested 0-based LSP locators in, same schema out, two directories, no git. Empirically hits kizu's `app.rs` split through a publishDiagnostics file (`uri` *and* 0-based `range.start.line` 528→16 *and* fission into layout.rs + navigation.rs *and* dest-owned `Content-Length` *and* kept `data`), sitbone's shifted `detect()` as LSP 44→74, voidtrace identity at line 0 without leftover-name, and a mixed LSP/SARIF/cargo stream with a stub git that never fires. SARIF `startLine: 529` staying 529 is the other half of the proof. The v0.2 byte frame is evidence the LSP object is real: scribe could not have grown `Content-Length` without first becoming a language-server stream. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just a backend.
