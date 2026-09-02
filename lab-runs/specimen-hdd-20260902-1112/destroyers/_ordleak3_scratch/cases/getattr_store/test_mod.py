class Box:
    def __init__(self):
        object.__setattr__(self, "_store", {"n": 0})
    def __getattr__(self, name):
        return object.__getattribute__(self, "_store")[name]
    def __setattr__(self, name, value):
        object.__getattribute__(self, "_store")[name] = value

box = Box()

def test_a():
    box.n = 1

def test_b():
    assert box.n == 0, box.n
