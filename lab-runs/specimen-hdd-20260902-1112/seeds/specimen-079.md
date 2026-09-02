CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

`helm template` of a chart whose default `values.yaml` is an empty map, plus a user values file that sets a key in that map to YAML null, drops the null key from `.Values`.

Chart `values.yaml`:

```
data: {}
```

User `values.yaml`:

```
data:
  foo: bar
  baz: ~
```

Template `templates/foo.yaml`:

```
data: {{.Values.data | quote}}
```

Helm v4.0.2 (`GitCommit: 94659f25033af6eb43fc186c24e6c07b1091800b`):

```
$ helm template chart --values values.yaml
---
# Source: foo/templates/foo.yaml
data: "map[foo:bar]"
```

Same files on helm v3.19.3 (`GitCommit: 0707f566a3f4ced24009ef14d67fe0ce69db4be9`):

```
data: "map[baz:<nil> foo:bar]"
```

If only the chart default is changed from `data: {}` to `data: ~`, helm v4.0.2 keeps `baz`:

```
data: "map[baz:<nil> foo:bar]"
```

The developer wants to know which identity of `baz` `.Values.data` actually contained after coalesce for each chart default (`{}` vs `~`): omitted key versus present-nil.

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

# COMMANDS

```
# chart/values.yaml: data: {}
# values.yaml:
#   data:
#     foo: bar
#     baz: ~

helm template chart --values values.yaml
# helm v4.0.2: data: "map[foo:bar]"
# helm v3.19.3: data: "map[baz:<nil> foo:bar]"

# chart/values.yaml edited to: data: ~
helm template chart --values values.yaml
# helm v4.0.2: data: "map[baz:<nil> foo:bar]"
```

Not executed on this lab host.

helm/helm
  pkg/chart/common/util/coalesce.go
  pkg/chart/common/util/coalesce_test.go

RELEVANT MATERIAL

### coalesce_tables_failing.go

# Reduced excerpt of coalesceTablesFullKey on failing_ref
# pkg/chart/common/util/coalesce.go

func coalesceTablesFullKey(printf printFn, dst, src map[string]interface{}, prefix string, merge bool) map[string]interface{} {
	if src == nil {
		return dst
	}
	if dst == nil {
		return src
	}
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
			if istable(dv) {
				coalesceTablesFullKey(printf, dv.(map[string]interface{}), val.(map[string]interface{}), fullkey, merge)
			}
		}
	}
	return dst
}

### coalesce_values_table_branch.go

# Reduced excerpt of coalesceValues on failing_ref
# pkg/chart/common/util/coalesce.go
# dest/user values override chart vc.

for key, val := range vc {
	if value, ok := v[key]; ok {
		if value == nil && !merge {
			delete(v, key)
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
	} else {
		v[key] = val
	}
}

### helm_template_split.txt

Chart values.yaml (case A):
  data: {}

Chart values.yaml (case B):
  data: ~

User values.yaml (both cases):
  data:
    foo: bar
    baz: ~

templates/foo.yaml:
  data: {{.Values.data | quote}}

helm v4.0.2 template, case A:
  data: "map[foo:bar]"

helm v3.19.3 template, case A:
  data: "map[baz:<nil> foo:bar]"

helm v4.0.2 template, case B:
  data: "map[baz:<nil> foo:bar]"

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
