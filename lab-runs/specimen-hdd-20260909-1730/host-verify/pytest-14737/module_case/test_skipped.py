import pytest
pytestmark = pytest.mark.skip(reason="package is disabled")
def test_should_be_skipped():
    assert False
