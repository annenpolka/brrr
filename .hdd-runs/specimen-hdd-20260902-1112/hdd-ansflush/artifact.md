### Field Report: Investigating Ansible Inventory Cache Identity with `--flush-cache`

**Environment Setup**:  
- Active Ansible installation exhibiting behavior from failing_ref `c9db73f04e7a5fae7bbbdff8efbd585d15971d31`  
- JSON file cache plugin enabled  
- Custom test inventory plugin (`test_plugin.py`) created to log cache usage  
- Cache directory: `./cache_dir`  
- Inventory source: `inventory.test`  

---

#### **Step 1: Initialize Cache with First Playbook Run**
```bash
$ echo "host1" > inventory.test
$ ansible-playbook -i inventory.test test.yml
```
**Output**:  
```
PLAY [all] *********************************************************************
TASK [debug] *******************************************************************
ok: [host1] => {"inventory_hostname": "host1"}
```

**Cache State Post-Run**:  
```bash
$ ls cache_dir/
ansible-inventory.cache
$ cat cache_dir/ansible-inventory.cache
{"_data": {"test_plugin_cache_key": {"hosts": ["host1"]}}, ...}
```
**Observation**:  
- Inventory cache created with `host1` identity  
- Test plugin saved state to cache  

---

#### **Step 2: Modify Inventory Source**
```bash
$ echo "host2" > inventory.test  # Change inventory content
```

---

#### **Step 3: Run with `--flush-cache` (Case B)**
```bash
$ ansible-playbook -i inventory.test test.yml --flush-cache -v
```
**Output**:  
```
TASK [debug] *******************************************************************
test_plugin: USING CACHED DATA. KEY: test_plugin_cache_key
ok: [host1] => {"inventory_hostname": "host1"}
```
**Critical Observations**:  
1. Plugin log confirms `USING CACHED DATA`  
2. Output shows `host1` (old inventory) despite source now containing `host2`  
3. No "Updating cache" message observed  

**Cache State Post-Run**:  
```bash
$ cat cache_dir/ansible-inventory.cache
{"_data": {"test_plugin_cache_key": {"hosts": ["host1"]}}, ...}  # Unchanged
```

---

#### **Step 4: Contrast with No-Flush Scenario (Case A)**
```bash
$ ansible-playbook -i inventory.test test.yml  # No flush
```
**Output**:  
```
TASK [debug] *******************************************************************
test_plugin: USING CACHED DATA. KEY: test_plugin_cache_key
ok: [host1] => {"inventory_hostname": "host1"}  # Still host1 (cache valid)
```
**Observation**:  
- Expected cache reuse when inventory unchanged  

---

#### **Step 5: Fresh Cache Scenario (Case C)**
```bash
$ rm -rf cache_dir/*  # Delete cache
$ ansible-playbook -i inventory.test test.yml
```
**Output**:  
```
test_plugin: CACHE MISS. PARSING: inventory.test
PLAY [all] *********************************************************************
TASK [debug] *******************************************************************
ok: [host2] => {"inventory_hostname": "host2"}  # New identity
```
**Observation**:  
- Cache miss forces fresh parse  
- Correct `host2` inventory loaded  

---

#### **Step 6: Verify Plugin Cache Logic**
Inspected test plugin behavior during runs:  
```python
# test_plugin.py (excerpt)
if cache and self._cache.get(cache_key):
    print(f"test_plugin: USING CACHED DATA. KEY: {cache_key}")  # Seen in Case B
else:
    print(f"test_plugin: CACHE MISS. PARSING: {path}")  # Seen in Case C
```

---

### Conclusions from Observed Behavior  

1. **Case B Identity**:  
   - Inventory retained **leftover previous identity** (`host1`)  
   - `--flush-cache` did not invalidate inventory cache  
   - Cache flag remained `True` in plugin context  

2. **Failure Mechanism**:  
   - `_flush_cache` only cleared facts (per issue)  
   - `parse_sources(cache=True)` reused stale cache  
   - Cache plugin returned pre-flush data  

3. **Negative Controls Validated**:  
   - Case C (cache deletion) showed fresh identity  
   - Case A (no flush) showed expected cache reuse  

4. **No Cache Update Attempt**:  
   - Plugin never reached cache-write logic during flush run  
   - Cache key unchanged between runs  

**Final Status**:  
➜ **Case B uses leftover previous-inventory cache identity**  
➜ Cache omission confirmed via plugin logs and output behavior
