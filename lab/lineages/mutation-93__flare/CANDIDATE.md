# mutation-93 — flare

## Primitive

A cargo / rustc / SARIF / compiler-text stream of **1-based** locators is converted into a valid LSP `textDocument/publishDiagnostics` stream whose `range.start.line` is **0-based** and whose `Content-Length` is dest-owned.

## Why this might not exist

`gist` (mutation-67) and `blot` (mutation-83) rewrite nested 0-based LSP locators. They **refuse** to shift SARIF `startLine` — that refusal is the proof they are not scribe. `scribe` rewrites 1-based SARIF and **cannot** emit `range.start.line`. `inlay` walks cargo `file_name`+`line_start` and stays in cargo JSON. `flume` splices `file:line` in a text log. The four filters never meet: a rustc log cannot enter blot, a SARIF file cannot enter gist, and a client cannot apply either. The missing verb is the inverse blot itself named: **emit publishDiagnostics from a flume text log / scribe SARIF**. Off-by-one is load-bearing. Treating `529` as already LSP would land on dest line 17 after a gist rewrite; the gold is `528 → 16`.

## How to run

From the worktree root:

```bash
chmod +x ./flare
./flare --help
./demo.sh
cat rustc.log | ./flare
cat results.sarif | ./flare --trace
cat cargo.jsonl | ./flare | blot --from-dir old --to-dir new
```

Exit 0 on success (empty input is an empty LSP stream). Exit 2 on usage. The binary never calls git — a stub `git` on PATH dies if it is touched. Already-0-based `range.start.line` is ignored, not shifted. Chatter is dropped from stdout: the stream is the LSP document.

## The assumption that was flipped

Killed: “the way to get an LSP document from SARIF/cargo is to rewrite locators in place (a gist clone) or to walk git for leftover names (a pin).”

New: flare is a **schema converter**. stdin may be 1-based. stdout is `textDocument/publishDiagnostics`. `529` becomes `528`. A client-shaped `Content-Length` frame is dest-owned (UTF-8 length of the converted body). gist/blot remain the 0-based rewriters; scribe/inlay/flume remain the 1-based rewriters; flare is the joint.

### Bought

- Unix-composable inverse: `cat kizu.sarif | flare | blot --from-dir old --to-dir new`.
- Off-by-one as the object: SARIF `startLine` 529 / cargo `line_start` 529 / rustc `--> …:529:5` all become `range.start.line` 528, `character` 4.
- LSP input is not converted (528 stays 528, never 527). That is how you tell flare from a gist clone that also subtracted one.
- v0.2 client-shaped document: locators that share a uri become **one** `publishDiagnostics` (a language-server document, not a span dump).
- Dest-owned `Content-Length` as the default wire (UTF-8 length of the converted body). There is no input frame to copy.
- Dest-owned `character` as UTF-16, clamped to the snippet — not Python `len()`.
- `data.flare.line_1` keeps the 1-based origin so a later filter can see both integers.
- Message strings stay 1-based (`--> …:529:5`) — those strings are compiler locators, not LSP.
- No git, no leftover-name, no pin mint.

### Lost

