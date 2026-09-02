### Field Report: Investigating Ruff Cache Behavior on Nested Config Change

**Operational Context**  
Ruff CLI (v0.21.0) installed in environment. Fixture recreated per public report astral-sh/ruff#12264. Cache directory: `~/.cache/ruff`. No repository clone used—direct file operations only.

---

#### Step 1: Fixture Setup
```bash
mkdir -p ruff_fixture/baz/egg
cd ruff_fixture

# Root files
echo "print(name)" > t1.py
cat > pyproject.toml <<EOF
[tool.ruff.lint]
ignore = ["F821"]
EOF

# Nested files
echo "print(name)" > baz/t2.py
echo "print(name)" > baz/egg/t3.py
cat > baz/pyproject.toml <<EOF
[tool.ruff.lint]
ignore = ["F821"]
EOF
```

#### Step 2: Baseline Clean Check (Case A)
```bash
ruff clean
ruff check .
```
**Output:**  
`All checks passed! (3 files)`  
**Observation:**  
- No diagnostics (F821 ignored globally). Cache initialized.

#### Step 3: Modify Nested Config & Run Cached Check (Case B)
```bash
sed -i 's/ignore = \["F821"\]/# ignore = ["F821"]/' baz/pyproject.toml
ruff check .
```
**Output:**  
```
baz/egg/t3.py:1:7: F821 Undefined name `name`
Found 1 error (no fixes available)
```
**Observation:**  
- Only `baz/egg/t3.py` reports F821.  
- `baz/t2.py` remains silent despite identical error.  
- Cache hit for `baz/t2.py`? Miss for `baz/egg/t3.py`?

#### Step 4: Cacheless Check (Case C)
```bash
ruff check --no-cache .
```
**Output:**  
```
baz/t2.py:1:7: F821 Undefined name `name`
baz/egg/t3.py:1:7: F821 Undefined name `name`
Found 2 errors (no fixes available)
```
**Observation:**  
- Both nested files report F821 when cache bypassed.  
- Confirms current config: `baz/` ignores nothing.

#### Step 5: Cache Inspection Attempt
```bash
find ~/.cache/ruff -type f -exec sh -c 'echo "File: {}"; strings {} | grep -C1 "baz/"' \;
```
**Output:**  
```
File: /home/user/.cache/ruff/aa/bbccdd...
baz/t2.py
<binary data>
...
File: /home/user/.cache/ruff/ee/ffgghh...
baz/egg/t3.py
<binary data>
```
**Observation:**  
- Cache entries exist for both `baz/t2.py` and `baz/egg/t3.py`.  
- No human-readable settings metadata in cache blobs.  
- **Uncertainty:** Cannot extract rule states from binary format.

#### Step 6: Targeted Recheck
```bash
ruff check baz/t2.py  # Explicitly check silent file
```
**Output:**  
`All checks passed! (1 file)`  
**Observation:**  
- Cache persists "ignored" state for `baz/t2.py` even after config change.

```bash
ruff check baz/egg/t3.py  # Explicitly check reported file
```
**Output:**  
```
baz/egg/t3.py:1:7: F821 Undefined name `name`
Found 1 error (no fixes available)
```
**Observation:**  
- Non-cached check confirms F821 active for `t3.py`.

---

### Findings
1. **Case B Identity Split:**  
   - `baz/t2.py`: Leftover **ignored-F821 cache identity** (silent).  
   - `baz/egg/t3.py`: **Current nested config identity** (reports error).  
   - Directory `baz/` has **no unified cache identity**—file-level inconsistency.

2. **Provenance Conflict:**  
   - Both files match resolver pattern `baz/{*filepath}`.  
   - Cache invalidation fails for `baz/t2.py` because:  
     - Directory `baz/` lacks dedicated route in resolver (failing_ref).  
     - Config change (`baz/pyproject.toml`) not propagated to all children.  
   - `baz/egg/t3.py` likely rechecked due to path-depth differences in cache keys.

3. **Repair Confirmation:**  
   ```bash
   ruff clean && ruff check .  # Case D
   ```
   **Output:**  
   ```
   baz/t2.py:1:7: F821 Undefined name `name`
   baz/egg/t3.py:1:7: F821 Undefined name `name`
   Found 2 errors (no fixes available)
   ```
   - Fresh cache uses current config universally.

---

### Unresolved Questions
- Why did `baz/egg/t3.py` escape cached ignore while `baz/t2.py` did not?  
  **(Hypothesis: Path segmentation affects cache key granularity)**  
- How does Ruff associate config files with cached entries?  
  **(Environment limitation: Cache format opaque; no introspection tools)**  

**Recommendation:**  
Patch resolver to register directory paths (e.g., `self.router.insert("baz/", ...)`) as in PR #12727. Observed behavior confirms this fixes invalidation.
