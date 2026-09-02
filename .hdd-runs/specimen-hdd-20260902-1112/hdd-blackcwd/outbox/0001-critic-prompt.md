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

`black --code` can keep the identity of a **previous project root / pyproject.toml** after the process CWD should have been a different directory. `find_project_root` is `@lru_cache`'d on `(srcs, stdin_filename)`. When `srcs` is empty it resolves `Path.cwd()` *inside* the cached function, so CWD is omitted from the cache key.

On failing_ref `c77093e228ff21a93638b42356aa0a4d2713aa17`:

```
@lru_cache
def find_project_root(
    srcs: Sequence[str], stdin_filename: str | None = None
) -> tuple[Path, str]:
    if stdin_filename is not None:
        srcs = tuple(stdin_filename if s == "-" else s for s in srcs)
    if not srcs:
        srcs = [str(_cached_resolve(Path.cwd()))]
    path_srcs = [_cached_resolve(Path(Path.cwd(), src)) for src in srcs]
    # walk parents for .git / .hg / pyproject.toml [tool.black]
```

Public report (psf/black PR 5152). In-process `black --code` from directory A then directory B (test `test_code_option_config` / `test_code_option_parent_config` with `change_directory`): leftover cached root from A; wrong pyproject.toml.

In-tree after the repair (not on failing_ref): public `find_project_root` resolves CWD and absolute srcs first; `_find_project_root_cached` is `@lru_cache`'d only on fully-resolved paths.

Case A — second `black --code` from the same CWD:
  project-root identity is current
  not leftover-after-cwd-change

Case B — `black --code` from a different CWD, leftover lru_cache:
  leftover: previous CWD's project root / pyproject.toml
  resolved CWD omitted from cache key (srcs=())
  wrong config applied

Case C — new process (empty lru_cache) from CWD B:
  current CWD root identity
  not leftover previous directory

Case D — CWD resolved before the cache key (post-repair shape, not on failing_ref):
  each directory gets its own pyproject.toml
  not leftover previous root

The developer wants to know which identity case B actually used for the project root after the CWD change: leftover previous-CWD pyproject, current CWD identity, or omitted (no cache).

# OBSERVED

Public psf/black PR 5152 squash `d246367ab471cd56298407858661d475c33b3e36` (parent `c77093e228ff21a93638b42356aa0a4d2713aa17`). Local black was not performed on this lab host.

PR body: when `srcs` is empty (`black --code`), `find_project_root` fell back to `os.getcwd()` inside `@lru_cache`. Cache key is only `(srcs, stdin_filename)`. Two calls from different directories with `srcs=()` share the leftover entry.

On failing_ref, `@lru_cache` sits on `find_project_root`. Resolved CWD is **not** part of the key. `_find_project_root_cached` is added by PR 5152.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-132 eslint leftover plugin name@version omitted from toJSON.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c77093e228ff21a93638b42356aa0a4d2713aa17
# src/black/files.py find_project_root @lru_cache

# public shape:
# leftover project root after black --code from a different CWD
# cache key omits resolved CWD when srcs is empty
# wrong pyproject.toml [tool.black]
```

Source-backed only. Do not execute untrusted checkouts on the host.

psf/black
  src/black/files.py
  tests/test_black.py
  pyproject.toml

RELEVANT MATERIAL

### find_project_root_failing.py

# Reduced excerpt of find_project_root on failing_ref
# src/black/files.py
# c77093e228ff21a93638b42356aa0a4d2713aa17
# CWD resolved inside @lru_cache. Key is (srcs, stdin_filename) only.

@lru_cache
def find_project_root(
    srcs: Sequence[str], stdin_filename: str | None = None
) -> tuple[Path, str]:
    if stdin_filename is not None:
        srcs = tuple(stdin_filename if s == "-" else s for s in srcs)
    if not srcs:
        srcs = [str(_cached_resolve(Path.cwd()))]
    path_srcs = [_cached_resolve(Path(Path.cwd(), src)) for src in srcs]
    # walk parents for .git / .hg / pyproject.toml [tool.black]

### leftover_identity_split.txt

Registry / fixture:
  black --code from two directories in one process
  leftover project-root pyproject after CWD change

Case A (second black --code, same CWD):
  current project-root identity
  not leftover-after-cwd-change

Case B (black --code from different CWD, leftover lru_cache):
  leftover: previous CWD's project root / pyproject.toml
  resolved CWD omitted from cache key (srcs=())
  wrong config applied

Case C (new process from CWD B):
  current CWD root identity
  not leftover previous directory

Case D (CWD resolved before cache key):
  each directory gets its own pyproject.toml
  not leftover previous root

Not this packet:
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)
  eslint leftover plugin name@version omitted from toJSON (specimen-132)

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

        ### Field Report: Investigating `black` Project Root Cache Behavior in Case B

**Operational Context:**  
Using the installed `black` formatter (version 22.10.0, matching failing_ref behavior) and Python 3.10 interpreter to probe cache behavior. Environment prohibits cloning untrusted repos; analysis relies on isolated code execution and directory manipulation.

---

### Step 1: Reproduce Cache Retention Scenario  
Created two directories (`/tmp/projectA`, `/tmp/projectB`) with distinct `pyproject.toml` files:  

```bash
mkdir -p /tmp/projectA && echo "[tool.black]\nline-length = 80" > /tmp/projectA/pyproject.toml
mkdir -p /tmp/projectB && echo "[tool.black]\nline-length = 120" > /tmp/projectB/pyproject.toml
```

Launched Python REPL to simulate `black --code` calls:  
```python
import os
import sys
from black import find_project_root  # Patched to match failing_ref code

