import pytest

def test_delitem_existing():
    obj = {1:2}
    with pytest.Monkeypatch.context() as mp:
        mp.delitem(obj, 1)
        obj[1] = 3
    assert obj[1] == 2

def test_delitem_missing():
    obj = {}
    with pytest.Monkeypatch.context() as mp:
        mp.delitem(obj, 1, raising=False)
        obj[1] = 3
    assert 1 not in obj
