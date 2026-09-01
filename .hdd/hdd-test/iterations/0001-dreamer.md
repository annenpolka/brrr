### Field Report: Investigating Test Failure with Unfamiliar CLI

**Step 1: Initial Test Execution**  
Ran the CLI's test command on the failing test suite:  
```bash
mystery-cli test --filter TestResourceAllocation
```
**Output:**  
```
[FAIL] TestResourceAllocation (0.42s)  
Error: Allocation mismatch - expected 512MB, actual: 0MB  
  at allocator.go:72 (AllocateResource)  
  at resource_test.go:115 (TestResourceAllocation)
```
*Observation:* Failure message indicates resource allocation discrepancy but provides no insight into *why* allocation returns 0MB. Stack trace points to implementation and test code equally.

**Step 2: Debug Session Initialization**  
Attempted to debug the specific test case:  
```bash
mystery-cli debug-test TestResourceAllocation --breakpoint allocator.go:70
```
**Output:**  
```
Debug session initialized  
⏳ Hitting breakpoint at allocator.go:70  
> func AllocateResource(ctx Context) (int, error) {  
    // Breakpoint set at resource calculation start  
```
*Observation:* CLI entered interactive debug mode successfully. Breakpoint hit at expected location.

**Step 3: State Inspection**  
Examined runtime state at breakpoint:  
```bash
(dbg) print ctx
```
**Output:**  
```
Context{  
  UserID: "user-7f3a",  
  Priority: HIGH,  
  Env: "production",  
  RequestedMB: 512,  
  AvailableMB: 2048  
}
```
```bash
(dbg) step
```
**Output:**  
```
Stepped into calculateQuota()  
> func calculateQuota(user string) int {  
    // Quota calculation logic
```
*Observation:* Context appears valid. Stepped into quota calculation function.

**Step 4: Quota Calculation Check**  
Inspected quota logic execution:  
```bash
(dbg) print user
"user-7f3a"
```
```bash
(dbg) step 5
```
**Output:**  
```
Stepped through:  
  line 42: quota := fetchUserQuota(user)  
  line 43: if quota == -1 { return 0 }  
  line 45: return applyModifiers(quota)  
```
```bash
(dbg) print quota
-1
```
*Observation:* Critical discovery - `fetchUserQuota` returns -1, triggering fallback to 0MB allocation. Failure message never mentioned user quota lookup.

**Step 5: Dependency Tracing**  
Traced origin of invalid quota value:  
```bash
(dbg) break fetchUserQuota
```
```bash
(dbg) continue
```
**Output:**  
```
Hitting breakpoint at storage.go:203  
> func fetchUserQuota(userID string) int {
```
```bash
(dbg) print userID
"user-7f3a"
```
```bash
(dbg) step
```
**Output:**  
```
>   return cache.Lookup(userID, "quota")
```
```bash
(dbg) eval cache.IsConnected()
false
```
*Observation:* Cache service disconnected. Queries return default -1 value. Test failure root cause is unavailable dependency, not logic error.

**Step 6: Validation**  
Confirmed hypothesis by forcing cache reconnection:  
```bash
(dbg) exec cache.Connect()
```
```bash
(dbg) continue
```
**Output:**  
```
Test passed after cache reconnection  
[PASS] TestResourceAllocation (0.39s)
```

**Conclusion:**  
The CLI's debugging capabilities revealed the true failure path:  
1. Disconnected cache service  
2. Quota lookup returns sentinel value (-1)  
3. Allocation logic interprets -1 as 0MB  
4. Test fails with allocation mismatch  

The original error message obscured this chain by focusing solely on the numeric discrepancy. The CLI enabled concrete observation of runtime state transitions across three layers (test → allocation → storage). No speculative tooling required.
