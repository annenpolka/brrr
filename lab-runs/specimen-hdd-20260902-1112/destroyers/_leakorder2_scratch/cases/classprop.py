class Box:
    bucket = []
    @classmethod
    def poke(cls):
        cls.bucket.append("a")
def test_a():
    Box.poke()
def test_b():
    assert Box.bucket == [], Box.bucket
