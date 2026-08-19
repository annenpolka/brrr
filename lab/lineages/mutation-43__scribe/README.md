# scribe

Rewrite stale locators *inside SARIF / clang JSON / Swift serialized diagnostics* from one directory snapshot onto another. Never talks to git. Never takes a locator as an argument. stdout is the same schema, still valid JSON.

`flume` splices `file:line` in a text log. `inlay` walks cargo/rustc JSON (`file_name` + `line_start` siblings). That is the wrong object for SARIF: the path is `physicalLocation.artifactLocation.uri` and the line is a nested integer `region.startLine`. A text splice misses the integer or unseals the document the moment the dest path contains `"`. `scribe` walks those schemas.

## Install / run

```bash
chmod +x ./scribe
./scribe --help
./demo.sh
```

Requires Python 3. Git is not a dependency.

## Interaction

```
cat results.sarif | scribe --from-dir oldtree --to-dir newtree
clang -fdiagnostics-format=json … 2>&1 | scribe --from-dir oldtree --to-dir newtree
scribe --from-dir oldtree --to-dir newtree run.sarif clang.json --trace
```

JSON values in, JSON values out. Nested locator objects move together (`uri` + `startLine`, clang `caret.file`/`line`/`offset`, Swift `key.filepath`/`key.line`). Locators inside string values (`message.text`, snippets) move too, including ANSI-wrapped paths. Pretty-printed values stay pretty; NDJSON stays one object per line. Confirmed deletions pass through unchanged. `--strict` exits 1 only when a locator cannot even be read from `--from-dir`.

Cargo `file_name` + `line_start` is not a locator here. That is inlay's schema.

## Examples

SARIF from before a file-split, pointed at today's tree. `startLine` stays an integer. `byteOffset` and `snippet` follow the dest line:

```bash
cat kizu.sarif | ./scribe --from-dir kizu-old --to-dir kizu-now
# physicalLocation.artifactLocation.uri → …/src/app/layout.rs
# region.startLine 529 → 17
# region.byteOffset dest-owned; snippet dest-owned
```

Pretty-printed SARIF stays pretty; a clang NDJSON stream stays compact:

```bash
jq . results.sarif | ./scribe --from-dir from --to-dir to
clang -fdiagnostics-format=json … 2>/dev/null | ./scribe --from-dir from --to-dir to
```

Dest path with a quote — a text splice would unseal the document:

```bash
echo '{"version":"2.1.0","runs":[{"tool":{"driver":{"name":"x"}},"results":[{"locations":[{"physicalLocation":{"artifactLocation":{"uri":"src/plain.py"},"region":{"startLine":1}}}]}]}]}' \
  | ./scribe --from-dir old --to-dir new
# {"…","uri":"src/quo\"te.py","region":{"startLine":1}…}   still json.loads
```
