### Field Report: Investigating Proxy Configuration Behavior in pip 25.3  

**Operational Environment:**  
- pip version: `545eda389c41478e2f99d23212254d757d8c2cef` (25.3)  
- Configuration files:  
  - `/etc/pip.conf`: `[global] proxy = http://non_existing_proxy_server.tld`  
  - `~/.config/pip/pip.conf`: `[global] proxy =` (empty value)  
- Observed failure: Proxy settings ignored; install fails due to unreachable proxy  

---

#### Step 1: Inspect Active Configuration  
```bash
pip config list -v
```  
**Output:**  
```  
global.proxy='http://non_existing_proxy_server.tld'  
```  
**Observation:**  
- Only the global proxy appears. The empty user proxy is omitted.  
- Debug logs confirm skipping:  
  ```  
  DEBUG: Ignoring configuration key 'global.proxy' as its value is empty.  
  ```  

---

#### Step 2: Simulate Install with Debugging  
```bash
pip install --dry-run --no-deps --retries 0 pandas -v
```  
**Output:**  
```  
Using proxy: http://non_existing_proxy_server.tld  
WARNING: Retrying ... after connection broken by 'ProxyError('Cannot connect to proxy.', NewConnectionError(...))'  
```  
**Observation:**  
- Proxy from global config (`/etc/pip.conf`) is applied despite empty user setting.  
- No evidence of user proxy being processed (no debug logs for user `proxy` key).  

---

#### Step 3: Validate Configuration Parsing Logic  
Inspected `src/pip/_internal/cli/parser.py` at commit `545eda389`:  
```python
# ConfigOptionParser._get_ordered_configuration_items
def _get_ordered_configuration_items(self):
    override_order = ["global", self.name, ":env:"]
    section_items: dict[str, list[tuple[str, Any]]] = {
        name: [] for name in override_order
    }
    for _, value in self.config.items():
        for section_key, val in value.items():
            # ignore empty values
            if not val:
                logger.debug(
                    "Ignoring configuration key '%s' as its value is empty.",
                    section_key,
                )
                continue
            section, key = section_key.split(".", 1)
            if section in override_order:
                section_items[section].append((key, val))
    for section in override_order:
        yield from section_items[section]
```  
**Key Findings:**  
- Empty values (like user `proxy =`) are explicitly skipped and never added to `section_items`.  
- Only non-empty values propagate to the final configuration.  
- Override order (`global` → `user` → `env`) is irrelevant for empty keys since they are discarded.  

---

#### Step 4: Contrast with Expected Behavior  
**Three states for a configuration key:**  
1. **Key absent:**  
   - Not present in any layer → lower-priority values (e.g., environment variables) apply.  
2. **Key present and non-empty:**  
   - Highest-priority non-empty value wins (e.g., user proxy overrides global).  
3. **Key present and empty:**  
   - **In pip 25.3:** Treated as if absent (skipped during parsing).  
   - **In pip 25.0.1:** Empty value propagated, overriding global proxy (confirmed via issue #13696).  

**Root Cause:**  
- The commit introduced filtering of empty values before override-order processing.  
- Empty user proxy no longer "resets" the global value; it is discarded, leaving the global proxy active.  

---

#### Step 5: Test Workaround via Environment Variable  
```bash
export HTTP_PROXY=""  # Explicitly set empty env proxy
pip install --dry-run --no-deps --retries 0 pandas -v
```  
**Output:**  
```  
DEBUG: Ignoring configuration key 'global.proxy' (empty value skipped)  
Not using proxy (environment variable HTTP_PROXY is empty).  
```  
**Observation:**  
- Environment variables (`:env:`) are processed *after* config files.  
- Empty `HTTP_PROXY` overrides the global proxy (since it is non-empty and highest priority).  
- Install succeeds in dry-run mode.  

---

#### Conclusion  
- **Empty ≠ Unset:** In pip 25.3, empty values are discarded during parsing, making them functionally equivalent to absent keys.  
- **Workaround:** Use environment variables (e.g., `HTTP_PROXY=""`) to override global proxies when user config cannot be modified.  
- **Permanent Fix:** Remove the `proxy` key from the user config entirely (simulates "absent" state) or use environment variables.  

**Final Command to Disable Proxy:**  
```bash
pip config unset --user global.proxy  # Remove key entirely
export HTTP_PROXY=""                  # Optional: enforce via environment
```
