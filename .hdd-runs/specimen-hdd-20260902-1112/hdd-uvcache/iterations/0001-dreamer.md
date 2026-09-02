### Field Report: Investigating Rust Cache Growth in CI Environment  

**Operator Log:**  
Following observed disk usage growth due to retained outdated workspace member fingerprints after lockfile updates. Using the installed developer CLI tool (`uv` per astral-sh/uv#20774 context) to inspect and manage cache entries.  

---

#### Step 1: Inspect current cache structure  
```bash
uv cache list --type=workspace-member --format=json
```  
**Output:**  
```json
[
  {
    "id": "fm_7a1b2c3d",
    "lockfile_hash": "a1b2c3d4e5",
    "created": "2024-06-15T08:30:00Z",
    "size": "124MB",
    "path": "/ci/cache/rust/fingerprints/project_a/fm_7a1b2c3d"
  },
  {
    "id": "fm_8e9f0a1b",
    "lockfile_hash": "f0e1d2c3b4",
    "created": "2024-06-18T11:20:00Z",
    "size": "131MB",
    "path": "/ci/cache/rust/fingerprints/project_a/fm_8e9f0a1b"
  },
  {
    "id": "fm_5c6d7e8f",
    "lockfile_hash": "a1b2c3d4e5",
    "created": "2024-06-10T14:15:00Z",
    "size": "118MB",
    "path": "/ci/cache/rust/fingerprints/project_b/fm_5c6d7e8f"
  }
]
```  
**Observation:**  
Multiple entries for same workspace members (`project_a`) with different `lockfile_hash` values. Most recent entry (June 18) has larger size.  

---

#### Step 2: Retrieve current lockfile hash  
```bash
uv lockfile-hash Cargo.lock
```  
**Output:**  
`f0e1d2c3b4` (matches June 18 entry)  

---

#### Step 3: Isolate outdated workspace fingerprints  
```bash
uv cache clean --type=workspace-member --exclude-lockfile-hash $(uv lockfile-hash Cargo.lock) --dry-run
```  
**Output:**  
```markdown
Matched 2 entries for deletion:
- fm_7a1b2c3d (lockfile: a1b2c3d4e5, 124MB)
- fm_5c6d7e8f (lockfile: a1b2c3d4e5, 118MB)
Total reclaimable: 242MB
```  
**Observation:**  
Dry run confirms two entries decoupled from current lockfile. No external dependency caches targeted.  

---

#### Step 4: Execute cleanup  
```bash
uv cache clean --type=workspace-member --exclude-lockfile-hash $(uv lockfile-hash Cargo.lock)
```  
**Output:**  
```markdown
Deleted 2 entries:
- fm_7a1b2c3d
- fm_5c6d7e8f
Freed 242MB disk space
```  

---

#### Step 5: Verify cache state  
```bash
uv cache list --type=workspace-member
```  
**Output:**  
```markdown
ID: fm_8e9f0a1b
Lockfile: f0e1d2c3b4 (current)
Size: 131MB
Path: /ci/cache/rust/fingerprints/project_a/fm_8e9f0a1b
```  
**Observation:**  
Only current lockfile entry retained. Disk usage reduced by 65% for workspace member fingerprints.  

---

**Conclusion:**  
The CLI tool (`uv`) successfully:  
1. Identified workspace-member cache entries tied to outdated lockfiles  
2. Isolated them from external dependency caches  
3. Reclaimed disk space without disrupting current artifacts  
**Recommendation:**  
Integrate `uv cache clean --type=workspace-member --exclude-lockfile-hash $(uv lockfile-hash Cargo.lock)` in CI workflow post-cache-restore.
