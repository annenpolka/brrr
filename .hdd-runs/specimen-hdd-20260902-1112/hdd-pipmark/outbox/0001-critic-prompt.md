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

A package extra `bar` is gated by an environment marker that is false on this interpreter (`python_version < "3"` on 3.14). Install still materializes the extra.

The developer wants to know whether the extra was installed even though its marker failed, and which extra should have been skipped.

# OBSERVED

Owned files/marker_extra.py. Host-executed:

extra bar
marker_ok False
installed True
should_skip True
wrongly_installed True

# COMMANDS

python3 files/marker_extra.py

TREE

files/marker_extra.py

RELEVANT MATERIAL

### marker_extra.py

#!/usr/bin/env python3
"""Owned analog: extra install ignores environment marker."""
def extra_wanted(extra, marker_ok):
    # failing: extra always installed
    return True

def extra_wanted_fixed(extra, marker_ok):
    return bool(marker_ok)

def main():
    extra = "bar"
    marker_ok = False  # python_version < "3" on 3.14
    installed = extra_wanted(extra, marker_ok)
    print("extra", extra)
    print("marker_ok", marker_ok)
    print("installed", installed)
    print("should_skip", not marker_ok)
    print("wrongly_installed", installed and not marker_ok)

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

        ### Field Report: Investigating Package Extra Marker Issue

**Current Environment State:**
- Python 3.14 interpreter
- Unfamiliar CLI tool detected in PATH (identifier: `envcli` via `which envcli`)
- `marker_extra.py` script outputs contradictory extra installation status

**Hypothesis:**  
The CLI tool (`envcli`) may provide diagnostics for environment marker enforcement. Need to verify if it can detect the package extra inconsistency reported by `marker_extra.py`.

---

#### Step 1: CLI Tool Discovery
```bash
envcli --version
```
**Output:**  
```
EnvInspector/0.7 (environment integrity scanner)
```

#### Step 2: Scan Active Environment
```bash
envcli scan --extras
```
**Output:**  
```
ERROR: Missing target. Use:
  envcli scan <PACKAGE_NAME>|all
```

#### Step 3: Identify Package Name from Script  
Inspected `marker_extra.py` for package references (none found). Broad scan attempted:
```bash
envcli scan all --extras
```
**Output:**  
```
Scanning all packages...  
* numpy==1.24.3 [no extras]  
* requests==2.28.2 [no extras]  
* corelib==3.14.0 [extras: bar]  # <-- Suspect package
```

#### Step 4: Inspect Problem Package
```bash
envcli inspect corelib --extras
```
**Output:**  
```
Package: corelib==3.14.0
Extras declared:
  bar (marker: python_version < "3")

Environment check:
  - Interpreter: Python 3.14
  - Marker 'python_version < "3"': FAILED

Extras installation status:
  bar: INSTALLED (⚠️ marker failed)
```

#### Step 5: Validate Against Script  
Re-ran script with package context:
```bash
python3 files/marker_extra.py
```
**Output:**  
```
extra bar
marker_ok False
installed True
should_skip True
wrongly_installed True  # Confirmed by CLI
```

#### Step 6: CLI Repair Attempt  
```bash
envcli repair corelib --extras
```
**Output:**  
```
Repairing extras for corelib:
  - Extra 'bar' removed (marker failed)
Success. Re-run scan to verify.
```

#### Step 7: Post-Repair Scan  
```bash
envcli inspect corelib --extras
```
**Output:**  
```
Package: corelib==3.14.0
[...]
Extras installation status:
  bar: NOT INSTALLED (remediation applied)
```

---

**Key Observations:**  
1. The CLI tool (`envcli`) detected the extra `bar` installed despite failed marker
2. Package `corelib` was identified as the affected package
3. Tool remediation removed the invalid extra
4. Script output was consistent with CLI diagnostics (marker_ok=False, installed=True)

**Unresolved Question:**  
Why did the package manager ignore the environment marker during initial installation? (Requires investigation of install logs - not within current CLI scope)

**Next Recommended Action:**  
```bash
envcli audit install-log corelib
```  
*(Pending verification of log access capabilities)*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
