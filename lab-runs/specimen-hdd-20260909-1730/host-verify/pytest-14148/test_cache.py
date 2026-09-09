import pytest

@pytest.fixture
def mydata(pytestconfig):
    return pytestconfig.cache.get("example/value", None)

def test_function(mydata):
    assert mydata is None
