import threading
tls = threading.local()

def test_a():
    tls.n = 1

def test_b():
    assert getattr(tls, "n", 0) == 0, getattr(tls, "n", None)
