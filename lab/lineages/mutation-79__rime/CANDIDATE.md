# mutation-79 — rime

## Primitive

Inverse printf as a stream filter whose input is a **partial bind** (what already matched + prefix leftover / truncated remainder), not a fresh log line. Emit the next concat template that consumes the leftover. Names bind. Middle-drop stuffing is a miss.

## Why this might not exist

weld (mutation-59) binds inverse-printf when a concat chain starts at an expression (`response() + "\nDone."`). It still fails when the proving string is a leftover *suffix* of a previous match or a `truncated:` remainder:

```
$ weld --templates leftover.js $'\nDone.'
— no template for: Done.     # rc=1
# normalize_query stripped the proving newline
```

lede/stump already *print* `prefix:` and `truncated:`. They do not consume them as the next concat. The conventional patch is “don’t strip the query” or “lower MIN_STATIC so `\nDone.` hits.” That still treats leftover as a fresh log line, and a one-hole `expr + "\n"` would match every log line.

The missing verb is still the stream filter, just one whose query is the leftover of a previous bind.

Discarded: grow a rustc parser; a second inverse-printf walker; leftover-name search; hide wrap with a one-line no-bindings guard; a one-hole `expr + "\n"` that matches every log line.

## How to run

```bash
chmod +x rime
./rime --selftest
./demo.sh
./rime --templates leftover.js --matched '{"ok":true}' --remainder $'\nDone.'
./rime --templates leftover.js --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
rg -n --type rust 'cleaned \+' kizu | ./rime --matched $'keep' --remainder $'\n'
printf '%s\n' '  tmpl:  failed to spawn `{cmd}`' '  prefix: 2026-08-19T23:50:01Z ERROR' \
  | ./rime --templates leftover.js
```

Exit 0 = leftover consumed. Exit 1 = miss (including same-template `truncated:` tails). Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2.

## Empirical transcript

### v0.1 working prototype

Copied weld's string-literal concat scanner (not a second walker). Changed the kernel: leftover static is pinned at known offsets (prefix leftover at the start, remainder at the end). Leading-hole `{body}\nDone.` binds the prior instance. Wrap `"```json\n" + response() + "\n```"` reconstructs from *both* leftovers. `cleaned + "\n"` is extracted as leftover-only and refused as a fresh query.

`./rime --selftest` → `selftest: ok`

```
$ ./rime --templates fixtures/src/leftover.js --matched '{"ok":true}' --remainder $'\nDone.'
  tmpl:  {body}\nDone.
  {body} = {"ok":true}

$ weld --templates fixtures/src/leftover.js $'\nDone.'
— no template for: Done.
```

### Failures that drove the first improvement

v0.1 bound `--prefix '… ERROR '` (trailing space) and then missed the actual weld record:

```
  prefix: 2026-08-19T23:50:01Z ERROR     # no trailing space
  tmpl:  failed to spawn `{cmd}`
```

The proving static is `" ERROR "` (spaces both sides). weld's leftover drops the trailing space; the space lives on the matched side. Witness `p in prefix` failed.

A second hole showed up on skills: hydrating `csharp.md` slurped a documentation string and swallowed the grep-line `Serialize(entry) + "\n"`. Same-template sitbone `truncated: deserted={0}…` exited 2 (usage) instead of miss.

### After the improvement (v0.2)

Prefix leftover matches a proving static that *straddles* prefix/matched. Unknown-type files (`.md`) are not hydrated — the grep line keeps the leftover concat. Same-template truncated remainder is exit 1, not usage.

`./rime --selftest` → `selftest: ok`

`./demo.sh` → `passed=19 failed=0`

```
$ printf '%s\n' '  tmpl:  failed to spawn `{cmd}`' \
    '  {cmd} = git apply --reverse' \
    '  prefix: 2026-08-19T23:50:01Z ERROR' \
    | ./rime --templates fixtures/src/leftover.js
  tmpl:  {ts} ERROR {body}
  {ts} = 2026-08-19T23:50:01Z
  {body} = failed to spawn `git apply --reverse`

$ rg -n 'Serialize(entry)' skills | ./rime --templates - \
    --matched '{"h":"H1"}' --remainder $'\n'
  tmpl:  {entry}\n
  {entry} = {"h":"H1"}
```

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/src/leftover.js/.go` | `--templates` file | leftover `\nDone.`; fence wrap; stamp prefix; leftover-only `{cleaned}\n`; middle-drop miss |
| `…/tenaoshi` | `rg Done.` / `json` | `response() + "\nDone."` leftover; fence wrap from prefix+remainder |
| `…/kizu` | `rg 'cleaned \+'` | `cleaned + "\n"` leftover-only after contentful prior; timestamp prefix leftover still a miss (no concat) |
| `…/skills` | `rg Serialize(entry)` | markdown grep-line `{entry}\n` after hydrate skip |
| `…/sitbone` | leftover `awayRecovered=0` | middle-drop miss; same-template truncated miss |
| ancestor weld | leftover remainder as argv | still misses `Done.` |

## Surprises

- weld's `truncated:` remainder is usually the rest of the *same* template (` deserted={0}…`), not a proving string. Consuming it as a next concat would be leftover-name search. rime refuses it.
- The leftover that *is* a proving string is `Hit.suffix` / `--remainder` / `prefix:` span leftover — weld prints the last and not always the first.
- `cleaned + "\n"` is extractable once leftover-only is a flag; the fresh-line refuse is the other half of the primitive.
- weld `prefix: 2026-08-19T23:50:01Z ERROR` does not include the trailing space of `" ERROR "`. The space is on the matched side. That is alignment, not guesswork.

## Failures

- kizu `failed to spawn` timestamp leftover has no concat (`ts + " ERROR " + body`). Prefix leftover with no next proving static is a miss.
- Interpolated tail only (`fatal: not a git repository` vs `git diff … failed: {1}`) still does not find a leading-hole format string. That is lede's suffix miss, not leftover concat.
- Compiler *messages* (`error: {e}`) still bind as fresh queries; rustc locators are refused.
- `MAX_FILE_BYTES = 2_000_000` still omits a godfile with no warning.
- Dynamic format strings remain invisible.
- A leftover remainder that is only punctuation (`.` / `` ` ``) is not enough static.

## Suggested mutations

- `strings.Join` / `fmt.Fprint` as sibling operators, not a walker.
- Reconstruct a *chain* of more than two templates (stamp then spawn then done) without re-ranking the inner hit as a second leftover.
- `--complete` leftover: refuse truncated proving strings (`\nDon` of `\nDone.`).

## Kill / keep

**Keep.** The flipped assumption is visible: weld misses leftover `\nDone.` as a fresh line; rime binds `{body}` from the prior instance; tenaoshi fence wrap reconstructs from prefix leftover + remainder; `cleaned + "\n"` hits only after a contentful leftover; middle-drop is still a miss. Do not grow a rustc parser or a second walker. Do not leftover-name search `deserted={0}`. Do not hide wrap with a one-line no-bindings guard.

## What the flipped assumption bought and lost

**Bought**

- Leftover `\nDone.` is `{body}\nDone.`, not a stripped `Done.` miss.
- `"```json\n" + response() + "\n```"` reconstructs from prefix leftover + remainder.
- `cleaned + "\n"` / `Serialize(entry) + "\n"` bind after a contentful leftover without matching every log line.
- weld `prefix:` records compose: `weld | rime`.

**Lost**

- Same-template truncated tails stay misses (intentional).
- Timestamp wrappers with no concat still miss (intentional).
- Fresh-line inverse-printf is still weld's job; leftover-only templates never hit a fresh query.
