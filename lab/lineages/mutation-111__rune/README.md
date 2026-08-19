# rune

Rewrite stale locators *inside an LSP `textDocument/publishDiagnostics` stream* from one directory snapshot onto another. Dest-own `character` as **UTF-16 code units** (the LSP spec unit), not Python `len()`. When every locator that bound against `--from-dir` moved off a uri, emit `diagnostics: []` for that origin so a client drops stale squiggles. Never talks to git. Never takes a locator as an argument. stdout is the same schema, still valid JSON.

`gist` rewrote 0-based `range.start.line` and copied `character` through as a source column. A dest line that ends in 😀 (one Python code point, two UTF-16 units) or is shorter than the source column then sits past the dest line. `rune` dest-owns that integer. `blot` is the origin-clear peel; rune keeps it. `scribe` is 1-based SARIF; this object is 0-based LSP.

## Install / run

```bash
chmod +x ./rune
./rune --help
./demo.sh
```

Requires Python 3.9+. Git is not a dependency.

## Interaction

```
cat publish.json | rune --from-dir oldtree --to-dir newtree
rust-analyzer … 2>/dev/null | rune --from-dir oldtree --to-dir newtree
rune --from-dir oldtree --to-dir newtree notify.json --trace
```

JSON values in, JSON values out. Nested locator objects move together (`uri` + `range.start.line` + `range.end.*`). **`character` is dest-owned as UTF-16**, not Python `len()`: a column past the dest line clamps to `utf16_len(dest)`; a column that still fits remaps through dest-line alignment (inserting 😀 before a later token moves that token's column). `data` is kept. File-split fission emits one notification per dest uri. If every bound locator left the origin uri, an extra notification with `diagnostics: []` is emitted for that origin. Version is dest-dropped on the clear. Pretty-printed values stay pretty; NDJSON stays one object per line. LSP `Content-Length` frames are dest-owned (UTF-8 byte length). Confirmed deletions pass through and do **not** emit an extra empty document.

Exit 0 if locators rewrote (or were confirmed deletions). Exit 1 if some locators could not be read from `--from-dir`. Exit 2 on usage.

SARIF `startLine` / cargo `file_name`+`line_start` are not locators here. 1-based SARIF is rejected, not silently shifted.

## Examples

A dest line that ends in a supplementary-plane emoji. Source columns 22 / 40 become the dest UTF-16 length (17), not Python `len()` (16):

```bash
cat wide.json | ./rune --from-dir wfrom --to-dir wto
# dest line  WIDE_TOKEN_QZX 😀     utf16=17  codepoints=16
# dest character 17 / 17           (not 16, not 22)
```

A dest line that *inserts* 😀 before a later token. Source column 15 still fits dest `utf16_len`, so clamp would keep 15 (the first surrogate of 😀). Dest-own remaps onto `extra_marker`:

```bash
cat align.json | ./rune --from-dir rfrom --to-dir rto
# src  WIDE_TOKEN_QZX extra_marker      character 15
# dst  WIDE_TOKEN_QZX 😀 extra_marker   character 18
```

A split godfile. Dest files get the diagnostics; the origin is cleared; `character: 4` stays 4 (dest line is long enough):

```bash
cat kizu.publish.json | ./rune --from-dir kizu-old --to-dir kizu-now
# params.uri  file:///…/src/app.rs  →  file:///…/src/app/layout.rs
# range.start.line  528 → 16     (not 17: that would be SARIF)
# character 4 kept
# plus a third notification: uri …/src/app.rs  diagnostics: []
```

A 1-based SARIF file is not converted:

```bash
cat kizu.sarif | ./rune --from-dir kizu-old --to-dir kizu-now --trace
# startLine 529 is still 529
# stderr: ignored  sarif  1-based region.startLine is not LSP
```
