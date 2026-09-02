# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A PEP 661 sentinel is passed as `dict.get`'s default. mypy infers the result as `str | sentinel` (the shared class), not `str | Unknown` (the value).

```
from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
```

```
test.py:8: error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]
```

A sibling case: `ALIAS = MISSING` then `assert_type(ALIAS, sentinel)` passes on the failing revision, and `func(ALIAS)` is rejected as type `Sentinel` rather than `MISSING`.

The developer wants to know which identity the checker kept after substituting the TypeVar in `dict.get`, and where the literal attached to `Unknown` went.

# OBSERVED

Public python/mypy#21866 / PR 21888. Failing world around `mypy/expandtype.py` `visit_type_var` and `test-data/unit/check-sentinels.test`.

`dict.get` is overloaded with a TypeVar default. Substituting `Unknown` (an `Instance` whose `last_known_value` is the sentinel literal) hits:

```
repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
```

After that copy, the type prints as the fallback class name `sentinel` / `Sentinel`, not `Unknown`.

In-tree `testSentinelReassignmentIsNotTypeAlias` on the failing revision:

```
MISSING = sentinel("MISSING")
ALIAS = MISSING
assert_type(ALIAS, sentinel)
func(ALIAS)  # E: Argument 1 to "func" has incompatible type "Sentinel"; expected "int | MISSING"
```

`reveal_type` on a bare sentinel value is supposed to show the value's name (e.g. `Unknown?`), while the class `sentinel` remains the type of the constructor.

This packet does not include a local clone; treat the snippets and error as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
mypy test.py
# in-tree:
pytest mypy/test/testcheck.py -k sentinels
```

Not executed on this lab host.

python/mypy
  mypy/expandtype.py
  mypy/erasetype.py
  mypy/messages.py
  test-data/unit/check-sentinels.test

RELEVANT MATERIAL

### dict_get_sentinel.py

from typing import assert_type
from typing_extensions import sentinel

Unknown = sentinel("Unknown")

def func(d: dict[str, str]) -> None:
    var = d.get("key", Unknown)
    assert_type(var, str | Unknown)
    # failing revision:
    # error: Expression is of type "str | sentinel", not "str | Unknown"  [assert-type]

### visit_type_var_failing.py

# Reduced excerpt of TypeExpander.visit_type_var on failing_ref
# mypy/expandtype.py

repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
return repl

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
