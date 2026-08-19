# gist

Rewrite stale locators *inside an LSP `textDocument/publishDiagnostics` stream* from one directory snapshot onto another. Never talks to git. Never takes a locator as an argument. stdout is the same schema, still valid JSON.

`flume` splices `file:line` in a text log. `inlay` walks cargo/rustc JSON (`file_name` + `line_start` siblings). `scribe` walks SARIF `physicalLocation.artifactLocation.uri` + 1-based `region.startLine`. That is the wrong object for a language server: the path is `uri` (often on the parent params object) and the line is a nested 0-based integer `range.start.line`. Off-by-one is load-bearing. A text splice misses the integer or unseals the document the moment the dest path contains `"`. `gist` walks that schema.

## Install / run

```bash
chmod +x ./gist
./gist --help
./demo.sh
```

Requires Python 3.9+. Git is not a dependency.

## Interaction

```
cat publish.json | gist --from-dir oldtree --to-dir newtree
rust-analyzer … 2>/dev/null | gist --from-dir oldtree --to-dir newtree
gist --from-dir oldtree --to-dir newtree notify.json --trace
```

JSON values in, JSON values out. Nested locator objects move together (`uri` + `range.start.line` + `range.end.*`). `data` is kept. Locators inside `message` strings move too (those strings are 1-based compiler `file:line`, not LSP). Pretty-printed values stay pretty; NDJSON stays one object per line. LSP `Content-Length` frames are dest-owned (UTF-8 byte length of the rewritten body). Confirmed deletions pass through unchanged.

A `publishDiagnostics` notification has **one** `uri` and **many** ranges. After a file-split those ranges may land in different dest files; gist fissions the notification into several of the same schema.

Exit 0 if locators rewrote (or were confirmed deletions). Exit 1 if some locators could not be read from `--from-dir`. Exit 2 on usage.

SARIF `startLine` / cargo `file_name`+`line_start` are not locators here. 1-based SARIF is rejected, not silently shifted.

## Examples

LSP from before a file-split, pointed at today's tree. `range.start.line` stays a 0-based integer:

```bash
cat kizu.publish.json | ./gist --from-dir kizu-old --to-dir kizu-now
# params.uri  file:///…/src/app.rs  →  file:///…/src/app/layout.rs
# range.start.line  528 → 16     (not 17: that would be SARIF)
```

A 1-based SARIF file is not converted:

```bash
cat kizu.sarif | ./gist --from-dir kizu-old --to-dir kizu-now --trace
# startLine 529 is still 529
# stderr: ignored  sarif  1-based region.startLine is not LSP
```

Dest path with a quote — a text splice would unseal the document:

```bash
echo '{"uri":"src/plain.py","diagnostics":[{"range":{"start":{"line":0,"character":0},"end":{"line":0,"character":1}},"message":"x"}]}' \
  | ./gist --from-dir old --to-dir new
# {"uri":"src/quo\"te.py","diagnostics":[…]}   still json.loads
```
