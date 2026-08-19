# DESTROYER — gist

Adversarial pass on the 0-based LSP locator rewriter. No rewrites: the failures are conceptual except pretty-JSON ingest (operational fail-open), left unpatched so the schema/path holes stay visible. Not leftover-name. Not pin.

- **gist** (mutation-67, v0.2.0) — `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb7959a1069d`
- Transcript: `/tmp/destroy-gist/transcript.txt`
- Follow-up: `/tmp/destroy-gist/followup.txt`
- Fixtures: `/tmp/destroy-gist/fixtures/`
- Attack driver: `/tmp/destroy-gist/attack.py`
- `./demo.sh` → `All demo checks passed.` after the attacks. `gist 0.2.0`.
- Peels (contrast only): **blot** origin `diagnostics: []`; **flare** 1-based → LSP.

Attacks: rustc multi-hunk snippets, `}`-only lines, UTF-16 `character` vs Python `len`, dest line shorter than column, mixed old+new paths, missing origin `diagnostics: []`, pretty-printed JSON with commentary, SARIF 1-based leaking into LSP.

Verdict: **mutate, do not kill.** kizu `528 → 16` (not 17) still holds. sitbone `44 → 74`. voidtrace line `0` identity does not jump to `cli.ts`. SARIF `startLine` 529 stays 529. Cargo `file_name`+`line_start` stays stale. `Content-Length` is dest-owned. Fission and `data` keep. The attacks show where a rustc snippet is one carry, where `}` is not a locator, where `character` is the source column, where a split leaves the origin document dirty, and where 1-based SARIF numbers sitting in an LSP field are faithfully treated as 0-based.

---

## Primitive restated

An LSP `textDocument/publishDiagnostics` stream is a document of *nested* locators. gist rewrites stale addresses from `--from-dir` onto `--to-dir` by content fingerprint and emits valid JSON of the same schema. The path is `uri` (often on the parent params object). The line is 0-based `range.start.line`. Off-by-one is load-bearing. `Content-Length` is dest-owned (UTF-8 byte length of the rewritten body). SARIF `startLine` / cargo `file_name`+`line_start` are not locators here.

---

## 1. rustc multi-hunk snippets — carry is `old_line+k`, not a locator (conceptual)

One `-->` and later gutters of a *different function* after a godfile split. `GUTTER_SPAN=24`. Carry is the first locator's dest offset.

Source `src/god.rs`: `fn alpha_unique_qzx` at 1-based 1, `fn gamma_brace_qzx` at 5, `fn beta_unique_qzx` at 32. Dest splits them into `alpha.rs` / `gamma.rs` / `beta.rs`. Dest `alpha.rs` has a 9-line header so dest of alpha is 1-based **10**.

```
$ ./gist --from-dir shift-from --to-dir shift-to --trace < multihunk-one-arrow.json
# stderr
moved	src/god.rs:0:3	src/alpha.rs:9:3	0.850	path or surrounding file changed
moved	src/god.rs:1:4	src/alpha.rs:10:4	0.850	path or surrounding file changed
# stdout message
  --> src/alpha.rs:10:4
   |
 10 | fn alpha_unique_qzx() {
 11 |     let alpha_body_qzx = 1;
   |
 14 | fn gamma_brace_qzx() {
 15 |     let gamma_body_qzx = 3;
   |
 32 | fn beta_unique_qzx() {
 33 |     let beta_body_qzx = 2;
# rc=0
```

`src/gamma.rs` and `src/beta.rs` never appear. Gutter 5 became 14 (`dest 10 + 4`) — gamma is claimed at `alpha.rs:14`, a file that does not contain it. Gutter 32 stayed 32: `delta=31 > 24`, `apply_gutter` refuses, hits are skipped on a gutter-only line, the number is the source line of a function that now lives in `beta.rs:1`.

Two `-->` arrows (honest rustc multi-span) *do* refresh carry:

```
$ two-arrow snippet  --> god.rs:1  and  --> god.rs:32
  --> src/alpha.rs:1:4
   |
  1 | fn alpha_unique_qzx() {
note: expected because of
  --> src/beta.rs:1:4
   |
  1 | fn beta_unique_qzx() {
# rc=0
```

The object is the snippet without a second `-->`. rustc often prints one caret and then later lines of the same function *or* of a neighbor that a later split pulled away. gist follows the first locator's offset inside `message`. That is not leftover-name; it is carry arithmetic.

---

## 2. `}`-only lines — trivial refuse, exit 1, locator stays (conceptual)

`}` is in `TRIVIAL_NORMS`. An LSP range whose start line is only `}` cannot fingerprint.

