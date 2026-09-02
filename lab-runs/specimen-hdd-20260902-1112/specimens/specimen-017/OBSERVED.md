# OBSERVED

Owned fixture files/pair_extras.py. Pair A PASS / pair B FAIL. Same extras map, same requested extra. Only observed difference: whether `requires` still contains the extra’s dependency.

Grounded in the same extra-request mismatch family as python-poetry/poetry#10314: extras map lists B, one object still has B in requires, the other does not.

## Captured host execution (stdlib, no third-party packages)
```
pair_A_fresh_requires recognized ['B'] resolved_extra_deps ['B'] PASS
pair_B_pruned_requires recognized ['B'] resolved_extra_deps [] FAIL
only_axis requires_contains_extra_dep
request A[foo]
```
