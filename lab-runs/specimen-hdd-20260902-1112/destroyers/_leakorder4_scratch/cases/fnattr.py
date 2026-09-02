def holder():
    pass
holder.acc = []
def test_a():
    holder.acc.append("a")
def test_b():
    assert holder.acc == [], holder.acc
