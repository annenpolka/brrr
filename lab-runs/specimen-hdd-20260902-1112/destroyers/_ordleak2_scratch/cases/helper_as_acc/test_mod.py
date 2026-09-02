from helper import bucket as acc

def test_a():
    acc.append("a")

def test_b():
    assert acc == [], acc
