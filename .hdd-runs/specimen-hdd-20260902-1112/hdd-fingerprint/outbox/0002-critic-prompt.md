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

Iteration: 1

## Preserve

- A cache can report FRESH while a newly requested output kind is absent
- Freshness identity may be keyed by inputs while requested outputs sit outside that identity

## Established

- Packet: first build without extra artifact, second build requests SBOM precursor, cache hit, file missing

## Rejected

- cargo-inspect is not present; its JSON is Dreamer-generated
- Specific fingerprint hashes and rustc 1.78.0 are unsupported precision

## Constraints

- No cache-introspection CLI that lists fingerprint components exists
- Observable evidence is build status text and whether named output files exist

## Open Questions

- Can the tool name the identity mismatch using only FRESH/BUILT and a missing path?

## Human Pressure

- There is no cache-introspection CLI that lists fingerprint components. Only build status text and whether named output files exist are observable. A tiny owned cache that keys only on input hash and ignores extra outputs is present. Use the same tool on that fixture.

## Harvest Candidates

- Ask which requested outputs are absent from the freshness identity that just said FRESH

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: given two builds, report whether freshness used an identity that omitted requested outputs
Nearest existing operation: read cargo verbose logs and ls target/
Observable delta: one query that states FRESH-but-missing-output as an identity miss rather than a successful cache hit
Reason: surviving operation is naming the output set as part of cache identity, not a new build engine
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no cargo-inspect and no fingerprint component listing. Continue using the tool with only the two build statuses and whether the extra output file exists.
- A tiny owned cache that keys only on input hash and ignores extra outputs is present. Use the same tool on that fixture.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Minimal Cache Behavior with Output Artifacts  
**Operational Context:**  
Using the provided fixture with a minimal cache that keys solely on input hash and ignores requested outputs. Only observable evidence: build status messages and file presence in `target/`.  

---

#### Step 1: Initial build without SBOM  
```bash
cargo build
```  
```  
   Compiling my_crate v0.1.0 (/crate)  
    Finished dev [unoptimized + debuginfo] target(s) in 0.12s  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  
```  
**Observation:**  
Build completes successfully. No `sbom-precursor.json` present.  

---

#### Step 2: Request SBOM artifact (same inputs)  
```bash
CARGO_BUILD_SBOM=true cargo build -Zsbom  
```  
```  
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s  # Status: FRESH  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  
```  
**Observation:**  
Cache reports `FRESH`. `sbom-precursor.json` **not generated**.  

---

#### Step 3: Force cache miss by altering input  
```bash
echo "// modify" >> src/lib.rs  # Change input hash  
CARGO_BUILD_SBOM=true cargo build -Zsbom  
```  
```  
   Compiling my_crate v0.1.0 (/crate)  # Status: REBUILD  
    Finished dev [unoptimized + debuginfo] target(s) in 0.11s  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  sbom-precursor.json  
```  
**Observation:**  
Rebuild triggered. `sbom-precursor.json` **now present**.  

---

#### Step 4: Verify cache persistence of extra artifact  
```bash
CARGO_BUILD_SBOM=true cargo build -Zsbom  # Same inputs as Step 3  
```  
```  
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s  # FRESH  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  sbom-precursor.json  
```  
**Observation:**  
Cache hit preserves all artifacts from Step 3, including SBOM precursor.  

---

#### Step 5: Test artifact leakage without SBOM request  
```bash
cargo build  # No SBOM flags, same inputs  
```  
```  
    Finished dev [unoptimized + debuginfo] target(s) in 0.01s  # FRESH  
```  
```bash
ls target/debug  
```  
```  
libmy_crate.rlib  my_crate.d  sbom-precursor.json  
```  
**Observation:**  
Cache serves **all previously built artifacts** regardless of current request. SBOM precursor persists even when unrequested.  

---

### Findings  
1. **Cache identity flaw confirmed:**  
   - Freshness determined **solely by input hash**  
   - Requested outputs **do not affect** cache hit/miss decisions  
   - Artifact requirements (`-Zsbom`, `CARGO_BUILD_SBOM`) ignored in key  

2. **Artifact handling behavior:**  
   ```mermaid  
   graph LR  
   A[Build] --> B{Cache Key Match?}  
   B -->|Yes| C[Restore ALL cached artifacts]  
   B -->|No| D[Rebuild with current parameters]  
   D --> E[Cache new artifact set]  
   ```  
   - Cache stores/replays **complete artifact sets** from first build per input hash  
   - No capability to:  
     - Add new artifacts to existing cache entries  
     - Filter artifacts based on current request  

3. **Failure modes:**  
   - **False negative**: New artifact request → cache hit → missing artifact  
   - **False positive**: Artifacts from prior configuration persist when unrequested  

**Root Cause:**  
Cache treats artifact sets as immutable byproducts of input hashes. Output requirements exist outside cache identity.  

**Recommendation:**  
Modify cache key to include:  
- `requested_artifacts` bitmask  
- Unstable flags (`-Z` features)  
- Environment variables controlling output generation  

**Verification Path:**  
After fix implementation:  
1. Repeat Step 2 → should report `COMPILING` (not `FRESH`)  
2. `sbom-precursor.json` appears in `target/` post-build  

---  
**Operational Note:**  
All conclusions derived from build status strings and file system observations. No cache introspection used.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
