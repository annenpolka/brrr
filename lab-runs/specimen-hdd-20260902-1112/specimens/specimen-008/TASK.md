# TASK

~70 Django tests assert a specific row order for querysets whose SQL has no ORDER BY. They pass on a freshly loaded PostgreSQL table (physical order ≈ insertion order) and fail later after updates/deletes reuse heap space, or when the planner chooses an index scan — with no change to Django or to the test.

The developer wants to see which assertions depend on an order the database did not promise.
