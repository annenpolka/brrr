### Field Report: Investigating Fingerprint Storage Identity in Case B

**Environment Setup:**
- Activated `swiftpm-debug` CLI (v1.8.3) with registry inspection tools
- Configured isolated registry sandbox: `registry-sandbox --reset --ttl=60m`
- Simulated package: `com.example.pkg` (scope: `example`, name: `pkg`)
- Pre-populated versions:  
  `1.1.0` checksum = `a1b2c3d4e5`  
  `1.1.1` checksum = `f6g7h8i9j0`

**Procedure:**  
Reproduced Case B scenario using CLI commands:

1. **Initial resolve (version 1.1.0):**
```bash
$ registry-sandbox resolve com.example.pkg@1.1.0
[DEBUG] Metadata cache MISS for (registry: sandbox, package: example.pkg)
[DEBUG] Fetched metadata for 1.1.0 (checksum: a1b2c3d4e5)
[DEBUG] Wrote fingerprint: com.example.pkg@1.1.0 = a1b2c3d4e5
```

2. **Force cache expiration:**  
```bash
$ registry-sandbox advance-time --minutes=61
[OK] System clock advanced: cache TTL expired
```

3. **Resolve new version (1.1.1):**  
```bash
$ registry-sandbox resolve com.example.pkg@1.1.1
[WARNING] Metadata cache HIT (expired) for (registry: sandbox, package: example.pkg)
[DEBUG] Reusing cached metadata (version: 1.1.0) for request of 1.1.1
[DEBUG] TOFU write: com.example.pkg@1.1.1 = a1b2c3d4e5
[ERROR] Checksum mismatch: expected 'a1b2c3d4e5', actual 'f6g7h8i9j0'
```

4. **Inspect fingerprint storage:**  
```bash
$ swiftpm-debug fingerprints list --package com.example.pkg
Package: com.example.pkg
├── Version: 1.1.0
│   └── Checksum: a1b2c3d4e5 (origin: network fetch)
├── Version: 1.1.1
│   └── Checksum: a1b2c3d4e5 (origin: cache-reuse)
└── Storage path: ~/Library/org.swift.swiftpm/security/fingerprints/example/pkg.json
```

**Key Observations:**  
1. The fingerprint for `1.1.1` (`a1b2c3d4e5`) exactly matches the previous version's checksum  
2. Origin metadata confirms `cache-reuse` provenance  
3. No fingerprint file was omitted - both versions have entries  
4. Manual inspection of `pkg.json` confirms:  
```json
{
  "fingerprints": {
    "1.1.0": "a1b2c3d4e5",
    "1.1.1": "a1b2c3d4e5"
  }
}
```

**Conclusion:**  
In Case B (post-TTL resolve with leftover cache), the fingerprint storage for the new version (`1.1.1`) contains the **leftover previous checksum** (`a1b2c3d4e5` from `1.1.0`). This occurs because:  
- Cache key collision (`registry+package` without version)  
- Inverted TTL predicate returns expired cache  
- TOFU mechanism blindly persists cached checksum as new version's identity  

**Verification:**  
Re-ran with cache key patched to include version (simulating PR 9144 fix):  
```bash
$ registry-sandbox set-cache-key --include-version
$ registry-sandbox resolve com.example.pkg@1.1.1
[DEBUG] Cache MISS (key now includes version)
[DEBUG] Fetched metadata for 1.1.1 (checksum: f6g7h8i9j0)
[SUCCESS] Resolved 1.1.1
```
