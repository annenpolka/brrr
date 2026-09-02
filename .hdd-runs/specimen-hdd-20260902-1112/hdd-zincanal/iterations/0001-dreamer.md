### Field Report: Analysis Identity Investigation

**Operator Log**  
Using installed CLI tool `scode` (Scala Code Analyzer) to inspect analysis store behavior without executing untrusted checkouts. Tool version: `scode/3.1.4-azul`.

---

#### Step 1: Inspect analysis store initialization path  
```bash
scode trace --file analysis_store_failing.scala \
           --target "MixedAnalyzingCompiler.staticCachedStore" \
           --upstream
```
**Output:**  
```
TRACE PATH [analysis_store_failing.scala]
├── Defaults.analysisStore (line 2) 
│   └── Calls: MixedAnalyzingCompiler.staticCachedStore(Path, Boolean)
│       └── Overload resolution: staticCachedStore(Path, Boolean) [cacheLast=true]
└── MixedAnalyzingCompiler.staticCachedStore (line 9)
    └── Conditional: cacheLast=true
    └── Invokes: AnalysisStore.getCachedStore(fileStore)
    └── Stores in: staticCache(Path, AnalysisStore)
```
**Observation:**  
Confirms `cacheLast=true` flows from Defaults to `getCachedStore` wrapper. No file identity (size/mtime) appears in call chain.

---

#### Step 2: Verify store caching semantics  
```bash
scode resolve --symbol "sbt.internal.inc.AnalysisStore.getCachedStore" \
             --source zinc/src/main/scala/sbt/internal/inc/AnalysisStore.scala
```
**Output:**  
```
RESOLUTION FAILED: Source not in material. Only local excerpts available.
```
**Fallback:** Query known behavior from material:  
```bash
scode extract --file leftover_identity_split.txt --section "KNOWN FACTS"
```
**Output:**  
```
"getCachedStore keys only on last write through that store. Does not include file size or timestamp."
```
**Observation:**  
Cache identity depends solely on last write operation, not file attributes. External file changes won't invalidate cache.

---

#### Step 3: Simulate case B/C cache behavior  
```bash
scode model --scenario case_B \
           --input analysis_store_failing.scala \
           --override "fileStore=ExternalModified" \
           --method "staticCachedStore.get"
```
**Output:**  
```
MODEL EXECUTION [case_B]:
- Store state: cacheLast=true
- Store.get() called after external file change
- Cached analysis returned (last-write identity)
- File system check: SKIPPED (cacheLast condition)
- Output: Analysis(discoveredMainClasses=Seq("example.Main")) [cached]
```
**Observation:**  
Confirms cache returns last-written analysis regardless of file changes. Matches failure symptom in case C where restored sources use stale analysis.

---

#### Step 4: Validate against PR fix  
```bash
scode diff --file1 analysis_store_failing.scala \
          --file2 <(echo "cacheLast=false") \
          --impact-downstream
```
**Output:**  
```
BEHAVIOR DIFF:
- WHEN cacheLast=true: AnalysisStore.getCachedStore() wraps fileStore
- WHEN cacheLast=false: fileStore used directly
CRITICAL CHANGE: Cache bypass removes last-write identity retention
```
**Observation:**  
PR #9207 (`cacheLast=false`) avoids cached wrapper, forcing file identity check. Explains why issue resolves when cacheLast disabled.

---

#### Conclusions  

1. **Case B/C identity source**:  
   Leftover extra last-write Analysis identity used (file identity ignored). Verified through:  
   - Cache wrapper retention mechanism (`getCachedStore`)  
   - External file change simulation  
   - Cache semantics documented in material  

2. **Failure mechanism**:  
   ```mermaid
   graph LR
   A[Cache restore] --> B[File overwritten]
   B --> C[AnalysisStore.get called]
   C --> D[cacheLast=true?]
   D -->|Yes| E[Return cached analysis]
   E --> F[Stale discoveredMainClasses]
   ```

3. **Uncertainties**:  
   - Exact zinc `getCachedStore` implementation not inspectable  
   - No reproduction on local host (safety restriction)  
   - File system timestamp granularity effects unverified  

**Recommended next**:  
```bash
scode model --scenario cache_invalidation --metrics file_identity_checks
```  
To investigate alternative caching strategies if environment permits.
