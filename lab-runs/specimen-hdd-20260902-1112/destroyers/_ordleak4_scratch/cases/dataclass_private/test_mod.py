from dataclasses import dataclass

@dataclass
class S:
    _n: int = 0

state = S()

def test_a():
    state._n += 1

def test_b():
    assert state._n == 0, state._n
