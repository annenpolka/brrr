from contextvars import ContextVar
v = ContextVar("ordleak4", default=0)

def test_a():
    v.set(1)

def test_b():
    assert v.get() == 0, v.get()
