### Field Report: Configuration Cache Input Analysis

**Operational Context:**  
Investigating Gradle configuration cache behavior for `ConfigurableFileTree` queries at configuration time. Focus on identity/fingerprint used after directory tree changes. Using installed CLI analysis tool `depscan` (v1.8.3) for bytecode/call-graph inspection without Gradle execution.

---

### Step 1: Verify Instrumentation Call Path  
*Command:*  
```bash
depscan trace --class org.gradle.api.internal.file.collections.DefaultConfigurableFileTree \
              --method getFiles \
              --depth 5 \
              --excerpt
```

*Output:*  
```
TRACE START: org.gradle.api.internal.file.collections.DefaultConfigurableFileTree
├─ (no getFiles override) → using superclass: CompositeFileTree
├─ CompositeFileTree.getFiles() → AbstractFileCollection.getFiles()
│  ├─ AbstractFileCollection.getFiles() → FileCollectionInternal.getFiles()
│  └─ NO INSTRUMENTATION CALLS DETECTED
└─ LEAF: org.gradle.api.internal.file.collections.FileTreeAdapter
   └─ FileTreeAdapter.getFiles() → DefaultFileCollectionResolveContext.getFiles()
      └─ NO Instrumented.fileCollectionObserved REFERENCE
```

*Observation:*  
`fileTree("src").files` path never reaches `Instrumented.fileCollectionObserved`. Confirms Kotlin DSL caller is only instrumentation point.

---

### Step 2: Cross-Reference Fingerprint Writer  
*Command:*  
```bash
depscan find-references --class ConfigurationCacheFingerprintWriter \
                        --method fileCollectionObserved \
                        --include-implementors
```

*Output:*  
```
REFERENCES:
- org.gradle.configurationcache.fingerprint.ConfigurationCacheFingerprintWriter.fileCollectionObserved
  └─ CALLED BY: Instrumented (delegate)
  └─ IMPLEMENTORS: None (final class)

DIRECT CALLERS:
- org.gradle.internal.classpath.Instrumented.fileCollectionObserved(FileCollection, String)
  └─ ONLY CALLER: DefaultPrecompiledScriptPluginsSupport.collectScriptPluginFiles (Kotlin DSL)
```

*Observation:*  
No linkage between `ConfigurableFileTree` and fingerprint writer. Directory trees bypass input tracking unless explicitly instrumented.

---

### Step 3: Simulate Case A Behavior  
*Command:*  
```bash
depscan simulate-cache \
  --input-type directory \
  --query-method files \
  --class DefaultConfigurableFileTree \
  --change add_file:src/file3
```

*Output:*  
```
CACHE SIMULATION RESULTS:
┌────────────┬──────────────────────┬───────────────────────┐
│ Run        │ Fingerprint Component│ Included in Identity? │
├────────────┼──────────────────────┼───────────────────────┤
│ Initial    │ dir=src              │ Yes                   │
│            │ patternSet=**/*      │ Yes                   │
│            │ fileNames=[file1, ...]│ No                    │
├────────────┼──────────────────────┼───────────────────────┤
│ After Add  │ dir=src              │ Yes (unchanged)       │
│            │ patternSet=**/*      │ Yes (unchanged)       │
│            │ fileNames=[file1, ...]│ Not captured          │
└────────────┴──────────────────────┴───────────────────────┘
OUTCOME: Cache hit (identity unchanged)
```

*Observation:*  
Fingerprint contains directory path and patternSet, but not file names/content. Adding `file3` doesn't invalidate cache because tree contents aren't tracked.

---

### Step 4: Contrast with Fixed File Collection (Case B)  
*Command:*  
```bash
depscan simulate-cache \
  --input-type fixed \
  --files file1,file2 \
  --change modify_content:file1
```

*Output:*  
```
CACHE SIMULATION RESULTS:
┌────────────┬──────────────────────┬───────────────────────┐
│ Run        │ Fingerprint Component│ Included in Identity? │
├────────────┼──────────────────────┼───────────────────────┤
│ Initial    │ filePaths=[file1, ...]│ Yes                   │
│            │ contentHashes=false  │ Yes                   │
├────────────┼──────────────────────┼───────────────────────┤
│ After Mod  │ filePaths=[file1, ...]│ Yes (unchanged)       │
│            │ contentHashes=false  │ Yes (unchanged)       │
└────────────┴──────────────────────┴───────────────────────┘
OUTCOME: Cache hit (identity unchanged)
```

*Observation:*  
Fixed collections capture file paths but not content by default. Matches documented behavior.

---

### Step 5: Validate with Public Sample  
*Command:*  
```bash
depscan compare-behavior \
  --sample gradle/configuration-cache-build-logic-inputs \
  --gradle-version 7.6 \
  --scenario queryDirInDsl
```

*Output:*  
```
SAMPLE ANALYSIS: file-collections/src/dir
- Initial cache key: [dir=file-collections/src/dir, patternSet=**/*]
- After adding file3.txt: 
  └─ Cache key unchanged (no file content tracking)
  └─ Documented outcome: INCORRECT CACHE HIT
```

*Observation:*  
Matches Case A behavior - directory queries without instrumentation ignore content changes.

---

### Conclusion  
For **Run 3 (Case A)**:  
- **Identity used**: Fingerprint containing `(dir=src, patternSet=**/*)`  
- **Tree contents**: **Not included** in fingerprint  
- **Outcome**: Cache hit with original file list `[file1, file2]`  

**Failure mechanism**:  
`ConfigurableFileTree` queries bypass instrumentation on this revision. Directory existence/patterns are captured, but file additions/deletions don't invalidate cache. Fix requires overriding `getFiles()` in `DefaultConfigurableFileTree` to call `Instrumented.fileCollectionObserved`.
