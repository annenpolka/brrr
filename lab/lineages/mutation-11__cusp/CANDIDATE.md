# mutation-11 — cusp

## Primitive

Report predicates whose constructed values sit on the cut: exclusive/inclusive numeric bounds, same-field off-by-one, sentinels, adjacent enum variants. No string-edit distance.

## Why this might not exist

Ancestor `nigh` joined constructed literals to branch cuts and classified CLOSED / NIGH / BRINK. NIGH was a string metric (typo, case, inflection, affix). That class is the same surface as name-alias tools, and on real trees it spent its budget on `ENOENT`≈`event` and `lib.py:3`≈`lib.py`.

The sharper object was already in the leftover column: a value that *sits on the bound*. `n > 3` with a constructed `3`. `statusCode == 401` with a constructed `400`. `status != "unknown"` with a constructed `"unknown"`. `phase === "done"` with a constructed `"running"` next to it in the declared enum. Fencepost, exclusive vs inclusive, sentinel — not spelling.

Linters ask "is this comparison silly?". Coverage asks "did a process cross it?". Mutation testing asks "would a test fail?". Nobody asks the static question: *given the values this tree already writes down, which cuts have a constructed value sitting on the knife-edge?*

## How to run

```bash
python3 bin/cusp fixtures
python3 bin/cusp --offby --brink path/
python3 bin/cusp --probe 3 fixtures
python3 bin/cusp --format tsv --offby fixtures | cut -f1,2,3,6,10
python3 bin/cusp --lhs statusCode /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi/Engine
./demo.sh
```

Exit: `0` clean, `1` any BRINK/OFFBY/SENTINEL/NEIGHBOR, `2` usage. `--report-only` always `0`.

## Empirical transcript

### Before (v0.1, commit `6e43cec`)

Fixtures already named the four statuses:

```
OFFBY      offby.swift:2  statusCode == 401     (400)
BRINK      excl.go:4  n > 3                     (3 exclusive)
BRINK      incl.go:4  n >= 4                    (4 inclusive)
BRINK      range.swift:2  code range [200, 300] (199/200/299/300)
SENTINEL   sentinel.py:2  err != -1
SENTINEL   sentinel.py:10  status != 'unknown'
NEIGHBOR   neighbor.ts:4  phase === 'done'      (running)
NEIGHBOR   enum_swift.swift:12  case absent, unknown, none  (present)
```

String-edit NIGH is gone: `typo.py` (`success`/`Success`/`sucess`) is silent.

Dogfood on real trees (v0.1 scoping: same field *or* same file):

| repo | files | gates | OFFBY | BRINK | SENTINEL | NEIGHBOR |
| --- | --- | --- | --- | --- | --- | --- |
| tenaoshi Engine | 31 | 161 | **50** | 40 | — | — |
| sitbone Sources | 25 | 60 | 2 | 7 | 16 | 3 |
| kizu src | 69 | 90 | 20 | 30 | 19 | — |

Real hits already present, drowned:

- tenaoshi `http.statusCode == 401` OFFBY against test `statusCode: 400`
- tenaoshi `(200..<300).contains(http)` BRINK against a **timeout** `TimeInterval = 300` in the same file
- sitbone `parts.count > 2` / `>= 3` with `suffix(2)` / `suffix(3)`
- sitbone `case .absent, .unknown, .none` — sentinel cluster

The 50 OFFBYs were `count == 1` vs constructed `0`, `count == 2` vs `1`, `schemaVersion == 1` vs a same-file `0`. Same-file number soup.

### After (v0.2)

Scoping driven by those failures:

- OFFBY of `{0,1,2,-1}` against `{0,1,2,-1}` is not a cut
- a producer with a field must share the gate's field (HTTP range no longer sits on `TimeInterval = 300`)
- same-file anonymous literals only attach to a distinctive cut (`|n|≥2` except ambient `0/1/-1`)
- tiny slice ranges (`0..<1`, `1...3`) dropped
- range subject is the full dotted argument: `(200..<300).contains(http.statusCode)` → field `statusCode`

