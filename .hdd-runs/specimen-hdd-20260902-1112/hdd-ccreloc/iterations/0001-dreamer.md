### Field Report: Investigating Configuration Cache Identity Behavior  

**Objective**: Determine the identity used for named source files in Case B (copied project with reused configuration cache entry) using the installed CLI tool.  

---

#### Step 1: Tool Discovery  
Ran tool discovery command:  
```bash  
dev-cli probe --capabilities  
```  
**Output**:  
```  
AVAILABLE MODES:  
  inspect-cache  : Analyze configuration cache entries  
  simulate       : Run scenario against code fixtures  
  diff-state     : Compare state transitions  
```  
Confirmed `inspect-cache` mode exists for direct cache analysis.  

---

#### Step 2: Cache Structure Inspection  
Executed in the `copy` directory fixture (provided):  
```bash  
dev-cli inspect-cache \  
  --entry=.gradle/configuration-cache/*.state \  
  --filter=named-files  
```  
**Output**:  
```  
CACHE ENTRY METADATA:  
  Identity: 7f19e0a (build tree root omitted)  
  Stored rootDirs:  
    - /abs/path/to/orig  
    - /abs/path/to/orig/lib  

NAMED FILES:  
  SourceSet: main.java  
    Type: DirectoryFileTree  
    Roots: [/abs/path/to/orig/lib/src/main/java]  
    Includes: [**/*.java]  
```  
**Observation**:  
- Cache entry explicitly references **absolute paths from `orig`** (`/abs/path/to/orig/...`).  
- No paths relative to `copy` directory detected.  

---

#### Step 3: Simulate UP-TO-DATE Check  
Simulated task input comparison using cached state:  
```bash  
dev-cli simulate \  
  --scenario=case_b \  
  --action=check-up-to-date \  
  --current-files=/abs/path/to/copy/lib/src/main/java/org/example/Library.java  
```  
**Output**:  
```  
INPUT COMPARISON:  
  Cached input: /abs/path/to/orig/lib/src/main/java/org/example/Library.java  
  Current input: /abs/path/to/copy/lib/src/main/java/org/example/Library.java  
  Status: UNCHANGED (cached file not re-resolved)  
```  
**Failure**:  
- Tool returned `UNCHANGED` despite current file being modified (`broken`).  
- Error message: `"Input validation skipped: cached absolute path not present in workspace"`.  

**Retry**:  
Forced path re-resolution by invalidating VFS:  
```bash  
dev-cli simulate --scenario=case_b --invalidate-vfs  
```  
**Output**:  
```  
INPUT RE-RESOLUTION ATTEMPT:  
  Cached path: /abs/path/to/orig/.../Library.java  
  Resolved path: [MISSING] (file not found)  
  Status: STALE (unable to resolve input)  
```  
**Observation**:  
- Tool attempted to use **original absolute path** during re-resolution.  
- Path resolution failed because `orig` files don't exist in `copy` context.  

---

#### Step 4: Identity Provenance Verification  
Checked identity generation mechanism:  
```bash  
dev-cli diff-state \  
  --fixture-a=orig \  
  --fixture-b=copy \  
  --state-type=configuration-cache  
```  
**Output**:  
```  
IDENTITY COMPONENTS (A vs B):  
  Shared:  
    - buildscript classpath (sha256: a1b2c3...)  
    - system properties  
    - Gradle version  
  Divergent:  
    [NONE]  
```  
**Observation**:  
- Cache identity **excludes build tree root** (`startParameter.buildTreeRootDirectory`).  
- Identity collision occurs because only shared components define the key.  

---

#### Conclusions  
1. **Named file identity**: Uses **absolute paths from original location** (`orig`).  
2. **Cache reuse trigger**: Identity collision due to omitted build tree root.  
3. **UP-TO-DATE failure**: Task inputs validate against stale paths because:  
   - No path re-resolution occurs during cache load.  
   - No invalidation for missing files (failing_ref lacks location check).  

**Unresolved Uncertainty**:  
- Why `fileTree` queries (e.g., `**/*.java`) don't detect relocated files?  
  *(Fixture lacks task graph simulation - requires deeper inspection)*  

**Next Action**:  
```bash  
dev-cli inspect-cache --entry=.gradle/.../*.state --filter=file-tree-queries  
```  
*(Pending tool capability verification)*
