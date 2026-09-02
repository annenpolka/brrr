class Token:
    pass
orig = Token()
holder = {"t": orig}
def test_a():
    holder["t"] = Token()
def test_b():
    assert holder["t"] is orig
