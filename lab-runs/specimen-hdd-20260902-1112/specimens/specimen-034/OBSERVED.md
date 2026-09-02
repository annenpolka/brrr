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
