# Host 実機 pytest#14448

Not Dreamer-facing. HOLD (rewrite display / PR). No View. Do not apply the PR.

Public examples from the PR description:

- `assert {'a': 1, 'b': 2}['a'] == 99`
- `assert (0 if True else 1) == 99`

| pytest | rc | messages |
| --- | --- | --- |
| 8.4.1 | 1 | `assert 1 == 99`; `assert 0 == 99` |
| 9.0.1 | 1 | same |
| 9.0.3 | 1 | same |
| 9.1.0 | 1 | same |
| 9.1.1 | 1 | same |

No `where 1 = {'a': 1, 'b': 2}['a']` (or IfExp) line on any version. Matches the PR's "before" claim. No 8/9 delta.

Leftover `--tb=short`: still `assert 1 == 99` / `assert 0 == 99` (no `where` line) on 8.4.1–9.1.1. Leftover `--assert=plain`: bare AssertionError both tests. Same as #14815/#14816.

Leftover `--setup-show`: still 2 fail, no changelog `where` subscript/IfExp line on 8.4.1–9.1.1. No View/export. PR stays 正解 off Dreamer.

Leftover `--tb=native`: still 2 failed; no changelog `where` line on 8.4.1–9.1.1. Native traceback does not add `where`. No View/export.
