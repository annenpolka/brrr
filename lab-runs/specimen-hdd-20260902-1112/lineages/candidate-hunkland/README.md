# hunkland

Compare where a patch insert landed with the line the hunk header named.

A unified-diff empty old-range (`@@ -2,0 +3 @@`) names new-file line 3. An
applier can insert at the 1-based old start instead and still exit 0. `diff`
plus `echo $?` still looks like a clean apply. This command prints `land`
versus `header`.

This is a text fixture, not pnpm and not git apply.

## Usage

```
hunkland ORIG RESULT --hunk '@@ -2,0 +3 @@' [--apply-exit N]
hunkland ORIG --applier PATH --hunk '@@ -2,0 +3 @@' [--insert TEXT]
```

| argument | meaning |
| --- | --- |
| `ORIG` | file before the insert |
| `RESULT` | file after the apply |
| `--hunk` | unified-diff hunk header |
| `--applier PATH` | Python module exposing `apply_hunk(text, old_start, old_count, insert)` |
| `--insert TEXT` | inserted text for `--applier` (default `inserted`) |
| `--apply-exit N` | apply process exit (default 0) |

Pass `RESULT` or `--applier`, not both.

## Output

Tab-separated rows.

```
header	3
header_line	second
land	2
land_line	inserted
apply_exit	0
match	no
verdict	mis-indexed
```

| row | meaning |
| --- | --- |
| `header` | new-file line named by `+N` in the hunk |
| `header_line` | text currently at that line in the result |
| `land` | 1-based line of the first inserted line in the result |
| `land_line` | text at `land` |
| `apply_exit` | apply process exit (`0` can still be `match no`) |
| `match` | `yes` when land equals header |
| `verdict` | `mis-indexed`, `aligned`, `no-insert`, or `apply-failed` |

`verdict mis-indexed` is apply exit 0 with land ≠ header.

## Example (specimen-020)

orig `first\nsecond\nthird\n`, hunk `@@ -2,0 +3 @@`, owned `apply_hunk`:

```
hunkland orig.txt --applier files/patch_insert.py --hunk '@@ -2,0 +3 @@'
```

`header` is 3 (`second`). `land` is 2 (`inserted`). `apply_exit` is 0.
`match` is `no`. `verdict` is `mis-indexed`.

An aligned result (`first\nsecond\ninserted\nthird\n`) is `land 3`,
`match yes`, `verdict aligned`.

## Boundary

Does not rebuild an installer or repair the applier. `land` is the first
inserted (or replaced) line; deletions are not named. `--applier` must
expose `apply_hunk`.
