class Box:
    __slots__ = ("n",)
    def __init__(self):
        self.n = 0
box = Box()
def test_a():
    box.n = 1
def test_b():
    assert box.n == 0
