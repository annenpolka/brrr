### Field Report: Investigating Configuration Cache Miss

**Operational Context:**  
Working within the provided environment with analog Python script (`cc_unused_prop.py`) and Gradle log snippet (`cc_miss.txt`). The unfamiliar CLI tool `cache-probe` is installed (discovered via `which cache-probe`). Its purpose: trace property access patterns in configuration-phase simulations.

---

#### Step 1: Verify environment and tool baseline
```bash
$ which cache-probe
/usr/local/bin/cache-probe

$ cache-probe --version
cache-probe 0.8.3 (configuration-phase tracer)
```

**Observation:**  
CLI responds with version. No documentation available. Proceeding with trial commands.

---

#### Step 2: Run analog script to generate baseline
```bash
$ python3 files/cc_unused_prop.py
used_keys path
unused idea.io.use.nio2
all_first a1b2c3d4e5f6 all_second f6e5d4c3b2a1 all_same False
used_first 98c7a6b54321 used_second 98c7a6b54321 used_same True
invalidate_unused True
```

**Observation:**  
Analog confirms unused property (`idea.io.use.nio2`) causes invalidation despite identical used properties (`path`). Matches Gradle's behavior.

---

#### Step 3: Apply `cache-probe` to analog output
```bash
$ cache-probe trace --source=files/cc_unused_prop.py --log=files/cc_miss.txt
[TRACE] Property access patterns detected:
  EXPLICIT_READ: path (via System.getProperty)
  IMPLICIT_SNAPSHOT: idea.io.use.nio2 (via System.getProperties() full capture)

[DIAGNOSTIC] Configuration identity contributors:
  USED: path
  UNUSED BUT CAPTURED: idea.io.use.nio2

[WARNING] 1 unused property in snapshot: 
  idea.io.use.nio2 (changed between runs)
```

**Observation:**  
CLI detects two access modes:  
- Direct read of `path` (explicitly used)  
- Full snapshot capture implicating `idea.io.use.nio2` (unused but included in identity)  

Output aligns with Gradle log's invalidation reason.

---

#### Step 4: Cross-reference with Gradle's behavior
```bash
$ cache-probe match --log=files/cc_miss.txt --pattern=IMPLICIT_SNAPSHOT
MATCH: System property 'idea.io.use.nio2' changed (IMPLICIT_SNAPSHOT)
  - Not directly read by configuration
  - Captured via full System.getProperties() call
  - Location: Kotlin DSL compilation (setIdeaIoUseFallback)
```

**Observation:**  
Tool confirms:  
1. `idea.io.use.nio2` was never directly accessed  
2. Inclusion in cache identity caused by Kotlin-DSL's `System.getProperties()` call  
3. Matches JetBrains/kotlin's `setIdeaIoUseFallback` behavior  

---

#### Step 5: Retry with narrowed properties
Simulate Gradle fix by restricting captured properties:
```bash
$ cache-probe simulate --used=path
[CONFIG_CACHE] Identity fingerprint: 98c7a6b54321
[RESULT] Run 1: Store entry
[RESULT] Run 2: Cache hit (fingerprint match)
```

**Observation:**  
When identity excludes implicitly captured properties (retaining only explicitly used `path`), cache hit occurs on second run. Confirms fix direction.

---

### Conclusions from Operations

1. **Root Cause:**  
   Kotlin-DSL compilation calls `System.getProperties()`, capturing all system properties (including `idea.io.use.nio2`) in configuration cache identity.

2. **Key Property Classification:**  
   | Property           | Accessed Explicitly? | In Cache Identity? | Causes Invalidation? |
   |--------------------|----------------------|--------------------|----------------------|
   | `path`             | Yes                  | Yes               | Only if changed     |
   | `idea.io.use.nio2` | No                   | Yes (implicit)    | Yes on change       |

3. **Resolution Path:**  
   - Gradle must stop including properties captured via `System.getProperties()` unless explicitly used  
   - Short-term mitigation: Avoid `System.getProperties()` in configuration phase  

**Unresolved Uncertainty:**  
Exact location of `System.getProperties()` call in Kotlin-DSL (line number) remains unknown without source access.

**Tool Artifacts:**  
Full `cache-probe` output saved to `/logs/cc_analysis_20240415.txt`
