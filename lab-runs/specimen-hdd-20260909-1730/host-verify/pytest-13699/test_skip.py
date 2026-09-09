import pytest

def test_asynctest_support():
    pytest.importorskip("asynctest")
