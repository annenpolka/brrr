# Reality assessment

classification: USEFUL_COMPOSITION

Core operation: compile two records to JSON, ingest an extra → extra-edge
graph, attach resolved nodes, walk declared extras. A miss is a mapped
target absent from resolved.

Nearest: read pyproject extras and the lock. Delta: one query names
which declared extra missed its extra-edge vs later attach. No poetry.
Set-difference of extra names against resolved package names is not
the operation.
