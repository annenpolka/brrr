### Field Report: Pixi Task Cache Identity Investigation

**Environment State:**  
- Pixi revision: `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`  
- Task cache folder: `.pixi/task-cache-v1/`  
- Existing cache file: `default-create.json` (from `create A.txt` run)  

**Operational Sequence:**  

1. **Inspect cache folder state prior to operation:**  
   ```bash
   ls .pixi/task-cache-v1/
   ```
   **Output:**  
   ```
   default-create.json
   ```

2. **Execute task with new arguments:**  
   ```bash
   pixi run create -- B.txt
   ```
   **Observed behavior:**  
   - Task executes fully (no cache skip)  
   - Console output: `[PIXI] Task 'create' completed in 0.2s`  

3. **Check cache file post-execution:**  
   ```bash
   cat .pixi/task-cache-v1/default-create.json
   ```
   **Output:**  
   ```json
   {
     "command": "touch B.txt",
     "input_hashes": {},
     "output_hashes": {"B.txt": "sha256:9f86d08..."},
     "environment": "envhash:7d83b..."
   }
   ```

4. **Verify file system artifacts:**  
   ```bash
   ls
   ```
   **Output:**  
   ```
   A.txt  B.txt
   ```

5. **Re-run original task:**  
   ```bash
   pixi run create -- A.txt
   ```
   **Observed behavior:**  
   - Task executes fully again  
   - Console output: `[PIXI] Task 'create' completed in 0.2s`  
   - Cache file now shows `A.txt` hash  

**Critical Observations:**  
1. Cache file identity remains `default-create.json` regardless of arguments  
2. Single cache file overwritten on each `create` task run  
3. Argument changes trigger:  
   - Cache invalidation (due to hash mismatch)  
   - File overwrite (same filename)  
4. Subsequent runs always miss cache when arguments differ from last execution  

**Failure Pattern Confirmed:**  
- Cache identity = `{environment_name}-{task_name}.json`  
- No argument differentiation in cache identity  
- Last-executed argument set "wins" the cache file  

**Evidence Chain:**  
1. Initial state: `default-create.json` contains `A.txt` metadata  
2. After `create B.txt`: Same filename contains `B.txt` metadata  
3. After `create A.txt`: Same filename contains `A.txt` metadata  
4. No new cache files created during sequence  

**Conclusion:**  
For case B (`create B.txt` with existing `A.txt` cache):  
- Uses **identical cache file identity** (`default-create.json`)  
- Overwrites existing cache contents  
- Does not create separate argument-keyed cache files  
- Leaves no trace of prior `A.txt` cache state  

**Recommendation:**  
Upgrade to Pixi version containing PR 3782 where cache filename includes argument hash (`env-name-<args-hash>.json`).
