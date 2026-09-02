acc = []
noise = []

def test_a():
    acc.append("a")
    noise.append("n")

def test_b():
    assert acc == [], acc
