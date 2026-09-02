# OBSERVED

Public helm/helm issue 31643 / PR 31644. Failing world in `pkg/chart/common/util/coalesce.go` around merge parent `e685076bc0435eb521a824ec592a4d86384209be` (also helm v4.0.2 `94659f25033af6eb43fc186c24e6c07b1091800b`).

`CoalesceValues` copies user vals then calls `coalesce(..., merge=false)`. `MergeValues` uses `merge=true` and is documented as keeping nulls. `helm template` uses coalesce.

When the chart default for a key is a table and the user value is also a table, `coalesceValues` does not delete the user table; it calls `coalesceTablesFullKey` with dest = user table, src = chart table:

```
} else if dest, ok := value.(map[string]interface{}); ok {
    src, ok := val.(map[string]interface{})
    if !ok {
        if val != nil {
            printf("warning: skipped value for %s.%s: Not a table.", subPrefix, key)
        }
    } else {
        merge := childChartMergeTrue(c, key, merge)
        coalesceTablesFullKey(printf, dest, src, concatPrefix(subPrefix, key), merge)
    }
}
```

Chart default `data: ~` makes `val` nil, so `src, ok := val.(map[string]interface{})` is false and the user table is left as-is (`foo`, `baz:<nil>`). Chart default `data: {}` is a table, so the nested merge runs.

`coalesceTablesFullKey` on that failing revision:

```
for key, val := range dst {
    if val == nil {
        src[key] = nil
    }
}
for key, val := range src {
    fullkey := concatPrefix(prefix, key)
    if dv, ok := dst[key]; ok && !merge && dv == nil {
        delete(dst, key)
    } else if !ok {
        dst[key] = val
    } else if istable(val) {
        ...
    }
}
```

Public reporter chart `foo` / user file as above. `helm template` quote of `.Values.data`:

- v4 + chart `data: {}` → `map[foo:bar]` (`baz` absent)
- v3 + chart `data: {}` → `map[baz:<nil> foo:bar]`
- v4 + chart `data: ~` → `map[baz:<nil> foo:bar]`

This packet does not include a local clone; treat the snippets and template split as the world. Do not execute untrusted checkouts on the host.
