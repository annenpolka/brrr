class Evil:
    def __repr__(self):
        raise RuntimeError("boom")
e = Evil()
def test_a():
    pass
def test_b():
    pass
