# mutation-26 — inlay

## Primitive

A compiler JSON stream is a document of locators, not a text log: walk every value, rewrite stale addresses from one directory snapshot onto another by content fingerprint, and emit valid JSON.

## Why this might not exist

`flume` (mutation-04) already relocates `file:line` in a stdin→stdout log. Its object is a *line of text*. `cargo --message-format=json` and `rustc --error-format=json` do not store addresses that way. The path is a `file_name` string. The line is a `line_start` integer. The human form, if it exists, is a `rendered` string with its own `-->` locator *and* a `NNN |` gutter. A text splice either misses the integers or unseals the document the moment the dest path contains `"`. Nobody shipped the filter that treats JSON values as the stream. `jq` does not know locators. `flume` does not know spans. Source maps are for minifiers.

## How to run

From the worktree root:

```bash
chmod +x ./inlay
./inlay --help
./demo.sh
cargo test --message-format=json | ./inlay --from-dir oldtree --to-dir newtree
rustc --error-format=json src/lib.rs 2>&1 | ./inlay --from-dir oldtree --to-dir newtree --trace
```

Exit 0 on success. `--strict` exits 1 if a locator cannot be read from `--from-dir`. Confirmed deletions pass through on stdout (they are answers, not errors); `--trace` reports them on stderr. The binary never calls git — a stub `git` on PATH dies if it is touched. Non-JSON chatter (`Compiling …`) passes through. Concatenated JSON values (NDJSON, pretty-printed objects, one array) are the ingest.

## The assumption that was flipped

Killed: “the stream is a text log; locators are `file:line` substrings; rewrite is a splice.”

New: inlay is a **JSON value rewriter**. `--from-dir` and `--to-dir` only. stdin is cargo / rustc / generic JSON; stdout is the same stream with locators rewritten *inside values*. A rustc `DiagnosticSpan` is one locator. A pytest `{filename, lineno}` is one locator. A `rendered` string is a value, not a log line.

### Bought

- Unix-composable on the stream cargo already emits. No `jq -r '.message.rendered' | flume | …` reconstruction.
- Structured pairs move together: `file_name` + `line_start` + `line_end`. Line fields stay JSON numbers.
- Re-serialization: dest paths with quotes, spaces, unicode, colons stay valid JSON.
- Pretty-printed single objects and NDJSON are the same stream (JSONDecoder.raw_decode).
- CI prefixes on `file_name` stay (`/home/runner/work/kizu/kizu/` + new relative path).
- Path-only cargo keys (`target.src_path`, `manifest_path`) are not locators. They have no line sibling.

### Lost

- Cannot name two SHAs; someone else must materialize trees (`git archive` in `demo.sh`).
- Cannot ask `inlay src/app.rs:529` as a one-shot. Everything is a JSON stream.
- Insignificant JSON whitespace is not preserved (validity, not byte identity).
- A lone `"line": 529` without a sibling file field is not a locator (by design).
- Annotating the original text (`# flume: old → new`) would break the schema; mappings live on stderr.

## Empirical transcript

### Working software (v0.1)

Synthetic cargo + rustc + generic JSON + `Compiling` chatter, stub `git` on PATH:

```
$ cat mixed.jsonl | ./inlay --from-dir from --to-dir to
   Compiling ugly v0.1.0
12:34:56 INFO starting build
{"reason":"compiler-artifact","package_id":"ugly@0.1.0","fresh":true}
{"reason":"compiler-message",…,"spans":[{"file_name":"src/app/layout.rs","byte_start":120,"line_start":4,…}],
 "rendered":"… --> src/app/layout.rs:4:1\n   |\n 4 | pub fn seen_hunk_fingerprint(\n"}
{"$message_type":"diagnostic","spans":[{"file_name":"/home/runner/work/ugly/ugly/src/app/navigation.rs","line_start":1,"byte_start":4004,…}],
 "rendered":"  --> …/src/app/navigation.rs:1:5\n   |\n14 | fn nearest_landing_forward…"}
{"ts":"12:34:56","file":"src/math/ops.py","line":3,"msg":"File \"src/math/ops.py\", line 3, in add"}
{"tool":"pytest","filename":"src/math/ops.py","lineno":7,"when":"call"}
{"note":"also see src/math/sauce.py:3","url":"http://localhost:8080/health"}
{"error":"doomed is gone","path":"src/calc.py","line":11}
{"file":"src/日本語.py","line":1}
{"file":"Sources/SitboneCore/PresenceArbiter.swift","line":23,…}
{"reason":"build-finished","success":false}
not a locator, just chatting about foo:bar and error:1
```

