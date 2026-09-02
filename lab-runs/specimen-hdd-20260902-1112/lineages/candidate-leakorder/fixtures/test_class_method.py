class TestOrder:
    bucket = []

    def test_a(self):
        TestOrder.bucket.append("a")

    def test_b(self):
        assert TestOrder.bucket == [], TestOrder.bucket
