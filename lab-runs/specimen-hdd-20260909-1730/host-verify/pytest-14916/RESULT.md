# Host 実機 pytest#14916 rewrite introspection gaps

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public examples:

- `assert [1, 2, 3] == [1, 2, 4]`
- `assert f() == 100` with `f` returning 42

| pytest | rewrite | `--assert=plain` |
| --- | --- | --- |
| 8.4.1 | rc=1; `assert [1, 2, 3] == [1, 2, 4]` + index diff; `assert 42 == 100` / `where 42 = f()` | rc=1 both fail |
| 9.0.1 | same | same |
| 9.0.3 | same | same |
| 9.1.0 | same | same |
| 9.1.1 | same | same |

Does not match the PR's claimed messages (`elements never shown`; `where 42 = <function f at 0x...>()`). Lists and `f()` already introspect. No 8/9 delta.

Leftover `--tb=short`: still 2 failed (`[1, 2, 3] == [1, 2, 4]`; `42 == 100`) on 8.4.1–9.1.1. Traceback style does not hide the already-present introspection. No View/export.

Leftover `--lf`/`--ff`/`--nf`: still **2 failed** on 8.4.1–9.1.1. Leftover `--sw`: 1 failed interrupted (hides the later fail). No View.

Leftover `--maxfail=1`: seed 2 failed then `--maxfail=1` **1 failed** (hides the later fail). No View.
