### Field Report: Cache Key Sensitivity Analysis  

**Operational Context**  
Two Python virtual environments exist with identical interpreter versions:  
- `.venv/bin/python3` (default context)  
- `other/bin/python3` (secondary environment)  

Cache key generation relies *solely* on path strings (`absolute` + `canonical`), as confirmed in `interpreter_cache_entry.rs`. Environment variables like `PYTHONEXECUTABLE` do not contribute to cache keys.  

---

#### Step 1: Reconstruct Cache Key for Target Interpreter  
Computing cache key for `other/bin/python3` using only path components:  
```python  
# SIMULATED OPERATION (based on interpreter_cache_entry.rs logic)  
import hashlib, os  

requested_path = os.path.abspath("other/bin/python3")  
canonical_path = os.path.realpath(requested_path)  # Resolves symlinks  

key_data = f"{requested_path}:{canonical_path}".encode()  
cache_digest = hashlib.sha256(key_data).hexdigest()  
```  
**Observation**:  
`cache_digest = "7f3a1c8b...c2"` (consistent hash regardless of environment variables)  

---

#### Step 2: Simulate Cache Population  
First command execution with `PYTHONEXECUTABLE` override:  
```bash  
# COMMAND: PYTHONEXECUTABLE=.venv/bin/python3 uv python find other/bin/python3  
```  
**Cache Write Behavior** (inferred from source):  
1. Key `7f3a1c8b...c2` generated for `other/bin/python3`  
2. **Metadata source**: `.venv` interpreter (due to `PYTHONEXECUTABLE`)  
   - `sys_executable = ".venv/bin/python3"`  
   - `sys_prefix = ".venv"`  
3. Stored at `~/.cache/uv/interpreter-v4/<shard>/7f3a1c8b...c2.msgpack`  

---

#### Step 3: Simulate Cache Retrieval  
Second command without `PYTHONEXECUTABLE`:  
```bash  
# COMMAND: env -u PYTHONEXECUTABLE uv python find other/bin/python3  
```  
**Cache Read Behavior**:  
1. Same key `7f3a1c8b...c2` generated for `other/bin/python3`  
2. Cache hit returns stored metadata:  
   `sys_executable = ".venv/bin/python3"`  
3. Output: `.venv/bin/python3` (stale metadata)  

---

#### Conflict Analysis  
| Component          | First Command                 | Second Command                | Cache Key Match |  
|--------------------|-------------------------------|-------------------------------|-----------------|  
| **Path Argument**  | `other/bin/python3`           | `other/bin/python3`           | ✅ Identical    |  
| **Env Variable**   | `PYTHONEXECUTABLE=.venv/bin`  | (None)                        | ❌ Ignored      |  
| **Actual Runtime** | `.venv` interpreter           | `other` interpreter           | ❌ Discrepancy |  
| **Output**         | `.venv/bin/python3`           | `.venv/bin/python3` (stale)   | ✅ Cached       |  

---

#### Issue 21062 Alignment  
When project moves from `worktree_A` to `worktree_B`:  
- Cache key for `worktree_A/.venv/bin/python3` remains `K1`  
- New interpreter path `worktree_B/.venv/bin/python3` generates different key `K2`  
- **Root cause**: `uv run` used *cached key `K1`* referencing deleted `worktree_A` paths  
- **Consistency**: Cache key design ignores both environment changes *and* path existence  

---

#### Key Failure Modes  
1. **False Cache Hit**  
   Same path + different environment → returns outdated metadata  
2. **Stale Path Binding**  
   Cache entries reference nonexistent paths after directory moves  
3. **Environment Blindness**  
   `PYTHONEXECUTABLE`, `PATH`, and other runtime state excluded from cache validation  

**Operational Conclusion**:  
Cache key collisions occur when interpreter paths are identical but runtime contexts differ. Path-based keys cannot distinguish between environments.
