### Field Report: Wildcard Checksum Identity Investigation  

**Operational Context**  
Using the installed `task` CLI (go-task/task at failing_ref `1e2121a99f`). Environment constraints prevent executing untrusted checkouts, so analysis relies on source inspection and documented behavior.  

---

#### Step 1: Inspect Cache Key Logic  
*Command:* Analyze `variables.go` and `taskfile/ast/task.go` at failing_ref.  
*Observation:*  
```go
// From variables.go (compiledTask):  
new := ast.Task{  
    Task: origTask.Task, // Retains wildcard template name (e.g., "build-*")  
    // No FullName field present  
}  

// From taskfile/ast/task.go (Name):  
func (t *Task) Name() string {  
    if t.Label != "" {  
        return t.Label  
    }  
    return t.Task // Returns template name ("build-*"), ignoring MATCH  
}  
```  
*Finding:* Fingerprint cache key is `Task.Name()` (template name). Wildcard parameter (`foo`/`bar`) is excluded.  

---

#### Step 2: Simulate Case B Behavior  
*Scenario:*  
- `.task/checksum/build-*` exists from prior `task build-foo` (Case A).  
- Run `task build-bar`.  

*Command:* Trace checksum lookup logic via source:  
```go  
// fingerprint.IsTaskUpToDate(key) uses:  
key := task.Name() // "build-*" for ANY wildcard instantiation  
```  
*Observation:*  
- `build-bar` uses **identical cache key** (`build-*`) as `build-foo`.  
- Tool finds existing `.task/checksum/build-*` and treats `build-bar` as up-to-date.  
- No new checksum file created for `bar`.  

---

#### Step 3: Verify Artifact State  
*Command:* Infer filesystem outcome:  
```bash  
# After Case A:  
$ ls .task/checksum  
build-*  # Checksum for 'foo'  

# After Case B (task build-bar):  
$ ls .task/checksum  
build-*  # Same file, unchanged  
```  
*Finding:*  
- Only `build-*` exists. No `build-bar` file created.  
- Checksum content remains the `foo` instantiation's fingerprint.  

---

#### Step 4: Conflict Check with Known Fix  
*Observation:*  
Post-fix (PR 1808) introduces `FullName`:  
```go  
// Fixed logic:  
key := task.FullName() // "build-foo" or "build-bar"  
```  
*Contrast with Case B:*  
- Failing_ref **lacks `FullName`**.  
- Wildcard instantiations **share single cache key** (`build-*`).  
- Leftover artifact: **Only `build-*` file exists**, reused for all instantiations.  

---

#### Conclusion  
For **Case B** (`task build-bar` with leftover `build-foo` checksum):  
- **Identity in `.task/checksum/`:** Leftover `build-*` file (from `foo`).  
- **State:** Single file persists; no per-instantiation checksum created.  
- **Mechanism:** Cache key omission of MATCH parameter causes reuse.  

**Evidence Chain:**  
1. Source confirms cache key = `Task.Name()` (template name).  
2. Issue #1795 verifies shared checksum across instantiations.  
3. Fix (PR 1808) explicitly corrects key to include MATCH.  

**Uncertainty:** Filesystem state inferred from source/logic (direct execution prohibited).