# Override with failing_ref implementation (simulated)
@lru_cache
def find_project_root(srcs, stdin_filename=None):
    if stdin_filename is not None:
        srcs = tuple(stdin_filename if s == "-" else s for s in srcs)
    if not srcs:
        srcs = (str(os.getcwd()),)  # Uses CWD at call time
    path_srcs = [os.path.abspath(src) for src in srcs]
    # ... (rest of original logic)

# Case B simulation
os.chdir("/tmp/projectA")
rootA, _ = find_project_root(())
print(f"Initial call (A): {rootA}")  # Output: /tmp/projectA

os.chdir("/tmp/projectB")
rootB, _ = find_project_root(())  # Same cache key: ((), None)
print(f"Subsequent call (B): {rootB}")
```

**Observation:**  
```
Initial call (A): /tmp/projectA
Subsequent call (B): /tmp/projectA  # Leftover from first call
```

**Failure Confirmed:**  
Cached project root remains `/tmp/projectA` despite CWD change to `/tmp/projectB`. Matches public report PSF/black#5152.

---

### Step 2: Verify Cache Key Composition  
Inspected cache keys using `find_project_root.cache_info()`:  
```python
print(find_project_root.cache_info())
```

**Output:**  
```
CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
```

**Key Insight:**  
Both calls used identical cache key `((), None)`. Current working directory not included in key.

---

### Step 3: Validate Root Determination Logic  
Added debug to simulated `find_project_root`:  
```python
    print(f"Active CWD: {os.getcwd()} | Using srcs: {path_srcs}")  # Added
```

**Output during first call (A):**  
```
Active CWD: /tmp/projectA | Using srcs: ['/tmp/projectA']
```

**Output during second call (B):**  
*No output* – Cache hit bypasses function body.

**Critical Finding:**  
**Actual project root identity:** Leftover `/tmp/projectA` value returned without re-computation. Current CWD (`/tmp/projectB`) never evaluated.

---

### Step 4: Contrast with Post-Fix Behavior  
Simulated repaired cache (key includes resolved paths):  
```python
@lru_cache
def fixed_find_project_root(srcs, stdin_filename=None):
    resolved_srcs = tuple(
        os.path.abspath(s) if s != "-" else stdin_filename 
        for s in (srcs or [os.getcwd()])
    )
    # ... (rest unchanged)

fixed_find_project_root(())  # Key now includes /tmp/projectA
os.chdir("/tmp/projectB")
fixed_find_project_root(())  # New key: (/tmp/projectB,)
```

**Output:**  
```
/tmp/projectB  # Correct current root
```

---

### Conclusion: Case B Identity  
**Project root used:** Leftover previous-CWD (`/tmp/projectA`).  
**Mechanism:**  
- Cache key `((), None)` identical across directories  
- `Path.cwd()` resolution occurs *inside* cached function  
- Cache hit returns prior result without re-executing CWD-dependent logic  

**Evidence Chain:**  
1. REPL output shows identical cache key  
2. Debug output confirms skipped re-evaluation  
3. Post-fix simulation resolves correctly  
4. Matches failure signature in PSF/black#5152  

**Uncertainty:** Exact filesystem traversal during initial cache population not verified (markers like `.git` could influence), but irrelevant to cache retention behavior.  

**Recommendation:** Adopt resolution strategy from PSF/black@d246367 (pre-resolve paths before caching).  

--- 

**Operational Note:** Environment constraints prevented live `black` execution on failing_ref; simulated logic matches source excerpts. No external repositories accessed.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
