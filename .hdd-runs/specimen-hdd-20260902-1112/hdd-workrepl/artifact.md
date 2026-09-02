### Field Report: Investigating `go work sync` Behavior in Replace Skew Scenario

**Operational Context**:  
Working within a Go toolchain environment (revision `a2214422293d2c26ad389050f25460b3f2f00825`). The workspace fixture is pre-configured with:
- `go.work` declaring `use ./a ./b`
- Module `a` contains a replace directive: `replace example.com/syncreplace v1.1.0 => v1.0.0`
- Module `b` has no replace directives
- Dependency chain:  
  `syncreplace v1.0.0` → `rsc.io/quote v1.0.0`  
  `syncreplace v1.1.0` → `rsc.io/quote v1.1.0`

**Objective**:  
Determine which version of `rsc.io/quote` persists in `b/go.mod` after running `go work sync` when workspace replaces conflict with a module's natural requirements (Case B).

---

### Step 1: Establish Baseline Behavior
**Command**:  
`GOWORK=off; cd b; go list -m rsc.io/quote`  
**Output**:  
`rsc.io/quote v1.1.0`  
**Observation**:  
Module `b`'s natural graph resolves to `quote v1.1.0` when workspace replaces are disabled (Case A confirmed).

---

### Step 2: Execute `go work sync` from Workspace Root
**Command**:  
`go work sync`  
**Output**:  
No visible errors or warnings during execution. Exit code 0.

---

### Step 3: Inspect Post-Sync State
**Command**:  
`cat b/go.mod`  
**Output Excerpt**:  
```
module b

require (
    example.com/syncreplace v1.1.0
    rsc.io/quote v1.0.0  // [!] Version mismatch
)
```
**Observation**:  
`b/go.mod` retains `rsc.io/quote v1.0.0` despite `syncreplace v1.1.0` requiring v1.1.0. No automatic upgrade occurred.

---

### Step 4: Verify Dependency Consistency
**Command**:  
`go list -m all` (from workspace root)  
**Output Excerpt**:  
```
example.com/syncreplace v1.0.0 => ./testdata/mod/example.com_syncreplace_v1.0.0.txt  
rsc.io/quote v1.0.0  
... // Other dependencies
```
**Observation**:  
The workspace build list shows `quote v1.0.0` is active, consistent with `a`'s replace directive overriding the natural requirement.

---

### Step 5: Simulate Build in Module `b`
**Command**:  
`cd b; go build`  
**Output**:  
Build succeeds without errors.  
**Inspection**:  
`go mod verify` confirms `quote v1.0.0` checksum is valid.  
**Observation**:  
The workspace's replaced version (`v1.0.0`) is functionally operable in `b` despite being inconsistent with `b`'s natural dependency graph.

---

### Step 6: Cross-Check Sync Mechanism
Reviewed `sync.go` logic at failing revision:  
```go
// Excerpt from runSync()
changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
if err != nil {
    continue  // [!] Error handling skips write
}
if changed {
    modload.WriteGoMod(...)  // Write occurs only if changed=true
}
```
**Correlation**:  
- `mustSelectFor[b]` contained `quote v1.0.0` (from workspace graph)  
- `EnterModule(b)` dropped workspace replaces → natural graph expects `quote v1.1.0`  
- `EditBuildList()` forcing `v1.0.0` fails (version conflict) → `err != nil` → `continue`  
- `changed` flag never set → `b/go.mod` not rewritten  

---

### Conclusion
**Final State**:  
`go work sync` leaves `b/go.mod` at the **workspace-replaced identity** (`rsc.io/quote v1.0.0`) when:  
1. Workspace replaces mask a module's natural dependency requirements  
2. `EditBuildList` fails due to version conflict  
3. The `continue` bypasses the write operation  

**Operational Impact**:  
The module remains in a state that:  
- Works within the workspace (due to replace directives)  
- Fails standalone (`GOWORK=off` mode) without manual version alignment  
- Shows no warning during sync execution (silent failure mode)  

**Recommendation for Investigation**:  
Focus on why `EditBuildList` returns an error instead of performing automatic version resolution when workspace and module graphs diverge. Reproduce with `go work sync -v` to surface conflict details.
