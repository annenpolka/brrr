from dataclasses import dataclass

@dataclass
class S:
    acc: list

state = S(acc=[])

def test_a():
    state.acc.append("a")

def test_b():
    assert state.acc == [], state.acc
