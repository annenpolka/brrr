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

EOLANG `Transpilation.version()` can keep the identity of a **previous transpile-cache result** after `-Deo.trackSteps=true` should have written the intermediate XMIRs of the transpile train. The cache-key fingerprint folds plugin version, bundled XSL fingerprint, `trackLocations`, `coverage`, and superclass. `tracking.steps()` is not part of that key. A later build with the flag on takes the leftover previous no-step-files result.

On failing_ref `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`:

```
String version() {
    return String.format(
        "%s-%s-%b-%b-%s",
        this.version,
        new Fingerprint(
            Stream.concat(
                Arrays.stream(Transpilation.XSLS), Arrays.stream(Transpilation.IMPORTS)
            ).toArray(String[]::new)
        ).get(),
        this.tracking.locations(), this.coverage, this.superclass
    );
}
```

`TrSpy` (the writer of step XMIRs) lives inside the transform that only runs on a cache miss. `locations()` is already in the key two fields away. `steps()` is not.

Public report (objectionary/eo#7628). Run 1 default: step files 0. Run 2 `-Deo.trackSteps=true` with shared cache: step files 0. Control with a private cache: step files 10. Warm cache of the previous no-steps identity stays current.

In-tree after the repair (not on failing_ref): `version()` folds `this.tracking.steps()` as a third boolean in the key.

Case A — second transpile, same flags, same XSL fingerprint:
  cache identity is current
  not leftover-after-flag

Case B — trackSteps flipped on, leftover cache hit:
  leftover: previous no-step-files transpile result
  steps() omitted from version() key
  shared cache

Case C — private cache / cache miss:
  fresh step XMIRs
  not leftover previous result

Case D — steps() in the cache key (post-repair shape, not on failing_ref):
  new key after trackSteps change
  not leftover previous result

The developer wants to know which identity case B actually used for the transpile output after the flag change: leftover previous-cache result (steps omitted), current step-writing transform, or omitted (no cache).

# OBSERVED

Public objectionary/eo#7628 (closed 2026-08-26). PR 7675 merge `34df04c9a5eb26c6718c9512d930c4653627d70f` (first parent `09ba1e478be7e2ef4fd1293828512ef9d05f38e6`). Local eo was not performed on this lab host.

Issue body: `-Deo.trackSteps=true` writes intermediate XMIRs only on a cache miss; the flag is not part of the cache key. A build that had it off leaves a cached result that a later build with it on takes as it is, producing no step files. Shared-cache BUILD B step files 0; private-cache CONTROL step files 10.

On failing_ref, `Transpilation.version()` formats plugin version, XSL fingerprint, locations(), coverage, superclass. `tracking.steps()` is read only when constructing the Xsline, after the cache lookup.

Not this packet: specimen-117 sbt leftover last-write zinc Analysis. specimen-075 rustc incremental fingerprint. specimen-148 buildah leftover RUN --mount from-stage.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
# eo-maven-plugin Transpilation.version / tracking.steps

# public shape:
# leftover transpile cache after -Deo.trackSteps=true
# version() key omits steps(); locations() is present
# private cache / miss writes the step XMIRs
```

Source-backed only. Do not execute untrusted checkouts on the host.

objectionary/eo
  eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  EOLANG Transpilation.version() global transpile cache
  leftover no-step-files result after trackSteps=true

Case A (second transpile, same flags, same XSL fingerprint):
  current cache identity
  not leftover-after-flag

Case B (trackSteps flipped on, leftover cache hit):
  leftover: previous no-step-files transpile result
  steps() omitted from version() key
  shared cache

Case C (private cache / cache miss):
  fresh step XMIRs
  not leftover previous result

Case D (steps() in the cache key):
  new key after trackSteps change
  not leftover previous result

Not this packet:
  sbt leftover last-write zinc Analysis (specimen-117)
  rustc incremental fingerprint (specimen-075)
  buildah leftover RUN --mount from-stage (specimen-148)

### transpile_failing.java

// Reduced excerpt of Transpilation.version cache key on failing_ref
// eo-maven-plugin/src/main/java/org/eolang/maven/Transpilation.java
// 09ba1e478be7e2ef4fd1293828512ef9d05f38e6
// version() folds locations()/coverage/superclass. steps() omitted.
// leftover previous no-step-files result after -Deo.trackSteps=true.

String version() {
    return String.format(
        "%s-%s-%b-%b-%s",
        this.version,
        new Fingerprint(
            Stream.concat(
                Arrays.stream(Transpilation.XSLS), Arrays.stream(Transpilation.IMPORTS)
            ).toArray(String[]::new)
        ).get(),
        this.tracking.locations(), this.coverage, this.superclass
    );
}

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

        ### Field Report: Cache Identity Analysis for EOLANG Transpilation

**Tool Used:** `cacheprobe` (unfamiliar CLI for cache behavior simulation)  
**Environment State:** Pre-loaded with `transpile_failing.java` and `leftover_identity_split.txt` fixtures. Cache registry emulation enabled.

---

#### Step 1: Inspect Cache Key Structure
```bash
cacheprobe inspect-key --source transpile_failing.java --method version
```
**Output:**  
```
CACHE KEY STRUCTURE DETECTED:
Format: "%s-%s-%b-%b-%s"
Components:
  [0] version: String (e.g., plugin version)
  [1] fingerprint: String (hash of XSLS+IMPORTS)
  [2] locations: boolean (trackLocations flag)
  [3] coverage: boolean
  [4] superclass: String
MISSING COMPONENTS: 
  steps() flag (detected in source but not included in key)
```

**Observation:**  
The cache key excludes `tracking.steps()` on failing_ref. Only `locations()`, `coverage`, and `superclass` are included alongside static artifacts.

---

#### Step 2: Simulate Case B (Leftover Cache Hit)
```bash
cacheprobe simulate \
  --key-version "1.5.0" \
  --key-fingerprint "a1b2c3d4" \
  --key-locations false \
  --key-coverage true \
  --key-superclass "Object" \
  --cache-state "leftover:no-steps" \
  --flag-trackSteps true
```
**Output:**  
```
CACHE RESULT: HIT (identity: 1.5.0-a1b2c3d4-false-true-Object)
OUTPUT ARTIFACTS: 
  main.xmir (hash: 9f86d081) 
INTERMEDIATE ARTIFACTS: 
  step-*.xmir: 0 files (cache hit skipped transform)
PROVENANCE: 
  Cache entry created at 2026-08-25T14:30:00Z (flags: trackSteps=false)
```

**Failure/Retry:**  
Attempted to force step-file generation by appending `--force-miss`:  
```bash
cacheprobe simulate [...] --force-miss
```
**Output:**  
```
ERROR: Cannot force miss with --force-miss: key matches existing entry. 
Override requires cache-key change (e.g., modified inputs).
```

**Observation:**  
The tool confirms the leftover artifact (built without `trackSteps`) is reused when the key matches. The `trackSteps=true` flag is ignored during cache lookup.

---

#### Step 3: Verify Key Sensitivity
Test if adding `steps()` to the key would break the hit:  
```bash
cacheprobe simulate \
  [...] \ # Same parameters as Step 2
  --key-steps true \ # Hypothetical inclusion
  --cache-state "leftover:no-steps"
```
**Output:**  
```
CACHE RESULT: MISS (key mismatch: '1.5.0-a1b2c3d4-false-true-Object-true' != '1.5.0-a1b2c3d4-false-true-Object')
OUTPUT ARTIFACTS: 
  main.xmir (hash: 7d3b9e5a) 
INTERMEDIATE ARTIFACTS: 
  step-*.xmir: 10 files generated
```

**Observation:**  
Including `steps()` in the key (as in post-repair) causes a cache miss, forcing fresh step-file generation. This matches Case D.

---

#### Step 4: Control Test (Case C - Private Cache)
```bash
cacheprobe simulate [...] --cache-state "empty"
```
**Output:**  
```
CACHE RESULT: MISS (no entry)
OUTPUT ARTIFACTS: 
  main.xmir (hash: 7d3b9e5a) 
INTERMEDIATE ARTIFACTS: 
  step-*.xmir: 10 files generated
```

**Observation:**  
With no prior cache, `trackSteps=true` triggers step-file generation as expected.

---

### Conclusion
**Case B Identity:**  
The transpile output uses the **leftover previous-cache result** (steps omitted). This is proven by:  
1. Cache key matching the prior entry (without `steps()`).  
2. Reused artifact's provenance showing original `trackSteps=false`.  
3. Failed retry to force step-file generation without key changes.  

**Root Cause:**  
The cache key's omission of `tracking.steps()` allowed a logically incompatible artifact (built without step tracking) to satisfy a request for step files. The fix (adding `steps()` to the key) corrects this by making the key reflect all relevant build parameters.  

**Recommendation:**  
Audit cache keys for all build flags affecting output artifacts. Flags that alter output structure (not just content) must be part of the key.  

**Final Tool Output:**  
```
SUMMARY:
  Case A: Key match → fresh artifact (irrelevant to leftover)
  Case B: Key match → leftover artifact (no steps)
  Case C: Key missing → fresh artifact (steps generated)
  Case D: Key mismatch → fresh artifact (steps generated)
```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
