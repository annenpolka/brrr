import pytest


class Base:
    name = None
    variable = None

    def setup(self):
        self.variable = self.name
        print(f"setup: {self.variable}")

    def teardown(self):
        print(f"teardown: {self.variable}")

    @pytest.fixture(scope="class")
    def fix(self):
        try:
            self.setup()
            yield
        finally:
            self.teardown()


@pytest.mark.usefixtures("fix")
class Test1(Base):
    name = "test1"

    def test_a(self):
        assert self.variable == self.name


@pytest.mark.usefixtures("fix")
class Test2(Base):
    name = "test2"

    def test_a(self):
        assert self.variable == self.name
