**Field Report: Investigating Zeitwerk Identity Case B**

**Current Environment State:**
- Developer CLI tool `zeitwerk-diag` active (v2.7.0)
- Source-backed analysis mode engaged
- Preloaded environment state: `fxn/zeitwerk@failing_ref` (8100bd1)
- Loaded artifacts: `autoload_path_set_by_me_failing.rb`, `inception_failing.rb`, `leftover_identity_split.txt`

**Objective:**
Determine which identity `MyGem::Foo` used during Case B reload:
1. Leftover gem inception (foreign loader)
2. Current app constant (this loader)
3. Omitted (no autoload)

**Investigation Sequence:**

---

**Step 1: Simulate Namespace Registration**
```shell
zeitwerk-diag register-namespace \
  --loader-id gemloader_1 \
  --cpath MyGem \
  --inception-file /gems/mygem/lib/my_gem.rb
```
**Output:**
```
Registered inception: [cpath: MyGem, abspath: /gems/mygem/lib/my_gem.rb, loader: gemloader_1]
```

**Step 2: Initialize App Loader State**
```shell
zeitwerk-diag create-loader \
  --loader-id apploader_1 \
  --autoload-paths app/models
```
**Output:**
```
Created loader: apploader_1
Autoload paths: [app/models]
```

**Step 3: Inject App Constant Definition**
```shell
zeitwerk-diag add-constant \
  --loader-id apploader_1 \
  --cpath MyGem::Foo \
  --source-location app/models/my_gem/foo.rb
```
**Output:**
```
Defined constant: MyGem::Foo
Loader: apploader_1
Source: app/models/my_gem/foo.rb
Autoload? false
```

**Step 4: Query Identity for `MyGem::Foo` (Pre-Reload)**
```shell
zeitwerk-diag check-identity \
  --loader-id apploader_1 \
  --cpath MyGem::Foo \
  --method autoload_path_set_by_me_for?
```
**Output:**
```
Checking cref: MyGem::Foo
┌──────────────────────────────┐
│ Method execution summary     │
├─────────────┬────────────────┤
│ cref.path   │ "MyGem::Foo"   │
│ autoload?   │ nil            │
│ Branch taken│ else (inception)│
│ Result      │ nil            │
└─────────────┴────────────────┘
Identity: NOT CLAIMED (no autoload path set by this loader)
```

**Step 5: Query Identity for Parent `MyGem`**
```shell
zeitwerk-diag check-identity \
  --loader-id apploader_1 \
  --cpath MyGem \
  --method autoload_path_set_by_me_for?
```
**Output:**
```
Checking cref: MyGem
┌──────────────────────────────┐
│ Method execution summary     │
├─────────────┬────────────────┤
│ cref.path   │ "MyGem"        │
│ autoload?   │ nil            │
│ Branch taken│ else (inception)│
│ Result      │ /gems/mygem/lib/my_gem.rb │
└─────────────┴────────────────┘
Identity: CLAIMED (inception path returned)
```

**Step 6: Simulate Reload Operation**
```shell
zeitwerk-diag simulate-reload \
  --loader-id apploader_1 \
  --strategy full_unload
```
**Output:**
```
Reload sequence for apploader_1:
1. Unloading constants...
   - Scanning namespace: MyGem (claimed by loader? YES)
   - Removing MyGem::Foo (child of claimed namespace)
2. Rebuilding autoloads...
   - No autoload defined for MyGem::Foo
   - Namespace MyGem remains (gem inception still registered)
Post-reload state:
   MyGem::Foo → MISSING
```

**Step 7: Verify Registry State**
```shell
zeitwerk-diag inspect-registry \
  --cpath MyGem
```
**Output:**
```
Registry entry for MyGem:
┌─────────────┬──────────────────────────────┐
│ Key         │ Value                        │
├─────────────┼──────────────────────────────┤
│ cpath       │ MyGem                        │
│ abspath     │ /gems/mygem/lib/my_gem.rb    │
│ loader      │ gemloader_1                  │
│ loader match│ foreign (not apploader_1)    │
└─────────────┴──────────────────────────────┘
```

**Conclusions from Observations:**
1. **`MyGem::Foo` identity**:  
   - Direct check returns `nil` (not claimed by loader)  
   - **Classification**: Omitted (no autoload path)  

2. **Failure mechanism**:  
   - Parent namespace `MyGem` incorrectly claimed due to gem inception registry leak  
   - Reload unloads all constants under claimed namespaces regardless of origin  
   - App-defined constant removed as namespace child item  

3. **Case B identity resolution**:  
   ```mermaid
   graph TD
     A[MyGem::Foo identity] --> B[Direct ownership check]
     B -->|autoload_path_set_by_me_for?| C[Returns nil]
     A --> D[Namespace ownership]
     D -->|parent MyGem claimed| E[Constants destroyed during namespace purge]
     C --> F[Final classification: Omitted]
   ```

4. **Key defect confirmed**:  
   Registry's `inception?` method returns path without loader validation, causing cross-loader ownership contamination.

**Recommendation for Verification:**  
Run same sequence with patched `Registry.inception?(cpath, loader)` (post-f9b21aa) to observe loader-boundary enforcement. No immediate action taken - awaiting operator approval to load repaired specimen.
