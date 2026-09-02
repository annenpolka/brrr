class Box:
    __slots__ = ("n", "__dict__")
    def __init__(self):
        self.n = 0
        self.extra = 0

box = Box()

def test_a():
    box.n += 1
    box.extra += 1

def test_b():
    assert box.n == 0 and box.extra == 0, (box.n, box.extra)
