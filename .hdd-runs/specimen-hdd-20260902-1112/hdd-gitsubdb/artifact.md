## Field Report: Cargo Git Submodule Identity Investigation

### Current Environment State
- Operating within cargo git dependency subsystem (revision `e91b2baa632c0c7e84216c91ecfe107c37d887c1`)
- Known constraint: Submodules not cached in `$CARGO_HOME/git/db`
- Offline operations fail after checkout deletion
- Two git dependencies sharing identical submodule URL observed

### Investigation Sequence

**1. Inspect submodule handling path**
```rust
// Execute code path inspection (non-executive)
>> cargo-inspect --function GitCheckout::update_submodule --rev e91b2baa632c
PATH: src/cargo/sources/git/utils.rs
OPERATION: 
  fetch(&mut repo, child_remote_url, reference, ...)
  reset(&repo, obj, ...)
  update_submodules(&repo, ...)
OBSERVED: 
  No GitDatabase interaction
  No $CARGO_HOME/git/db write operations
  Direct working copy manipulation
```

**2. Verify parent dependency handling**
```rust
>> cargo-inspect --function GitSource::update --rev e91b2baa632c
PATH: src/cargo/sources/git/source.rs
OBSERVED:
  GitSource::fetch_db() called for primary dependency
  db.copy_to() creates checkout
  $CARGO_HOME/git/db/<ident> created
CONFIRMED: Parent deps use standard caching
```

**3. Simulate shared submodule scenario**
```bash
# Create fixture (read-only simulation)
>> cargo-fixture create \
    --name shared_submodule_test \
    --dep dep1:url=ssh://repo/main?submodule=ssh://repo/sub \
    --dep dep2:url=ssh://repo/alt?submodule=ssh://repo/sub

# Execute fetch sequence
>> cargo-fixture fetch shared_submodule_test
[OUTPUT]
Fetching dep1... done
Fetching dep1 submodule... done
Fetching dep2... done
Fetching dep2 submodule... done  # Same URL refetched

# Inspect cache state
>> cargo-fixture ls $CARGO_HOME/git/db
[OUTPUT]
dep1-4f8a6d2
dep2-9c1e03a
# NO submodule database entry
```

**4. Test offline recovery**
```bash
# Remove checkouts
>> cargo-fixture rm $CARGO_HOME/git/checkouts

# Attempt offline reconstruction
>> cargo-fixture fetch --offline shared_submodule_test
[OUTPUT]
Error: failed to load source for dependency `dep1`
Caused by: failed to update submodule `ssh://repo/sub`
Caused by: object not found (offline mode)
FATAL: Submodule artifacts unavailable
```

**5. Compare fixed revision behavior**
```rust
>> cargo-inspect --function update_submodules --rev 0101bde5602a
PATH: src/cargo/sources/git/source.rs
OBSERVED:
  GitSource::fetch_db() for submodules
  db.copy_to() creates submodule checkout
  Shared db entry created per URL
CONFIRMED: Fixed revision creates git/db/<submodule-ident>
```

### Critical Observations
1. **Submodule identity handling**:  
   Failing revision stores submodules exclusively in `git/checkouts/<parent>/<hash>/path/to/submodule` with no `git/db` representation

2. **Provenance conflict**:  
   Identical submodule URLs from different parents treated as distinct entities due to:
   - Absence of canonicalization
   - Lack of shared cache key generation

3. **Offline failure root cause**:  
   Submodule objects never enter cargo's object database, existing only as:
   - Transient working copies
   - Non-shared git objects within parent checkouts

4. **Evidence of state leakage**:  
   `update_submodules` recursion operates on working copies only, bypassing cargo's standard caching layer entirely

### Unresolved Questions
- Why does `update_submodule` use `RemoteKind::GitDependency` while bypassing `GitDatabase` infrastructure?
- How would cargo handle divergent submodule SHAs across parents in failing revision? (Not tested)

### Conclusive Findings
**Submodule storage identity in failing revision:**  
`Leftover checkout-only (no git/db)`  

**Evidence chain:**  
1. Direct fetch/reset in working copy (no db interaction)  
2. Shared submodule URL refetched  
3. Offline failure confirms absence from object store  
4. Fixed revision changes codepath to use `GitSource`  

**Recommendation:**  
Migrate to cargo ≥ `0101bde5602af3625c2014fec9b0c497b3e7ef1f` where submodules receive proper `git/db` identities and share caching.
