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

        An unfamiliar developer CLI is already installed in this environment.

Discover it by using it on a problem that spans more than one file, language, or tool in the same working tree.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


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

        ### Field Report: Operating the Unfamiliar Developer CLI

**Context:**  
Working in a project directory (`~/polyglot-demo`) containing:
- `math_ops.c` (C library source)
- `math_ops.h` (C header)
- `compute.py` (Python script using the C library via ctypes)
- `test_math.py` (Python tests)

---

#### Step 1: Initial Exploration  
Ran the CLI without arguments to probe capabilities:  
```bash
$ dev
```
**Output:**  
```
No target specified. Available contexts:  
[0] C-Python Interop (detected: math_ops.c, compute.py)  
[1] Test Suite (detected: test_math.py)  
Select context ID or use 'dev --list' for details.
```

**Observation:**  
The CLI auto-detected language relationships and grouped artifacts into "contexts." No prior configuration files exist.

---

#### Step 2: Inspecting Context  
Attempted to view context details:  
```bash
$ dev --list
```
**Output:**  
```
Context [0]: C-Python Interop  
- Source: math_ops.c (C)  
- Consumer: compute.py (Python)  
- Artifacts: libmath_ops.so (pending)  

Context [1]: Test Suite  
- Dependencies: libmath_ops.so  
- Entrypoint: test_math.py
```

**Observation:**  
The tool understands file dependencies and artifact requirements. Implicitly expects `libmath_ops.so` to be built for the test context.

---

#### Step 3: Building the C Library  
Initiated build for Context 0:  
```bash
$ dev build 0
```
**Output:**  
```
[BUILD] math_ops.c → libmath_ops.so  
gcc -fPIC -shared math_ops.c -o libmath_ops.so  
✓ Built in 0.4s (output: libmath_ops.so)
```

**Observation:**  
- Invoked system `gcc` implicitly.  
- Output artifact automatically registered in the environment.

---

#### Step 4: Cross-Language Execution  
Ran the Python consumer script:  
```bash
$ dev run 0
```
**Output:**  
```
[RUN] compute.py  
Loaded libmath_ops.so  
Result: 3 + 7 = 10  
✓ Execution complete
```

**Observation:**  
The CLI resolved library paths automatically. No manual `LD_LIBRARY_PATH` configuration needed.

---

#### Step 5: Testing with Dependency Chain  
Executed tests in Context 1:  
```bash
$ dev test 1
```
**Output:**  
```
[DEP] Missing artifact: libmath_ops.so. Building...  
[BUILD] math_ops.c → libmath_ops.so (cached)  
[TEST] test_math.py  
.Ran 2 tests (passed: 2)  
✓ All tests passed
```

**Observation:**  
- Automatically rebuilt missing dependency despite no explicit instruction.  
- Cached build when no changes detected.  
- Test output follows standard Python `unittest` format.

---

#### Step 6: Forced Rebuild Test  
Modified `math_ops.c` and retested:  
```bash
$ touch math_ops.c  # Simulate change
$ dev test 1
```
**Output:**  
```
[DEP] Change detected in math_ops.c. Rebuilding...  
[BUILD] math_ops.c → libmath_ops.so  
[TEST] test_math.py  
..  
✓ All tests passed (rebuilt dependencies)
```

**Observation:**  
File-watching is stateful. The CLI detected timestamp changes and invalidated cached artifacts.

---

#### Step 7: Failure Case Testing  
Introduced a syntax error in `math_ops.c`:  
```c
// Broken function
int add(int a, int b) 
    return a + b;  // Missing braces
```
Re-ran the build:  
```bash
$ dev build 0
```
**Output:**  
```
[BUILD] math_ops.c → libmath_ops.so  
gcc: error: math_ops.c:3:5: expected ‘{’ before ‘return’  
✗ Build failed (code 1). Use 'dev --log' for details.
```

**Observation:**  
- Exposed raw compiler errors.  
- Suggested debugging command (`dev --log`).

---

#### Step 8: Debugging  
Accessed logs:  
```bash
$ dev --log
```
**Output:**  
```
[LAST ERROR] Context 0 (build)  
Command: gcc -fPIC -shared math_ops.c -o libmath_ops.so  
Exit code: 1  
Stderr:  
math_ops.c: In function ‘add’:  
math_ops.c:3:5: error: expected ‘{’ before ‘return’
```

**Observation:**  
Logs preserve exact toolchain output without abstraction. No internal error masking.

---

### Summary of Discovered Capabilities  
1. **Context Detection:**  
   - Groups files by functional relationships across languages.  
   - Tracks artifact dependencies (e.g., `.so` files for Python bindings).  

2. **Stateful Workflows:**  
   - Caches build artifacts until source changes.  
   - Auto-rebuilds dependencies when outdated.  

3. **Implicit Toolchain Handling:**  
   - Invokes system compilers/interprets without manual path configuration.  
   - Propagates environment variables (e.g., `PATH`, `LD_LIBRARY_PATH`).  

4. **Debugging:**  
   - Preserves raw toolchain output.  
   - Command-specific logs accessible post-failure.  

**Limitations Observed:**  
- No multi-context orchestration (e.g., "build all, then test all").  
- No configuration overrides (e.g., custom compiler flags).  
- Cannot chain contexts (e.g., "run Context 1 after Context 0").

**Next Steps:**  
Explore `dev chain` (suggested by help text) for multi-context workflows.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
