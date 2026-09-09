import pytest

class TestFixt:

    @pytest.fixture(scope="class")
    def fixt(self):
        yield

    def test_1(self, fixt):
        pass

    def test_2(self, fixt):
        pass
