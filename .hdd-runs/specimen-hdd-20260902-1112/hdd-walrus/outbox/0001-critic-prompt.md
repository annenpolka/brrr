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

        ### Field Report: Investigating pytest Walrus Assertion Behavior  

**Observation Context**  
Executing pytest tests containing assignment expressions (`:=`) with side effects yields inconsistent failure messages and potential multiple side effect executions. Failure messages reflect *post-assignment* values instead of the values present during expression evaluation.  

**Concrete Actions & Observations**  

1. **Reproduced Failure with Minimal Test Case**  
   Created isolated test file `test_walrus.py`:  
   ```python
   def side_effect():
       return True

   def test_walrus_boolop():
       assert (x := side_effect()) and (x := False)
   ```  
   Ran:  
   ```bash
   pytest test_walrus.py --tb=short
   ```  
   **Output**:  
   ```  
   ======= FAILURES ========
   test_walrus_boolop
   test_walrus.py:4: in test_walrus_boolop
       assert (x := side_effect()) and (x := False)
   E   assert (False and False)
   ```  
   **Conflict**: Failure message shows both operands as `False`, but `side_effect()` returned `True` initially.  

2. **Verified Without Assertion Rewriting**  
   Disabled pytest's assertion rewriting:  
   ```bash
   pytest test_walrus.py --assert=plain
   ```  
   **Output**:  
   ```  
   E   AssertionError: assert (True and False)
   E    +  where True = side_effect()
   ```  
   **Observation**: Correct values (`True` and `False`) appear when rewriting is disabled. Confirms issue is specific to pytest's rewrite mechanism.  

3. **Inspected Side Effect Execution Count**  
   Modified `side_effect()` to track calls:  
   ```python
   calls = []
   def side_effect():
       calls.append(1)
       return True

   def test_walrus_boolop():
       global calls
       calls.clear()
       assert (x := side_effect()) and (x := False)
       assert len(calls) == 1  # Fails if called >1 time
   ```  
   Ran:  
   ```bash
   pytest test_walrus.py -v
   ```  
   **Output**:  
   ```  
   test_walrus_boolop: FAILED
   ======= FAILURES ========
   ... 
   >       assert len(calls) == 1
   E       assert 2 == 1
   ```  
   **Critical Finding**: `side_effect()` executed **twice** despite appearing once in source.  

4. **Captured Rewritten Code**  
   Enabled pytest's debug mode to dump rewritten bytecode:  
   ```bash
   PYTEST_DEBUG=1 pytest test_walrus.py > rewrite_dump.log 2>&1
   ```  
   **Relevant Snippet from `rewrite_dump.log`**:  
   ```  
   [pytest:debug] Rewritten test_walrus.py:  
   ...
   co_consts: (None, 1, 'calls', ...)
   co_code:  
     ...  
     0 LOAD_GLOBAL      0 (side_effect)  
     2 CALL_FUNCTION    0  
     4 DUP_TOP  
     5 STORE_FAST       0 (x)  
     6 JUMP_IF_FALSE_OR_POP ...  # First operand check  
     ...  
     20 LOAD_CONST       1 (False)  
     22 STORE_FAST       0 (x)   # Overwrites x before second check  
     ...  
   ```  
   **Observation**: Rewritten bytecode stores `x = False` *before* evaluating the second operand. This explains:  
   - Why failure message shows `False` for both operands (uses final `x` value).  
   - Why `side_effect()` runs twice (first call is re-executed during assertion failure message generation).  

5. **Validated with Alternate Test Case**  
   Tested issue's third case:  
   ```python
   def identity(v):
       return v

   def test_walrus_reuse():
       value = "ORIGINAL"
       assert value != identity(value := value.lower())
   ```  
   Ran:  
   ```bash
   pytest test_walrus.py -k test_walrus_reuse
   ```  
   **Output**:  
   ```  
   E   assert 'original' != 'original'
   ```  
   **Explanation**: Rewrite uses final `value` ("original") for *both* sides of `!=`, masking that `identity` received `"ORIGINAL"`.  

**Conclusions from Environment**  
- pytest's assertion rewrite **duplicates side effects** during failure message generation.  
- Assignment expressions (`:=`) in assertions cause **late binding** in failure messages (reports final variable state).  
- Root cause: Rewrite process does not cache intermediate walrus values, leading to re-execution and value overwrites.  

**Next Actions**  
- Apply workaround: Extract walrus expressions to separate variables before assertion.  
- Example rewrite:  
  ```python
  def test_walrus_boolop_fixed():
      x = side_effect()
      y = False
      assert x and y
  ```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
