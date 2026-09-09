import pytest


@pytest.fixture(params=[3])
def a(request):
    return 'a' * request.param


@pytest.fixture(params=[2])
def b(request):
    return 'b' * request.param


@pytest.fixture
def ab(a, b):
    return ':'.join([a, b])


class OverridenMixin(object):
    @pytest.fixture
    def ab(self, ab):
        """Just override 'ab' in this class"""
        return '--{}--'.format(ab)


class TestNormal(object):
    def test_ab(self, ab):
        assert ab == 'aaa:bb'

    @pytest.mark.parametrize('a,b', [(1, 1)], indirect=True)
    def test_ab_with_different_parameters(self, ab):
        assert ab == 'a:b'


class TestOverriden(OverridenMixin):
    def test_ab(self, ab):
        assert ab == '--aaa:bb--'

    @pytest.mark.parametrize('a,b', [(1, 1)], indirect=True)
    def test_ab_with_different_parameters(self, ab):
        assert ab == '--a:b--'
