# mutation-111 — rune

## Primitive

An LSP `character` is a UTF-16 code-unit offset on a dest line: rewrite 0-based locators from directory A onto B by content fingerprint, dest-own that integer as UTF-16 (not Python `len()`), and when every locator that bound against `--from-dir` moved off a uri, emit `diagnostics: []` for the origin.

## Why this might not exist

`gist` (mutation-67) is the 0-based LSP rewriter. After a godfile split it fissions `app.rs` into `layout.rs` + `navigation.rs` and dest-owns `Content-Length`. It copies `character` through as the source column. LSP's unit is UTF-16; Python `len()` is code points. A dest line that ends in 😀 is 16 code points and 17 UTF-16 units; a source column 22 sits past both. gist keeps 22. `blot` peels the missing origin `diagnostics: []` and later clamped to UTF-16 as a v0.2 add-on. The missing verb as a *first* object is **rune**: dest-own `character` as UTF-16, and keep blot's empty-clear so a split does not leave the origin dirty. `scribe`'s 1-based `startColumn` is not `character`. `jq` does not know UTF-16.

## How to run

From the worktree root:

```bash
chmod +x ./rune
./rune --help
./demo.sh
cat publish.json | ./rune --from-dir oldtree --to-dir newtree
cat publish.json | ./rune --from-dir oldtree --to-dir newtree --trace
```

Exit 0 when locators rewritten (confirmed deletions are answers). Exit 1 if some locators cannot be read from `--from-dir`. Exit 2 on usage. The binary never calls git — a stub `git` on PATH dies if it is touched. Non-JSON chatter passes through. Concatenated JSON values (NDJSON, pretty-printed objects, JSON-RPC notifications, LSP byte frames) are the ingest.

## The assumption that was flipped

Killed: “`character` is a source column you can copy; Python `len()` of the dest line is close enough.”

New: rune is still a **0-based LSP rewriter**, and the dest snapshot owns **`character` as UTF-16**. A column past `utf16_len(dest_line)` clamps (not Python `len()`). A column that still fits remaps through dest-line UTF-16 alignment, so inserting 😀 before a later token moves that token's column instead of landing on a trailing surrogate. When every bound locator moved away, stdout includes `diagnostics: []` for the origin uri. Version is dest-dropped on that clear. Same-file shifts, confirmed deletions, and missing-range leftovers do **not** emit an extra empty document. SARIF `startLine` stays 1-based on purpose. Off-by-one is still load-bearing: kizu gold is `528 → 16`, not `529 → 17`. kizu `character: 4` stays 4 (dest line long enough).

### Bought

- Nested 0-based rewrite, fission, dest-owned `Content-Length`, `data` keep, pretty vs NDJSON, SARIF/cargo reject (gist).
- Dest-owned `character` as UTF-16 code units: clamp when past the dest line; remap through dest alignment when it still fits.
- Client-clear: origin uri gets `diagnostics: []` when every locator bound against `--from-dir` moved away (blot peel).
- Dest-dropped `version` on the origin-clear.
- `--trace` reports `cleared` for the origin uri.
- Framed LSP: origin-clear is its own dest-owned `Content-Length` frame.

### Lost

- Same losses as gist (no SHA names, no one-shot locator, no cargo/SARIF rewrite, not pin, no git).
- A stream that mixed old and new paths still only rewrites what binds against `--from-dir`.
- Alignment remaps by UTF-16 code-unit opcodes, not a token-level fingerprint. A dest line that is a different token at the same offset can still keep a fitted column if SequenceMatcher calls the block equal.

## Empirical transcript

### Working software (v0.1)

Synthetic JSON-RPC publishDiagnostics, stub `git` on PATH. One `app.rs` notification fissioned to `layout.rs` + `navigation.rs` **and** an origin-clear. Wide dest line dest-owns `character` as UTF-16:

```
$ cat wide.json | ./rune --from-dir wfrom --to-dir wto
{"uri":"src/wide.py","diagnostics":[{"range":{"start":{"line":0,"character":17},"end":{"line":0,"character":17}},…}]}
# dest line  WIDE_TOKEN_QZX 😀     utf16=17  codepoints=16
# source character 22 / 40
# dest character 17 / 17           (not 16, not 22)
```

gist would have kept 22 / 40. Clamping to Python `len()` would have emitted 16.

```
$ cat mixed.jsonl | ./rune --from-dir from --to-dir to
   Compiling ugly v0.1.0
{"jsonrpc":"2.0",…,"uri":"…/src/app/layout.rs","diagnostics":[{… line 3 …}]}
{"jsonrpc":"2.0",…,"uri":"…/src/app/navigation.rs","diagnostics":[{… line 0 …}]}
{"jsonrpc":"2.0",…,"uri":"…/src/app.rs","diagnostics":[]}
```

gist v0.2 would have stopped after navigation.rs. The third object is blot's peel: `diagnostics: []` on the origin uri, version dest-dropped. Confirmed deletion (`src/calc.py` 0-based 10) stays one object — **not** an extra empty. SARIF `startLine: 4` stays 4. Cargo `file_name`+`line_start` stays `src/app.rs:4`. Framed LSP: 3 frames, dest-owned `Content-Length` 259 / 265 / 142.

Real copies (`git archive` into temp dirs; rune itself never talks to git):

```
$ cat kizu.publish.json | ./rune --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# uri   file:///home/runner/work/kizu/kizu/src/app.rs
#    →  file:///home/runner/work/kizu/kizu/src/app/layout.rs
# range.start.line  528 → 16   (integer, 0-based; not 17)
# character 4 kept
# message    --> …/src/app/layout.rs:17:5
# gutter     17 | pub fn seen_hunk_fingerprint(
# data       {"check":"keep"}
# second notification  src/app.rs → src/app/navigation.rs, line 542 → 21
# third notification   uri …/src/app.rs  diagnostics: []   version dropped
```

