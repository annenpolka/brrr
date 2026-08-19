# nigh

How close does this repository's own vocabulary come to each branch cut?

`nigh` scans source and fixtures for **gates** (comparisons against literals: `kind == "beam"`, `retries > 3`) and **producers** (literals that construct a value rather than test it). It reports the distance field:

| status | meaning |
| --- | --- |
| **CLOSED** | the compared-to value is never constructed in-repo |
| **NIGH** | no exact producer, but a near-miss (typo, case, inflection, affix) |
| **BRINK** | a corpus number sits on an inequality cut (`--brink`) |
| **ONE-SIDED** | corpus values only ever take one side (`--one-sided`) |
| **BALANCED** | both sides exist (`--all`) |

This is not dead-code detection (the branch is syntactically live) and not coverage (nothing is executed). It answers a different question: *given the values this program already talks about, which cuts does it never touch, and which ones does it graze?*

Default report is **CLOSED** and **NIGH**. Exit `1` if either appears, `0` if clean, `2` on usage/IO. `--report-only` forces `0`.

## Run

```bash
python3 bin/nigh path/to/repo
python3 bin/nigh --nigh --closed src tests
python3 bin/nigh --probe beam src
printf 'success\nSuccess\n' | python3 bin/nigh --probe - src
python3 bin/nigh --format tsv src | cut -f1,2,3,6
python3 bin/nigh --lhs kind src          # only this discriminant
```

```bash
./demo.sh
```

## Examples

Typo and inflection — the cut is never constructed, but the tree almost says it:

```text
NIGH       nigh_typo.py:2  status == 'success'
           NIGH   'Success'  nigh_typo.py:7  (case)
           NIGH   'sucess'   nigh_typo.py:7  (typo d=1)

NIGH       nigh_inflect.ts:2  flag === 'has_more'
           NIGH   'hasMore'  nigh_inflect.ts:9  (inflection)
```

A family member that is switched on but never built:

```text
CLOSED     family.ts:2  action.kind === 'action.never-built'
           family 'action.resolved-beam', 'action.resolved-radial', ...
```

A number sitting on the closed side of a door (`--brink`):

```text
BRINK      brink.go:4  n > 3
           HIT    8
           BRINK  3
```

The inverse join — a value in, gates out:

```bash
$ python3 bin/nigh --probe success fixtures
HIT        nigh_typo.py:2  status == 'success'
```

## Why this is a Unix primitive

`comm` compares two sorted files. `nigh` compares two extracted columns of a repository — *predicates* vs *constructed literals* — with a distance, not a boolean. `--probe` inverts the join. `--format tsv` is the pipe form.
