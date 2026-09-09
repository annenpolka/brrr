import pytest

@pytest.fixture(scope="class")
def class_fix():
    return "from-module"

class Base:
    def test_base(self, class_fix):
        assert class_fix == "from-module"

class TestChild(Base):
    def test_child(self, class_fix):
        assert class_fix == "from-module"
