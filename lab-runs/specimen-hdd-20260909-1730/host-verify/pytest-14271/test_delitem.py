def test_item(monkeypatch):
    d = {}
    with monkeypatch.context() as mp:
        mp.delitem(d, "k", raising=False)
        d["k"] = 42
    assert "k" in d
    assert d["k"] == 42
