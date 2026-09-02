acc = []

def test_a():
    acc.append("a")

def test_b():
    acc.append("b")
    assert acc == ["b"], acc
