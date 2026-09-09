import pytest

@pytest.fixture
def skipping_base():
    pytest.skip("backend unavailable")

@pytest.fixture
def derived(skipping_base):
    return "derived"

@pytest.mark.parametrize("val", ["fixture:derived", "plain-1", "plain-2"])
def test_param(val):
    assert val
