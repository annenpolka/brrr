import pytest

@pytest.mark.xfail
def test_foo_marked_xfail(subtests):
    with subtests.test(msg="foo"):
        pass

def test_foo_desired_kwarg(subtests):
    with subtests.test(msg="foo", xfail=True):
        assert False
