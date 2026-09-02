import hypothesis as h
import hypothesis.strategies as st

@h.given(st.dictionaries(st.integers(), st.integers()))
def test(d):
    h.note(f"{d=}")
    assert sorted(d) == list(d)
