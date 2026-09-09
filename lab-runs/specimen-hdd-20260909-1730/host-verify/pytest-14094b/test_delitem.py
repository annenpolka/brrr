import pytest
import types

def test_delitem_existing():
    obj = {1: 2}
    with pytest.MonkeyPatch.context() as mp:
        mp.delitem(obj, 1)
        obj[1] = 3
    assert obj[1] == 2

def test_delitem_missing():
    obj = {}
    with pytest.MonkeyPatch.context() as mp:
        mp.delitem(obj, 1, raising=False)
        obj[1] = 3
    assert 1 not in obj

def test_delattr_missing():
    obj = types.SimpleNamespace()
    with pytest.MonkeyPatch.context() as mp:
        mp.delattr(obj, "prop", raising=False)
        obj.prop = 3
    assert not hasattr(obj, "prop")
