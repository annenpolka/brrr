box = {"n": 0}

def test_a():
    box["n"] = 1

def test_b():
    assert box["n"] == 0, box
