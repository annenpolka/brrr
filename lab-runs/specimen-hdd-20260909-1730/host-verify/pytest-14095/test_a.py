from pytest import fixture

@fixture(scope="module")
def a():
    return 0

@fixture(scope="module")
def b(a):
    return a

def test_b_is_zero(b):
    assert b == 0

class TestClass:
    @fixture(scope="module")
    def a(self):
        return 1

    def test_b_is_one(self, b):
        assert b == 1