```
$ cat kizu.sarif | ./rune --from-dir kizu-b4e6a5d --to-dir kizu-HEAD --trace
# startLine 529 unchanged; byteOffset 18000 unchanged
# stderr: ignored	sarif	-	-	1-based region.startLine is not LSP range.start.line; use scribe
```

```
$ cat sit.json | ./rune --from-dir sitbone-a95da43 --to-dir sitbone-HEAD
# uri PresenceArbiter.swift  range.start.line 44 → 74
# character 16 stays 16
# same dest uri: one object, no extra empty
```

```
$ cat vt.json | ./rune --from-dir voidtrace-HEAD --to-dir voidtrace-HEAD
# evaluate.ts line 39 KERNEL_ENGINE_VERSION identity
# evaluate.ts line 0  import { stays; does not jump to cli.ts clones
```

Exit 2 with no `--from-dir`. Exit 1 on `src/does-not-exist.rs`. Exit 0 on confirmed deletion.

`./demo.sh` exits 0.

### After the improvement (v0.2)

v0.1 clamped a column past the dest line to `utf16_len` (17, not Python `len()` 16). A column that still *fits* dest `utf16_len` was kept — so inserting 😀 before a later token left `character` 15 on the first surrogate of the emoji. Dest-own remaps through dest-line UTF-16 alignment:

```
$ cat align.json | ./rune --from-dir rfrom --to-dir rto
# src  WIDE_TOKEN_QZX extra_marker      character 15 / 27
# dst  WIDE_TOKEN_QZX 😀 extra_marker   character 18 / 30
# clamp-only would have kept 15 (inside 😀)
```

The wide-line clamp fixture is unchanged (`22 / 40` → `17 / 17`). kizu `character: 4` stays 4. sitbone `character: 16` stays 16. `./demo.sh` still exits 0.

## Dogfood targets

- Synthetic two-directory fixture in `./demo.sh`: JSON-RPC publishDiagnostics, origin-clear, deletion (no extra empty), same-file shift (no extra empty), Location, overlapping ranges, missing range, file://, unicode, dest path containing `"`, pretty vs NDJSON, cargo-negative, SARIF-negative, unique-token trees, stub git, exit 0/1/2, dest-owned `Content-Length` including the empty-clear frame, UTF-16 `character` clamp vs Python `len()`, UTF-16 remap through dest alignment.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` and `HEAD` (9480-line `src/app.rs` split → `layout.rs` 0-based 16 / `navigation.rs` 0-based 21 **and** origin `app.rs` `diagnostics: []`). Parallel SARIF `startLine: 529` stays 529.
- Copies of sitbone (`detect()` 0-based 44 → 74, same file, **no** extra empty). voidtrace identity at line 0.

## Surprises

- The gist hole on `character` is visible as a *wrong unit*, not a wrong line. kizu `528 → 16` can be perfect and `character: 22` on a dest line that ends in 😀 is still past the line. UTF-16 17 vs Python `len()` 16 is only visible once a supplementary-plane scalar is the dest.
- Origin-clear is still required. Dest-owning the column does not dest-own the origin document. The third kizu notification (`uri …/src/app.rs`, `diagnostics: []`) is blot's peel sitting next to the UTF-16 object.
- Confirmed deletion is not a clear. Same-file shift (sitbone `44 → 74`) must not emit a sibling empty.
- kizu `character: 4` and sitbone `character: 16` staying put is evidence, not a miss: those dest lines are long enough in UTF-16 and the prefix is equal.
- Clamp-only dest-own is incomplete. Source column 15 on `WIDE_TOKEN_QZX extra_marker` *fits* dest `utf16_len` 30 after inserting 😀, so v0.1 kept 15 — the first surrogate of the emoji, not `extra_marker`. The dest line owns the column only once alignment moves 15 → 18.

## Failures

- rustc multi-hunk snippets whose later gutter numbers are *not* old_line+k (a split function) will follow the first locator's offset inside `message` and can land wrong.
- Common/`}`-only lines refuse to fingerprint (`unresolved`) and pass through; exit 1.
- Alignment remaps by UTF-16 opcodes, not a token-level fingerprint. A dest line that is a different token at an equal-block offset keeps that offset.
- A log that already mixes old *and* new paths will rewrite only what binds against `--from-dir`.
- Concatenated pretty-printed objects with leading commentary on the same line as `{` can fail `raw_decode` and pass through as raw.

## Suggested mutations

- Token-level dest-own: map `character` onto the dest occurrence of the source identifier, not SequenceMatcher opcodes.
- Inverse: emit publishDiagnostics *from* a flume text log / scribe SARIF, so the four filters meet in the middle.
- `--watch` a pinfile of LSP logs, rewrite on tree change. Do not become pin.

## Kill / keep

**Keep.** The flipped assumption is the unit: gist already moved 0-based locators; rune dest-owns `character` as UTF-16 (17, not Python `len()` 16, not source 22; and 15 → 18 when dest inserts 😀) and keeps blot's origin `diagnostics: []` when every bound locator left. Empirically hits kizu's `app.rs` split (`528 → 16` *and* `character: 4` *and* fission *and* origin `diagnostics: []` *and* dest-owned `Content-Length` 259/265/142 *and* kept `data`), sitbone's `detect()` 44→74 with **no** extra empty, voidtrace identity at line 0 without leftover-name, and a mixed LSP/SARIF/cargo stream with a stub git that never fires. SARIF `startLine: 529` staying 529 is the other half of the proof. v0.2 remap is evidence the LSP object is the dest line in UTF-16, not a cap: blot's clamp would have left 15 inside 😀. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just a backend.
