acc = []

def test_a():
    global acc
    del acc

def test_b():
    global acc
    assert "acc" in globals()
    acc = ["reborn"]
