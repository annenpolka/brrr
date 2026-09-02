box = {"n": float("nan")}

def test_a():
    box["n"] = 1.0

def test_b():
    import math
    assert math.isnan(box["n"]), box
