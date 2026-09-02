acc = []
other = set()

def test_a():
    acc.append("a")
    other.add("x")

def test_b():
    assert acc == [] and other == set(), (acc, other)
