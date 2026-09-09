from unittest import TestCase, skipIf
import pytest

@skipIf(True, "reason")
class Foo(TestCase):
    @pytest.fixture(autouse=True)
    def something(self):
        assert 0

    def test_bar(self):
        pass
