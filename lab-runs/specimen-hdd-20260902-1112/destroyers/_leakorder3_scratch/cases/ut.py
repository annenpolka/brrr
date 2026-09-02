class TestOrder:
    bucket = []
    def test_a(self):
        self.bucket.append("a")
    def test_b(self):
        assert self.bucket == [], self.bucket
