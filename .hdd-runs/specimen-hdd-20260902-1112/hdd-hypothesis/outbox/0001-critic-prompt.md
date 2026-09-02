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

A Hypothesis checkout sits at a11ec6f2ba4c1d08df6e355730d2a25d317492db (hypothesis 6.47.0 class).

A `@given` test fails on a dict whose iteration order is not sorted by key. The pytest assertion shows one order. The Hypothesis “Falsifying example” block prints another. Copying that printed example into `@example()` makes the test pass.

Python 3.7+ dicts preserve insertion order. The test under study depends on that order.

Outcome sought: why the printed failing input is not the input that failed, and what would make a reported example a faithful reproduction.

# OBSERVED

HypothesisWorks/hypothesis#3370, Python 3.8.11, pytest-5.4.3, hypothesis-6.47.0.

```python
import hypothesis as h
import hypothesis.strategies as st

@h.given(st.dictionaries(st.integers(), st.integers()))
def test(d):
    h.note(f"{d=}")
    assert sorted(d) == list(d)
```

Failure:

```
d = {0: 0, 1: 0}

    @h.given(st.dictionaries(st.integers(), st.integers()))
    def test(d):
        h.note(f"{d=}")
>       assert sorted(d) == list(d)
E       assert [0, 1] == [1, 0]
E         At index 0 diff: 0 != 1

-------------------------------------------------------------------------------- Hypothesis --------------------------------------------------------------------------------
Falsifying example: test(
    d={0: 0, 1: 0},
)
d={1: 0, 0: 0}
```

Three views of the same run disagree:

- pytest `d =` line: `{0: 0, 1: 0}` (sorted)
- assertion: `list(d)` is `[1, 0]` so insertion order was `1` then `0`
- Hypothesis note: `d={1: 0, 0: 0}`
- Hypothesis “Falsifying example”: `d={0: 0, 1: 0}`

Copying the Falsifying example into `@example(d={0: 0, 1: 0})` does not fail.

`hypothesis.vendor.pretty._dict_pprinter_factory` at this revision:

```python
        keys = obj.keys()
        # if dict isn't large enough to be truncated, sort keys before
        # displaying
        if not (p.max_seq_length and len(obj) >= p.max_seq_length):
            try:
                keys = sorted(keys)
            except Exception:
                # Sometimes the keys don't sort.
                pass
        for idx, key in p._enumerate(keys):
```

Existing test `test_dict` only checks `{}` and `{1: 1}`.

# COMMANDS

Not executed in this packet. Commands as reported.

```bash
git clone https://github.com/HypothesisWorks/hypothesis.git
cd hypothesis
git checkout a11ec6f2ba4c1d08df6e355730d2a25d317492db
```

Reproducer:

```bash
pytest -s test.py
```

Pretty-printer unit tests:

```bash
pytest hypothesis-python/tests/cover/test_pretty.py -k dict
python -c "from hypothesis.vendor import pretty; print(pretty.pretty({1: 1, 0: 0}))"
```

At this revision the last command prints `{0: 0, 1: 1}` even though the literal was written `{1: 1, 0: 0}`.

TREE (failing checkout fragment)

hypothesis/                              # a11ec6f2ba4c1d08df6e355730d2a25d317492db
└── hypothesis-python/
    ├── src/hypothesis/vendor/pretty.py  # _dict_pprinter_factory
    └── tests/cover/test_pretty.py       # test_dict

Working file:

test.py                                  # @given dict order assertion

RELEVANT MATERIAL

### hypothesis-python/src/hypothesis/vendor/pretty.py.fragment

# failing_ref a11ec6f2ba4c1d08df6e355730d2a25d317492db
# _dict_pprinter_factory inner

        if cycle:
            return p.text("{...}")
        p.begin_group(1, start)
        keys = obj.keys()
        # if dict isn't large enough to be truncated, sort keys before
        # displaying
        if not (p.max_seq_length and len(obj) >= p.max_seq_length):
            try:
                keys = sorted(keys)
            except Exception:
                # Sometimes the keys don't sort.
                pass
        for idx, key in p._enumerate(keys):
            if idx:
                p.text(",")
                p.breakable()
            p.pretty(key)
            p.text(": ")
            p.pretty(obj[key])
        p.end_group(1, end)

### hypothesis-python/tests/cover/test_pretty.py.fragment

def test_dict():
    assert pretty.pretty({}) == "{}"
    assert pretty.pretty({1: 1}) == "{1: 1}"

### test.py

import hypothesis as h
import hypothesis.strategies as st

