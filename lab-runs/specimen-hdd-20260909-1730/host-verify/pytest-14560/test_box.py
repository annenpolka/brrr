import pytest

class DictWrap(dict):
    def __getattr__(self, name):
        return self[name]

@pytest.mark.parametrize("val", [DictWrap(a=1)])
def test_wrap(val):
    assert val["a"] == 1

@pytest.mark.parametrize("val", [{"a": 1}])
def test_plain_dict(val):
    assert val["a"] == 1
