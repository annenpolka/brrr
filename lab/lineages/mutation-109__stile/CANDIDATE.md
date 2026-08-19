# mutation-109 — stile

## Primitive

Inverse printf as a stream filter whose proving string must be **distinctive**. A proving string that is only a newline / fence marker / <4 distinctive static chars is not a template unless there are ≥2 expression holes. Incomplete fence leftovers refuse (caulk complete operand). Names bind. Middle-drop stuffing is a miss.

## Why this might not exist

weld (mutation-59) welds concat backward from a later string. DESTROYER_WELD named the 4-char floor as the product's footgun: `{body}abcd` matches every log line, and an incomplete fence `"```json\n"` is a truncated success.

    # thin.go
    body + "abcd"

    $ ./weld --templates thin.go 'ERROR worker crashed abcd'
      tmpl:  {body}abcd
      {body} = ERROR worker crashed     # every log line ending abcd

    $ ./weld --templates concat.swift $'```json\n{"ok":true}'
      tmpl:  ```json\n{response}\n```
      {response} = {"ok":true}
      truncated: \n```                  # proving operand cut

The conventional patch is “raise `visible < 4` to 6.” That still counts length, so `{body}abcdef` is the same lie, and `"\nDone."` is one raise away from dying. Lowering the floor so `{cleaned}\n` extracts matches every log line (rime's object). The missing verb is still the stream filter, just one whose proving string is **distinctive**, not 4 characters long.

Discarded: grow a rustc parser; a second inverse-printf walker; leftover-name search; hide wrap with a one-line no-bindings guard; lower `visible < 4` so `{cleaned}\n` matches every log line.

## How to run

```bash
chmod +x stile
./stile --selftest
./demo.sh
rg -n --type js 'response\(\)' /path | ./stile $'{"ok":true}\nDone.'
./stile --templates concat.go '/tmp/x: permission denied'
rg -n --type swift 'source graphemes' /path | ./stile \
  'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
./stile --templates src.rs -e '   --> src/git/revert.rs:46:18'
./stile --templates extracted.txt --any < build.log
```

Exit 0 = every argument matched (stdin / `--any`: any line; `--any` stops after the first hit; `--any --complete` skips truncated). Exit 1 = miss. Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2.

## Empirical transcript

### v0.1 working prototype

Copied weld's string-literal concat scanner (not a second walker). Replaced `visible < 4` with distinctive static: newlines, fence ticks, and wrapping space do not count; a bare alnum suffix is not a proving string. ≥2 expression holes still keep `": "`. Truncation that cuts a proving concat operand, or that drops a fence-marker closer, refuses (caulk complete operand). `response() + "\nDone."` still binds.

`./stile --selftest` → `selftest: ok`

weld vs stile on the 4-char floor and the incomplete fence:

    $ ./weld --templates fixtures/src/thin.go 'ERROR worker crashed abcd'
      tmpl:  {body}abcd
      {body} = ERROR worker crashed     # rc=0

    $ ./stile --templates fixtures/src/thin.go 'ERROR worker crashed abcd'
    — no template for: ERROR worker crashed abcd   # rc=1

    $ ./stile --templates fixtures/src/concat.js $'{"ok":true}\nDone.'
      tmpl:  {response}\nDone.
      {response} = {"ok":true}

    $ ./weld --templates fixtures/src/concat.swift $'```json\n{"ok":true}'
      tmpl:  ```json\n{response}\n```
      truncated: \n```                  # rc=0

    $ ./stile --templates fixtures/src/concat.swift $'```json\n{"ok":true}'
    — no template for: ```json
    {"ok":true}                         # rc=1

Middle-drop still misses (`failed read with EPERM`; sitbone `awayRecovered=0`). rustc `--> src/git/revert.rs:46:18` is still a locator.

### Failures that drove the first improvement

v0.1 refused a missing fence closer, then lied on the unclosed opener of the same object:

    # "```json\n" + response()   # no closer
    $ ./stile --templates unclosed.js $'```json\n{"ok":true}\n```'
      tmpl:  ```json\n{response}
      {response} = {"ok":true}\n```     # closer stuffed into the hole

That is leftover stuffing, not inverse-printf of the opener-only concat. DESTROYER_WELD already named it: a complete fenced paste against an unclosed `"```json\n" + response()` binds the closer into `{response}`.

### After the improvement (v0.2)

A trailing hole of a fence-opener template must not swallow a fence-marker leftover. The opener-only template still binds the body. The complete fence still binds `{response}={"ok":true}` without stuffing.

`./stile --selftest` → `selftest: ok`

