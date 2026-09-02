class Boom:
    def __repr__(self):
        raise RuntimeError("boom")

box = Boom()

def test_a():
    pass

def test_b():
    pass
