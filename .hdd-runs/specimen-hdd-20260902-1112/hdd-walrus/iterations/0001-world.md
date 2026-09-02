# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A pytest assertion uses assignment expressions (`:=`) together with a function that has a visible side effect (append to a list).

The developer wants to know what values the assertion actually compared, and how many times the side-effecting function ran, because the failure message and the test's own counters disagree.

Do not assume a root cause. Use the installed unfamiliar CLI on this problem.

# OBSERVED

Public issue pytest-dev/pytest#14445 / PR 14447 (failing world, pytest `main` around the issue):

Snippet:

```python
def side_effect():
    return True

def test_walrus_boolop():
    assert (x := side_effect()) and (x := False)
```

Reported failure explanation on the failing revision:

```
E       assert (False and False)
```

The first call as written returns True. The explanation shows False for that operand.

A second family of cases: an operand evaluated *before* a later assignment-expression is reported with the *post*-assignment value, not the value that operand actually saw. Example shape:

```python
assert value != identity(value := value.lower())
```

A third family: a follow-up `assert a is None` after a walrus in the same module can pass when asked only via process exit code, and fail when asked via returned values from an in-process rewrite check.

Side-effect counters in related cases increment more than once for a source expression that a plain Python interpreter evaluates once.

# COMMANDS

```
pytest testing/test_assertrewrite.py -k walrus --tb=short
```

Exact in-tree names on the failing ref are in the public issue. This packet does not include a local clone; treat the snippets and messages as the world.

pytest-dev/pytest
  src/_pytest/assertion/rewrite.py
  testing/test_assertrewrite.py
  testing/test_assertrewrite_coverage.py

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
