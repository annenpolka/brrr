import pytest
class TestClass:
    @pytest.fixture(scope="class")
    def sample(self):
        return "sample"
    def test_sample(self, sample):
        assert sample == "sample"