```
$ publishDiagnostics  uri=src/god.rs
    range.start.line=2   # 0-based of the `}` that closes alpha
    range.start.line=6   # 0-based of the `}` that closes gamma

$ ./gist --from-dir split-from --to-dir split-to --trace
unresolved	src/god.rs:2:0	-	0.000	line is too trivial to fingerprint
unresolved	src/god.rs:6:0	-	0.000	line is too trivial to fingerprint
# stdout still uri=src/god.rs  line 2 and line 6
# rc=1
```

The neighbor body *does* bind:

```
$ range.start.line=1   # `    let alpha_body_qzx = 1;`
moved	src/god.rs:1:4	src/alpha.rs:1:4	0.825
# uri src/alpha.rs  line 1   rc=0
```

A rustc "expected `}`" diagnostic is a first-class LSP locator and gist will not move it. Exit 1 is "some locators could not be read from `--from-dir`" — honest, and the client keeps squiggles on the origin `}`.

---

## 3. UTF-16 `character` vs Python `len` — source column, not the spec unit (conceptual)

LSP `character` is UTF-16 code units. gist `rewrite_range` copies `character` through. blot (peel) clamps to `utf16_len(dest_line)`.

Dest line, identity trees (`--from-dir == --to-dir`):

```
WIDE_TOKEN_QZX 😀
# Python len = 16
# UTF-16    = 17    (U+1F600 is one code point, two code units)
```

```
$ ./gist --from-dir wide2-to --to-dir wide2-to < utf16-identity.json
# character 16 (python len) stays 16
# character 22 / end 40 stay 22 / 40     past the line
# rc=0

$ ./blot --from-dir wide2-to --to-dir wide2-to < utf16-identity.json
# character 16 stays 16
# character 22 / end 40 become 17 / 17   clamp to utf16_len
```

16 is a valid UTF-16 offset (the trailing surrogate of 😀). It is **not** the end of the line. The LSP end is 17. Clamping to Python `len()` would have been a dest-owned lie; gist does not clamp at all. kizu gold `character: 4` on `layout.rs` 0-based 16 is unchanged (dest line is long enough). sitbone `character: 16` on `detect()` stays 16. Those are not the hole.

---

## 4. dest line shorter than column — same missing dest-own (conceptual)

When the dest line *binds* but is shorter than the source column:

```
src: fn wide_anchor_qzx() { let pad = "XXXXXXXXXXXXXXXXXXXX"; }
dst: fn wide_anchor_qzx() { let pad = "😀"; }     # utf16=40
src: LONG_COLUMN_TOKEN_ABCDEFGHIJKLMNOPQRSTUVWXYZ = "yyyy…"
dst: LONG_COLUMN_TOKEN_ABCDEFGHIJKLMNOPQRSTUVWXYZ = 1     # len=48

$ range.start.line=1  character=40  end.character=50
# gist  end.character=50     past dest
# blot  end.character=48     clamp
```

When dest text drifts below `RESOLVE_THRESHOLD` (score 0.378 / 0.410 on `WIDE_TOKEN_QZX = "xxx"` → `WIDE_TOKEN_QZX 😀`) the locator is **deleted** and passed through with the source column still attached. Two paths to a column past the dest line: bind-and-keep, or fail-and-keep. Neither dest-owns `character`.

---

## 5. mixed old+new paths — only `--from-dir` binds (conceptual)

A stream that already mixes dest uris with origin uris:

```
{"method":"textDocument/publishDiagnostics","params":{
  "uri":"src/alpha.rs",   # already dest; not in --from-dir
  "diagnostics":[{"range":{"start":{"line":0,…}},
    "message":"already dest: src/alpha.rs:1 and leftover src/god.rs:1"}]}}
{"method":"textDocument/publishDiagnostics","params":{
  "uri":"src/god.rs",
  "diagnostics":[{"range":{"start":{"line":0,…}},
    "message":"still origin src/god.rs:1"}]}}
```

```
$ ./gist --from-dir split-from --to-dir split-to --trace
unresolved	src/alpha.rs:0:0	-	0.000	source path not in from-dir
moved	src/god.rs:1	src/alpha.rs:1	0.850
moved	src/god.rs:0:0	src/alpha.rs:0:0	0.850
# first notification uri still src/alpha.rs (passthrough)
# its message: "already dest: src/alpha.rs:1 and leftover src/alpha.rs:1"
# second notification moved to src/alpha.rs
# rc=1
```

The dest-already uri does not bind (not in `--from-dir`) and passes through. The 1-based `src/god.rs:1` *inside that message* still rewrites, so both halves of the sentence now say `src/alpha.rs:1`. `relatedInformation.location.uri` already pointing at `src/alpha.rs` is the same unresolved. gist rewrites what `--from-dir` can see. A log that has already been half-applied is not a second snapshot.

---

## 6. missing origin `diagnostics: []` — fission is not a client-clear (conceptual, blot peel)

One `god.rs` notification, two ranges, both move. gist emits dest documents only.

