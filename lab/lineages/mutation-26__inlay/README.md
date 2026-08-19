# inlay

Rewrite stale locators *inside JSON values* from one directory snapshot onto another. Never talks to git. Never takes a locator as an argument. stdout is valid JSON.

`flume` splices `file:line` in a text log. That is the wrong object for `cargo --message-format=json` and `rustc --error-format=json`: the address is a `file_name` string plus a `line_start` integer, and a text splice can unseal the document. `inlay` walks values.

## Install / run

```bash
chmod +x ./inlay
./inlay --help
./demo.sh
```

Requires Python 3. Git is not a dependency.

## Interaction

```
cargo test --message-format=json | inlay --from-dir oldtree --to-dir newtree
rustc --error-format=json … 2>&1 | inlay --from-dir oldtree --to-dir newtree
inlay --from-dir oldtree --to-dir newtree cargo.jsonl rustc.json --trace
```

JSON values in, JSON values out. Structured span objects (`file_name` + `line_start`) and generic `{file,line}` pairs move together. Locators inside string values (`rendered`, messages) move too. Non-JSON chatter passes through. Mappings, if you want them, are `--trace` on stderr. Confirmed deletions pass through unchanged.

## Examples

Cargo compiler-message from before a file-split, pointed at today's tree. The span fields are numbers, not `file:line` text. The `rendered` gutter and `byte_start` follow the dest line:

```bash
cat cargo.jsonl | ./inlay --from-dir kizu-old --to-dir kizu-now
# {"reason":"compiler-message","message":{"spans":[{"file_name":".../src/app/layout.rs","line_start":17,"byte_start":787,…
#   "rendered":"… --> …/src/app/layout.rs:17:5\n   |\n 17 | pub fn seen_hunk_fingerprint(\n"}}
```

Pretty-printed rustc JSON (one object, not NDJSON):

```bash
rustc --error-format=json src/app.rs | jq . | ./inlay --from-dir from --to-dir to
```

Generic JSON log with a dest path that would break a text splice:

```bash
echo '{"file":"src/plain.py","line":1}' | ./inlay --from-dir old --to-dir new
# {"file":"src/quo\"te.py","line":1}
```
