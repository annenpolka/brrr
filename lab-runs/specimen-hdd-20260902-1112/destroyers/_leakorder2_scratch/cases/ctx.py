from contextvars import ContextVar
v = ContextVar("v", default=None)
def test_a():
    v.set("a")
def test_b():
    assert v.get() is None
