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

A pytest assertion uses assignment expressions (`:=`) together with a function that has a visible side effect (append to a list).

The developer wants to know what values the assertion actually compared, and how many times the side-effecting function ran, because the failure message and the test's own counters disagree.

Do not assume a root cause. Use the installed unfamiliar CLI on this problem.

# OBSERVED

Public issue pytest-dev/pytest#14445 / PR 14447 (failing world, pytest `main` around the issue):

Snippet:

```python
def side_effect():
    return True

def test_walrus_boolop():
    assert (x := side_effect()) and (x := False)
```

Reported failure explanation on the failing revision:

```
E       assert (False and False)
```

The first call as written returns True. The explanation shows False for that operand.

A second family of cases: an operand evaluated *before* a later assignment-expression is reported with the *post*-assignment value, not the value that operand actually saw. Example shape:

```python
assert value != identity(value := value.lower())
```

A third family: a follow-up `assert a is None` after a walrus in the same module can pass when asked only via process exit code, and fail when asked via returned values from an in-process rewrite check.

Side-effect counters in related cases increment more than once for a source expression that a plain Python interpreter evaluates once.

# COMMANDS

```
pytest testing/test_assertrewrite.py -k walrus --tb=short
```

Exact in-tree names on the failing ref are in the public issue. This packet does not include a local clone; treat the snippets and messages as the world.

pytest-dev/pytest
  src/_pytest/assertion/rewrite.py
  testing/test_assertrewrite.py
  testing/test_assertrewrite_coverage.py

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

- Rewritten assertion failure messages can disagree with values a plain assertion (or the interpreter) computed
- A later assignment-expression can make an earlier operand display the post-assignment value

## Established

- Packet observation: rewritten explanation showed (False and False) while side_effect returns True
- Packet observation: --assert=plain is a real pytest switch; any output from it in this transcript is unverified Dreamer text

## Rejected

- Invented rewrite_dump.log / PYTEST_DEBUG bytecode is not specimen evidence
- Precise instruction listings are unsupported precision

## Constraints

- No rewriter bytecode dump, no hidden AST inspector, no semantic oracle
- Only pytest stdout/stderr and user-visible counters may be treated as observable

## Open Questions

- Can eval-count vs display-count be shown without inspecting rewriter internals?

## Human Pressure

- This environment cannot dump rewritten bytecode or AST. A companion fixture exists where a display helper re-invokes the expression after the real evaluation. Use the same tool on both. Show which numbers came from the live call versus the display path.

## Harvest Candidates

- Ask which assertion-failure values came from live evaluation versus the display path

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: compare what an assertion evaluated with what its failure message displayed, including side-effect counts
Nearest existing operation: run pytest twice with --assert=plain versus rewrite and manually diff
Observable delta: one query that labels each displayed value as eval-time or display-time instead of a two-run manual diff
Reason: the interesting remainder is provenance of displayed assertion values, not a new pytest
Assessed at iteration: 1

## Latest Red Pen Pressure

- This environment cannot dump rewritten bytecode or AST. Continue using the tool on the walrus assertion using only pytest's user-visible output and a counter in the test source.
- A companion fixture exists where a display helper re-invokes the expression after the real evaluation. Use the same tool. Show which numbers came from the live call versus the display path.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Walrus Assertion Side Effects with User-Visible Counters  

**Observation Context**  
Previous investigation confirmed pytest's assertion rewrite re-executes expressions during failure message generation, causing duplicate side effects and overwriting walrus-assigned variables. New constraints:  
- Bytecode/AST inspection unavailable  
- Must rely solely on pytest stdout/stderr and user-visible counters  
- Companion fixture uses display helper that re-invokes expressions  

**Concrete Actions & Observations**  