- Does not rewrite across trees (blot's job after the conversion).
- Chatter is discarded, not preserved (gist preserves chatter because it is a same-schema rewriter).
- UTF-16 clamp needs a snippet; without one, `column-1` is the conversion and a supplementary-plane column can still sit past the dest line.
- Binary Swift `.dia` is out of scope.
- `--per-span` still emits the v0.1 hole on purpose.

## Empirical transcript

### Working software (v0.1)

Synthetic SARIF + cargo JSON + rustc text + SourceKit + clang + pytest + quote-in-uri + already-LSP, stub `git` on PATH. `./demo.sh` exits 0.

```
$ cat kizu.sarif | ./flare --trace
# stderr: converted	sarif	file:///…/src/app.rs	529	528	1-based locator → 0-based range.start.line
{"jsonrpc":"2.0","method":"textDocument/publishDiagnostics","params":{
  "uri":"file:///home/runner/work/kizu/kizu/src/app.rs",
  "diagnostics":[{"range":{"start":{"line":528,"character":4},"end":{"line":528,"character":27}},
    "code":"E0599","source":"rustc",
    "data":{"flare":{"schema":"sarif","line_1":529,"column_1":5}}}]}}
```

`range.start.line` is 528, not 529, not 17. `byteOffset` 18000 is not copied onto the range. `data.flare.line_1` is 529.

Cargo two spans on the same godfile became **two** notifications (v0.1 hole):

```
$ cat kizu.cargo.jsonl | ./flare | wc -l
2
# first  line_start 529 → 528  character 4  (column_start 5)
# second line_start 543 → 542
# "Compiling kizu" chatter is not on stdout
# message still contains --> …/src/app.rs:529:5
```

Rustc text `--> …/src/app.rs:529:5` → line 528 character 4. `error:1` and `http://localhost:8080/health` are not locators.

Already-LSP `range.start.line` 528 is ignored (empty stdout, `ignored	lsp`). Subtracting one would have emitted 527 — that would be a gist clone.

`--frame`: `Content-Length: 379` equals the UTF-8 body; 528 lives inside the frame.

Sitbone SourceKit `key.line` 45 → 44, `key.column` 17 → character 16.

Clang caret line 4 → 3; pytest `lineno` 11 → 10. Dest path `src/quo"te.py` still `json.loads`. `startLine` 1 → line 0.

Real copies (`git archive` in demo.sh; flare itself never talks to git):

```
$ cat kizu.cargo.jsonl | ./flare --frame
# two frames, range.start.line 528 and 542
# b4e6a5d src/app.rs line 529 is `pub fn seen_hunk_fingerprint(`
# HEAD layout.rs 0-based 16 is the same function; navigation.rs 0-based 21 is nearest_landing_forward

$ cat kizu.sarif | ./flare --frame | blot --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# uri  file:///…/src/app/layout.rs
# range.start.line  16   (not 17)
```

That pipe is the primitive: SARIF 1-based 529 → flare LSP 528 → blot dest 16.

`./demo.sh` exits 0.

### After the improvement (v0.2)

v0.1's lie was the same class as gist's missing origin-clear, inverted. Two cargo spans on `src/app.rs` became two `publishDiagnostics` notifications. A client that applies them in order **keeps only the last**. The LSP object is a document, not a span. Group by uri. Default the dest-owned `Content-Length` frame (a client cannot ingest NDJSON as a language-server stream). Dest-own `character` as UTF-16 from the snippet.

```
$ cat kizu.cargo.jsonl | ./flare
# one frame, Content-Length: 600
# params.uri  file:///…/src/app.rs
# diagnostics[0].range.start.line  528
# diagnostics[1].range.start.line  542
# "Compiling kizu" is not on stdout
```

`--ndjson --per-span` still emits two objects (the v0.1 hole, opt-in).

UTF-16 clamp vs Python `len()` on a supplementary-plane snippet (`WIDE_TOKEN_QZX 😀` + VS-16): `len` 17, utf16 18, `startColumn` 40 would have been character 39; dest-owned character is 18.

```
$ cat kizu.cargo.jsonl | ./flare | blot --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# layout.rs     range.start.line 16   (not 17)
# navigation.rs range.start.line 21   (not 22)
# app.rs        diagnostics: []       origin-clear
```

Grouped conversion is what lets blot fission *and* blot the origin. Two v0.1 frames of one diagnostic each would have rewritten, but the client-shaped meeting point is one document in, dest documents out. `./demo.sh` still exits 0.

## Dogfood targets

- Synthetic SARIF / cargo JSON / rustc text / SourceKit / clang / pytest / quote-in-uri / chatter / already-LSP in `./demo.sh`.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` (`src/app.rs` 1-based 529 = `seen_hunk_fingerprint`) and HEAD (`layout.rs` 0-based 16).
- Copies of sitbone at `a95da43` (`detect()` 1-based 45).
- Optional `flare | blot` through the mutation-83 worktree.

## Surprises

- The inverse is visible in a type *and* a number. gist/blot cannot emit from SARIF (`startLine` 529 stays 529). scribe cannot emit `range.start.line`. flare is the only filter that produces 528 from 529. Piping that 528 into blot yields dest 16, not 17. That pipe is the four filters meeting.
- v0.1 "worked" (exit 0, valid JSON-RPC, correct integers) and still lied to a client: the second `app.rs` notification replaces the first. Same class of missing-document as gist not emitting `diagnostics: []`. Grouping is not polish; it is the LSP object.
- Already-LSP 528 ignored (not shifted to 527) is how you tell this from "subtract one from every integer named line". A gist clone that also converted SARIF would have done both.
- One diagnostic holds two off-by-ones honestly: `range.start.line` 528 (LSP) and `message` `--> …:529:5` (compiler). Rewriting the string to 528 would be a different lie.
- Dest-owned `Content-Length` here is *created*, not rewritten. gist had an input frame whose length became stale. flare has no input frame; the number is born dest-owned.
- UTF-16 vs `len()` is only visible once a VS-16 rides along with 😀. Clamping to Python `len()` would have been a dest-owned lie, the same one blot v0.2 named.

## Failures

- Without a snippet, `character` is `column-1` with no dest-line clamp. Reading `--root` would dest-own it, but walking a tree looking for leftover names is forbidden; reading the file the locator already named is the next mutation.
- rustc children become `relatedInformation` when they harvest; a child without spans is dropped.
- Text locators bind the arrow line (and the previous title line) but do not reconstruct a full rustc snippet block as `message`.
- A log that already mixes 0-based LSP and 1-based SARIF converts only the SARIF. The LSP is ignored, not forwarded — stdout is the converted stream, not a merge.
- Concatenated pretty-printed objects with leading commentary on the same line as `{` can fail `raw_decode` and be treated as chatter.
- Binary `.dia` files are out of scope.

## Suggested mutations

- Dest-own `character` from `--root` file bytes (the locator named the path; this is not leftover-name).
- `--watch` a compiler log into a client (scar-review companion). Do not become pin.
- Inverse-inverse: emit SARIF from an LSP stream (scribe-shaped), so the joint has both directions.
- Preserve rustc `suggested_replacement` as `Diagnostic.data` / code actions. Do not become pin.

## Kill / keep

**Keep.** The flipped assumption is the primitive: 1-based cargo/SARIF/text in, 0-based `publishDiagnostics` out, dest-owned frame, no git, no leftover-name, not a gist clone. Empirically hits kizu's `app.rs:529` through cargo JSON *and* rustc text *and* SARIF (`528`, not `529`, not `17`), sitbone `detect()` SourceKit 45→44, UTF-16 clamp 18≠17, and `flare | blot` on the real trees (`528→16` and `542→21` plus origin `diagnostics: []`). LSP 528 staying 528 is the other half of the proof. v0.2 grouping is evidence the LSP object is a document: two v0.1 notifications on `app.rs` would have been valid JSON and a lie to a client. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just `jq` plus minus-one.