`line_start` is still an integer. Dest path `src/quo"te.py` dumps as `src/quo\"te.py` and `json.loads`. Pretty-printed one-object input is consumed as one value, not line-by-line.

Real copies (`git archive` into temp dirs; inlay itself never talks to git):

```
$ cat kizu.jsonl | ./inlay --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
# spans.file_name  /home/runner/work/kizu/kizu/src/app.rs
#               →  /home/runner/work/kizu/kizu/src/app/layout.rs
# spans.line_start 529 → 17   (integer)
# rendered locator   …/src/app/layout.rs:17:5
# rendered gutter    529 | pub fn seen_hunk_fingerprint(     ← stale
# spans.byte_start   18000                             ← stale
# second object      src/app.rs:543 → src/app/navigation.rs:22
```

```
$ cat sit.jsonl | ./inlay --from-dir sitbone-a95da43 --to-dir sitbone-HEAD
# file/line  PresenceArbiter.swift 45 → 75
# msg        …PresenceArbiter.swift:75:17: error:…
# url / timeout:5 chatter untouched
```

```
$ cat tena.jsonl | ./inlay --from-dir tenaoshi-a41089c --to-dir tenaoshi-HEAD
# line_start 12 → 12 (identity, score 1.000)
```

### Failures recorded against v0.1

kizu's cargo diagnostic is only half-rewritten. The span address moved 529 → 17; the rest of the object still describes the *source* snapshot:

```
"file_name": "/home/runner/work/kizu/kizu/src/app/layout.rs",
"line_start": 17,
"byte_start": 18000,
"rendered": "… --> …/src/app/layout.rs:17:5\n   |\n529 | pub fn seen_hunk_fingerprint(\n"
```

flume's first miss was the same gutter, in a text log. inlay's miss is stronger: the JSON is now *internally inconsistent*. A later tool that reads `line_start` and `rendered` together, or seeks to `byte_start`, is handed a lie. v0.1 "worked" (exit 0, valid JSON) and left that lie in the value.

### After the improvement (v0.2)

When a span object resolves, the dest snapshot owns the rest of the diagnostic: `byte_start` / `byte_end` recomputed as UTF-8 offsets, `text[].text` taken from dest lines, `rendered` gutters carried like rustc's own snippet. Same kizu log:

```
$ cat kizu.jsonl | ./inlay --from-dir kizu-b4e6a5d --to-dir kizu-HEAD
{"reason":"compiler-message",…,
 "spans":[{"file_name":"/home/runner/work/kizu/kizu/src/app/layout.rs",
           "byte_start":787,"byte_end":810,"line_start":17,"line_end":17,…,
           "text":[{"text":"pub fn seen_hunk_fingerprint(",…}]}],
 "rendered":"error[E0599]: no method named seen_hunk_fingerprint\n  --> /home/runner/work/kizu/kizu/src/app/layout.rs:17:5\n   |\n 17 | pub fn seen_hunk_fingerprint(\n"}
{"$message_type":"diagnostic",…,
 "spans":[{"file_name":"src/app/navigation.rs","line_start":22,"byte_start":850}],
 "rendered":"File \"src/app/navigation.rs\", line 22, in nearest_landing_forward"}
```

Synthetic rustc block `src/app.rs:14` → `src/app/navigation.rs:1` now takes its gutter (`14 | fn nearest_landing…` → ` 1 | fn nearest_landing…`) and `byte_start` 4004 → 4. sitbone/tenaoshi streams unchanged (no rustc gutter). `./demo.sh` exits 0.

