class Box:
    def __init__(self):
        self._n = 0

box = Box()

def test_a():
    box._n += 1

def test_b():
    assert box._n == 0, box._n
