class Box:
    def __init__(self):
        self._n = 0
    @property
    def n(self):
        return self._n
    @n.setter
    def n(self, v):
        self._n = v

box = Box()

def test_a():
    box.n += 1

def test_b():
    assert box.n == 0, box.n
