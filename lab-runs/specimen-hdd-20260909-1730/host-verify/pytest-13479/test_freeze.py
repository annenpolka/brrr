import pytest
from freezegun import freeze_time

@freeze_time()
class TestA:
    @pytest.fixture
    def ff(self):
        return 1

    def test_a(self, ff):
        assert ff == 1
