acc = []

def test_a():
    global acc
    acc.append("a")
    acc = list(acc)

def test_b():
    assert acc == [], acc
