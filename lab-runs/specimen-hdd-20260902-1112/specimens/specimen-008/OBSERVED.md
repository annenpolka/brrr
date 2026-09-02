# OBSERVED

Public Django ticket 37255 / PR 21745.

- Assertions compare queryset results to a list with a fixed order.
- Generated SQL has no ORDER BY.
- Failures appear after heap reuse or planner index scans.
- Same tests, same Django revision, different storage layout → different result order.
