from collections import namedtuple
Box = namedtuple("Box", "acc")
state = Box(acc=[])

def test_a():
    state.acc.append("a")

def test_b():
    assert state.acc == [], state.acc
