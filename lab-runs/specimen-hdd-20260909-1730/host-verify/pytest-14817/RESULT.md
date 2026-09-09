# Host 実機 pytest#14817 method-call rewrite display

Not Dreamer-facing. HOLD no View. Do not apply the PR.

Public example from the changelog (desired after): `where 42 = Obj().compute()`.

| pytest | rewrite | `--assert=plain` |
| --- | --- | --- |
| 8.4.1 | rc=1; `assert 42 == 100`; `where 42 = compute()`; `where compute = <Obj>.compute`; `where <Obj> = Obj()` | rc=1 bare AssertionError |
| 9.0.1 | same bound-method intermediates | same |
| 9.0.3 | same | same |
| 9.1.0 | same | same |
| 9.1.1 | same | same |

Instance leftover `obj = Obj(); assert obj.compute() == 100` on 8.4.1/9.1.0/9.1.1: still `where 42 = compute()` + `where compute = <Obj>.compute` (no `obj.compute()` single line).

Leftover `--tb=short` method and instance: still bound-method intermediates (`where 42 = compute()` / `<Obj>.compute`) on 8.4.1–9.1.1, not changelog `Obj().compute()`. `--tb=short` does not collapse the rewrite.

Native Python 3.14: AssertionError, no pytest `where` tree. Host matches the PR's "before" (bound method as a separate intermediate), not the single-line `Obj().compute()`. No 8/9 delta. No View/export.

Leftover `--setup-show test_method.py`: still bound-method intermediates (`where 42 = compute()` / `<Obj>.compute` / `Obj()`) on 8.4.1–9.1.1. `--setup-show` does not change rewrite display. No View.

Leftover `--assert=plain test_method.py`: 1 failed, bare AssertionError (no bound-method `where` intermediates) on 8.4.1–9.1.1. Plain assert drops the rewrite display. No View.
