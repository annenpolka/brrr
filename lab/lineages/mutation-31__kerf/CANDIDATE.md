# mutation-31 — kerf

## Primitive

Given a constructed value, emit the numeric/enum cuts it sits on. Stream TSV. The value is the query; the tree is a haystack of predicates.

## Why this might not exist

Ancestor `cusp` (mutation-11) already specialized to the brink: exclusive/inclusive bounds, same-field off-by-one, sentinels, adjacent enum variants. Its default walked the tree and asked *which of this repository's own literals sit on its cuts?*. `--probe VALUE` inverted the join — and then threw the answer away. Exact equality was silent (`401` vs `statusCode == 401` produced no row). Evidence was a fake `<probe>:0`. Default format was a wrapped human report. Stdin was an opt-in after `--probe -`.

A test runner, a log, a fixture file does not want the tree's autobiography. It has a value in hand (`400`, `-1`, `unknown`) and wants the predicates whose knife-edge that value occupies, one TSV row per sit, grep-exit. That is `comm` from the other side. `cusp --probe` was a flag on a linter. `kerf` is the filter.

Discarded (more conventional): keep `cusp` and default `--format tsv`. That leaves the corpus join in charge. The missing verb is *value in, cuts out*.

## How to run

```bash
python3 bin/kerf 3 fixtures
python3 bin/kerf 400 path/
printf '3\n401\nunknown\n' | python3 bin/kerf path/
python3 bin/kerf --header 401 path/ | cut -f1,2,3,5,7
python3 bin/kerf statusCode=400 path/
python3 bin/kerf --scan --format human path/
./demo.sh
```

Exit (probe): `0` any sit, `1` none, `2` usage. `--report-only` always `0`.
`--scan` keeps the linter convention: `1` if the tree sits on itself.

Columns: `value status path line lhs op rhs reason field`.

## Empirical transcript

### Before (v0.1)

`./demo.sh` exits 0. The invert is the default:

```
$ python3 bin/kerf 401 fixtures
401	HIT	offby.swift	2	statusCode	==	401	exact	statusCode

$ python3 bin/kerf 400 fixtures
400	OFFBY	offby.swift	2	statusCode	==	401	off-by-one	statusCode

$ python3 bin/kerf 3 fixtures
3	BRINK	excl.go	4	n	>	3	exclusive	n
3	BRINK	incl.go	4	n	>=	4	exclusive	n
```

Ancestor `cusp --probe 401` was empty. HIT is the class the invert could not live without.

Dogfood, v0.1:

| query | tree | what happened |
| --- | --- | --- |
| `400` | tenaoshi Engine | OFFBY `http.statusCode == 401` — the money shot — plus HIT `contextGraphemes == 400` |
| `401` | tenaoshi Engine | HIT `statusCode == 401`, and OFFBY `contextGraphemes == 400` (401 is one step from an unrelated 400) |
| `statusCode=400` | tenaoshi Engine | only the 401 cut |
| `2` | sitbone Sources | HIT `last.count == 2`, BRINK `parts.count > 2` / `>= 3` |
| `0` | kizu src | **55 rows**: 21 HIT on `== 0`, 19 SENTINEL `> 0`, 15 BRINK of which most are `for i in 0..n` |
| `0` | voidtrace packages+apps | **252 rows** |
| `1000` | kizu src | BRINK `max_line_number < 1000` |
| `92` | tenaoshi Engine | HIT `byte == 92` (backslash) |
| `sucess` | fixtures | silent |

### After (v0.2)

One scoping pass, driven by those rows — not a second primitive:

- loop ranges (`for i in 0..5`, lhs `_`/`i`/`range`) are not cuts
- ambient `{0,1,-1}` is not HIT on `== 0` unless the query is field-qualified (`n=0`)
- HTTP 100–599 OFFBY only against HTTP-ish fields (`statusCode`, `http.statusCode`, `code`). Bare `401` no longer sits on `graphemes == 400`

`./demo.sh` still exits 0. New fixture guards: `grapheme.py`, `loop.rs`, `zero.py`.

Recount:

| query | tree | v0.1 | v0.2 |
| --- | --- | --- | --- |
| `401` | tenaoshi Engine | HIT statusCode **+ OFFBY contextGraphemes==400** | **HIT statusCode only** |
| `400` | tenaoshi Engine | HIT graphemes + OFFBY 401 | same (400 *is* the graphemes cut; 401 is the HTTP one) |
| `statusCode=400` | tenaoshi Engine | OFFBY 401 only | unchanged |
| `0` | kizu src | 21 HIT + 15 BRINK + 19 SENTINEL = **55** | **3 BRINK + 19 SENTINEL = 22** (loop `0..n` gone; `== 0` gone; leftover is `>= 1` last-miss) |
| `0` | voidtrace packages+apps | 58 HIT + 65 BRINK + 129 SENTINEL = **252** | **65 BRINK + 129 SENTINEL = 194** (HIT `== 0` gone; leftover BRINK is `count < 1`) |
| `2` | sitbone Sources | HIT `last.count==2`, BRINK `parts.count > 2` | unchanged |
| `92` | tenaoshi Engine | HIT `byte == 92` | unchanged |
| `91` | tenaoshi Engine | OFFBY `byte == 92` + ASCII range | unchanged |

The leftover `count < 1` / `>= 1` with probe `0` is a real exclusive bound (0 is the last miss). Boring, not wrong. `n=0` still HIT.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi,voidtrace,skills}` (read-only)
- `fixtures/` — exclusive, inclusive, range, off-by-one, sentinel, neighbor, plus negatives (typo, comments, 0/1 count, HTTP-vs-timeout)

## Surprises

- Flipping the default without adding HIT makes `kerf 401` silent — the value *is* the cut, and ancestor classify dropped exact equality. Invert without HIT is a broken grep.
- `statusCode=400` was already the right query language; bare `401` still leaked onto `contextGraphemes == 400` because probe OFFBY had no field affinity.
- Probe `300` *should* sit on `(200..<300).contains(http.statusCode)`. That is the invert question. The timeout `TimeInterval = 300` leak is a `--scan` bug, not a probe bug.

## Failures

- `count < 1` / `>= 1` with probe `0` is a correct exclusive bound and also boring (voidtrace 65 of these).
- Associated-value Swift enums and Rust `FocusPhase::Drift` paths remain half-extracted (ancestor).
- `case .away, .nil` matching probe `unknown` via the sentinel-name list is still a stretch.
- `code` as an HTTP-ish field will also attach 401 OFFBY onto a character-code `== 400`.

## Suggested mutations

- `--miss` : emit values that sat on nothing (the other `comm` column).
- HTTP family as a named enum even without a field token, for HIT/OFFBY among 400/401/403/404.
- Stream `--scan` TSV into `kerf` as a second input (cuts on stdin, values on argv).

## Kill / keep

**Keep.** The object is the inverted join, not a flag on a linter. Value in, TSV cuts out, grep exit, HIT for exact, `--scan` if you still want the autobiography. The first dogfood's 55 `0`s and the grapheme-400 OFFBY were the same knife-edge problem ancestor hit as 0/1 soup — after one cut, `kerf 401 Engine` is the 401 gate and `kerf 400 Engine` is the test value that never fires it.
