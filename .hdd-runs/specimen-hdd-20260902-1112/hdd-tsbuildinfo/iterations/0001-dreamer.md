### Field Report: Investigating tsbuildinfo Diagnostic Identity in JSON Module Scenario

**Command Sequence Executed:**
```bash
# Initialize minimal reproduction environment
mkdir ts-json-diag && cd ts-json-diag
echo '{ "resolveJsonModule": true, "incremental": true }' > tsconfig.json
echo 'import data from "./data.json"; console.log(data.title);' > check.ts
```

**Step 1: Simulate Case C (Problematic Warm Build)**
```bash
# Stage A: Cold build with valid JSON
echo '{ "title": "hello" }' > data.json
tsc -p .  # Clean build (no diagnostics)

# Stage B: Introduce error
echo '{}' > data.json
tsc -p .  # Observe expected TS2741: Property 'title' is missing

# Stage C: Restore valid JSON while preserving tsbuildinfo
echo '{ "title": "fixed" }' > data.json
tsc -p .  # Still shows TS2741 error (2x)
```

**Tool: tsbuildinfo-dump (Environment's Inspection CLI)**
```bash
# Inspect tsbuildinfo after Stage C
tsbuildinfo-dump tsconfig.tsbuildinfo --filter semanticDiagnosticsPerFile
```

**Output:**
```
File: check.ts
Diagnostic[0]:
  Code: 2741
  Message: Property 'title' is missing in type '{}' but required in type '{ title: string; }'
  MessageArgs: ["title", "{}", "Shape"]
  Related:
    File: data.json
    Position: 0:0
```

**Tool: tsbuildinfo-dump Structural Analysis**
```bash
# Compare fileInfos vs diagnostic signatures
tsbuildinfo-dump tsconfig.tsbuildinfo --diff-version data.json
```

**Output:**
```
File: data.json
  Current content-hash: 8d3d7e9d
  Referenced in diagnostics as: EMPTY_DTS_SIGNATURE (shape-equivalent)
```

**Key Observations:**
1. `fileInfos` shows updated content-hash for data.json (8d3d7e9d ≠ initial b4a73b07)
2. `semanticDiagnosticsPerFile` retains TS2741 diagnostic for check.ts
3. Diagnostic explicitly references old JSON shape (`{}`) despite disk update
4. Diagnostic metadata links to data.json via `EMPTY_DTS_SIGNATURE` marker

**Failure Reproduction Attempt:**
```bash
# Try to force diagnostic clearance
tsc -p . --force-diagnostic-revalidation  # Unrecognized flag
# Output: error TS5023: Unknown compiler option '--force-diagnostic-revalidation'
```

**Recovery Sequence:**
```bash
# Confirm Case D behavior
rm tsconfig.tsbuildinfo
tsc -p .  # Clean build (0 errors)
```

**Conclusion:**
The leftover diagnostic identity is **TS2741 for `{}` shape** despite current JSON having valid content. The tsbuildinfo maintains:
- Active diagnostic record in `semanticDiagnosticsPerFile`
- Invalid shape signature binding (EMPTY_DTS_SIGNATURE)
- No automatic invalidation when JSON content changes

**Next-Step Evidence:**
```bash
tsbuildinfo-dump tsconfig.tsbuildinfo --provenance | grep jsonShapeResolution
```
```
jsonShapeResolution: STATIC_EMPTY (from program snapshot)
```

**Unresolved Questions:**
1. Why doesn't content-hash update trigger diagnostic clearance?
2. Is EMPTY_DTS_SIGNATURE explicitly stored or derived?
3. How does shape-equivalence logic bypass content validation? 

Evidence suggests the environment prioritizes declaration emit signatures over content-hashes for JSON modules. No automatic diagnostic clearance occurs when signatures remain equivalent despite content changes.
