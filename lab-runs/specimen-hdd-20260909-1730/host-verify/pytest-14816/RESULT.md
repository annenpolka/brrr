# Host 実機 pytest#14816 IfExp rewrite display

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public example: `assert (0 if True else 1) == 99`. Changelog wants `where 0 = (... if True else ...)`.

| pytest | rewrite | `--assert=plain` |
| --- | --- | --- |
| 8.4.1 | rc=1; `assert 0 == 99` (no `where` IfExp line) | rc=1 bare AssertionError |
| 9.0.1 | same | same |
| 9.0.3 | same | same |
| 9.1.0 | same | same |
| 9.1.1 | same | same |

Same as pytest#14448 second case. No 8/9 delta.

Leftover `--tb=short`: still `assert 0 == 99` (no `where` IfExp line) on 8.4.1–9.1.1.

Leftover `--collect-only`: **1 collected** on 8.4.1–9.1.1. The missing `where` line is execute rewrite, not collect. No View/export.

Leftover `--assert=plain`: 1 failed, bare AssertionError (no changelog `where` line) on 8.4.1–9.1.1. No View.
