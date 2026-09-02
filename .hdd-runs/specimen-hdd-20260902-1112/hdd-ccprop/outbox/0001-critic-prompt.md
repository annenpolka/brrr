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

A Gradle configuration-cache hit is expected on the second `./gradlew :help --configuration-cache`. Instead the second run stores a new entry:

```
Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.
```

The third run then hits. Nothing in the build script reads `idea.io.use.nio2`. Some plugin or Kotlin-DSL compile path called `System.getProperties()` during configuration.

The developer wants to know which properties entered the configuration-cache identity, and which of those were actually read by configuration.

# OBSERVED

Public gradle/gradle#30145 / PR 38081. Failing world: a configuration-time `System.getProperties()` (or `props.putAll(System.getProperties())`) snapshots every system property into the configuration-cache fingerprint.

Kotlin DSL compilation can set `idea.io.use.nio2` via `setIdeaIoUseFallback` (JetBrains/kotlin `compiler/cli/cli-common/.../environment/util.kt`). Gradle also calls that helper. The property can differ between the first store and the second load even on CI agents with no IDE.

Public second-run log:

```
Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.
```

Third run hits. `help` does not mention the property.

Owned analog `files/cc_unused_prop.py` (host-executed):

```
used_keys path
unused idea.io.use.nio2
all_first <hash> all_second <other> all_same False
used_first <hash> used_second <same> used_same True
invalidate_unused True
```

This packet does not include a local Gradle clone. Do not execute Gradle on this host.

# COMMANDS

```
./gradlew :help --configuration-cache
# second run (failing):
#   cannot be reused because system property 'idea.io.use.nio2' has changed
python3 files/cc_unused_prop.py
```

Not executed on this lab host except the owned analog.

TREE

files/cc_unused_prop.py
files/cc_miss.txt

RELEVANT MATERIAL

### cc_miss.txt

Calculating task graph as configuration cache cannot be reused because system property 'idea.io.use.nio2' has changed.

### cc_unused_prop.py

#!/usr/bin/env python3
"""Owned analog: unused property in a full snapshot invalidates identity."""
import hashlib, json

USED = ("path",)
UNUSED = "idea.io.use.nio2"

def ident(props, mode):
    if mode == "all":
        payload = json.dumps(props, sort_keys=True)
    else:
        payload = json.dumps({k: props[k] for k in USED if k in props}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]

def main():
    a = {"path": "/app", UNUSED: "false"}
    b = {"path": "/app", UNUSED: "true"}
    print("used_keys", *USED)
    print("unused", UNUSED)
    print("all_first", ident(a, "all"), "all_second", ident(b, "all"), "all_same", ident(a, "all") == ident(b, "all"))
    print("used_first", ident(a, "used"), "used_second", ident(b, "used"), "used_same", ident(a, "used") == ident(b, "used"))
    print("invalidate_unused", ident(a, "all") != ident(b, "all") and ident(a, "used") == ident(b, "used"))

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

        ### Field Report: Investigating Configuration Cache Miss

**Operational Context:**  
Working within the provided environment with analog Python script (`cc_unused_prop.py`) and Gradle log snippet (`cc_miss.txt`). The unfamiliar CLI tool `cache-probe` is installed (discovered via `which cache-probe`). Its purpose: trace property access patterns in configuration-phase simulations.

---

#### Step 1: Verify environment and tool baseline
```bash
$ which cache-probe
/usr/local/bin/cache-probe

$ cache-probe --version
cache-probe 0.8.3 (configuration-phase tracer)
```

**Observation:**  
CLI responds with version. No documentation available. Proceeding with trial commands.

---

#### Step 2: Run analog script to generate baseline
```bash
$ python3 files/cc_unused_prop.py
used_keys path
unused idea.io.use.nio2
all_first a1b2c3d4e5f6 all_second f6e5d4c3b2a1 all_same False
used_first 98c7a6b54321 used_second 98c7a6b54321 used_same True
invalidate_unused True
```

**Observation:**  
Analog confirms unused property (`idea.io.use.nio2`) causes invalidation despite identical used properties (`path`). Matches Gradle's behavior.

---

#### Step 3: Apply `cache-probe` to analog output
```bash
$ cache-probe trace --source=files/cc_unused_prop.py --log=files/cc_miss.txt
[TRACE] Property access patterns detected:
  EXPLICIT_READ: path (via System.getProperty)
  IMPLICIT_SNAPSHOT: idea.io.use.nio2 (via System.getProperties() full capture)

[DIAGNOSTIC] Configuration identity contributors:
  USED: path
  UNUSED BUT CAPTURED: idea.io.use.nio2

[WARNING] 1 unused property in snapshot: 
  idea.io.use.nio2 (changed between runs)
```

**Observation:**  
CLI detects two access modes:  
- Direct read of `path` (explicitly used)  
- Full snapshot capture implicating `idea.io.use.nio2` (unused but included in identity)  

Output aligns with Gradle log's invalidation reason.

---

#### Step 4: Cross-reference with Gradle's behavior
```bash
$ cache-probe match --log=files/cc_miss.txt --pattern=IMPLICIT_SNAPSHOT
MATCH: System property 'idea.io.use.nio2' changed (IMPLICIT_SNAPSHOT)
  - Not directly read by configuration
  - Captured via full System.getProperties() call
  - Location: Kotlin DSL compilation (setIdeaIoUseFallback)
```

**Observation:**  
Tool confirms:  
1. `idea.io.use.nio2` was never directly accessed  
2. Inclusion in cache identity caused by Kotlin-DSL's `System.getProperties()` call  
3. Matches JetBrains/kotlin's `setIdeaIoUseFallback` behavior  

---

#### Step 5: Retry with narrowed properties
Simulate Gradle fix by restricting captured properties:
```bash
$ cache-probe simulate --used=path
[CONFIG_CACHE] Identity fingerprint: 98c7a6b54321
[RESULT] Run 1: Store entry
[RESULT] Run 2: Cache hit (fingerprint match)
```

**Observation:**  
When identity excludes implicitly captured properties (retaining only explicitly used `path`), cache hit occurs on second run. Confirms fix direction.

---

### Conclusions from Operations

1. **Root Cause:**  
   Kotlin-DSL compilation calls `System.getProperties()`, capturing all system properties (including `idea.io.use.nio2`) in configuration cache identity.

2. **Key Property Classification:**  
   | Property           | Accessed Explicitly? | In Cache Identity? | Causes Invalidation? |
   |--------------------|----------------------|--------------------|----------------------|
   | `path`             | Yes                  | Yes               | Only if changed     |
   | `idea.io.use.nio2` | No                   | Yes (implicit)    | Yes on change       |

3. **Resolution Path:**  
   - Gradle must stop including properties captured via `System.getProperties()` unless explicitly used  
   - Short-term mitigation: Avoid `System.getProperties()` in configuration phase  

**Unresolved Uncertainty:**  
Exact location of `System.getProperties()` call in Kotlin-DSL (line number) remains unknown without source access.

**Tool Artifacts:**  
Full `cache-probe` output saved to `/logs/cc_analysis_20240415.txt`

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
