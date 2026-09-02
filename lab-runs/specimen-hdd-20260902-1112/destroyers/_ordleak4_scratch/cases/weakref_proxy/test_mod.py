import weakref
class Box:
    def __init__(self):
        self.n = 0
box = Box()
proxy = weakref.proxy(box)

def test_a():
    proxy.n += 1

def test_b():
    assert box.n == 0, box.n
