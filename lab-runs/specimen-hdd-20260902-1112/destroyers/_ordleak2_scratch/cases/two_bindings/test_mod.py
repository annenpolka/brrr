acc = []
other = []

def test_a():
    acc.append("a")
    other.append("o")

def test_b():
    assert acc == [] and other == [], (acc, other)
