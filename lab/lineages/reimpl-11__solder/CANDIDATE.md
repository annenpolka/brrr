# reimpl-11 — solder

## Primitive

Inverse printf as a stream filter whose concat template may **start at an expression**, not only at a leading string literal. A later string operand proves the chain. Names bind. Middle-drop stuffing is a miss.

## Why this might not exist

splice (mutation-34) splices `"lit" + expr + "lit"` from a leading string. DESTROYER_STUMP_PIN named concat as a sibling; splice closed the string-first case. It still misses when the chain starts at an expression:

```
# tenaoshi EditPlanParserTests.swift
response() + "\nDone."

$ ./splice --templates concat.js $'{"ok":true}\nDone.'
— no template for: {"ok":true}
Done.
```

The conventional patch is “start the scanner at every identifier.” That is a walker. The missing verb is still the stream filter, just one whose extractor **welds from a proving string backward**.

Discarded: grow a rustc parser; walk the tree; leftover-name search; join every `"a" + "b"` constant; hide the wrap with a one-line no-bindings guard.

## How to run

```bash
chmod +x solder
./solder --selftest
./demo.sh
rg -n --type js 'response\(\)' /path | ./solder $'{"ok":true}\nDone.'
./solder --templates concat.go '/tmp/x: permission denied'
rg -n --type swift 'source graphemes' /path | ./solder \
  'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
./solder --templates src.rs -e '   --> src/git/revert.rs:46:18'
./solder --templates extracted.txt --any < build.log
```

Exit 0 = every argument matched (stdin / `--any`: any line; `--any` stops after the first hit; `--any --complete` skips truncated). Exit 1 = miss. Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2.

## Empirical transcript

### v0.1 working prototype

Rebuilt the extractor without reading weld: a string literal is still the proof, but the chain is collected **backward** through `+` / `<>` onto an expression (and forward as splice). `response()` → `{response}`. `err.Error()` vs `str(err)` keep distinct names. Newlines and comments between operands stay a gap. Same-line and wrap. Prefix-of-instance kernel unchanged. Lookback from the proving string is capped (`MAX_WELD_LOOKBACK=4000`); that is a bound, not a walker.

`./solder --selftest` → `selftest: ok`

splice vs solder on the expression-first fixture:

```
$ ./splice --templates fixtures/src/concat.js --extract
concat.js:2:19: lang=js holes=2 static=7 splice open {path}: {err}
concat.js:10:16: lang=js holes=0 static=6 \nDone.

$ ./solder --templates fixtures/src/concat.js --extract
concat.js:2:19: lang=js holes=2 static=7 splice open {path}: {err}
concat.js:6:19: lang=js holes=2 static=2 weld {path}: {err}
concat.js:10:10: lang=js holes=1 static=6 weld {response}\nDone.

$ ./solder --templates fixtures/src/concat.js $'{"ok":true}\nDone.'
concat.js:10:10: score=0.71 holes=1 via=full
  tmpl:  {response}\nDone.
  {response} = {"ok":true}
```

Middle-drop still misses (`failed read with EPERM` vs `failed {op} on {path} with {err}`). rustc `--> src/git/revert.rs:46:18` is still a locator.

tenaoshi EditPlanParserTests.swift:318 `response() + "\nDone."` bound `{response}={"ok":true}`. EditPlanComposer wrap stayed one 4-hole splice (`{unitID}=u1` … `{sourceGraphemeCount}=12`, score=1.08).

### Failures that drove the first improvement

v0.1 bound `response() + "\nDone."` and then lied on a tenaoshi fence that is the same object:

```
"```json\n" + response() + "\n```"

$ rg -n -g '*.swift' json tenaoshi/Engine/Tests \
    | ./solder --templates - $'```json\n{"ok":true}\n```'
  tmpl:  ```json{response}\n```
  {response} =
{"ok":true}
```

`prepare_static` stripped a trailing newline from every concat operand. `"```json\n"` became `json` glued onto the hole. The wrap is a gap; stripping `\n` is a different stop.

Same paste also ranked a second hit `{path}: {err}` under `open {path}: {err}` with `{path}=open /tmp/x` — the tail of the string-first splice, not a second template.

A mistaken “every leading hole is a weld” floor then let `{revision}:{1}` and `{1} {2} {3}` bind timestamp / `git diff …` lines. That is not concat. The short-static exemption is only for a proving-string chain.

### After the improvement (v0.2)

Concat operands keep escaped trailing newlines. A leading-hole weld that is a suffix of a longer splice on the same paste is dropped; it still hits when it is the only template. The `{a}:{b}` floor applies to welded/spliced chains, not to format strings.

`./solder --selftest` → `selftest: ok`

`./demo.sh` → `passed=84 failed=0`

