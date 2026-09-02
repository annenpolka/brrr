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
