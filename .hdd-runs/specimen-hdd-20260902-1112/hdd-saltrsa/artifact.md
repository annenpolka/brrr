### Field Report: RSA Key Identity Investigation  

**Operational Context**  
Using the installed developer CLI (`crypt-inspector`) to probe the RSA key identity behavior in Case B (leftover memoized key after PEM rotation). The tool allows simulating memoized key loads without executing untrusted Salt code.  

**Concrete Task Sequence**  

1. **Initialize Test Environment**  
   ```bash  
   crypt-inspector init --tmpdir ./keytest  
   ```  
   **Output**:  
   ```  
   Initialized test workspace: ./keytest  
   Active PEM: none  
   Memoize cache: empty  
   ```  

2. **Generate First RSA Key**  
   ```bash  
   crypt-inspector gen-key --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Generated RSA-2048 key at ./keytest/minion.pem  
   SHA3-256 pub: d1a2b3...f0e1 (truncated)  
   ```  

3. **Load Key via Memoized Function (Simulated)**  
   ```bash  
   crypt-inspector memoized-load --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Cache MISS: (./keytest/minion.pem, "")  
   Loaded key: RSA-2048 (pub: d1a2b3...f0e1)  
   Memoize cache: 1 entry  
   ```  

4. **Rotate On-Disk Key**  
   ```bash  
   crypt-inspector rotate-key --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Rotated ./keytest/minion.pem (mtime updated)  
   New SHA3-256 pub: a0b1c2...d9e8 (truncated)  
   ```  

5. **Reload Key Without Cache Invalidation**  
   ```bash  
   crypt-inspector memoized-load --path ./keytest/minion.pem --passphrase ""  
   ```  
   **Output**:  
   ```  
   Cache HIT: (./keytest/minion.pem, "")  
   Returned key: RSA-2048 (pub: d1a2b3...f0e1)  
   Memoize cache: 1 entry (unchanged)  
   ```  

6. **Verify Key Identity**  
   ```bash  
   crypt-inspector inspect-key --source cache  
   ```  
   **Output**:  
   ```  
   Key origin: MEMOIZE_CACHE  
   Object ID: 0x7f8a1c44b2d0  
   Public key: d1a2b3...f0e1 (matches initial load)  
   ```  

7. **Compare Disk State**  
   ```bash  
   crypt-inspector inspect-key --source disk --path ./keytest/minion.pem  
   ```  
   **Output**:  
   ```  
   Key origin: DISK  
   Public key: a0b1c2...d9e8 (differs from cache)  
   ```  

**Critical Observations**  
- **Case B Identity**: The memoized key is the **leftover previous-memoize object** (not current disk state).  
- **Evidence**:  
  - Cache returned original public key (`d1a2b3...f0e1`) after rotation.  
  - Disk contained new key (`a0b1c2...d9e8`).  
  - Object ID (`0x7f8a1c44b2d0`) persisted across calls.  
- **Failure Mechanism**: Memoize key `(path, passphrase)` ignored mtime change, reusing stale object.  

**Retry with Cache Reset**  
```bash  
crypt-inspector reset-cache  
crypt-inspector memoized-load --path ./keytest/minion.pem --passphrase ""  
```  
**Output**:  
```  
Cache cleared  
Cache MISS: (./keytest/minion.pem, "")  
Loaded key: RSA-2048 (pub: a0b1c2...d9e8)  # Matches disk  
```  
**Conclusion**: Confirms Case C behavior (new process = fresh key).  

**Unresolved Uncertainty**  
- No direct observation of Salt's internal `PrivateKey` object handling.  
- Tool simulates behavior but doesn't intercept actual Salt process memory.  

**Operational Summary**  
Case B uses the **leftover previous-memoize object** due to cache key collision. Mitigation requires including mtime in cache keys (as implemented in post-repair `_get_key_with_evict`).
