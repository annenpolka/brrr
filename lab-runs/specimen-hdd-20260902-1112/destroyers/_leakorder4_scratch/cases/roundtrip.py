acc = []

def test_a():
    acc.append("a")
    acc.clear()

def test_b():
    assert acc == [], acc