@h.given(st.dictionaries(st.integers(), st.integers()))
def test(d):
    h.note(f"{d=}")
    assert sorted(d) == list(d)

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

        ### Field Report: Investigating Hypothesis Dictionary Printing Discrepancy

**Current Environment State:**
- Hypothesis commit: `a11ec6f2ba4c1d08df6e355730d2a25d317492db`
- Python 3.8.11
- Test file `test.py` contains order-sensitive dictionary test
- Hypothesis vendor pretty printer sorts small dict keys before printing

**Hypothesis:** The pretty printer's key sorting causes falsifying examples to lose insertion order information.

---

#### **Command Sequence & Observations**

1. **Confirm original failure:**
```bash
pytest -s test.py
```
```output
d = {0: 0, 1: 0}
>       assert sorted(d) == list(d)
E       assert [0, 1] == [1, 0]
E         At index 0 diff: 0 != 1
-------------------------------------------------------------------------------- Hypothesis --------------------------------------------------------------------------------
Falsifying example: test(
    d={0: 0, 1: 0},
)
d={1: 0, 0: 0}
```
*Observation:* Three conflicting views:
- Pytest shows `{0:0, 1:0}` (sorted keys)
- Assertion shows `[1, 0]` (insertion order: 1 first)
- Hypothesis note shows `{1:0, 0:0}` (insertion order)
- Falsifying example shows `{0:0, 1:0}` (sorted keys)

2. **Verify pretty printer behavior:**
```bash
python -c "from hypothesis.vendor import pretty; print(pretty.pretty({1: 1, 0: 0}))"
```
```output
{0: 0, 1: 1}
```
*Observation:* Vendor pretty printer sorts keys regardless of insertion order.

3. **Modify pretty printer to preserve insertion order:**
```bash
sed -i '/# if dict isn.t large enough to be truncated/,/pass/ s/^/# /' hypothesis-python/src/hypothesis/vendor/pretty.py
```
Modified code fragment:
```python
        keys = obj.keys()
        # # if dict isn't large enough to be truncated, sort keys before
        # # displaying
        # if not (p.max_seq_length and len(obj) >= p.max_seq_length):
        #     try:
        #         keys = sorted(keys)
        #     except Exception:
        #         # Sometimes the keys don't sort.
        #         pass
        for idx, key in p._enumerate(keys):
```

4. **Re-run test with modified printer:**
```bash
pytest -s test.py
```
```output
d = {1: 0, 0: 0}
>       assert sorted(d) == list(d)
E       assert [0, 1] == [1, 0]
E         At index 0 diff: 0 != 1
-------------------------------------------------------------------------------- Hypothesis --------------------------------------------------------------------------------
Falsifying example: test(
    d={1: 0, 0: 0},
)
d={1: 0, 0: 0}
```
*Observation:* All outputs now consistent:
- Pytest shows `{1:0, 0:0}` (insertion order)
- Assertion fails on `[1, 0]` (insertion order)
- Hypothesis note shows `{1:0, 0:0}`
- Falsifying example shows `{1:0, 0:0}`

5. **Verify reproduction fidelity:**
Added to `test.py`:
```python
@h.example(d={1: 0, 0: 0})
def test_repro():  # Separate test for explicit example
    d = {1: 0, 0: 0}
    assert sorted(d) == list(d)
```
```bash
pytest -s test.py::test_repro
```
```output
>       assert sorted(d) == list(d)
E       assert [0, 1] == [1, 0]
E         At index 0 diff: 0 != 1
```
*Observation:* Explicit example with insertion order now fails as expected.

6. **Sanity check pretty printer output:**
```bash
python -c "from hypothesis.vendor import pretty; print(pretty.pretty({1: 1, 0: 0}))"
```
```output
{1: 1, 0: 0}
```
*Observation:* Printer now preserves insertion order.

---

#### **Conclusions**

1. **Root Cause:**  
The vendor pretty printer's key sorting (`pretty._dict_pprinter_factory`) altered dictionary representation in falsifying examples, destroying insertion order information critical for reproduction.

2. **Faithful Reproduction Requirement:**  
Preserving insertion order in printed outputs matches:
- Python 3.7+ `repr()` behavior
- Actual test failure conditions
- Hypothesis's internal note mechanism

3. **Resolution Path:**  
Disabling key sorting in the pretty printer for dictionaries:
- Maintains Hypothesis's error reporting structure
- Preserves critical ordering information
- Aligns printed examples with actual failing inputs

**Unresolved Question:**  
Why did the original test's `h.note(f"{d=}")` show insertion order while the falsifying example used sorted keys?  
*Answer:* `h.note` uses Python's native string formatting (preserves order), while falsifying examples use Hypothesis's custom pretty printer (sorted keys).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
