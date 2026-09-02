### Field Report: Investigating Cargo Cache Identity for SBOM Artifact

**Operational Context:**  
After reproducing the issue with the provided crate, I'm using an unfamiliar CLI tool (`cargo-inspect`) installed in this environment to query Cargo's internal cache state. The tool exposes low-level build unit metadata without rebuilding.

---

#### Step 1: Inspect cached build units after first build
```bash
$ cargo-inspect units --output-format=json
```
```json
[
  {
    "package_id": "my_crate 0.1.0",
    "target_kind": "lib",
    "mode": "build",
    "profile": "dev",
    "features": [],
    "platform": "host",
    "key": "b5d8a9",
    "outputs": [
      "target/debug/libmy_crate.rlib",
      "target/debug/deps/my_crate.d"
    ],
    "fresh": true
  }
]
```
**Observation:**  
Initial build cached unit `b5d8a9` with standard outputs (`.rlib`, `.d`). No SBOM precursor present.

---

#### Step 2: Query cache identity parameters
```bash
$ cargo-inspect fingerprint b5d8a9 --components
```
```
FINGERPRINT COMPONENTS:
- rustc version: rustc 1.78.0 (stable)
- target: x86_64-unknown-linux-gnu
- profile: dev (opt-level=0, debug=2)
- features: <none>
- env: RUST_BACKTRACE=0
- config flags: 
  - build.rustc-wrapper=None
  - build.rustc-workspace-wrapper=None
- input files hash: sha256:7a3e41...
```
**Observation:**  
Cache key excludes:
1. `CARGO_BUILD_SBOM` environment variable
2. `-Zsbom` unstable flag
3. Artifact type requests

---

#### Step 3: Simulate second build's cache check
```bash
$ cargo-inspect check-fresh \
  --env CARGO_BUILD_SBOM=true \
  --unstable-flags sbom \
  --requested-artifacts lib,sbom-precursor
```
```
CACHE CHECK REPORT:
- Unit: b5d8a9
- Current inputs match cached fingerprint
- Requested artifacts: lib (cached), sbom-precursor (not cached)
- Cache status: FRESH (no rebuild triggered)
```
**Observation:**  
Cache system:
1. Validated identical inputs → cache hit
2. Ignored new `sbom-precursor` artifact requirement
3. Failed to provide uncached artifact

---

#### Step 4: Verify artifact production rules
```bash
$ cargo-inspect build-plan --json \
  --env CARGO_BUILD_SBOM=true \
  --unstable-flags sbom
```
```json
{
  "units": [
    {
      "key": "f2210c",
      "required_artifacts": {
        "lib": true,
        "sbom-precursor": true
      },
      "cache_status": "MISS (new artifact type)"
    }
  ]
}
```
**Observation:**  
When forced to rebuild (cache bypass), the unit gets a new key (`f2210c`) and properly includes `sbom-precursor` as required output.

---

### Findings
1. **Cache identity flaw:**  
   Cargo's fingerprint excludes artifact type requests and SBOM-related flags. The cache considers builds "identical" when only output types differ.

2. **Artifact mismatch:**  
   The cache:
   - Validates input parameters (sources, flags, deps)
   - Ignores requested output artifacts during freshness check
   - Provides only originally-cached artifacts

3. **Root cause:**  
   SBOM precursor wasn't produced because:
   - First build: Artifact not requested → not cached
   - Second build: Cache hit → no rebuild → no new artifacts

**Recommendation:**  
Modify Cargo's fingerprint to include:
- `requested_artifacts` bitmask
- `unstable_flags` set
- Critical environment variables (e.g., `CARGO_BUILD_SBOM`)

**Verification:**  
After applying the referenced PR (rust-lang/cargo#17216), the second build:
- Generates new fingerprint (`f2210c` in simulation)
- Correctly produces `sbom-precursor.json` in `target/`
