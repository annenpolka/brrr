# mutation-34 — splice

## Primitive

Inverse printf as a stream filter whose template may be **several adjacent literals/expressions joined with `+` / `<>` / `fmt.Sprint`**, not one format call. Names bind. Middle-drop stuffing is a miss.

## Why this might not exist

invert (mutation-15), stump (mutation-23), and lede (mutation-33) all treat one template literal. DESTROYER_STUMP_PIN and DESTROYER_PIN_INVERT already named the hole and called it a sibling, not a patch:

```
# concat.go
return errors.New("open " + path + ": " + err.Error())

$ ./invert --templates concat.go --extract
concat.go:4:20: lang=go holes=0 static=5 open

$ ./invert --templates concat.js 'open /tmp/x: permission denied'
— no template for: open /tmp/x: permission denied
```

The Go query “succeeds” only when a sibling `fmt.Errorf` lives in the same slurp. The `+` chain is two short literals, never one template.

lede then closed middle-drop stuffing (`{to} = idle awayRecovered=0`). Concat stayed a sibling. The conventional patch is “lower MIN_STATIC so `open ` hits.” That still does not name `{path}`. The missing verb is still the stream filter, just one whose extractor **splices the chain**.

Discarded: grow a rustc parser; walk the tree; leftover-name search; join every `"a" + "b"` constant.

## How to run

```bash
chmod +x splice
./splice --selftest
./demo.sh
rg -n --type js '"[^"]+"\s*\+' /path | ./splice 'open /tmp/x: permission denied'
./splice --templates concat.go 'open /tmp/x: permission denied'
rg -n --type swift 'source graphemes' /path | ./splice \
  'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
./splice --templates src.rs -e '   --> src/git/revert.rs:46:18'
./splice --templates extracted.txt --any < build.log
```

Exit 0 = every argument matched (stdin / `--any`: any line; `--any` stops after the first hit; `--any --complete` skips truncated). Exit 1 = miss. Exit 2 = usage or binary stdin. Directories on `--templates`/`--files` exit 2.

## Empirical transcript

### v0.1 working prototype

Copied lede's stream ingest and prefix-of-instance kernel. Changed the extractor: after a string literal, look ahead for `+` / `<>`; treat `fmt.Sprint` / `fmt.Sprintln` args as the same chain. Expressions become named holes (`err.Error()` → `{err.Error}`, `str(err)` → `{err}`). Constituent `"open "` is not emitted. Same-line only.

`./splice --selftest` → `selftest: ok`

lede vs splice on the destroyer file (no sibling format string):

```
$ ./lede --templates fixtures/src/concat.go --extract
concat.go:10:20: lang=go holes=0 static=5 open
concat.go:14:9:  lang=go holes=0 static=5 open
concat.go:18:20: lang=go holes=0 static=5 open

$ ./splice --templates fixtures/src/concat.go --extract
concat.go:10:20: lang=go holes=2 static=7 splice open {path}: {err.Error}
concat.go:14:9:  lang=go holes=1 static=5 splice open {path}
concat.go:18:9:  lang=go holes=2 static=7 splice open {path}: {err}

$ ./lede --templates fixtures/src/concat.js 'open /tmp/x: permission denied'
— no template for: open /tmp/x: permission denied   # rc=1

$ ./splice --templates fixtures/src/concat.js 'open /tmp/x: permission denied'
concat.js:2:19: score=0.70 holes=2 via=full
  tmpl:  open {path}: {err}
  {path} = /tmp/x
  {err} = permission denied
```

Middle-drop still misses (`failed read with EPERM` vs `failed {op} on {path} with {err}`; sitbone `awayRecovered=0` stitch). rustc `--> src/git/revert.rs:46:18` is still a locator.

### Failures that drove the first improvement

v0.1 stopped the chain at a newline. Real Swift errors wrap the `+`:

```
return "invalid original range for unit \(unitID): \(start)..<\(end) "
    + "(source graphemes: \(sourceGraphemeCount))"
```

That is **string + string**, holes inside the literals, not `+ expr`. Same-line `+ path` never saw it.

```
$ rg -n -g '*.swift' 'source graphemes' tenaoshi/Engine/Sources \
    | ./splice --templates - \
      'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
# v0.1: two fragments, two hits
  tmpl:  (source graphemes: {sourceGraphemeCount})   {sourceGraphemeCount} = 12
  tmpl:  invalid original range for unit {unitID}: {start}..<{end}
         {unitID}=u1 {start}=3 {end}=8
# not one template. the join is the miss.
```

