# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Helm Values Coalescence Behavior

**Operational Context:**  
Working within Helm CLI environment (v3.19.3 and v4.0.2) to diagnose coalescence behavior of `null` keys in values files. Focus on concrete command execution and output observation per provided fixtures.

---

### Step 1: Reproduce Observed Behavior  
*Executed with Helm v4.0.2:*  
```bash
# Case A: Chart values.yaml = {}
$ cat chart/values.yaml
data: {}

$ helm template chart --values values.yaml
---
# Source: chart/templates/foo.yaml
data: "map[foo:bar]"

# Case B: Chart values.yaml = ~
$ sed -i 's/data: {}/data: ~/' chart/values.yaml  # Modify default

$ helm template chart --values values.yaml
---
# Source: chart/templates/foo.yaml
data: "map[baz:<nil> foo:bar]"
```

*Executed with Helm v3.19.3 (same chart/user files):*  
```bash
# Case A: Chart values.yaml = {}
$ helm template chart --values values.yaml
---
# Source: chart/templates/foo.yaml
data: "map[baz:<nil> foo:bar]"
```

**Observation:**  
- v4.0.2 drops `baz` when chart default is `{}` but preserves it as `<nil>` when default is `~`.  
- v3.19.3 preserves `baz` as `<nil>` regardless of chart default.  

---

### Step 2: Probe Value Identity in Templates  
*Modified template to inspect key existence:*  
```yaml
# templates/inspect.yaml
baz_exists: {{ hasKey .Values.data "baz" | quote }}
baz_value: {{ if hasKey .Values.data "baz" }}{{ .Values.data.baz | typeOf }}{{ else }}ABSENT{{ end }}
```

*Executed with v4.0.2 (Case A - chart default = {}):*  
```bash
$ helm template chart --values values.yaml
---
# Source: chart/templates/inspect.yaml
baz_exists: "false"
baz_value: ABSENT
```

*Executed with v4.0.2 (Case B - chart default = ~):*  
```bash
$ helm template chart --values values.yaml
---
# Source: chart/templates/inspect.yaml
baz_exists: "true"
baz_value: <nil>
```

**Observation:**  
- When `baz` is omitted (Case A/v4), `hasKey` returns `false`.  
- When `baz` is present as null (Case B/v4), its type is reported as `<nil>`.  

---

### Step 3: Test Value Coalescence in Go Template Logic  
*Added explicit nil check:*  
```yaml
# templates/coalesce.yaml
baz_value: {{ if .Values.data.baz }}NOT_NULL{{ else }}{{ if hasKey .Values.data "baz" }}NULL{{ else }}ABSENT{{ end }}{{ end }}
```

*Executed with v4.0.2 (Case A):*  
```bash
$ helm template chart --values values.yaml
---
# Source: chart/templates/coalesce.yaml
baz_value: ABSENT
```

*Executed with v4.0.2 (Case B):*  
```bash
$ helm template chart --values values.yaml
---
# Source: chart/templates/coalesce.yaml
baz_value: NULL
```

**Observation:**  
- `if .Values.data.baz` fails for both absent keys and null values.  
- Combining `hasKey` and explicit null checks distinguishes:  
  - `ABSENT`: Key removed during coalescence  
  - `NULL`: Key present with null value  

---

### Step 4: Verify Workaround Consistency  
*Tested across versions with unified template:*  
```yaml
# Unified template (templates/diagnostic.yaml)
{{- $data := .Values.data }}
result: |
  EXISTS: {{ hasKey $data "baz" }}
  EXPLICIT_NULL: {{ and (hasKey $data "baz") (eq $data.baz nil) }}
```

*Output v4.0.2 (Case A):*  
```
result: |
  EXISTS: false
  EXPLICIT_NULL: false
```

*Output v4.0.2 (Case B):*  
```
result: |
  EXISTS: true
  EXPLICIT_NULL: true
```

*Output v3.19.3 (Case A):*  
```
result: |
  EXISTS: true
  EXPLICIT_NULL: true
```

**Conclusion:**  
- **Absent key:** `hasKey` returns `false` (v4.0.2 Case A).  
- **Present-null:** `hasKey` returns `true` AND `eq .Value nil` returns `true` (v4.0.2 Case B, v3.19.3 Case A).  
- Workaround template logic reliably distinguishes both states across tested versions.  

---

### Artifacts Generated:  
1. `templates/inspect.yaml` - Key existence probe  
2. `templates/coalesce.yaml` - Null/absent differentiation logic  
3. `templates/diagnostic.yaml` - Unified test template  

**Final State:**  
Helm environment retains modified chart files (`values.yaml` and templates) for continued diagnosis. No external tools or speculative changes introduced.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
