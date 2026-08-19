# cusp

Which of this repository's own constructed values sit on a branch cut?

`cusp` scans source for **gates** (comparisons against a bound: `retries > 3`, `phase == "done"`, `status != "unknown"`, `(200..<300).contains(code)`) and **producers** (literals that construct a value). It reports only the brink:

| status | meaning |
| --- | --- |
| **BRINK** | a corpus number sits on an exclusive or inclusive bound |
| **OFFBY** | same-field equality is one step away (`401` vs constructed `400`) |
| **SENTINEL** | `0` / `-1` / `"unknown"` / `"none"` sits on the excluded or domain edge |
| **NEIGHBOR** | a constructed enum variant is adjacent to the compared-to set |

This is not string-edit distance. Typos, case folds, and `has_more`/`hasMore` inflections are out of scope. It is not dead-code detection and not coverage. The question is: *given the values this tree already writes down, which predicates have a constructed value sitting on the cut?*

Default report is those four statuses. Exit `1` if any appear, `0` if clean, `2` on usage/IO. `--report-only` forces `0`.

## Run

```bash
python3 bin/cusp path/to/repo
python3 bin/cusp --offby --brink src tests
python3 bin/cusp --probe 3 src
printf '401\nunknown\n' | python3 bin/cusp --probe - src
python3 bin/cusp --format tsv src | cut -f1,2,3,6,10
python3 bin/cusp --lhs statusCode src
```

```bash
./demo.sh
```

## Examples

Exclusive bound — the last miss is constructed:

```text
BRINK      excl.go:4  n > 3
           exclusive bound; 3 is constructed (last miss)
           CUT    3  excl.go:8  (exclusive)
```

Inclusive bound — the first hit is constructed:

```text
BRINK      incl.go:4  n >= 4
           inclusive bound; 4 is constructed (first/last hit)
           CUT    4  incl.go:8  (inclusive)
```

Off-by-one on the same field:

```text
OFFBY      offby.swift:2  statusCode == 401
           same-field neighbor is off by one from the cut
           CUT    400  offby.swift:9  (off-by-one field=statusCode)
```

The inverse join — a value in, the cuts it sits on out:

```bash
$ python3 bin/cusp --probe 3 fixtures
BRINK      excl.go:4  n > 3
```

## Why this is a Unix primitive

`comm` compares two sorted files. `cusp` compares two extracted columns — *predicates* vs *constructed literals* — and keeps only the rows that sit on the cut. `--probe` inverts the join. `--format tsv` is the pipe form.
