# mutation-91 — caulk

## Primitive

Inverse printf as a stream filter whose leftover must be a **complete concat operand**. Truncated proving strings (`\nDon` of `\nDone.`) are a miss. Names bind. Middle-drop stuffing is a miss. `cleaned + "\n"` after a contentful leftover still only hits when leftover is complete.

## Why this might not exist

rime (mutation-79) reconstructs the next concat from a partial bind. It still binds a leftover that is only a prefix of the proving string:

```
$ rime --templates leftover.js --matched '{"ok":true}' --remainder $'\nDon'
  tmpl:  {body}\nDone.
  {body} = {"ok":true}
  truncated: e.     # rc=0
```

The conventional patch is “require `--complete` on the fresh-line kernel.” That still treats leftover as a prefix-of-instance query. A leftover that is not a complete operand is not inverse-printf: `\nDon` is not `"\nDone."`.

The missing verb is still the leftover stream filter, just one whose leftover **equals a concat operand**.

Discarded: grow a rustc parser; a second inverse-printf walker; leftover-name search; hide wrap with a one-line no-bindings guard; a one-hole `expr + "\n"` that matches every log line.

## How to run

```bash
chmod +x caulk
./caulk --selftest
./demo.sh
./caulk --templates leftover.js --matched '{"ok":true}' --remainder $'\nDone.'
./caulk --complete --templates leftover.js --matched '{"ok":true}' --remainder $'\nDon'
./caulk --templates leftover.js --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
rg -n --type rust 'cleaned \+' kizu | ./caulk --matched $'keep' --remainder $'\n'
printf '%s\n' '  tmpl:  failed to spawn `{cmd}`' '  prefix: 2026-08-19T23:50:01Z ERROR' \
  | ./caulk --templates leftover.js
```

Exit 0 = leftover consumed (complete operand). Exit 1 = miss (including truncated proving strings and same-template `truncated:` tails). Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2. Leftover mode is `--complete` by default.

## Empirical transcript

### v0.1 working prototype

Copied weld/rime's string-literal concat scanner (not a second walker). Changed the leftover kernel: leftover static must equal a concat operand. `last.startswith(rem)` is gone when complete. Wrap requires both leftovers complete. Truncated leftover prints `leftover is not a complete operand` instead of binding `{body}`.

`./caulk --selftest` → `selftest: ok`

```
$ ./caulk --templates fixtures/src/leftover.js --matched '{"ok":true}' --remainder $'\nDone.'
  tmpl:  {body}\nDone.
  {body} = {"ok":true}

$ ./caulk --templates fixtures/src/leftover.js --matched '{"ok":true}' --remainder $'\nDon'
— leftover is not a complete operand: \nDon  (of \nDone.)     # rc=1

$ rime --templates fixtures/src/leftover.js --matched '{"ok":true}' --remainder $'\nDon'
  tmpl:  {body}\nDone.
  truncated: e.     # rc=0
```

### Failures that drove the first improvement

v0.1 refused `\nDon` on argv, then misread rime's leftover record:

```
$ rime ... --remainder $'\nDon' | ./caulk --templates leftover.js
— no template for leftover: e.     # rc=1
```

rime prints both `rem: \nDon` (the leftover) and `truncated: e.` (rest of the operand). Parser preferred `truncated:` over `rem:`, so leftover became `e.` instead of the truncated proving string. Completeness refused the wrong leftover.

A second hole: truncated wrap *prefix* leftover with a complete remainder diagnosed remainder `\n```` as incomplete of `"```json\n"`.

### After the improvement (v0.2)

Leftover remainder is `remainder:` / `rem:`. `truncated:` is rest-of-operand, not leftover, unless no rem was named. rime's column-padded `rem:    \\nDon` lstrips pad spaces before decode. Diagnosis names the leftover that is actually a proper prefix of an operand.

`./caulk --selftest` → `selftest: ok`

`./demo.sh` → `passed=25 failed=0`

```
$ rime --templates leftover.js --matched '{"ok":true}' --remainder $'\nDon' \
    | ./caulk --templates leftover.js
