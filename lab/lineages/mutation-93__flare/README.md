# flare

Emit an LSP `textDocument/publishDiagnostics` stream from cargo / rustc / SARIF / compiler-text locators. Never talks to git. Never takes a locator as an argument. stdout is JSON-RPC whose `range.start.line` is **0-based**.

`gist` and `blot` rewrite nested 0-based LSP locators and **refuse** to shift SARIF `startLine`. `scribe` rewrites 1-based SARIF and **cannot** emit `range.start.line`. The missing verb is the inverse: **create** the LSP document from the 1-based schemas. Off-by-one is load-bearing. SARIF `529` becomes LSP `528`, not `529` and not `17`.

## Install / run

```bash
chmod +x ./flare
./flare --help
./demo.sh
```

Requires Python 3.9+. Git is not a dependency.

## Interaction

```
cat rustc.log | flare
cat cargo.jsonl | flare --trace
cat results.sarif | flare --frame
flare --uri-prefix file:///home/runner/work/kizu/kizu kizu.sarif
```

1-based locators in, `textDocument/publishDiagnostics` out. Cargo `file_name`+`line_start`, SARIF `region.startLine`, rustc `--> file:line:col`, Python `File ", line`, clang caret, Swift `key.line` are converted. Already-0-based LSP `range.start.line` is **not** shifted (that is gist/blot). Chatter is dropped from stdout: the stream is the LSP document, not the input with numbers rewritten in place.

v0.2 is **client-shaped**: diagnostics that share a uri are one notification (a language server document, not a span dump). `Content-Length` is dest-owned as the UTF-8 byte length of that body. `character` is dest-owned as UTF-16 code units and clamped to the snippet, not Python `len()`. `--ndjson` drops the frame; `--per-span` restores one notification per locator.

Exit 0 on success (including empty input). Exit 2 on usage. The binary never calls git.

## Examples

SARIF 1-based gold becomes LSP 0-based. The integer in the range is not the integer in the region:

```bash
cat kizu.sarif | ./flare
# params.uri              file:///…/src/app.rs
# region.startLine        529
# range.start.line        528     (not 529, not 17)
# range.start.character   4       (startColumn 5, 1-based → 0-based)
```

Cargo / rustc JSON, same off-by-one:

```bash
cat cargo.jsonl | ./flare --trace
# stderr: converted  cargo  …/src/app.rs  529  528  1-based locator → 0-based range.start.line
```

Client-shaped byte frame (default). `Content-Length` is dest-owned (length of the converted body), not a passthrough of any input header. Two cargo spans on `app.rs` share one document:

```bash
cat cargo.jsonl | ./flare
# Content-Length: <utf-8 length of the JSON-RPC body>\r\n
# Content-Type: application/vscode-jsonrpc; charset=utf-8\r\n
# \r\n
# {"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
#    "uri":"file:///…/src/app.rs",
#    "diagnostics":[ {line 528}, {line 542} ]}}
```

Pipe into blot/gist so the four filters meet in the middle: flare creates the 0-based document, blot rewrites it across trees (`528 → 16` on kizu's godfile split) and can emit origin `diagnostics: []`.
