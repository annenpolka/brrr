class Box:
    _bucket = []
    @property
    def bucket(self):
        return Box._bucket
def test_a():
    Box._bucket.append("a")
def test_b():
    assert Box._bucket == [], Box._bucket
