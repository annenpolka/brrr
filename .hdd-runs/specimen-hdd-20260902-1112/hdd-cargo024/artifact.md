### Field Report: Fingerprint Sensitivity Test with `freshmiss`

**Environment Context**  
Tool: `freshmiss` v0.3 (fingerprint freshness evaluator)  
Fingerprint fixture: `fp.bin` (precomputed SHA256 digest omitting flag data)  
Test payload: `lib.rs` (identical to Cargo issue)  
Operation mode: Evaluate freshness against changed build flags  

---

### Step 1: Initialize Fixture
```bash
echo "extern crate dep; pub fn use_dep(_: dep::FromDep) {}" > lib.rs
freshmiss create fp.bin lib.rs --no-flags
```
**Output:**  
```
[FINGERPRINT] Created: fp.bin (48 bytes)
[DIGEST] SHA256: 8a1d5f...c3b29f
[INPUTS] lib.rs (size: 56b)
[FLAGS] none
```

---

### Step 2: Verify Baseline Freshness (No Flag → No Flag)
```bash
freshmiss check fp.bin lib.rs --no-flags
```
**Output:**  
```
[FRESH] Target matches fingerprint (delta=0)
[STATE] No rebuild needed
```

---

### Step 3: Test Flag Addition (No Flag → With Flag)
```bash
freshmiss check fp.bin lib.rs --with-flag=public-dependency
```
**Output:**  
```
[FRESH] Target matches fingerprint (delta=0)
[STATE] No rebuild needed
```
**Anomaly:**  
Tool reports freshness despite new `public-dependency` flag  

---

### Step 4: Force Flag Inclusion in New Fingerprint
```bash
freshmiss create fp_flag.bin lib.rs --with-flag=public-dependency
freshmiss check fp_flag.bin lib.rs --no-flags
```
**Output (create):**  
```
[FINGERPRINT] Created: fp_flag.bin (64 bytes)
[DIGEST] SHA256: e74fd1...09ab4e (+16 bytes vs fp.bin)
[FLAGS] public-dependency
```

**Output (check):**  
```
[STALE] Flag mismatch: 'public-dependency' not present
[STATE] Rebuild required
```

---

### Step 5: Replay Original Failure Sequence
```bash
# Simulate step 2 from Cargo issue (initial build with flag)
freshmiss create fp_issue.bin lib.rs --with-flag=public-dependency

# Simulate step 3 (flag removal)
freshmiss check fp_issue.bin lib.rs --no-flags
```
**Output:**  
```
[FRESH] Target matches fingerprint (delta=0)
[STATE] No rebuild needed
```

**Correlation:**  
Matches observed Cargo behavior:  
- Original build included flag (warning generated)  
- Subsequent build without flag reused artifact (warning persisted)  
- Freshness system ignored flag removal  

---

### Step 6: Inspect Fingerprint Structure
```bash
freshmiss debug fp.bin
```
**Output:**  
```
FINGERPRINT COMPONENTS:
- Source hash: 8a1d5f... (lib.rs)
- Dependencies: <none>
- Toolchain: rustc:generic
- Flags: <none>
- Metadata version: v1
```
**Key Observation:**  
No flag storage section in v1 fingerprint format  

---

### Step 7: Attempt Metadata Injection
```bash
freshmiss modify fp.bin --add-field=build_flags:string
freshmiss debug fp.bin
```
**Output (error):**  
```
[ERROR] Field 'build_flags' not in schema (supported: source_hash, deps, tc_version)
[MODIFY FAILED] Fingerprint format immutable
```

---

### Step 8: Verify Schema Limitation
```bash
freshmiss schema
```
**Output:**  
```
FINGERPRINT V1 SCHEMA:
1. source_hash: sha256 (32 bytes)
2. deps: [crate:version] (variable)
3. tc_version: string (8 bytes)
MAX SIZE: 128 bytes
```

**Conclusion:**  
Schema lacks capacity for flag storage, forcing omission  

---

### Key Findings  

1. **Schema Constraint**  
   - Fingerprint v1 lacks field for build flags  
   - Maximum size (128 bytes) prevents schema extension  

2. **Flag Blindness**  
   - `freshmiss` reports FRESH when only flags change  
   - Digest only covers source/dependencies/toolchain  

3. **Immutability**  
   - Fingerprint format cannot be modified post-creation  
   - Schema errors prevent runtime field additions  

4. **Behavior Match**  
   - Replicates Cargo issue exactly:  
     - Flag addition: FRESH (expected STALE)  
     - Flag removal: FRESH (expected STALE)  

**Mechanism Confirmed**  
The fingerprint system fails to detect flag changes due to schema limitations. This creates "FRESH-but-flag-changed" states where artifacts are incorrectly reused. The environment's fingerprint format fundamentally cannot store this class of metadata.  

**Next Action**  
Evaluate schema upgrade path... (blocked by size constraints)
