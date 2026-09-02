acc = []

def test_a():
    global acc
    acc = ["a"]

def test_b():
    assert acc == [], acc
