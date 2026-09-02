class Box:
    def __init__(self):
        object.__setattr__(self, "_hidden", 0)
    def __eq__(self, other):
        return True
    def __repr__(self):
        return "Box()"
    def bump(self):
        object.__setattr__(self, "_hidden", object.__getattribute__(self, "_hidden") + 1)
    def val(self):
        return object.__getattribute__(self, "_hidden")

box = Box()

def test_a():
    box.bump()

def test_b():
    assert box.val() == 0, box.val()
