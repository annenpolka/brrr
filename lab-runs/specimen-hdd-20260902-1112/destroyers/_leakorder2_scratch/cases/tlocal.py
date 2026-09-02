import threading
loc = threading.local()
def test_a():
    loc.v = ["a"]
def test_b():
    assert not hasattr(loc, "v")
