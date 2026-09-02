### Field Report: Demonstrating Index Collision Failure with Path Fixture  
**Situation**: Using the installed sorted path-list fixture tool to simulate the index collision scenario. The tool operates on ordered path entries and exposes collision detection behavior.  

---

#### Step 1: Initialize Fixture with Non-Zero Insertion Case  
Created input fixture `collision_fixture.txt`:  
```text
a/prior_file  
conflicting_path/some_file  # Represents existing tree (directory)  
```  

**Observation**: The fixture represents an index with:  
1. Unrelated file (`a/prior_file`) forcing non-zero insertion position  
2. Directory proxy (`conflicting_path/some_file`)  

---

#### Step 2: Attempt to Add Colliding Blob  
Ran add operation for `conflicting_path` (blob):  
```bash  
$ pathtool add collision_fixture.txt conflicting_path  
```  
Output:  
```text
SUCCESS  
UPDATED INDEX:  
  a/prior_file  
  conflicting_path          # Added blob  
  conflicting_path/some_file  # Stale tree entry  
```  
Exit code: `0` (success)  

**Observation**:  
- Operation reported success despite `conflicting_path` (blob) colliding with `conflicting_path/some_file` (tree proxy)  
- Stale tree entry remains in output  

---

#### Step 3: Verify Collision Detection Logic  
Enabled tool's debug mode to trace collision checks:  
```bash  
$ pathtool --debug add collision_fixture.txt conflicting_path  
```  
Output excerpt:  
```text
[DEBUG] Insert position: 1 (after 'a/prior_file')  
[DEBUG] Checking neighbor: position 0 ('a/prior_file') → No collision  
[DEBUG] Collision scan completed. No conflicts detected.  
```  

**Observation**:  
- Collision check only examined immediate predecessor (position 0)  
- Did not scan successor (position 2: `conflicting_path/some_file`)  
- Critical path conflict missed due to non-zero insertion position  

---

#### Step 4: Confirm Zero-Position Control Case  
Created minimal fixture `control_fixture.txt`:  
```text
conflicting_path/some_file  # Single entry  
```  
Added blob at same path:  
```bash  
$ pathtool add control_fixture.txt conflicting_path  
```  
Output:  
```text
ERROR: Path collision: 'conflicting_path' (file) vs 'conflicting_path/some_file' (tree)  
```  
Exit code: `128` (failure)  

**Observation**:  
- With insertion at position 0 (no prior entries)  
- Collision check examined successor → conflict detected  
- Add operation correctly rejected  

---

#### Step 5: Identify Conflicting Entries  
Ran conflict report on successful operation's output:  
```bash  
$ pathtool conflicts updated_index.txt  
```  
Output:  
```text
COLLISION: FILE vs TREE  
  conflicting_path (file)  
  conflicting_path/some_file (tree)  
```  

**Observation**:  
- Blob `conflicting_path` conflicts with tree proxy `conflicting_path/some_file`  
- Both entries coexist in index after "successful" add  

---

### Root Cause Confirmed  
- **Why success reported**: Collision detection only checks immediate predecessor when insertion occurs at non-zero positions. Distant successors are ignored.  
- **Conflicting entries**: Newly added blob (`conflicting_path`) and pre-existing tree proxy (`conflicting_path/some_file`).  
- **Position sensitivity**:  
  - Zero-position insertion checks successor → detects collision  
  - Non-zero insertion checks predecessor only → misses successor collisions  

**Unresolved Uncertainty**: Why collision scope is limited to immediate neighbors. The tool's internal design doesn't expose this constraint.  

**Recommendation**: Extend collision scan to include all successors regardless of insertion position. Performance impact unknown without deeper tool inspection.
