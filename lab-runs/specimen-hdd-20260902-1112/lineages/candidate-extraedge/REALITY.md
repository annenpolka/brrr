# Reality assessment

classification: USEFUL_COMPOSITION

Core operation: join declared extras to extra-edge targets on two
records of the same package version via an extras table. A miss is a
mapped target absent from resolved.

Nearest: read pyproject extras and the lock. Delta: one query names
which declared extra missed its extra-edge vs later attach. No poetry.
Set-difference of extra names against resolved package names is not
the operation.