A one-line `if newline: continue` would hide the wrap and still drop string+string interpolations.

### After the improvement (v0.2)

Newlines and comments are a gap, not a stop. A `+` chain of interpolating strings is one splice when the joined body has holes. `"foo" + "bar"` with no holes is still two literals.

`./splice --selftest` → `selftest: ok`

`./demo.sh` → `passed=73 failed=0`

```
$ rg -n -g '*.swift' 'source graphemes' tenaoshi/Engine/Sources \
    | ./splice --templates - \
      'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
EditPlanComposer.swift:70:20: score=1.08 holes=4 via=full
  tmpl:  invalid original range for unit {unitID}: {start}..<{end} (source graphemes: {sourceGraphemeCount})
  {unitID} = u1
  {start} = 3
  {end} = 8
  {sourceGraphemeCount} = 12

$ rg -n -g '*.swift' 'exactly one retry' tenaoshi \
    | ./splice --templates - \
      'EditPlan validation failed after exactly one retry: blank id; retry: overlap'
EditPlanGenerator.swift:86:9: holes=2 via=full
  {firstValidationError} = blank id
  {retryValidationError} = overlap

$ rg -n -g '*.swift' 'sentence-atomicity' tenaoshi/Engine/Sources \
    | ./splice --templates - \
      'sentence-atomicity violation in unit u: nonstructural candidates change different sentence ordinals (1 and 2); split independent …'
  {unit.id} = u
  {existing} = 1
  {ordinal} = 2
```

## Dogfood targets

| Target | Producer | What we threw at it |
| --- | --- | --- |
| `fixtures/src/concat.*` | `--templates` file | destroyer `+` / `<>` / `fmt.Sprint`, no sibling printf; 3-hole middle-drop |
| `…/tenaoshi` | `rg` wrap + same-line | EditPlanComposer 4-hole wrap; EditPlanGenerator retry wrap; `response()` same-line; sentence-atomicity 3-line join |
| `…/kizu` | `rg format!\|anyhow!` | still binds `git diff single file failed`; timestamp span; rustc locator refuse |
| `…/sitbone` | `rg awayRecovered` | full 7-hole + abridged prefix; middle-drop still a miss |
| `…/voidtrace` | existing invert dogfood | still pass |

## Surprises

- The destroyer case is easy once `+` is a token. The *real* miss was string+string with interpolations on the next line — tenaoshi's production error style, not `"open " + path`.
- `str(err)` / `err.Error()` need different names (`{err}` vs `{err.Error}`). Naming the empty-call receiver and the single-arg inner is enough; leftover-name search is not.
- `fmt.Sprintf` must stay printf. `Sprint(?:ln)?\(` does not match `Sprintf`.
- `"Here is the plan:\n" + response()` is already one line and already a hit in v0.1. The wrap harvest was a different object.

## Failures

- Expression-first concat (`response() + "\nDone."`) still starts only from a string. Suffix-only hole. Same class as lede's `fatal: not a git repository` vs `git diff … failed: {1}`.
- Interpolated tail only still does not find a leading-hole template.
- Compiler *messages* (`error: {e}`) still bind; only rustc locators are refused.
- `MAX_FILE_BYTES = 2_000_000` still omits a godfile with no warning.
- Dynamic format strings remain invisible.
- `"a" + n + 1` is treated as two concat holes once a string started the chain (JS would; Go would not compile).

## Suggested mutations

- Start a chain from `expr + "lit"` when a string operand proves it is concat (the `response() + "\nDone."` miss).
- Reconstruct a chain of templates from `truncated:` remainder + `prefix:` leftover (stump/lede leftover).
- `strings.Join` / `fmt.Fprint` as sibling operators, not a walker.

## Kill / keep

**Keep.** The flipped assumption is visible: concat.js hits without a sibling format string; tenaoshi wrapped `+` is one 4-hole splice; middle-drop is still a miss. Do not grow a rustc parser or a walker. Do not hide the wrap with a one-line no-bindings guard and call concat fixed.

## What the flipped assumption bought and lost

**Bought**

- `"open " + path + ": " + err` is `open {path}: {err}`, not `holes=0 static=5 open`.
- `fmt.Sprint("open ", path, ": ", err)` is the same object.
- Wrapped Swift interpolations joined with `+` bind every name.
- lede's prefix-of-instance rule survived (sitbone middle-drop, 7-hole abridged).

**Lost**

- Expression-first tails still miss.
- A string that starts a `+` chain will not also be emitted as a short static decoy (intentional).
