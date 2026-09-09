import pytest

@pytest.fixture(scope="module")
def a():
    return 4

@pytest.fixture(scope="module")
def b(a):
    return a * 2

class TestA:
    def test_b(self, b):
        assert b == 8

class TestB:
    @pytest.fixture(scope="module")
    def a(self):
        return 3
    def test_b(self, b):
        assert b == 6
