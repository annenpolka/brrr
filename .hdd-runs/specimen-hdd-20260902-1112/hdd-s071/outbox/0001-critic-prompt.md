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

A tiny build cache keys freshness by input hash only. First build writes `out.bin`
and also writes an empty `out.sbom` stub as a side effect of hashing (extra was
not requested). Second build asks for extra output `out.sbom` from the same
inputs. Cache reports FRESH. `out.sbom` exists. Its bytes are the empty stub.

The developer wants to know whether the extra file was produced for this request
or leftover from the identity write, and which requested outputs were outside
that identity.

# OBSERVED

Owned fixture files/cache_build_stub.py. Host-executed:

first BUILT extra_requested False extra_exists True extra_bytes 0 key 9280cc7e16e9
second FRESH extra_requested True extra_exists True extra_bytes 0 key 9280cc7e16e9
same_key True
stub_leftover True

# COMMANDS

python3 files/cache_build_stub.py

TREE

files/cache_build_stub.py

RELEVANT MATERIAL

### cache_build_stub.py

import hashlib, json, tempfile
from pathlib import Path

def key(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()[:12]

def build(cache, outdir, inputs, extra=False):
    k = key(inputs)
    hit = k in cache
    extra_path = outdir / "out.sbom"
    if not hit:
        (outdir / "out.bin").write_text("bin:" + inputs["src"])
        extra_path.write_text("")
        cache.add(k)
    status = "FRESH" if hit else "BUILT"
    return status, extra_path.exists(), extra_path.stat().st_size, k

def main():
    cache = set()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        inputs = {"src": "hello"}
        s1, e1, n1, k1 = build(cache, out, inputs, extra=False)
        s2, e2, n2, k2 = build(cache, out, inputs, extra=True)
        print("first", s1, "extra_requested", False, "extra_exists", e1, "extra_bytes", n1, "key", k1)
        print("second", s2, "extra_requested", True, "extra_exists", e2, "extra_bytes", n2, "key", k2)
        print("same_key", k1 == k2)
        print("stub_leftover", e2 and n2 == 0)

if __name__ == "__main__":
    main()

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

        ### Field Report: Cache Artifact Provenance Investigation  

**Command Sequence & Observations:**  

1. **Initial Cache State Inspection**  
   Ran the provided fixture to confirm baseline behavior.  
   ```bash
   python3 files/cache_build_stub.py
   ```  
   **Output:**  
   ```
   first BUILT extra_requested False extra_exists True extra_bytes 0 key 9280cc7e16e9
   second FRESH extra_requested True extra_exists True extra_bytes 0 key 9280cc7e16e9
   same_key True
   stub_leftover True
   ```  
   **Observation:**  
   Confirms the issue: `out.sbom` is empty in both builds despite being explicitly requested only in the second. Key `9280cc7e16e9` is reused.  

2. **Invoke Developer CLI for Cache Diagnostics**  
   Used the installed `cachetool` CLI to inspect the cache entry for key `9280cc7e16e9`.  
   ```bash
   cachetool inspect 9280cc7e16e9 --detail
   ```  
   **Output:**  
   ```
   Cache Key: 9280cc7e16e9
   Outputs Registered: 
     - out.bin
   Side Effects: 
     - out.sbom (stub, 0 bytes)
   Build Metadata:
     - Requested Outputs: [out.bin]
     - Extra Outputs: [out.sbom] (implicit)
   ```  
   **Observation:**  
   The cache entry explicitly lists `out.bin` as the only requested output during the first build. `out.sbom` is labeled as an "implicit" side effect.  

3. **Probe Output Provenance in Second Build**  
   Executed a forced rebuild with `cachetool` while requesting `out.sbom`:  
   ```bash
   cachetool build --inputs '{"src":"hello"}' --output out.bin --extra out.sbom --force
   ```  
   **Output:**  
   ```
   Building...  
   Outputs: 
     out.bin: UPDATED (hash: a1b2...)
     out.sbom: UPDATED (hash: c3d4...)
   Cache Miss (forced rebuild)
   ```  
   **Observation:**  
   Forcing a rebuild generates non-empty `out.sbom` (new hash). Confirms the stub was *not* generated during the second build in the original scenario.  

4. **Validate Cache Behavior with Explicit Extra Output**  
   Repeated the original sequence using `cachetool` directly:  
   ```bash
   # First build (no extra)
   cachetool build --inputs '{"src":"hello"}' --output out.bin
   # Second build (with extra)
   cachetool build --inputs '{"src":"hello"}' --output out.bin --extra out.sbom
   ```  
   **Output:**  
   ```
   [First run] Cache Miss. Built: [out.bin]. Side Effect: [out.sbom] (stub).  
   [Second run] Cache Hit. Outputs: [out.bin] (fresh), [out.sbom] (stub reused).  
   ```  
   **Observation:**  
   The tool explicitly distinguishes between requested outputs (`out.bin`) and reused side effects (`out.sbom`).  

**Key Findings:**  
- **Provenance of `out.sbom`**: The empty `out.sbom` in the second build is a *reused artifact* from the first build's implicit side effect, not generated anew.  
- **Outputs Outside Identity**: Only `out.bin` is treated as a cacheable output tied to the key. `out.sbom` is ephemeral and not part of the cache identity, even when requested.  
- **Root Cause**: The cache conflates explicit outputs with implicit side effects. Requesting `out.sbom` does not invalidate the cache hit because it isn’t part of the keying logic.  

**Unresolved Uncertainty:**  
The CLI confirms side effects aren’t tracked in cache keys, but it’s unclear if this is intentional design or a bug. Further testing with varied inputs/extra outputs is needed.  

**Recommended Next Command:**  
```bash
cachetool build --inputs '{"src":"world"}' --output out.bin --extra out.sbom
```  
To verify if changing inputs (new key) generates a non-stub `out.sbom` when explicitly requested.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
