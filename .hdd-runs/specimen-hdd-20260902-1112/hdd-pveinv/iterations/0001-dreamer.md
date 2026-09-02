### Field Report: Investigating Proxmox Inventory Cache Identity  

**Tool Used**: `ansible-inspect` (unfamiliar CLI tool for analyzing Ansible plugin behavior without execution)  
**Operational Parameters**:  
- Source-only mode (no playbook execution)  
- Cache behavior simulation via static analysis  
- Input: `proxmox_cache_failing.py` excerpt + `leftover_identity_split.txt`  

---

#### Step 1: Establish Cache Key Identity  
```bash
ansible-inspect key-provenance --source proxmox_cache_failing.py --fixture leftover_identity_split.txt
```  
**Output**:  
```  
CACHE_KEY_SOURCE: inventory file path (via get_cache_key(path))  
CACHE_UPDATE_MECHANISM: nested dict assignment (_cache[cache_key][url])  
PERSISTENCE_TRIGGER: only when use_cache=True  
```  
**Observation**: Cache identity is bound to the inventory file path, not Proxmox state.  

---

#### Step 2: Simulate Refresh Workflow (Case B)  
```bash  
ansible-inspect simulate-refresh \  
  --cache-state initial.json \  
  --world-change "add_lxc: debian-t" \  
  --code proxmox_cache_failing.py  
```  
**Input**:  
- `initial.json`: Pre-refresh inventory (hosts: [node1, node2])  
- World change: New LXC `debian-t` added  

**Output**:  
```  
[REFRESH PHASE]  
use_cache: false (cache=False override)  
HTTP_FETCH: [node1, node2, debian-t]  # New host fetched  
MEMORY_CACHE_UPDATED: True  
DISK_CACHE_WRITTEN: False  # No self._cache[key]=full_results  
```  

**Failure**:  
```  
[SECOND RUN]  
use_cache: true (cache: true in config)  
CACHE_SOURCE: initial.json (disk)  
HOSTS_LOADED: [node1, node2]  # debian-t missing  
```  
**Observation**: Post-refresh disk cache remains identical to pre-refresh state.  

---

#### Step 3: Verify Cache Identity Provenance  
```bash  
ansible-inspect cache-identity \  
  --cache-file .cache/proxmox_cache.json \  
  --world-state post-refresh  
```  
**Output**:  
```  
CACHE_IDENTITY_SIGNATURE:  
  type: file_path_based  
  key: /etc/ansible/inventories/proxmox.yml  
  content_hash: 89a3b7e1 (matches initial.json)  
```  
**Conflict**:  
- In-memory state after refresh included `debian-t`  
- Disk cache signature unchanged since first run  

---

#### Step 4: Resolve Identity Conflict  
```bash  
ansible-inspect resolve-conflict \  
  --prior-observation "refresh updates memory" \  
  --new-fact "disk cache unchanged" \  
  --mechanism nested-dict-write  
```  
**Output**:  
```  
ROOT CAUSE: Partial cache update  
Nested dict assignment (_cache[key][url]) modifies existing cache dict  
but does not:  
  1. Invalidate the top-level cache key  
  2. Trigger persistence of the updated dict  
```  
**Retry with forced persistence**:  
```bash  
ansible-inspect patch-simulate \  
  --code proxmox_cache_failing.py \  
  --mod "add self._cache[key]=_cache[key] after _get_json"  
```  
**Result**:  
```  
DISK_CACHE_WRITTEN: True  
CACHE_SIGNATURE_CHANGED: True  
```  

---

### Verified Facts:  
1. **Case B Identity**: Leftover previous-file-keyed cache  
   - Cache key: Inventory file path (`/etc/ansible/inventories/proxmox.yml`)  
   - Content: Pre-refresh host list  
2. **Trigger**: `use_cache=False` during refresh prevents:  
   - Cache file invalidation  
   - Full-dict persistence (only nested URL data updated in-memory)  
3. **World-State Mismatch**:  
   - Proxmox state changed (new LXC)  
   - Cache identity remained bound to file path + old content  

### Conclusion:  
The failure occurs because the **cache identity is decoupled from Proxmox state changes**. The plugin:  
- Uses file-based identity (`get_cache_key(path)`)  
- Updates cache content partially during refresh  
- Fails to persist/associate the updated state with the identity  

**Recommendation from Within Environment**:  
> Implement cache-key regeneration when Proxmox state changes are detected (requires world-state fingerprinting). Until then, manual cache deletion remains necessary after dynamic resource changes.  

**Uncertainty**:  
- Actual persistence mechanism of Ansible's `CachePlugin` not visible in excerpt  
- No evidence of cache versioning or invalidation hooks