`./demo.sh` → `passed=94 failed=0`

    $ ./stile --templates unclosed.js $'```json\n{"ok":true}\n```'
    — no template                       # rc=1  closer not stuffed

    $ ./stile --templates unclosed.js $'```json\n{"ok":true}'
      tmpl:  ```json\n{response}
      {response} = {"ok":true}

    $ ./stile --templates fixtures/src/concat.swift $'```json\n{"ok":true}\n```'
      tmpl:  ```json\n{response}\n```
      {response} = {"ok":true}

    $ rg -n -g '*.swift' 'Done\.' tenaoshi \
        | ./stile --templates - $'{"ok":true}\nDone.'
      tmpl:  {response}\nDone.
      {response} = {"ok":true}

    $ rg -n -g '*.swift' json tenaoshi/Engine/Tests \
        | ./stile --templates - $'```json\n{"ok":true}'
    — no template                       # incomplete fence leftover

    $ rg -n -g '*.swift' 'source graphemes' tenaoshi/Engine/Sources \
        | ./stile --templates - \
          'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
      {unitID} = u1
      {sourceGraphemeCount} = 12

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/src/concat.*` / `thin.go` | `--templates` file | distinctive floor; incomplete fence; unclosed stuffing refuse; expr-first `\nDone.`; 3-hole middle-drop |
| `…/tenaoshi` | `rg` wrap + fence | 4-hole wrap; `response() + "\nDone."`; full fence binds; incomplete fence refuses |
| `…/kizu` | `rg format!\|anyhow!` | still binds `git diff single file failed`; timestamp span; rustc locator refuse; `cleaned + "\n"` stays a miss |
| `…/sitbone` | `rg awayRecovered` | full 7-hole; middle-drop still a miss |
| `…/skills` | `rg Serialize(entry)` | newline-only `expr + "\n"` stays a miss |
| ancestor weld | same fixtures | `{body}abcd` hits; incomplete fence truncated-success; stile misses both |

## Surprises

- Distinctive is not a higher floor. `"\nDone."` has five leftover chars (`Done.`) and a delimiter; `"abcd"` has four letters and nothing else. Counting stripped length could not tell them apart.
- ≥2 expression holes still keep `{a}:{b}` / `{path}: {err}`. That is the assignment, and also DESTROYER_WELD's URL lie. Occupancy of a longer splice is not a property of the extractor.
- The incomplete-fence refuse and the unclosed-opener stuffing refuse are the same leftover: a fence-marker operand that is not complete in the query must not become a hole value.

## Failures

- `{a}:{b}` still matches `https://example.com:443` and can rank under a fence paste. Two holes with a 1-char proving string are allowed; they are still every-colon-line.
- `{path}: {err}` as a suffix of `open {path}: {err}` still hits when the longer splice is not in this stream.
- Import `"errors"` is still a no-hole fragment (not a concat splice).
- `cleaned + "\n"` (kizu teardown) is still not a template: newline-only suffix is not distinctive. Leftover-only hit is caulk's job.
- Compiler *messages* (`error: {e}`) still bind; only rustc locators are refused.
- `MAX_FILE_BYTES = 2_000_000` still omits a godfile with no warning.
- `fmt.Sprint` spaces, `strings.Join` / `push_str` remain sibling operators, not a walker.
- Dynamic format strings remain invisible.

## Suggested mutations

- A 1-char two-hole (`{a}:{b}`) is not inverse-printf of a URL; `{path}: {err}` as occupancy of a longer splice is a ranking kernel, not a floor.
- `strings.Join` / `fmt.Fprint` as sibling operators, not a walker.
- Warn (or slurp) `MAX_FILE_BYTES`; raw ingest already has no ceiling.

## Kill / keep

**Keep** if the flipped assumption is visible: weld binds `{body}abcd` and truncated-succeeds an incomplete fence; stile misses both; `response() + "\nDone."` still binds on fixture and tenaoshi; unclosed opener does not stuff `\n```` into `{response}`; middle-drop is still a miss. Do not grow a rustc parser or a second walker. Do not leftover-name search `deserted={0}`. Do not hide wrap with a one-line no-bindings guard. Do not lower the floor so `{cleaned}\n` matches every log line.

## What the flipped assumption bought and lost

**Bought**

- `{body}abcd` is not a template. The 4-char floor is gone.
- Incomplete fence leftover ` ```json\n{"ok":true} ` is not `{response}` truncated.
- Unclosed `"```json\n" + response()` does not swallow the closer.
- `response() + "\nDone."` is still `{response}\nDone.`.
- ≥2 holes still keep `path + ": " + err`.

**Lost**

- Bare alnum suffixes stay misses (intentional).
- Newline-only / fence-marker-only suffixes stay misses (intentional).
- Truncated leftover proving strings (`\nDon`, cut `\n````) stay misses (intentional).
- 1-char two-hole `{a}:{b}` still hits URLs (assignment exception).
