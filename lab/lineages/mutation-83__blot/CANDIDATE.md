# mutation-83 — blot

## Primitive

An LSP `textDocument/publishDiagnostics` stream is a document of nested 0-based locators: rewrite them from directory A onto B by content fingerprint, and when every locator that bound against `--from-dir` moved off a uri, emit `diagnostics: []` for that origin uri so a client drops stale squiggles.

## Why this might not exist

`gist` (mutation-67) is the 0-based LSP rewriter. After a godfile split it fissions one notification into dest files (`app.rs` → `layout.rs` + `navigation.rs`) and dest-owns `Content-Length`. It does **not** publish an empty document for the origin. A client that already applied the old notification keeps squiggles on `app.rs`. That empty notification is not a SARIF region, not a cargo span, not a pin, and not a leftover-name search. `scribe` cannot emit it: `startLine` is 1-based and scribe does not speak `publishDiagnostics`. `jq` does not know which uri was the origin. The missing verb is **blot**: dest-own the origin document as empty.

## How to run

From the worktree root:

```bash
chmod +x ./blot
./blot --help
./demo.sh
cat publish.json | ./blot --from-dir oldtree --to-dir newtree
cat publish.json | ./blot --from-dir oldtree --to-dir newtree --trace
```

Exit 0 when locators rewritten (confirmed deletions are answers). Exit 1 if some locators cannot be read from `--from-dir`. Exit 2 on usage. The binary never calls git — a stub `git` on PATH dies if it is touched. Non-JSON chatter passes through. Concatenated JSON values (NDJSON, pretty-printed objects, JSON-RPC notifications, LSP byte frames) are the ingest.

## The assumption that was flipped

Killed: “fission into dest uris is enough; the origin document can vanish from the stream.”

New: blot is still a **0-based LSP rewriter**, and the dest snapshot also owns the **origin document**. When every bound locator moved away, stdout includes `diagnostics: []` for the origin uri. Version is dest-dropped on that clear so a stale integer cannot reject it. Same-file shifts, confirmed deletions, and missing-range leftovers do **not** emit an extra empty document. SARIF `startLine` stays 1-based on purpose. Off-by-one is still load-bearing: kizu gold is `528 → 16`, not `529 → 17`.

### Bought

- Everything gist v0.2 bought (nested 0-based rewrite, fission, dest-owned `Content-Length`, `data` keep, pretty vs NDJSON, SARIF/cargo reject).
- Client-clear: origin uri gets `diagnostics: []` when every locator bound against `--from-dir` moved away.
- Dest-dropped `version` on the origin-clear (same class of lie as a dest version on a moved uri).
- `--trace` reports `cleared` for the origin uri.
- Framed LSP: origin-clear is its own dest-owned `Content-Length` frame.
- v0.2: dest-owned `character` as UTF-16 code units, clamped to the dest line (not Python `len()`).

### Lost

- Same losses as gist (no SHA names, no one-shot locator, no cargo/SARIF rewrite, not pin, no git).
- A stream that mixed old and new paths still only rewrites what binds against `--from-dir`.
- `character` is clamped, not remapped through a column-level fingerprint; a dest line that is a different token at the same UTF-16 offset keeps that offset if it still fits.

## Empirical transcript

### Working software (v0.1)

Synthetic JSON-RPC publishDiagnostics, stub `git` on PATH. One `app.rs` notification fissioned to `layout.rs` + `navigation.rs` **and** an origin-clear:

```
$ cat mixed.jsonl | ./blot --from-dir from --to-dir to
   Compiling ugly v0.1.0
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///…/src/app/layout.rs","diagnostics":[{… range.start.line 3 …}]}}
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///…/src/app/navigation.rs","diagnostics":[{… range.start.line 0 …}]}}
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///…/src/app.rs","diagnostics":[]}}
```

gist v0.2 would have stopped after navigation.rs. The third object is the primitive: `diagnostics: []` on the origin uri, version dest-dropped.

Confirmed deletion (`src/calc.py` 0-based 10) stays one object with the doomed diagnostic — **not** an extra empty. Same-file sitbone-shaped shift keeps `version`. SARIF `startLine: 4` stays 4. Cargo `file_name`+`line_start` stays `src/app.rs:4`. Missing-range diagnostics stay on `src/calc.py`. Unique-token `src/old.py` → `pkg/new.py` also emits origin `diagnostics: []`. Pretty JSON-RPC stays pretty (two pretty objects). Compact NDJSON stays compact (four lines: dest+clear × two notifications). Dest path with `"` still `json.loads`. Framed LSP: 3 frames, dest-owned `Content-Length` 259 / 265 / 142; empty-clear body is 142 UTF-8 bytes, not the source 312.

Focused client-clear:

```
$ cat clear.json | ./blot --from-dir from --to-dir to --trace
{"jsonrpc":"2.0",…,"uri":"…/src/app/layout.rs","diagnostics":[{… line 3 …}]}
{"jsonrpc":"2.0",…,"uri":"…/src/app.rs","diagnostics":[]}
# stderr: cleared	file:///…/src/app.rs	-	-	origin uri emptied; every locator moved away
```

Real copies (`git archive` into temp dirs; blot itself never talks to git):

```
$ cat kizu.publish.json | ./blot --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# uri   file:///home/runner/work/kizu/kizu/src/app.rs
#    →  file:///home/runner/work/kizu/kizu/src/app/layout.rs
# range.start.line  528 → 16   (integer, 0-based; not 17)
# character 4 kept
# message    --> …/src/app/layout.rs:17:5     (1-based inside the string)
# gutter     17 | pub fn seen_hunk_fingerprint(
# data       {"check":"keep"}
# second notification  src/app.rs → src/app/navigation.rs, line 542 → 21
# third notification   uri …/src/app.rs  diagnostics: []   version dropped
```

