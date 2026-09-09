import pytest


class TestClass:

    @classmethod
    @pytest.fixture(scope="class")
    def sample(cls):
        return "sample"

    def test_sample(self, sample):
        assert sample == "sample"