## Dogfood targets

- Synthetic two-directory fixture in `./demo.sh`: cargo wrapper, rustc diagnostic, pytest `{filename,lineno}`, generic `{file,line}`, Swift pairs, Python split/rename/delete, Rust file-split, Swift shift + identity, unicode, `src/weird:colon.py`, `notes/file with spaces.txt`, dest path containing `"`, pretty-printed JSON, `Compiling` / URL / timestamp / `error:1` noise. Stub git on PATH.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/kizu` at `b4e6a5d` and `HEAD` (9480-line `src/app.rs` split), plus the live working tree as `--to-dir`.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` at `a95da43` and `HEAD` (`detect()` 45 → 75), plus live tree.
- Copies of `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` at `a41089c` and `HEAD` (`KinsokuEngine.transform` still line 12), plus live tree.

## Surprises

- The flip is visible in a type: flume can never rewrite `line_start` because it is not a substring. The first cargo object in the fixture is the proof.
- `target.src_path` looks like a path and is not a locator. Leaving it stale is correct — cargo is naming the crate root, not a diagnostic span. A path-only rewriter would have moved it and lied about the package.
- Unique-basename binding still makes Swift JSON usable: `{"file":"PresenceArbiter.swift","line":45}` has no tree prefix.
- Silent pass-through of deletions is the right JSON default. `{"path":"src/calc.py","line":11}` (doomed) staying in the object is honest.
- Pretty-printed input falling out of NDJSON line splitting is why ingest is `raw_decode`, not `for line in stdin`. That is the JSON object, not an add-on flag.
- rustc's `529 |` gutter is not a locator *and* not a field. v0.1 rewrote the span and the `-->` and still shipped a contradictory document. The first real-schema dogfood was the only way to see it; the fix is dest-owned bytes/snippets/gutters, which flume's line splice cannot grow.

## Failures

- rustc multi-hunk snippets whose later gutter numbers are *not* old_line+k (a split function) will follow the first locator's offset and can land wrong.
- Common/`}`-only lines refuse to fingerprint (`unresolved`) and pass through.
- `byte_start` assumes `\n` UTF-8 and rustc's 1-based character column. Wide chars and `\r\n` files can be off by a few bytes.
- `code.explanation` in a rustc diagnostic is a book example; it only rewrites if a path binds against `--from-dir`. Foreign stdlib help spans (`library/core/src/cmp.rs`) stay.
- A log that already mixes old *and* new paths will rewrite only what binds against `--from-dir`.
- Concatenated pretty-printed objects with leading commentary on the same line as `{` can fail `raw_decode` and pass through as raw.
- Whole-tree walk of a dirty kizu working tree (~2700 e2e fixtures) is acceptable but not free; copies via `git archive` are the intended dogfood.

## Suggested mutations

- SARIF / clang JSON / Swift serialized diagnostics as first-class schemas (`uri`, `startLine`, `physicalLocation`).
- ANSI-aware matching inside `rendered` so colorized cargo JSON still inlays.
- `--watch` a pinfile of JSON logs, rewrite on tree change (scar-review companion).
- Inverse: emit rustc JSON *from* a flume text log, so the two filters meet in the middle.
- `soul`: rare-token file identity across a language rewrite, same JSON contract.

## Kill / keep

**Keep.** The flipped assumption is the primitive: JSON values in, JSON values out, two directories, no git. Empirically hits kizu's `app.rs` split (span *and* rendered gutter *and* dest `byte_start`), sitbone's shifted `detect()`, tenaoshi's identity `transform`, and a mixed cargo/rustc/pytest stream with a stub git that never fires. The v0.2 dest-owned diagnostic is evidence the JSON object is real: flume could not have grown `byte_start` without first becoming a value walker. Kill only if a later generation proves the real object is a durable pin (`slip mint`) and this filter is just a backend.
