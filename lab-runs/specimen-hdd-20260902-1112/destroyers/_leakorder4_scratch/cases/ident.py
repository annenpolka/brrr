sentinel = object()
box = {"s": sentinel}

def test_a():
    box["s"] = object()

def test_b():
    assert box["s"] is sentinel
