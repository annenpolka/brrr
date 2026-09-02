from collections import deque
acc = deque()

def test_a():
    acc.append("a")

def test_b():
    assert list(acc) == [], list(acc)
