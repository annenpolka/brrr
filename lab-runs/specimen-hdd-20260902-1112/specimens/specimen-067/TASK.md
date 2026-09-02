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
