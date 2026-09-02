CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Home Assistant pytest collection: a parent directory appears more than once in the argument list. Fixtures registered from conftest are “not found” for tests collected after unrelated paths. Order of CLI path arguments changes whether fixtures resolve.

The developer wants to know whether the same directory is still the same collection object, and which fixture definitions are bound to which object identities.

# OBSERVED

Public issue pytest-dev/pytest#14635 / PR 14645.

Symptom: fixture closure computation fails for tests collected after unrelated paths. Conftest fixtures were registered against a Directory node that is no longer the node later collection looks up.

A regression test name on the PR: `test_fixture_closure_order_independence_with_parametrize`.

`--keep-duplicates file.py file.py` is still expected to collect the file twice (that behavior is separate).

# COMMANDS

```
pytest path/a path/b path/a --collect-only
```
Order of overlapping directory arguments changes fixture resolution on the failing revision.

<repo>/conftest.py
<repo>/tests/...
CLI args include a parent directory more than once

RELEVANT MATERIAL

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
