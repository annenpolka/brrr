from contextvars import ContextVar
v = ContextVar("v", default=0)

def test_a():
    v.set(1)

def test_b():
    assert v.get() == 0