— leftover is not a complete operand: \nDon  (of \nDone.)     # rc=1

$ ./caulk --templates leftover.js --matched '{"ok":true}' \
    --prefix $'```json' --remainder $'\n```'
— leftover is not a complete operand: ```json  (of ```json\n)
```

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/src/leftover.js/.go` | `--templates` file | complete `\nDone.`; truncated `\nDon`; fence wrap; stamp prefix; leftover-only `{cleaned}\n`; middle-drop miss |
| `…/tenaoshi` | `rg Done.` / `json` | complete `response() + "\nDone."`; truncated `\nDon` miss; fence wrap complete; truncated wrap rem/prefix miss |
| `…/kizu` | `rg 'cleaned \+'` | `cleaned + "\n"` leftover-only after contentful complete leftover; truncated leftover does not steal `{cleaned}\n`; timestamp prefix leftover still a miss (no concat) |
| `…/sitbone` | leftover `awayRecovered=0` | middle-drop miss |
| ancestor rime | leftover remainder as argv / pipe | still binds `\nDon`; pipe of truncated leftover is now a complete-operand miss |

## Surprises

- rime's leftover truncated bind prints two fields: leftover remainder and rest-of-operand. Preferring `truncated:` hid the proving-string leftover.
- weld's `truncated:` remainder is usually the rest of the *same* template (` deserted={0}…`), not a proving string. Consuming it as a next concat would be leftover-name search. caulk still refuses it.
- `cleaned + "\n"` leftover-only is already a complete operand (`\n`). Truncated leftover of a longer concat (`\nDon`) does not steal it.
- weld `prefix: 2026-08-19T23:50:01Z ERROR` does not include the trailing space of `" ERROR "`. The space is on the matched side. That is a complete operand reconstructed from leftover+matched, not a truncated leftover.

## Failures

- kizu `failed to spawn` timestamp leftover has no concat (`ts + " ERROR " + body`). Prefix leftover with no next proving static is a miss.
- Interpolated tail only (`fatal: not a git repository` vs `git diff … failed: {1}`) still does not find a leading-hole format string.
- Compiler *messages* (`error: {e}`) still bind as fresh queries; rustc locators are refused.
- `MAX_FILE_BYTES = 2_000_000` still omits a godfile with no warning.
- Dynamic format strings remain invisible.
- A leftover remainder that is only punctuation (`.` / `` ` ``) is not enough static. rime's rest-of-operand `e.` is not a proving string.

## Suggested mutations

- `strings.Join` / `fmt.Fprint` as sibling operators, not a walker.
- Reconstruct a *chain* of more than two templates (stamp then spawn then done) without re-ranking the inner hit as a second leftover.
- Complete leftover of `strings.Builder.WriteString` operands, still not a walker.

## Kill / keep

**Keep** if truncated vs complete leftover is the visible flip: rime binds leftover `\nDon`; caulk misses it as not a complete operand; complete `\nDone.` still binds `{body}`; leftover-only `{cleaned}\n` hits only when leftover is complete `\n`; middle-drop is still a miss. Do not grow a rustc parser or a second walker. Do not leftover-name search `deserted={0}`. Do not hide wrap with a one-line no-bindings guard.

## What the flipped assumption bought and lost

**Bought**

- Leftover `\nDon` is not `{body}\nDone.` truncated. It is not inverse-printf.
- Leftover `\nDone.` is still `{body}\nDone.` with `{body}` from the prior instance.
- `"```json\n" + response() + "\n```"` still reconstructs from complete prefix leftover + remainder.
- `cleaned + "\n"` binds after a contentful leftover only when leftover is the complete `\n` operand.

**Lost**

- Truncated leftover proving strings stay misses (intentional).
- Same-template truncated tails stay misses (intentional).
- Timestamp wrappers with no concat still miss (intentional).
- Fresh-line inverse-printf is still weld's job; leftover-only templates never hit a fresh query.