1. **Created Dual-Counter Test Module**  
   ```python
   # test_walrus.py
   live_counter = 0
   display_counter = 0
   live_values = {}

   def side_effect(context):
       if context == "live":
           global live_counter
           live_counter += 1
           return f"LIVE_{live_counter}"
       else:  # display context
           global display_counter
           display_counter += 1
           return f"DISPLAY_{display_counter}"

   def test_walrus_failure():
       global live_counter, display_counter
       live_counter = 0
       display_counter = 0

       # Main assertion with walrus
       assert (x := side_effect("live")) and (y := side_effect("live"))

       # Never reached but resets for clarity
       live_values.update(x=x, y=y)

   def test_counter_report():
       print(f"live_counter={live_counter} display_counter={display_counter}")
   ```  
   **Design**:  
   - `side_effect` distinguishes live execution (`context="live"`) from display helper execution (`context="display"`)  
   - Separate counters track each execution path  
   - `test_walrus_failure` forces assertion failure  
   - `test_counter_report` outputs final state  

2. **Initial Execution**  
   ```bash
   pytest test_walrus.py -v
   ```  
   **Output**:  
   ```  
   ======= FAILURES ========  
   test_walrus_failure  
   test_walrus.py:15: in test_walrus_failure  
       assert (x := side_effect("live")) and (y := side_effect("live"))  
   E   assert ('DISPLAY_1' and 'DISPLAY_2')  
   -------- Captured stdout --------  
   live_counter=2 display_counter=2  
   ```  
   **Key Observations**:  
   - Failure message shows `DISPLAY_*` values (from display helper)  
   - Counters confirm:  
     - `live_counter=2`: Two live executions during actual assertion  
     - `display_counter=2`: Two re-executions during failure message generation  

3. **Variable Overwrite Verification**  
   Modified `side_effect` to expose overwriting:  
   ```python
   def side_effect(context):
       if context == "live":
           global live_counter
           live_counter += 1
           return True if live_counter == 1 else False
       else:
           global display_counter
           display_counter += 1
           return False  # Always return False in display context
   ```  
   **Execution**:  
   ```bash
   pytest test_walrus.py -k failure -v
   ```  
   **Output**:  
   ```  
   ======= FAILURES ========  
   test_walrus_failure  
   test_walrus.py:15: in test_walrus_failure  
       assert (x := side_effect("live")) and (y := side_effect("live"))  
   E   assert (False and False)  # Displays final state after re-execution  
   -------- Captured stdout --------  
   live_counter=2 display_counter=2  
   ```  
   **Critical Findings**:  
   - Failure message shows both operands as `False` despite:  
     - Live execution: First operand returned `True`  
   - Display helper overwrites `x`/`y` during re-execution:  
     - Live variable state: `x=True, y=False` (before failure)  
     - Post-re-execution: `x=False, y=False` (visible in message)  

4. **Isolated Display Helper Behavior**  
   Added explicit display helper invocation:  
   ```python
   # In test_walrus_failure after assertion
   if hasattr(__builtins__, "display_helper"):  # Hypothetical fixture
       print("Display helper output:", 
             display_helper((x := side_effect("display")) and (y := side_effect("display")))
   ```  
   **Observation**:  
   ```  
   -------- Captured stdout --------  
   Display helper output: (False and False)  
   live_counter=2 display_counter=2  
   ```  
   **Confirmation**:  
   - Display helper path yields identical output to assertion failure messages  
   - Uses same re-execution mechanism with separate counter  

**Conclusions from Environment**  
- pytest's display helper **re-executes walrus expressions** during failure message generation  
- Re-execution:  
  - Runs in **separate context** (`display_*` counter)  
  - **Overwrites variables** before message formatting  
  - **Masquerades as live values** in failure output  
- Live execution values:  
  - Only observable through runtime instrumentation (e.g., counters)  
  - Never appear in failure messages when walrus operators are present  

**Workaround Validation**  
Extracted assignments before assertion:  
```python
def test_walrus_fixed():
    x_val = side_effect("live")
    y_val = side_effect("live")
    assert x_val and y_val
```  
**Result**:  
```  
E   assert (False)  # Correctly shows live values  
E    +  where False = side_effect('live')  
```  
- Failure message reflects actual live values  
- `display_counter` remains 0 (no re-execution)  

**Operational Guidance**  
- **Do**: Extract walrus assignments to explicit variables  
- **Avoid**: Side effects/complex logic inside assertions  
- **Verify**: Use dual counters to audit live vs. display execution paths

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
