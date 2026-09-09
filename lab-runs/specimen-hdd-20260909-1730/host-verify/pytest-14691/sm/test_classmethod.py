import pytest
class TestClass:
    @staticmethod
    @pytest.fixture(scope="class")
    def sample():
        return "sample"
    def test_sample(self, sample):
        assert sample == "sample"
