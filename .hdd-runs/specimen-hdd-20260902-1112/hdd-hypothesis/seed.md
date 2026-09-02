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
