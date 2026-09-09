import types

def test_attribute(monkeypatch):
    obj = types.SimpleNamespace()
    with monkeypatch.context() as mp:
        mp.delattr(obj, "attr", raising=False)
        obj.attr = 42
    assert hasattr(obj, "attr")
