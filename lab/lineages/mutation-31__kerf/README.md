# kerf

Given a constructed value, emit the cuts it sits on.

`cusp` asked the tree: *which of your own literals sit on your predicates?* `kerf` flips the join. The value is the query. The tree is a haystack of numeric and enum bounds. Stdout is the cuts — stream TSV, one row per sit.

| status | meaning |
| --- | --- |
| **HIT** | the value *is* the compared-to (`401` on `statusCode == 401`) |
| **BRINK** | exclusive or inclusive bound (`3` on `n > 3`) |
| **OFFBY** | one step from equality or a range endpoint (`400` on `== 401`) |
| **SENTINEL** | `0` / `-1` / `"unknown"` on the excluded or domain edge |
| **NEIGHBOR** | adjacent enum variant (`running` on `phase === "done"`) |

Not string-edit distance. Not coverage. Not “is this comparison silly?”. A test runner, a log, a fixture — hand it the value, get the predicates whose knife-edge that value occupies.

Default: TSV, no header, no summary. Exit `0` if any cut, `1` if none, `2` usage. `--report-only` forces `0`. `--scan` is the ancestor corpus join (exit `1` if the tree sits on itself).

## Run

```bash
python3 bin/kerf 3 path/to/repo
python3 bin/kerf 400 Engine/
printf '3\n401\nunknown\n' | python3 bin/kerf src/
python3 bin/kerf --header 401 src/ | column -t -s $'\t'
python3 bin/kerf statusCode=400 src/
python3 bin/kerf --lhs statusCode 400 src/
python3 bin/kerf --scan --format human src/
```

```bash
./demo.sh
```

## Examples

`3` is the last miss of `n > 3`:

```text
$ python3 bin/kerf 3 fixtures
3	BRINK	excl.go	4	n	>	3	exclusive	n
3	BRINK	incl.go	4	n	>=	4	exclusive	n
```

`401` *is* the cut — ancestor `--probe` stayed silent here; invert reports HIT:

```text
$ python3 bin/kerf 401 fixtures
401	HIT	offby.swift	2	statusCode	==	401	exact	statusCode
```

`400` is one step away, the test value that never fires the 401 gate:

```text
$ python3 bin/kerf 400 fixtures
400	OFFBY	offby.swift	2	statusCode	==	401	off-by-one	statusCode
```

Field-qualified values (`statusCode=400`, `n=0`) bind the probe to a lhs. Bare `0`/`1`/`-1` do not HIT `== 0`; they still sit on sentinel bounds (`n > 0`, `err != -1`). HTTP 100–599 only OFFBY against HTTP-ish fields, so `401` does not sit on `graphemes == 400`.

Columns: `value status path line lhs op rhs reason field`. Pipe with `awk`, `join`, `comm`.

## Why this is a Unix primitive

`grep` takes a pattern, emits matching lines. `kerf` takes a value, emits matching *predicate cuts*. `--scan` is `cusp`. The default is the inverse join a test runner can stream:

```bash
printf '400\n401\n403\n' | kerf Engine/ | awk -F'\t' '$2=="OFFBY"'
```
