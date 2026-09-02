# OBSERVED

Public issue pytest-dev/pytest#14635 / PR 14645.

Symptom: fixture closure computation fails for tests collected after unrelated paths. Conftest fixtures were registered against a Directory node that is no longer the node later collection looks up.

A regression test name on the PR: `test_fixture_closure_order_independence_with_parametrize`.

`--keep-duplicates file.py file.py` is still expected to collect the file twice (that behavior is separate).
