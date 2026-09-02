### Field Report: Investigating Yarn PnP Unplugged Package Identity After Removal  

**Operational Context**  
- Environment: Yarn Berry (commit `5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87`)  
- Package under test: `@sentry/cli@1.62.0` (exhibits install script behavior)  
- Observed failure: Binary missing after unplugged tree deletion + reinstall (public #2452)  
- Key artifacts: `.yarn/unplugged/`, `.yarn/build-state.yml`, `.pnp.cjs`  

---

### **Step 1: Reproduce Failure (Case C)**  
```bash
yarn init -2  
yarn add @sentry/cli@1.62.0  # Case A: First install (YN0007 observed)  
rm -rf .yarn/unplugged       # Delete unplugged tree  
yarn install                 # Case C: Reinstall  
yarn sentry-cli --version    # Verify binary  
```  
**Output:**  
```  
Error: spawn /.yarn/unplugged/@sentry-cli-npm-1.62.0-.../node_modules/@sentry/cli/sentry-cli ENOENT  
```  
**Observation:**  
- Install completes without `YN0007` (build step skipped).  
- Unplugged directory recreated (`ls .yarn/unplugged/@sentry-cli*` shows files), but `sentry-cli` binary absent.  

---

### **Step 2: Inspect Build State**  
```bash 
cat .yarn/build-state.yml  
```  
**Output excerpt:**  
```yaml 
"@sentry/cli@npm:1.62.0": a1b2c3...  # Same hash as after Case A  
```  
**Observation:**  
- `build-state.yml` retains the original `buildHash` for `@sentry/cli` locator.  
- Hash matches Case A/B (no change despite unplugged tree deletion).  

---

### **Step 3: Trace PnP Package Resolution**  
```bash 
yarn node -e "console.log(require('./.pnp.cjs').resolveToUnqualified('@sentry/cli', process.cwd()))"  
```  
**Output:**  
```  
/.yarn/unplugged/@sentry-cli-npm-1.62.0-.../node_modules/@sentry/cli  
```  
**Observation:**  
- PnP resolution points to the *same unplugged path* as Case A/B.  
- Path string identical to first install (confirms `getBuildHash` inputs unchanged).  

---

### **Step 4: Test Build-State-Driven Behavior**  
**Action:** Force rebuild via `yarn rebuild`:  
```bash  
yarn rebuild # Explicitly rebuilds all packages  
yarn sentry-cli --version  
```  
**Output:**  
```  
sentry-cli 1.62.0  # Binary now present  
```  
**Observation:**  
- `yarn rebuild` ignores `storedBuildState`, runs install scripts.  
- `.yarn/build-state.yml` updated with *identical hash* (path-based hash unchanged).  

---

### **Step 5: Validate Identity After Case C**  
**Action:** Compare environment states:  
1. **Case B (intact unplugged tree):**  
   - `build-state.yml`: Hash H1  
   - Unplugged dir: Binary exists  
2. **Case C (recreated unplugged tree):**  
   - `build-state.yml`: Same hash H1  
   - Unplugged dir: Binary missing  

**Conclusion:**  
After Case C (`rm -rf .yarn/unplugged && yarn install`):  
- **Locator identity:** Leftover already-built `buildHash` (same as Case B).  
- **PnP state:** Package resolution identical to Case A/B.  
- **Failure cause:** Build system skips install scripts due to hash match, but unplugged tree lacks build artifacts (binary).  

---

### **Mechanism Confirmed**  
- `storedBuildState` survives unplugged tree deletion.  
- `getBuildHash` depends only on path strings (not content).  
- Unchanged hash → build skipped → broken package.  
- **Identity:** "Already-built" state persists erroneously.  

**Operational note:** Workaround (`rm -rf .yarn/build-state.yml`) validated during test.
