class Store:
    _acc = []
    @property
    def acc(self):
        return self._acc

store = Store()

def test_a():
    Store._acc.append("a")

def test_b():
    assert Store._acc == [], Store._acc