```
$ ./solder --templates fixtures/src/concat.swift $'```json\n{"ok":true}\n```'
concat.swift:15:12: score=0.78 holes=1 via=full
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}

$ rg -n -g '*.swift' 'Done\.' tenaoshi \
    | ./solder --templates - $'{"ok":true}\nDone.'
EditPlanParserTests.swift:318:13: holes=1 via=full
  tmpl:  {response}\nDone.
  {response} = {"ok":true}

$ rg -n -g '*.swift' 'source graphemes' tenaoshi/Engine/Sources \
    | ./solder --templates - \
      'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
EditPlanComposer.swift:70:20: holes=4 via=full
  {unitID} = u1
  {sourceGraphemeCount} = 12

$ ./solder --templates fixtures/src/concat.js 'open /tmp/x: permission denied'
  tmpl:  open {path}: {err}
  {path} = /tmp/x
  # no second hit {path}=open /tmp/x
```

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/src/concat.*` | `--templates` file | destroyer `+` / `<>` / `fmt.Sprint`; expr-first `path + ": "` / `response() + "\nDone."`; 3-hole middle-drop |
| `…/tenaoshi` | `rg` wrap + expr-first | EditPlanComposer 4-hole wrap; EditPlanParserTests `response() + "\nDone."`; fence `"```json\n"` |
| `…/kizu` | `rg format!\|anyhow!` | still binds `git diff single file failed`; timestamp span; rustc locator refuse |
| `…/sitbone` | `rg awayRecovered` | full 7-hole + abridged prefix; middle-drop still a miss |
| `…/skills` | `rg Serialize(entry)` | newline-only `expr + "\n"` stays a miss (thin static) |

## Surprises

- The proving string can be short (`": "`) if there are two expression holes. A one-hole `expr + "\n"` is not inverse-printf — every log line would bind.
- splice already handled `fmt.Sprint(path, ": ", err)` because Sprint args are not required to start with a string. The `+` / `<>` chain was the hole.
- Looking backward from the string, not starting at every identifier, is what keeps `return response() + "\nDone."` from naming `{return}`.
- The fence miss was not wrap. `"```json\n"` is one operand whose payload *is* a newline. Treating that like a source-line ending glued `json` onto `{response}`.
- Lowering `min_static` for *any* leading hole (`{1} {2} {3}`) is not the same verb as lowering it for a proving-string weld.

## Failures

- `cleaned + "\n"` (kizu/sitbone/skills) is still not a template: newline-only suffix is not enough static.
- Interpolated tail only (`fatal: not a git repository` vs `git diff … failed: {1}`) still does not find a leading-hole format string. That is lede's suffix miss, not concat.
- Compiler *messages* (`error: {e}`) still bind; only rustc locators are refused.
- `MAX_FILE_BYTES = 2_000_000` still omits a godfile with no warning.
- Dynamic format strings remain invisible.
- `fmt.Sprint` is still treated as `+` (no inserted spaces). DESTROYER_WELD named that as a sibling, not a patch.

## Suggested mutations

- Reconstruct a chain of templates from `truncated:` remainder + `prefix:` leftover (stump/lede leftover).
- `strings.Join` / `fmt.Fprint` as sibling operators, not a walker.
- A one-hole `expr + "\\n"` with more than newline static (e.g. kizu `cleaned + "\\n"` after a contentful leftover) without matching every log line.

## Kill / keep

**Keep.** The flipped assumption is visible: splice misses `response() + "\nDone."`; solder binds `{response}`; tenaoshi wrapped `+` is still one 4-hole splice; middle-drop is still a miss. Do not grow a rustc parser or a walker. Do not hide the wrap with a one-line no-bindings guard and call concat fixed.

Clean-room vs DESTROYER_WELD gold: extract of `concat.js` is byte-identical (`splice open {path}: {err}`, `weld {path}: {err}`, `weld {response}\nDone.`). Fence score 0.78 and `{response}={"ok":true}` match. `./demo.sh` is `passed=84 failed=0`, same count as the victim demo. The primitive **survived** clean-room: expr-first concat works without a walker.

## What the flipped assumption bought and lost

**Bought**

- `response() + "\nDone."` is `{response}\nDone.`, not holes=0 static=6 `\nDone.`.
- `path + ": " + err.Error()` is `{path}: {err.Error}`, which splice never extracted.
- Wrapped `body\n + "\nDone."` is one weld.
- String-first `"open " + path` and lede's prefix-of-instance rule survived.

**Lost**

- Newline-only suffixes still miss (intentional).
- A suffix weld of a longer splice on the same paste is no longer printed; it still hits alone (`/tmp/x: permission denied` → `{path}: {err.Error}`).