```
$ ./gist --from-dir split-from --to-dir split-to
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///work/src/alpha.rs","diagnostics":[{… line 0, data.id=a}]}}
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///work/src/beta.rs","diagnostics":[{… line 0, data.id=b}]}}
# no third object. version dest-dropped on the moved uris.
# rc=0

$ ./blot --from-dir split-from --to-dir split-to
# same two dest objects, plus
{"jsonrpc":"2.0",…,"params":{"uri":"file:///work/src/god.rs","diagnostics":[]}}
```

Framed:

| tool | frames | Content-Length | `diagnostics:[]` |
| --- | --- | --- | --- |
| gist | 2 | 233 / 231 (synthetic) | 0 |
| blot | 3 | 233 / 231 / 120 | 1 |

Real kizu `app.rs` split, compact framed publishDiagnostics:

| tool | frames | Content-Length | origin empty |
| --- | --- | --- | --- |
| gist | 2 | 471 / 311 | no |
| blot | 3 | 471 / 311 / **142** | `uri …/src/app.rs` `diagnostics:[]` |

A client that already applied the old `app.rs` notification keeps stale squiggles. Fission looks complete on stdout. The missing document is the origin. sitbone same-file shift (`44 → 74`) correctly emits **no** extra empty — dest uri *is* the origin. Confirmed deletion (`calc.py` 0-based 10) stays one object with a non-empty `diagnostics` array. Those two must not become a clear.

gist `explode_publish_params` only builds `diagnostics: []` when *both* dest buckets and origin leftovers are empty (an already-empty publish). After a split, buckets are non-empty and the origin list is empty, so the clear is never appended. blot is that append.

---

## 7. pretty-printed JSON with commentary — `{` on a chatter line is not a value (operational, fail-open)

`scan_stream` `raw_decode`s only when the remaining bytes start with `{` or `[`. Leading commentary on the same line as `{` makes the whole pretty object chatter.

```
$ printf 'note: %s\n' "$(cat pretty-publish.json)" | gist --from-dir split-from --to-dir split-to
note: {
  "jsonrpc": "2.0",
  "method": "textDocument/publishDiagnostics",
  "params": {
    "uri": "src/god.rs",          # STALE
    "diagnostics": [{ "range": { "start": { "line": 0 } },
                      "message": "see src/god.rs:1" }]
  }
}
# rc=0   no --trace rows   locators never seen
```

Same fail-open for `prefix{…}` and `// stale locator {` + the rest of the pretty object. Continuation lines start with space, so they are never JSON either.

A newline *before* `{` works:

```
$ printf '// stale locator\n%s\n' "$(cat pretty-publish.json)" | gist …
# uri src/alpha.rs   message see src/alpha.rs:1   rc=0
```

Two concatenated pretty objects with `{` in column 0 also rewrite. Compact NDJSON without a prefix is fine. The hole is commentary glued to `{`. Exit 0 with stale locators is a green pipe.

---

## 8. SARIF 1-based leaking into LSP — refuse is whole-object; a stuffed integer is 0-based (conceptual, flare peel)

Gold refuse still holds. That is half the primitive.

```
$ cat kizu.sarif | ./gist --from-dir kizu-b4e6a5d --to-dir kizu-HEAD --trace
# startLine 529 unchanged; byteOffset 18000 unchanged
# stderr: ignored	sarif	-	-	1-based region.startLine is not LSP range.start.line; use scribe
# rc=0

$ cargo file_name=src/god.rs line_start=32
# ignored	cargo	…  file_name and line_start stay
```

`flare` (peel) is the inverse: `529 → 528`. gist must not do that conversion. Confirmed:

```
$ cat kizu.sarif | ./flare --trace
converted	sarif	…/src/app.rs	529	528	1-based locator → 0-based range.start.line
# range.start.line = 528
```

Three leaks around that refuse:

**Sibling `startLine` rides along.** An honest 0-based diagnostic that also carries SARIF keys:

```
$ hybrid  uri=src/god.rs  range.start.line=0  startLine=32
          range.startLine=32  region.startLine=32
# gist → uri src/alpha.rs  range.start.line=0
#         startLine 32, range.startLine 32, region.startLine 32  still there
```

The dest file is 4 lines long. A client that reads `startLine` goes to line 32.

**Stuffed 1-based integer in `range.start.line` is not rejected.** It is fingerprinted as 0-based file line `n+1`.

```
$ kizu  range.start.line=529   # SARIF startLine dropped into an LSP field
# gist → src/app/layout.rs  range.start.line=17     # NOT 16
# file line 530 is `    seen: &BTreeMap…`  → dest 1-based 18 → LSP 17

$ local  range.start.line=32   # 1-based of beta fn is 32; LSP of beta fn is 31
# gist → src/beta.rs  line 1     # the *body* (`let beta_body_qzx`), not the fn
```

