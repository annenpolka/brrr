class Box:
    bucket = []

class TestOrder:
    def test_a(self):
        Box.bucket.append("a")
    def test_b(self):
        assert Box.bucket == [], Box.bucket
