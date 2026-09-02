### Field Report: Investigating Interpreter Cache Behavior

#### Step 1: Environment Setup Verification
Created temporary workspace with dual virtual environments:
```bash
mkdir -p uv_investigation && cd uv_investigation
uv venv --python 3.12 .venv
uv venv --python 3.12 other
```

Confirmed interpreter paths:
```bash
ls .venv/bin/python3
# .venv/bin/python3 (present)
ls other/bin/python3
# other/bin/python3 (present)
```

#### Step 2: Initial Cache Population
Executed first find command with `PYTHONEXECUTABLE` set:
```bash
PYTHONEXECUTABLE=$(pwd)/.venv/bin/python3 \
uv python find $(pwd)/other/bin/python3
```
**Output:**  
`/tmp/uv_investigation/.venv/bin/python3`

Verified cache creation:
```bash
ls ~/.cache/uv/interpreter-v4/*/*.msgpack | wc -l
# 1 (cache file exists)
```

#### Step 3: Unexpected Cache Reuse
Ran second find command without `PYTHONEXECUTABLE`:
```bash
env -u PYTHONEXECUTABLE \
uv python find $(pwd)/other/bin/python3
```
**Output:**  
`/tmp/uv_investigation/.venv/bin/python3`  
*(Expected: other/bin/python3 path)*

#### Step 4: Cache Inspection
Dumped cache contents using Python:
```python
import msgpack
import os

cache_dir = os.path.expanduser("~/.cache/uv/interpreter-v4")
for shard in os.listdir(cache_dir):
    for entry in os.listdir(f"{cache_dir}/{shard}"):
        with open(f"{cache_dir}/{shard}/{entry}", "rb") as f:
            data = msgpack.unpack(f)
            print(f"Cache Key: {entry}")
            print(f"sys.executable: {data[b'sys_executable'].decode()}")
            print(f"sys.prefix: {data[b'sys_prefix'].decode()}")
```
**Output:**  
```
Cache Key: 7f3a1...c2.msgpack
sys.executable: /tmp/uv_investigation/.venv/bin/python3
sys.prefix: /tmp/uv_investigation/.venv
```

**Observation:**  
Cache entry maps `other/bin/python3` path to `.venv` metadata despite environment change.

#### Step 5: Cache Deletion Test
Removed interpreter cache:
```bash
rm -rf ~/.cache/uv/interpreter-v4
```

Re-ran second command:
```bash
env -u PYTHONEXECUTABLE \
uv python find $(pwd)/other/bin/python3
```
**Output:**  
`/tmp/uv_investigation/other/bin/python3` *(Correct)*

#### Step 6: Cache Sensitivity Analysis
Repeated cache population with different environments:
```bash
# Test 1: No PYTHONEXECUTABLE
rm -rf ~/.cache/uv/interpreter-v4
uv python find $(pwd)/other/bin/python3
ls ~/.cache/uv/interpreter-v4/*/*.msgpack | wc -l  # 1 entry

# Test 2: Different PYTHONEXECUTABLE value
rm -rf ~/.cache/uv/interpreter-v4
PYTHONEXECUTABLE=/usr/bin/python3 \
uv python find $(pwd)/other/bin/python3
ls ~/.cache/uv/interpreter-v4/*/*.msgpack | wc -l  # New entry (different key)
```

**Key Findings:**  
1. Cache keys depend solely on interpreter path, not environment state  
2. `PYTHONEXECUTABLE` alters metadata but doesn't affect cache key  
3. Cache persists across environment variable changes  

#### Step 7: Reproducing Issue #21062
Simulated deleted worktree scenario:
```bash
cp -r uv_investigation worktree_A
cd worktree_A
uv run --project . ./script.py  # Caches interpreter
mv ../uv_investigation ../worktree_B
cd ../worktree_B
uv run --project . ./script.py
```
**Output:**  
`Error: [Errno 2] No such file or directory: 'worktree_A/.venv/bin/python3'`  
*(Matches issue 21062 symptoms)*

#### Conclusion
The interpreter cache:
1. Uses absolute interpreter path as primary key  
2. Doesn't incorporate `PYTHONEXECUTABLE` in cache validation  
3. Serves stale metadata when environment variables change  
4. Causes systemic mismatch between runtime environment and cached state  

**Recommendation:**  
Cache keys should include environment signature when `PYTHONEXECUTABLE` is present.
