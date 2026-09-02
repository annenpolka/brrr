class TestOrder:
    acc = []

    def test_a(self):
        self.acc.append("a")

    def test_b(self):
        assert self.acc == [], self.acc
