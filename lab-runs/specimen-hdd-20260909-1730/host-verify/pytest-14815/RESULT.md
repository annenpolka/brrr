# Host 実機 pytest#14815 subscript rewrite display

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public example: `assert {'a': 1, 'b': 2}['a'] == 99`. Changelog wants `where 1 = {'a': 1, 'b': 2}['a']`.

| pytest | rewrite |
| --- | --- |
| 8.4.1 | rc=1; `assert 1 == 99` (no `where` subscript line) |
| 9.0.1 | same |
| 9.0.3 | same |
| 9.1.0 | same |
| 9.1.1 | same |

Same as pytest#14448 first case. No 8/9 delta.

Leftover `--tb=short`: still `assert 1 == 99` (no `where` subscript line) on 8.4.1–9.1.1.

Leftover `--setup-show`: still `assert 1 == 99` (no `where` subscript line) on 8.4.1–9.1.1. No View/export.

Leftover `--assert=plain`: 1 failed, bare AssertionError (no changelog `where` line) on 8.4.1–9.1.1. No View.
