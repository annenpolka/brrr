# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

~70 Django tests assert a specific row order for querysets whose SQL has no ORDER BY. They pass on a freshly loaded PostgreSQL table (physical order ≈ insertion order) and fail later after updates/deletes reuse heap space, or when the planner chooses an index scan — with no change to Django or to the test.

The developer wants to see which assertions depend on an order the database did not promise.

# OBSERVED

Public Django ticket 37255 / PR 21745.

- Assertions compare queryset results to a list with a fixed order.
- Generated SQL has no ORDER BY.
- Failures appear after heap reuse or planner index scans.
- Same tests, same Django revision, different storage layout → different result order.

# COMMANDS

Django test suite on PostgreSQL after updates/deletes that reuse heap pages. Not executed on the lab host.

django/tests/  (~70 tests asserting unordered queryset order)

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
