import pytest


class MyFixture:
    def __init__(self, mode):
        self.mode = mode

    def do_something(self):
        pass


@pytest.fixture(params=['first_mode', 'second_mode'])
def myfixture(request):
    yield MyFixture(request.param)


def test_myfixture_default(myfixture):
    assert isinstance(myfixture, MyFixture)
    assert myfixture.mode in {'first_mode', 'second_mode'}
    myfixture.do_something()


@pytest.mark.parametrize('myfixture', ['first_mode'], indirect=True)
def test_myfixture_single_mode1(myfixture):
    assert isinstance(myfixture, MyFixture)
    assert myfixture.mode == 'first_mode'
    myfixture.do_something()


@pytest.mark.parametrize('myfixture', ['second_mode'], indirect=True)
def test_myfixture_single_mode2(myfixture):
    assert isinstance(myfixture, MyFixture)
    assert myfixture.mode == 'second_mode'
    myfixture.do_something()
