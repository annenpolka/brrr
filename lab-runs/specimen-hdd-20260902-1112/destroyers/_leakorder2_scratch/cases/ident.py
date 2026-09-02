orig = object()
holder = [orig]
def test_a():
    holder[0] = object()
def test_b():
    assert holder[0] is orig