```
$ cat kizu.sarif | ./blot --from-dir kizu-b4e6a5d --to-dir kizu-HEAD --trace
# startLine 529 unchanged; byteOffset 18000 unchanged
# stderr: ignored	sarif	-	-	1-based region.startLine is not LSP range.start.line; use scribe
```

```
$ cat sit.json | ./blot --from-dir sitbone-a95da43 --to-dir sitbone-HEAD
# uri PresenceArbiter.swift  range.start.line 44 → 74
# same dest uri: one object, no extra empty (detect() did not leave the file)
```

```
$ cat vt.json | ./blot --from-dir voidtrace-HEAD --to-dir voidtrace-HEAD
# evaluate.ts line 39 KERNEL_ENGINE_VERSION identity
# evaluate.ts line 0  import { stays; does not jump to cli.ts clones
```

Exit 2 with no `--from-dir`. Exit 1 on `src/does-not-exist.rs`. Exit 0 on confirmed deletion.

`./demo.sh` exits 0.

### After the improvement (v0.2)

`character` is dest-owned as UTF-16, the LSP spec unit. gist/blot v0.1 kept the source column; a dest line shorter than that column, or one ending in a supplementary-plane emoji, left a column past the line. Clamp to `utf16_len(dest_line)`, not Python `len()`.

```
$ cat wide.json | ./blot --from-dir wfrom --to-dir wto
# dest line  WIDE_TOKEN_QZX 😀     utf16=17  codepoints=16
# source character 22 / 40
# dest character 17 / 17           (not 16, not 22)
```

kizu `character: 4` on `layout.rs` 0-based 16 is unchanged (dest line is long enough). sitbone `character: 16` on `detect()` stays 16. `./demo.sh` still exits 0.

## Dogfood targets

- Synthetic two-directory fixture in `./demo.sh`: JSON-RPC publishDiagnostics, origin-clear, deletion (no extra empty), same-file shift (no extra empty), Location, overlapping ranges, missing range, file://, unicode, dest path containing `"`, pretty vs NDJSON, cargo-negative, SARIF-negative, unique-token trees, stub git, exit 0/1/2, dest-owned `Content-Length` including the empty-clear frame, UTF-16 `character` clamp vs Python `len()`.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` and `HEAD` (9480-line `src/app.rs` split → `layout.rs` 0-based 16 / `navigation.rs` 0-based 21 **and** origin `app.rs` `diagnostics: []`). Parallel SARIF `startLine: 529` stays 529.
- Copies of sitbone (`detect()` 0-based 44 → 74, same file, **no** extra empty). voidtrace identity at line 0.

## Surprises

- The gist hole is visible as a *missing document*, not a wrong integer. Fission into dest uris looks complete on stdout and still leaves a client dirty. The third kizu notification (`uri …/src/app.rs`, `diagnostics: []`) is the proof; `range.start.line: 16` (not 17) is still the other half.
- Origin-clear must dest-drop `version`. Keeping the source version 12 would let a client that has since edited `app.rs` discard the clear — the same class of lie as publishing a dest file with the origin's version.
- Confirmed deletion is not a clear. `src/calc.py` 0-based 10 staying on origin with a non-empty `diagnostics` array is honest; emitting `[]` would wipe a diagnostic the dest snapshot still cannot place.
- Same-file shift (sitbone `detect()` 44 → 74) must not emit a sibling empty. The dest uri *is* the origin; the rewritten notification already replaces the document.
- UTF-16 vs Python `len()` is only visible on a supplementary-plane scalar (and a VS-16 that came along with 😀). `len("WIDE_TOKEN_QZX 😀")` was 16; LSP wants 17. Clamping to 16 would have been a dest-owned lie.

## Failures

- rustc multi-hunk snippets whose later gutter numbers are *not* old_line+k (a split function) will follow the first locator's offset inside `message` and can land wrong.
- Common/`}`-only lines refuse to fingerprint (`unresolved`) and pass through; exit 1.
- `character` is clamped to dest UTF-16 length, not remapped through a column fingerprint. A dest line that is a different token at the same offset keeps that offset if it fits.
- A log that already mixes old *and* new paths will rewrite only what binds against `--from-dir`.
- Concatenated pretty-printed objects with leading commentary on the same line as `{` can fail `raw_decode` and pass through as raw.
- Whole-tree walk of a dirty kizu working tree (~2700 e2e fixtures) is acceptable but not free; copies via `git archive` are the intended dogfood.

## Suggested mutations

- Column-level dest-own: map source UTF-16 character through the dest line's token, not just clamp.
- Inverse: emit publishDiagnostics *from* a flume text log / scribe SARIF, so the four filters meet in the middle.
- `--watch` a pinfile of LSP logs, rewrite on tree change (scar-review companion). Do not become pin.

## Kill / keep

**Keep.** The flipped assumption is the missing document: gist already moved 0-based locators; blot dest-owns the origin uri as `diagnostics: []` when every bound locator left. Empirically hits kizu's `app.rs` split through a publishDiagnostics file (`528 → 16` *and* fission *and* origin `diagnostics: []` *and* dest-owned `Content-Length` 259/265/142 *and* kept `data`), sitbone's shifted `detect()` as LSP 44→74 with **no** extra empty, voidtrace identity at line 0 without leftover-name, and a mixed LSP/SARIF/cargo stream with a stub git that never fires. SARIF `startLine: 529` staying 529 is the other half of the proof. v0.2 UTF-16 clamp is evidence the LSP object is real: scribe's 1-based `startColumn` is not `character`, and Python `len()` is not the spec unit. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just a backend.
