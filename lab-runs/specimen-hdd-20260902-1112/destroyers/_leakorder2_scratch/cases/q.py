import queue
q = queue.Queue()
def test_a():
    q.put("a")
def test_b():
    assert q.empty()
