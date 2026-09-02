# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
