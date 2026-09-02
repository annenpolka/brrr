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