`./demo.sh` still exits 0. New fixture guards: `noise.py` (`count == 1` with `[0,1,2]`) is silent; `timeout.swift` does not put `300` on the HTTP range.

Recount (same roots):

| repo | v1 OFFBY / BRINK / SENTINEL | v2 |
| --- | --- | --- |
| tenaoshi Engine | 50 / 40 / — | **4 / 7 / 6** |
| sitbone Sources | 2 / 7 / 16 | **1 / 4 / 6** (+ 3 NEIGHBOR) |
| kizu src | 20 / 30 / 19 | **0 / 23 / 7** |
| voidtrace packages+apps | — | 12 / 47 / 77 |
| skills | — | 0 / 0 / 0 (2 gates, neither on a cut) |

### Findings that survived scrutiny

**tenaoshi** — `http.statusCode == 401` in `CodexResponsesClient.swift:130` vs constructed `400` on the same field in tests. The tree talks about unauthorized and about bad-request, one step apart, and only tests the 401 cut. Also `byte == 92` (backslash) with constructed `91`/`93` in the same ASCII walk — a literal fencepost.

**sitbone** — `parts.count > 2` / `>= 3` in `BrowserSiteIdentity.swift` with `suffix(2)` and `suffix(3)`. Exclusive and inclusive bounds on the same host-splitter, both inhabited. `PresenceStatus` switch groups `.absent, .unknown, .none`; `.unknown` is constructed as a live sentinel. `FocusPhase` `case .flow` / `.drift` / `.away` sit next to each other as NEIGHBOR.

**voidtrace** — `criticalTier < 0` and `event.timeMs < 0` with constructed `0` on the same field: the numeric sentinel is the domain edge the kernel actually writes.

**kizu** — `max_line_number < 1000` still finds a constructed `1000`. Some of that is still anonymous-literal leakage (see Failures).

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu,tenaoshi,voidtrace,skills}` (read-only)
- `fixtures/` — exclusive, inclusive, range, off-by-one, numeric/string sentinel, TS union neighbor, Swift enum cluster, plus negatives (typo, comments, 0/1 count, HTTP-vs-timeout)

## Surprises

- Killing NIGH did not empty the report. The brink column was the part that pointed at real fences (401/400, suffix(2) vs `> 2`, `.unknown`).
- Swift `.foo` cases, which ancestor nigh never treated as gates, are the enum half of the primitive. sitbone's presence sentinel cluster only exists because of that.
- `(200..<300).contains(http.statusCode)` is the exclusive/inclusive bound in the wild — and the first dogfood immediately confused it with a 300-second timeout. Field identity *is* the metric, once you throw spelling away.
- `err != -1` needs unary-minus folding. The lexer yields OTHER `-` + NUMBER `1`. Without it the numeric sentinel class is dead in Python.

## Failures (remaining)

- Rust/Swift `0..5` / `0..<5` loops still look like range gates (`lhs=_`). Span > 2 escapes the tiny-range filter.
- `max_line_number < 1000` can sit on an anonymous `1000` in the same file (kizu timestamps).
- `> 0` / `>= 0` on a named field (`currentPhaseDuration`, `baseTier`) is a correct sentinel and also boring.
- `case .away, .nil` matching a constructed `"zero"` via the sentinel-name list is a stretch.
- JSON-schema `enum: ["none", ...]` inflates voidtrace SENTINEL when code compares against `none`/`0`.
- Associated-value Swift enums and Rust `FocusPhase::Drift` paths are only half-extracted.

## Suggested mutations

- Drop loop ranges (`for i in 0..n`, `0..<count`) unless the subject is a domain field.
- Treat HTTP status codes as a named family (400/401/403/404) even without a shared field token.
- `--probe` against stdin as a `comm`-style filter in a test runner.
- Enum ordinal gates (`phase >= .running`).

## Kill / keep

**Keep, as a brutal specialization.** The missing Unix column was never "how close are these two strings?". It was "does this tree construct a value that sits on this predicate's cut?". Four statuses, one join, `--probe` inverts it, TSV pipes it. The first dogfood's 50 OFFBYs were 0/1 soup; after one cut of the knife the leftover is 401/400, suffix(2), and `.unknown`.