Honest kizu gold is `528 → 16`. Treating 529 as already-LSP lands on 17. That is why flare exists. gist will not warn.

**A SARIF wrapper traps an LSP payload.** `$schema` + `version: 2.1.0` + `runs` plus a nested `textDocument/publishDiagnostics` is `ignored	sarif` and the inner `range.start.line` is not rewritten. Foreign-schema refuse is whole-object. Nested `physicalLocation` inside `data` is the other direction: outer LSP moves, `data.region.startLine` 32 stays (correct refusal, dest-stale 1-based next to dest 0-based).

---

## What survived

- Gold kizu: `range.start.line` **528 → 16**, not 17. `character` 4 kept. message `--> …/layout.rs:17:5`. gutter `17 | pub fn seen_hunk_fingerprint(`. `data.check` kept. version dest-dropped. fission into `layout.rs` + `navigation.rs` (`542 → 21`). live working tree as `--to-dir` still finds `layout.rs`.
- Gold kizu SARIF: `startLine` 529, `byteOffset` 18000, `ignored	sarif`.
- Gold sitbone: `44 → 74`, message `:75:17`, version kept, **no** extra empty (same-file shift).
- Gold voidtrace: `evaluate.ts` 39 and **0** identity. `cli.ts` does not appear. Not leftover-name.
- Gold cargo: `file_name` + `line_start` stale.
- Dest-owned `Content-Length` after rewrite; `Content-Type` kept; chatter before the frame survives.
- Two-`-->` rustc multi-span rewrites both paths and both gutters.
- Neighbor body of a `}` binds.
- Pretty JSON with `{` in column 0 stays pretty and rewrites. Compact NDJSON stays compact.
- `./demo.sh` all passed. `gist 0.2.0`. Victim not rewritten.

---

## Kill / keep

**Keep. Mutate. Do not rewrite in this pass.**

The object is still “nested 0-based LSP locators in, same schema out, two directories, no git.” `528 → 16`, sitbone `44 → 74`, voidtrace line 0, SARIF 529 staying 529, dest-owned `Content-Length`, fission, `data` keep — all still true. Nothing in this battery turned gist into pin, leftover-name, or a SARIF rewriter. Do not kill because `diagnostics: []` is missing, because `character` is Python, or because a rustc gutter followed the first `-->`. Those are mutations. Killing them would throw away a real 0-based schema gate to hide a carry or a column.

| do not kill because | mutate toward |
| --- | --- |
| kizu `528 → 16` (not 17); sitbone `44 → 74`; voidtrace line 0; SARIF 529 stays; cargo stale; dest-owned `Content-Length`; fission; `data` keep | **Origin-clear (blot).** When every bound locator leaves a uri, emit `diagnostics: []` for the origin. Dest-drop `version` on that clear. Same-file shift and confirmed deletion must *not* grow an extra empty. |
| | **Dest-own `character` as UTF-16 (blot).** Clamp to `utf16_len(dest_line)`, not Python `len()`. kizu `character: 4` stays. A dest line shorter than the source column, or one ending in 😀, must not keep 22. |
| | **Gutter carry is not `old+k` across a split.** Re-fingerprint later gutters, or only carry while the dest file still contains that line. Two-`-->` already works. One-`-->` + `32 \|` must not claim `beta` lives in `alpha.rs`. |
| | **`}` is a locator if a unique neighbor binds.** Exit 1 + pass-through on `}`-only is refuse, not dest. Inherit the surrounding non-trivial line (the rustc "expected `}`" object). |
| | **Ingest: `{` after commentary is still JSON, or fail closed.** `note: {` / `prefix{` exiting 0 with stale `src/god.rs` is a green pipe. Newline-then-`{` already works. |
| | **Mixed dest uris identity-bind against `--to-dir` when absent from `--from-dir`.** Unresolved+exit 1 on an already-fresh dest path is the wrong severity. Message `file:line` must not rewrite origin slices inside a dest-already diagnostic into a sentence that now names dest twice. |
| | **SARIF keys on an LSP object are not payload.** Strip or refuse `startLine` / `region.startLine` sitting next to dest `range.start.line`. Stuffing 529 into `range.start.line` should not silently land on dest 17 — that conversion is flare's (`529 → 528`) then gist's (`528 → 16`). |
| | Pretty `{` glued to chatter: fail closed exit 2, or `raw_decode` from the first `{`. Do not `errors=replace` a half-applied stream into a successful rewrite. |

Do not grow a pin. Do not search leftover names. The next mutation is already named: blot owns the missing origin document and the UTF-16 column; flare owns 1-based → 0-based. gist stays the 0-based rewriter. A later gist that swallowed those peels without keeping `528 → 16` would be the kill.

Do not grow a review platform. The object remains a Unix filter on nested LSP locators.
