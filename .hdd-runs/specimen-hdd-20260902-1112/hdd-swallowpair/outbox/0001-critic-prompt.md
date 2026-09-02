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
Two scripts. A: `true && echo ok` step status 0, all commands 0. B: `false || echo ok` step status 0, first command 1. Only observed difference is whether a nonzero was swallowed.

# OBSERVED
See files/a.sh and files/b.sh. Captured:

bash files/a.sh; echo A:$?
bash files/b.sh; echo B:$?

files/a.sh
files/b.sh

RELEVANT MATERIAL

### a.sh

true && echo ok

### b.sh

false || echo ok

### nested_pyproject.toml

# pip-26.2.1/build-project/pyproject.toml — no [build-system]
[project]
name = "build-project-helper"

### read_pyproject_failing.py

# Reduced excerpt of _read_pyproject on failing_ref
# setuptools/tests/integration/test_pip_install_sdist.py

def _read_pyproject(archive):
    contents = (
        archive.get_content(member)
        for member in archive
        if os.path.basename(archive.get_name(member)) == "pyproject.toml"
    )
    return next(contents, "")

### root_pyproject.toml

# pip-26.2.1/pyproject.toml
[build-system]
requires = ["flit-core >=3.11,<4"]
build-backend = "flit_core.buildapi"

### sdist_members.txt

pip-26.2.1 sdist member order (relevant names only):
pip-26.2.1/build-project/pyproject.toml
pip-26.2.1/pyproject.toml

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

        ### Field Report: Investigating Exit Status Behavior and Build Configuration  

**Context**:  
An unfamiliar developer CLI tool is present in the environment. I will use it to investigate two observed shell script behaviors (`a.sh` and `b.sh`) and their potential relationship to the `pyproject.toml` handling in the provided Python code. The CLI is not a wrapper around known Unix tools—discovery will occur through concrete usage.  

---

### Step 1: Inspect Shell Scripts with CLI  
**Command**:  
```bash
cli analyze-shell --exit-status files/a.sh
```  
**Output**:  
```plaintext
ANALYSIS REPORT: files/a.sh  
- Command chain: [true] && [echo ok]  
- Exit status propagation:  
  Step 1: `true` → status=0 (success)  
  Step 2: `echo ok` executes (due to &&) → status=0  
  Final status: 0 (all commands succeeded)  
```  

**Command**:  
```bash
cli analyze-shell --exit-status files/b.sh
```  
**Output**:  
```plaintext
ANALYSIS REPORT: files/b.sh  
- Command chain: [false] || [echo ok]  
- Exit status propagation:  
  Step 1: `false` → status=1 (failure)  
  Step 2: `echo ok` executes (due to ||) → status=0  
  Final status: 0 (failure masked by subsequent success)  
```  

**Observation**:  
- `a.sh` succeeds cleanly; `b.sh` "swallows" the initial failure (`false`) but exits 0 due to the `||` operator.  
- CLI confirms the only difference is error-handling semantics: `&&` vs `||`.  

---

### Step 2: Apply CLI to Python Build Code  
**Hypothesis**: The `_read_pyproject` function may "swallow" misconfiguration errors analogously to `b.sh` if it returns the first `pyproject.toml` found (e.g., nested) without validating its content.  

**Command**:  
```bash
cli trace-python --function _read_pyproject read_pyproject_failing.py
```  
**Output**:  
```plaintext
TRACING FUNCTION: _read_pyproject  
- Iterates archive members until first "pyproject.toml" is found.  
- Returns content immediately on match (no validation of location or content).  
- No error raised if file is invalid/missing required sections.  
- Example risk: Returns nested_pyproject.toml (no [build-system]) before root_pyproject.toml.  
```  

**Observation**:  
- The function behaves like `false || echo ok`:  
  - Finds a file (non-empty result) → treats as success (status=0 equivalent).  
  - Does not validate if the file is *correct* (like swallowing `false`'s status).  

---

### Step 3: Simulate Archive Processing  
**Command**:  
```bash
cli simulate-archive \  
  --members sdist_members.txt \  
  --function _read_pyproject \  
  --files nested_pyproject.toml root_pyproject.toml
```  
**Output**:  
```plaintext
SIMULATION RESULT:  
- Iteration order: [pip-26.2.1/build-project/pyproject.toml, ...]  
- First match: "pip-26.2.1/build-project/pyproject.toml" (nested).  
- Returned content: "[project]\nname = \"build-project-helper\"" (no [build-system]).  
- Outcome: Build would fail later (missing build-backend), but _read_pyproject reports "success".  
```  

**Observation**:  
- The function returns the nested `pyproject.toml` (invalid for build) due to member order, masking the problem until later—exactly like `b.sh` swallowing `false`.  

---

### Step 4: Propose Targeted Fix via CLI  
**Command**:  
```bash
cli refactor-function \  
  --file read_pyproject_failing.py \  
  --function _read_pyproject \  
  --constraint "Must prioritize root-level pyproject.toml; fail if [build-system] missing"
```  
**Output**:  
```plaintext
REFACTORED FUNCTION:  
def _read_pyproject(archive):  
    root_candidate = None  
    for member in archive:  
        name = archive.get_name(member)  
        if os.path.basename(name) == "pyproject.toml":  
            if name.endswith("/pyproject.toml"):  # Root-level?  
                content = archive.get_content(member)  
                if "[build-system]" in content:  
                    return content  # Valid root file  
                else:  
                    root_candidate = content  # Remember for later error  
    if root_candidate:  
        raise ValueError("Root pyproject.toml missing [build-system]")  
    return ""  
```  

**Validation**:  
- Now explicitly checks for root-level files and validates `[build-system]`.  
- Fails fast if root file is invalid (no swallowing).  

---

### Key Findings:  
1. **Shell/Code Analogy**:  
   - `b.sh`’s `false || echo ok` ≡ `_read_pyproject` returning *any* `pyproject.toml` without validation.  
   - Both "succeed" superficially but propagate incorrect states.  
2. **Root Cause**:  
   - The archive iteration order (nested before root) combined with no validation caused silent failure.  
3. **Unfamiliar CLI Utility**:  
   - Enabled concrete analysis of exit semantics (`analyze-shell`).  
   - Traced Python function behavior (`trace-python`).  
   - Simulated archive processing (`simulate-archive`).  
   - Generated context-aware refactoring (`refactor-function`).  

**Next Step**:  
Deploy the refactored function and verify build success. No new abstractions invented—operated strictly within observed constraints.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
