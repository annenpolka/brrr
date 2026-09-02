#!/usr/bin/env python3
"""Emit sealed REAL_SOURCE_BACKED packet specimen-079 (helm empty-map default vs user null)."""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index

SPEC_ID = "specimen-079"


packet = dict(
    id=SPEC_ID,
    manifest="""
id: specimen-079
kind: REAL_SOURCE_BACKED
repository: helm/helm
failing_ref: e685076bc0435eb521a824ec592a4d86384209be
fixed_ref: 5b78ee8dff513f402aba593eb7e6b286714518fd
source_issue: https://github.com/helm/helm/issues/31643
source_pr: https://github.com/helm/helm/pull/31644
mechanism_tags:
  - empty-map-default
  - user-null-omitted
  - coalesce-nil-identity
ecosystem: helm
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7500
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

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
""",
    observed="""# OBSERVED

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
""",
    commands="""# COMMANDS

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
""",
    tree="""helm/helm
  pkg/chart/common/util/coalesce.go
  pkg/chart/common/util/coalesce_test.go
""",
    source="""repository: helm/helm
pr: https://github.com/helm/helm/pull/31644
issue: https://github.com/helm/helm/issues/31643
failing_ref (merge first parent): e685076bc0435eb521a824ec592a4d86384209be
fixed_ref (merge commit): 5b78ee8dff513f402aba593eb7e6b286714518fd
head_sha: 0298b2ffd0823eead74c75e1b890b0bf47d0db62
merged_at: 2026-01-31T13:03:56Z
merged_by: banjoh
changed_files: pkg/chart/common/util/coalesce.go, pkg/chart/common/util/coalesce_test.go
reporter_failing_release: helm v4.0.2 GitCommit 94659f25033af6eb43fc186c24e6c07b1091800b
reporter_v3_contrast: helm v3.19.3 GitCommit 0707f566a3f4ced24009ef14d67fe0ce69db4be9
pr_title: fix(values): preserve nil values when chart default is empty map
""",
    answer_key="""KNOWN FIX (sealed): helm/helm PR 31644 merge 5b78ee8dff513f402aba593eb7e6b286714518fd.

coalesceTablesFullKey copied dest nils into src, then deleted every dest key that was nil. An empty-map chart default therefore dropped user `baz: ~` as an omitempty-style absence, so `helm template` printed `map[foo:bar]` instead of `map[baz:<nil> foo:bar]`. Chart default `data: ~` skipped the table merge and kept present-nil. Repair: snapshot which src keys were originally non-nil, and delete dest's nil only when the user is nullifying a chart default that actually existed (`srcOriginalNonNil[key]`).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (chart default `data: {}` drops user `baz: ~` from `.Values.data`; chart default `data: ~` keeps `baz:<nil>`; v4 vs v3 quote of the same files)
reproducibility: source-backed issue/PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — same user null is omitted or present-nil depending on whether the chart default was an empty map or YAML null
ecosystem: helm / go templates
mechanism_family: empty-map-default, user-null-omitted, coalesce-nil-identity

Packet is the failing world only. Do not assume a root cause.
""",
    files={
        "coalesce_tables_failing.go": """# Reduced excerpt of coalesceTablesFullKey on failing_ref
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
""",
        "coalesce_values_table_branch.go": """# Reduced excerpt of coalesceValues on failing_ref
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
""",
        "helm_template_split.txt": """Chart values.yaml (case A):
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
""",
    },
)


if __name__ == "__main__":
    dest = SPECIMENS / SPEC_ID
    if dest.exists():
        raise SystemExit(f"{dest} already exists; refusing to overwrite")
    path = emit(packet)
    seed = write_seed(SPECIMENS / SPEC_ID)
    print(path)
    print(seed)
    update_index()
