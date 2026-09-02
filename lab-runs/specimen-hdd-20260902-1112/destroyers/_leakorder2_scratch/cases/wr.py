import weakref
box = []
reg = weakref.WeakSet()
def test_a():
    box.append(object())
    reg.add(box[0])
def test_b():
    assert len(reg) == 0
