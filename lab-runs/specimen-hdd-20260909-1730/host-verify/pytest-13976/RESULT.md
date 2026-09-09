# Host 実機 pytest#13976 comment fixture-params override

Not Dreamer-facing. HOLD no View. PR not applied. Related #14591.

Public comment mini: fixture `params=["a","b","c"]` plus `@pytest.mark.parametrize("target", ["a","b"], indirect=True)`.

| pytest | collect | run |
| --- | --- | --- |
| 8.4.1 | rc=0; `test_foo[a]` `test_foo[b]` | rc=0 2 passed |
| 9.0.1 | same | same |
| 9.0.3 | same | same |
| **9.1.0** | **rc=2; duplicate parametrization of `target`** | **rc=2 same ERROR** |
| 9.1.1 | rc=0; `test_foo[a]` `test_foo[b]` | rc=0 2 passed |

Matches the commenter: worked on 9.0.3, broke on 9.1.0, restored on 9.1.1. Same family as #14591.

Leftover: fixture in `conftest.py` (commenter's layout) is the **same** 9.1.0-only duplicate.

Leftover `pytest_generate_tests` workaround (paramless fixture + generate_tests for default, skip if already parametrized): collect/run **5 passed** (`test_foo[a/b]` + `test_default[a/b/c]`) on 8.4.1/9.0.1/9.0.3/**9.1.0**/9.1.1. Workaround works on 9.1.0. Not applied as a product.

Leftover `ids=["A","B"]` on the parametrize: still duplicate `target` on 9.1.0; 8.4.1/9.0.3/9.1.1 collect `test_foo[A]` `test_foo[B]`. ids= does not rescue 9.1.0.

Leftover `pytest.param("a")` / `pytest.param("b")`: still duplicate on 9.1.0; 8.4.1/9.0.3/9.1.1 collect `test_foo[a]` `test_foo[b]`.

Leftover `--setup-show test_override.py`: same split (8.4.1–9.0.3/9.1.1 SETUP `target['a']`/`target['b']` 2 passed; 9.1.0 duplicate at collect).

Leftover `--tb=short test_override.py`: same split (8.4.1–9.0.3/9.1.1 2 passed; 9.1.0 collection `duplicate parametrization of 'target'`). `--tb=short` does not change collect errors. No View/export.




Leftover `--setup-plan test_override.py`: 8.4.1/9.0.1/9.0.3/9.1.1 2 items, SETUP `target['a']`/`['b']`. **9.1.0** rc=2 collect ERROR `duplicate parametrization of 'target'` (plan does not run). Same 9.1.0-only collect miss as execute. No View.

Leftover `--lf` explicit `test_override.py`: 8.4.1/9.1.1 2 pass. **9.1.0** collect duplicate; `--lf` still collect duplicate. Bare `--lf` without a file arg walks leftover nested `gen/`/`conftest_layout/` copies (collection collisions). Collect-error is not last-failed. No View.
