import threading
lock = threading.Lock()

def test_a():
    lock.acquire()

def test_b():
    assert not lock.locked(), "locked"
