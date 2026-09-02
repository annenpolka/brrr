class Bag:
    def __init__(self):
        self.xs = []
    def __call__(self):
        return self.xs
bag = Bag()
def test_a():
    bag.xs.append("a")
def test_b():
    assert bag.xs == [], bag.xs
