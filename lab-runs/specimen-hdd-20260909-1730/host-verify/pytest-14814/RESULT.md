# Host 実機 pytest#14814 walrus/starred rewrite operands

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public examples:

- `assert collect((x := 1), identity(x := 2)) == (1, 2)`
- `items = [1]; assert collect(*items, identity(items := [9])) == (1, [9])`

| pytest | rewrite | `--assert=plain` |
| --- | --- | --- |
| 8.4.1 | rc=1; walrus-tuple 1 pass; starred ` (9, [9]) == (1, [9])` | rc=0 2 passed |
| 9.0.1 | same | same |
| 9.0.3 | same | same |
| 9.1.0 | same | same |
| 9.1.1 | same | same |

Native Python 3.14 (no pytest): both asserts pass. Parenthesized walrus-tuple does not reproduce the PR's `(2, 2)` rewrite claim. Starred operand does.

Bare `collect(x := 1, identity(x := 2))`: rewrite, `--assert=plain`, and native all pass 8.4.1–9.1.1.

Leftover `--tb=short`: still 1 failed / 2 passed; starred ` (9, [9]) == (1, [9])` on 8.4.1–9.1.1. Traceback style does not change the rewrite. No View/export.

Leftover `--collect-only`: **3 collected** on 8.4.1–9.1.1. Starred/walrus rewrite is execute, not collect. No View/export.

Leftover `--setup-show`: still 1 failed 2 passed (starred rewrite) on 8.4.1–9.1.1. `--setup-show` does not change rewrite operands. No View.

Leftover `--assert=plain`: **3 passed** on 8.4.1–9.1.1 (starred rewrite fail is assertion-rewrite only). No View.
