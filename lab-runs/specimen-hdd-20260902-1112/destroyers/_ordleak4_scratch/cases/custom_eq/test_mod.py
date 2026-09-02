class Box:
    def __init__(self):
        self.n = 0
    def __eq__(self, other):
        return True
    def __repr__(self):
        return "Box()"

box = Box()

def test_a():
    box.n += 1

def test_b():
    assert box.n == 0, box.n
