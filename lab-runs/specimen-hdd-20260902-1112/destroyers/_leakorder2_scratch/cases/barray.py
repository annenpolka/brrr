buf = bytearray(b"xx")
def test_a():
    buf[0] = 65
def test_b():
    assert buf[0] == ord("x"), buf
