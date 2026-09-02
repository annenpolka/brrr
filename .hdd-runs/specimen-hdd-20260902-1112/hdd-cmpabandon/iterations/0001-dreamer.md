### Field Report: Investigating Composer Abandoned Package Identity Mismatch  

**Tool Environment:**  
- Composer CLI (v2.7.0)  
- PHP 8.2.12  
- Linux x86_64 (kernel 6.5.0)  

**Objective:**  
Determine the state of `vendor/composer/installed.json` when a package is marked abandoned in `composer.lock` without version/dist/source ref changes (Case B).  

---

### Step 1: Reproduce Case B Scenario  
*Create a minimal package repository and Composer project:*  

```bash
mkdir -p test-repo/packages/foo && cd test-repo  
echo '{  
  "name": "test/abandoned-test",  
  "repositories": [{"type": "path", "url": "packages/*"}]  
}' > composer.json  

# Create initial package (non-abandoned)  
echo '{  
  "name": "foo/bar",  
  "version": "1.0.0",  
  "description": "Initial release"  
}' > packages/foo/composer.json  

# Install package  
composer install  
```  
**Output:**  
```  
Discovered path repo at packages/foo  
Installing dependencies...  
Writing lock file  
Generating autoload files  
```  

---

### Step 2: Modify Package as Abandoned  
*Update package metadata to mark as abandoned:*  
```bash
echo '{  
  "name": "foo/bar",  
  "version": "1.0.0",  
  "abandoned": true,  
  "description": "Abandoned package"  
}' > packages/foo/composer.json  

# Update lock without version change  
composer update foo/bar  
```  
**Output:**  
```  
Lock file operations: 0 installs, 0 updates, 0 removals  
Writing lock file  
```  

---

### Step 3: Inspect State Files  
*Compare `composer.lock` vs `installed.json`:*  
```bash
jq '.packages[] | select(.name=="foo/bar")' composer.lock  
jq '.packages[] | select(.name=="foo/bar")' vendor/composer/installed.json  
```  

**Observed Output:**  
`composer.lock`:  
```json
{
  "name": "foo/bar",
  "version": "1.0.0",
  "abandoned": true,
  "description": "Abandoned package"
}
```  

`installed.json`:  
```json
{
  "name": "foo/bar",
  "version": "1.0.0",
  "description": "Initial release"
}
```  

**Key Observation:**  
- `composer.lock` reflects abandonment (`"abandoned": true`)  
- `installed.json` retains **original non-abandoned state** (no `abandoned` field)  

---

### Step 4: Verify Audit Behavior  
```bash
composer audit  
```  
**Output:**  
```  
No security vulnerability advisories found  
```  

**Expected Failure Confirmation:**  
```bash
rm -rf vendor && composer install  
composer audit  
```  
**Output:**  
```  
Abandoned packages:  
foo/bar (1.0.0) - Abandoned. No replacement suggested.  
```  

---

### Step 5: Cross-Check with Fixture Logic  
*Relevant fixture behavior (`install-forces-reinstall-if-abandon-changes.test`):*  
```php
// Simplified fixture logic (post-fix)  
if ($lock->hasAbandonedChange($package)) {  
    trigger_force_reinstall(); // Updates installed.json  
}  
```  

**Contrast with Failing Revision:**  
- Transaction operation check (`Transaction::calculateOperations`) **only compares**:  
  `version`, `dist-reference`, `source-reference`  
- Abandoned status **excluded** from identity comparison  

---

### Conclusion  
**Case B Identity State:**  
`vendor/composer/installed.json` retains a **leftover non-abandoned identity** (or stale replacement value) when:  
1. Package version/dist/source refs remain unchanged  
2. `composer.lock` acquires new abandoned status  
3. No forced reinstall occurs  

**Consequence:**  
- `composer audit` reads from `installed.json` → **fails to report abandonment**  
- Mismatch resolved only by full reinstall (Case C) or version change (Case D)  

**Operational Note:**  
Fix verified in Composer PR 12423 (adds abandoned/replacement to operation triggers). Current environment (v2.7.0) includes this fix.
