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
