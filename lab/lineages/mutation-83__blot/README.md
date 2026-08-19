# blot

Rewrite stale locators *inside an LSP `textDocument/publishDiagnostics` stream* from one directory snapshot onto another. When every locator that bound against `--from-dir` moved off a uri, emit `diagnostics: []` for that **origin** uri so a client drops stale squiggles. Never talks to git. Never takes a locator as an argument. stdout is the same schema, still valid JSON.

`gist` rewrote 0-based `range.start.line` and fissioned a split `app.rs` into `layout.rs` + `navigation.rs`. After that rewrite a client that had already applied the old notification still showed squiggles on `app.rs`, because gist never published an empty document for the origin. `blot` is that missing notification. `scribe` is 1-based SARIF; this object is 0-based LSP. Dest-owned `Content-Length` is kept.

## Install / run

```bash
chmod +x ./blot
./blot --help
./demo.sh
```

Requires Python 3.9+. Git is not a dependency.

## Interaction

```
cat publish.json | blot --from-dir oldtree --to-dir newtree
rust-analyzer … 2>/dev/null | blot --from-dir oldtree --to-dir newtree
blot --from-dir oldtree --to-dir newtree notify.json --trace
```

JSON values in, JSON values out. Nested locator objects move together (`uri` + `range.start.line` + `range.end.*`). `character` is dest-owned as UTF-16 code units (the LSP spec unit), clamped to the dest line — not Python `len()`. `data` is kept. File-split fission still emits one notification per dest uri. **If every bound locator left the origin uri, an extra notification with `diagnostics: []` is emitted for that origin.** Version is dest-dropped on the clear (a stale integer would make a client discard it). Pretty-printed values stay pretty; NDJSON stays one object per line. LSP `Content-Length` frames are dest-owned (UTF-8 byte length of each rewritten body, including the empty-clear body). Confirmed deletions pass through unchanged and do **not** emit an extra empty document.

Exit 0 if locators rewrote (or were confirmed deletions). Exit 1 if some locators could not be read from `--from-dir`. Exit 2 on usage.

SARIF `startLine` / cargo `file_name`+`line_start` are not locators here. 1-based SARIF is rejected, not silently shifted.

## Examples

A split godfile. Dest files get the diagnostics; the origin is cleared:

```bash
cat kizu.publish.json | ./blot --from-dir kizu-old --to-dir kizu-now
# params.uri  file:///…/src/app.rs  →  file:///…/src/app/layout.rs
# range.start.line  528 → 16     (not 17: that would be SARIF)
# plus a third notification: uri …/src/app.rs  diagnostics: []
```

A 1-based SARIF file is not converted:

```bash
cat kizu.sarif | ./blot --from-dir kizu-old --to-dir kizu-now --trace
# startLine 529 is still 529
# stderr: ignored  sarif  1-based region.startLine is not LSP
```

Byte-framed LSP. Each fissioned body (including origin-clear) gets a dest-owned `Content-Length`:

```bash
cat framed.bin | ./blot --from-dir old --to-dir new
# Content-Length: <utf-8 length of layout.rs body>
# Content-Length: <utf-8 length of navigation.rs body>
# Content-Length: <utf-8 length of {"…","uri":"…/app.rs","diagnostics":[]}>
```
