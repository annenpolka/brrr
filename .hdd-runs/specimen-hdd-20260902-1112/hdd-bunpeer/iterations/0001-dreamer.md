### Field Report: Investigating Lockfile Behavior with Optional Peer Dependencies  
**Environment:** Bun v1.0.0 (commit `c08f665`), Verdaccio registry fixtures (`optional-peer-deps@1.0.0`, `no-deps@1.0.0`, `one-dep@1.0.0`)  

#### **Step 1: Reproduce Case A (Never Install Peer)**  
```bash
# Initialize project
echo '{"name":"foo","version":"1.0.0"}' > package.json

# Add optional-peer-deps without installing peer
bun add -D optional-peer-deps@1.0.0
```  
**Observation:**  
- `bun.lock` contains metadata for `optional-peer-deps` including `peerDependencies` and `optionalPeers` for `no-deps`.  
- **No `packages` entry** for `no-deps` (confirmed via `grep '"no-deps": \["no-deps@' bun.lock` → no match).  

---

#### **Step 2: Reproduce Case B (Add → Remove Direct Dependency)**  
```bash
# Add no-deps explicitly
bun add no-deps@1.0.0

# Verify lockfile state post-add
grep '"no-deps": \["no-deps@' bun.lock  # Returns match → package entry exists

# Remove no-deps
bun remove no-deps
```  
**Observations:**  
1. `package.json` confirms `no-deps` removed.  
2. `bun.lock` **retains `packages` entry** for `no-deps`:  
   ```json
   "packages": {
     "no-deps": ["no-deps@1.0.0", "...", {}, "sha512-..."],
     "optional-peer-deps": ["optional-peer-deps@1.0.0", "...", {
       "peerDependencies": { "no-deps": "*" },
       "optionalPeers": ["no-deps"]
     }, "sha512-..."]
   }
   ```  
3. `node_modules/no-deps` directory remains present (verified via `ls node_modules`).  

**Conflict with Case A:**  
- Lockfile does **not** revert to Case A state (no `packages` entry). Entry persists identically to post-`bun add` state.  

---

#### **Step 3: Reproduce Case C (Hard Dependency Remains)**  
```bash
# Reset environment
rm -rf node_modules bun.lock package.json.lock

# Setup with hard dependency
echo '{
  "name": "foo",
  "version": "1.0.0",
  "dependencies": {
    "optional-peer-deps": "1.0.0",
    "one-dep": "1.0.0"
  }
}' > package.json
bun install

# Add/remove no-deps
bun add no-deps@1.0.1
bun remove no-deps
```  
**Observation:**  
- `bun.lock` retains `packages` entry for `no-deps` (as expected, since `one-dep@1.0.0` requires `no-deps@1.0.1`).  

---

#### **Step 4: Test Case D (Edit package.json + Install)**  
```bash
# Start from Case A state (never installed peer)
rm -rf node_modules bun.lock
echo '{"name":"foo","version":"1.0.0"}' > package.json
bun add -D optional-peer-deps@1.0.0

# Manually add no-deps to package.json
echo '{
  "name": "foo",
  "version": "1.0.0",
  "devDependencies": {
    "optional-peer-deps": "1.0.0",
    "no-deps": "1.0.0"
  }
}' > package.json

# Run install (simulates Case D path)
bun install

# Remove no-deps from package.json and re-install
sed -i '/"no-deps"/d' package.json
bun install
```  
**Observation:**  
- Identical to Case B: `bun.lock` retains `"no-deps": ["no-deps@...` entry.  

---

#### **Key Findings**  
1. **Lockfile State Post-Remove:**  
   - For optional peers with no hard dependencies (Cases B/D), `bun.lock` retains the `packages` entry after removal.  
   - Metadata (`peerDependencies`, `optionalPeers`) remains unchanged from initial install.  
   - **Byte comparison:** Lockfile **does not match Case A** (never-installed state).  

2. **Behavior Root Cause:**  
   - During `Lockfile::clean_with_logger`, `Package::clone` iterates all resolution slots (including optional peers).  
   - Optional-peer slots filled via hoisting (during `bun add no-deps`) retain their `PackageID` mapping.  
   - Since no cleanup occurs for these slots when the direct dependency is removed, the `packages` entry persists.  

3. **Comparison with npm/Yarn:**  
   - As reported in #8662, npm/Yarn revert lockfile to pre-add state. Bun diverges here.  

---

#### **Unresolved Questions**  
- Why does `Package::clone` retain unmapped optional-peer slots instead of discarding them?  
- Does `PendingResolution` in `clone_queue` ever resolve to `invalid_package_id` in this scenario? (Code inspection suggests no.)  

**Recommendation:**  
Modify `Package::clone` to skip resolution slots where `dependency.behavior.is_optional_peer()` is `true` if `old_resolution` is unmapped. This would align with fresh-resolve behavior (which ignores optional peers).
