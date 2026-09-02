# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A crate is built once. A second build requests an extra artifact kind (SBOM precursor) for the same unit via `CARGO_BUILD_SBOM=true` and `-Zsbom`. Cargo reports the unit fresh. The extra artifact is missing from the target directory.

The developer wants to know what the cache considered “the same build” and which requested outputs were not part of that identity.

# OBSERVED

Public rust-lang/cargo#15695 / PR 17216.

1. Build without SBOM — succeeds, unit in cache.
2. Rebuild same unit with SBOM requested.
3. Cache hit. Expected SBOM precursor is not in top-level target output.

Regression test on the PR: build once without SBOM, enable it, assert precursor appears. On the failing revision it does not.

# COMMANDS

```
cargo build
CARGO_BUILD_SBOM=true cargo build -Zsbom
ls target/  # precursor missing on failing revision
```
Do not run cargo against untrusted checkouts on the host.

crate/
  Cargo.toml
  src/lib.rs
target/   # unit cached; extra output kind absent

RELEVANT MATERIAL

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
