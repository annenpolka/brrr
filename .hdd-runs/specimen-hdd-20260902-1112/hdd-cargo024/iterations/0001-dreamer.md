### Field Report: Investigating Cargo Fingerprint Invalidation with `-Zpublic-dependency`

**Environment Context**  
Nightly toolchain: `cargo 1.97.0-nightly (4f9b52075)`, `rustc` with `exported_private_dependencies` lint  
Project structure: `foo` crate exposing `dep::FromDep` in public API  
Prior state: Replicated upstream failure from `ac87f85a9bfe1816fa5d4e805d8182a12d61d047`  

---

### Step 1: Verify Initial State
```bash
cargo clean
cargo -Zpublic-dependency check --message-format=short
```
**Output:**  
```
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.18s
```
**Observation:**  
- Warning appears as expected  
- `target/` directory populated  

---

### Step 2: Trigger Unexpected Behavior
```bash
cargo check --message-format=short
```
**Output:**  
```
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.02s
```
**Anomalies:**  
1. Warning persists despite flag removal  
2. No `[CHECKING] foo` line → No recompilation occurred  
3. Execution time reduced (0.02s vs 0.18s) → Artifact reuse  

---

### Step 3: Inspect Build Artifacts
```bash
ls -l target/debug/.fingerprint/foo-*
```
**Output:**  
```
-rw-r--r-- 1 user group 1675 Feb 15 10:30 dep-fingerprint
-rw-r--r-- 1 user group  142 Feb 15 10:30 dep-lib-foo
```
**Observation:**  
Fingerprint files modified during initial `-Zpublic-dependency` run remain unchanged after second check.  

---

### Step 4: Check Dependency Metadata
```bash
cat target/debug/.fingerprint/foo-*/dep-lib-foo
```
**Output:**  
```
dep:0.1.0
```
**Observation:**  
Dependency tracking file shows only crate name/version. No evidence of `public-dependency` flag state.  

---

### Step 5: Clean and Test Inverse Case
```bash
cargo clean
cargo check --message-format=short
cargo -Zpublic-dependency check --message-format=short
```
**Output (final command):**  
```
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.01s
```
**Anomalies:**  
1. No warning when flag is *added*  
2. No `[CHECKING]` line → No recompilation  
3. Execution time minimal (0.01s) → Artifact reuse  

---

### Step 6: Force Recompilation Attempt
```bash
touch src/lib.rs
cargo -Zpublic-dependency check --message-format=short
```
**Output:**  
```
[COMPILING] foo v0.0.1
src/lib.rs:3:13: [WARNING] type `FromDep` from private dependency 'dep' in public interface
[WARNING] `foo` (lib) generated 1 warning
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in 0.21s
```
**Observation:**  
- Warning appears after source modification  
- Confirms lint works when compilation occurs  

---

### Key Findings  
1. **Fingerprint Gap**  
   - Toggling `-Zpublic-dependency` doesn't invalidate fingerprints  
   - `target/debug/.fingerprint` files show no change when flag is toggled  

2. **Artifact Reuse Behavior**  
   - Cargo skips recompilation when flag changes  
   - Uses existing artifacts regardless of flag state  

3. **Warning Display Logic**  
   - Warnings reappear if artifacts exist from previous `-Zpublic-dependency` run  
   - Clean builds suppress warnings correctly  

4. **Metadata Shortcoming**  
   - Current fingerprint files (`dep-lib-foo`) track dependency presence but not *how* they're used  
   - No evidence of lint-related flags in fingerprint data  

**Conclusion**  
The core issue is fingerprint invalidation: Cargo's dependency tracking doesn't account for changes in `exported_private_dependencies` lint requirements. The tool treats artifacts as valid across flag-toggling events because:  
- Fingerprints don't encode lint configuration  
- Artifact metadata doesn't record private/public dependency usage  
- Recompilation only triggers on source/dependency version changes  

This creates state-dependent warning behavior tied to build history rather than current flags. The environment requires either:  
1. Manual `cargo clean` between flag changes, or  
2. Fundamental changes to Cargo's fingerprinting of lint configurations  

**Next Action**  
Inspect `cargo` internals for fingerprint composition logic regarding unstable flags... (awaiting further CLI tool exploration)
