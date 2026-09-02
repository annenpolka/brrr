### Field Report: Investigating Gradle Configuration Cache File Collection Identity

**Tool:** Unfamiliar CLI analysis utility (observed as `codeq` v1.7.3)  
**Objective:** Determine stored identity of `FileCollection` in Case B after configuration cache load on failing_ref (`92fc31994d51f`)

---

#### Step 1: Inspect serialization boundary for base directory
```bash
codeq analyze --target=ConfigurableFileCollectionCodec_failing.kt \
             --focus=encode \
             --query="writeContext"
```

**Output:**
```
ENCODING PATH:
  encodePreservingIdentityOf()
    └─ codec.run { encodeContents(value) }  [writes: FileCollectionContainer]
    └─ writeBoolean(value.isFinalizing)      [writes: primitive]
  NO DETECTION OF:
    - PathToFileResolver
    - ProjectDirectory
    - RelativePathResolutionContext
```

**Observation:** Base directory not serialized. Only contents and finalization flag written.

---

#### Step 2: Trace deserialization factory resolution
```bash
codeq analyze --target=ConfigurableFileCollectionCodec_failing.kt \
             --focus=decode \
             --query="fileCollectionFactory"
```

**Output:**
```
DECODING PATH:
  fileCollectionFactory.configurableFiles() 
    [SOURCE: isolate-scoped service]
    [TYPE: DefaultFileCollectionFactory]
  └─ .from(contents) 
    [RESOLUTION CONTEXT: factory.baseDir]
```

**Follow-up:**  
```bash
codeq resolve-symbol DefaultFileCollectionFactory \
                  --commit=92fc31994d51f \
                  --symbol=baseDir
```

**Output:**
```
SYMBOL: org.gradle.api.internal.file.DefaultFileCollectionFactory
FIELD:  final File baseDir [IMMUTABLE]
SETUP:  Injected at build scope via:
  BuildScopeServices.configure(..., fileResolver)
  └─ fileResolver.baseDir = build.rootDir
```

**Observation:** Deserialization uses root-scoped factory with immutable rootDir base.

---

#### Step 3: Verify provider-backed collection spec
```bash
codeq analyze --target=ProviderBackedFileCollectionSpec_failing.kt \
             --query="storage"
```

**Output:**
```
PROVIDER-BACKED SPEC:
  Stored element: ProviderInternal<*> only
  NO CONTEXT ATTACHMENTS:
    - No project reference
    - No resolver identity
    - No path relativity metadata
```

**Failure test:**  
```bash
codeq test-hypothesis "spec preserves baseDir" \
                     --files=ProviderBackedFileCollectionSpec_failing.kt \
                     --constraint="FileResolver"
```
```
❌ HYPOTHESIS REJECTED
0 matches for FileResolver in:
  - Constructor params
  - Serialized fields
  - Companion objects
```

---

#### Step 4: Cross-validate with absolute path case
```bash
codeq compare-case --case=A --case=B \
                  --input=leftover_identity_split.txt \
                  --filter="serialization"
```

**Output:**
```
CASE A (absolute):
  [ENCODE] path: /abs/sub/someFile.txt → stored as absolute
  [DECODE] no resolution needed → no baseDir usage

CASE B (provider-relative):
  [ENCODE] provider captured WITHOUT resolution context
  [DECODE] provider evaluated + resolved via isolate.factory.baseDir
  DELTA: Resolution context switched from subproject to root
```

**Key Finding:** Serialized form contains unresolved provider + no resolution context, forcing re-resolution against deserialization environment's baseDir.

---

#### Conclusion from Tool Operation
The named `FileCollection` in Case B stores **only the unresolved provider**. After configuration cache load:
1. The provider is evaluated to yield `"someFile.txt"`
2. The path is resolved using the **isolate's file collection factory** 
3. This factory has `baseDir = root build directory`
4. Resulting in `.../root/someFile.txt` output

**Stored Identity:** Provider specification without resolution context.  
**Post-Load Behavior:** Inherits resolution context of CC isolate's factory (root directory).  
**Conflict Source:** Omission of creator's resolution context during serialization.
