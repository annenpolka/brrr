import pytest

@pytest.fixture(params=["a1", "a2"])
def A(request):
    return request.param

@pytest.fixture(params=["b1", "b2"])
def B(request):
    return request.param

@pytest.fixture
def C():
    return "c"

@pytest.fixture
def A_B(A, B):
    return (A, B)

@pytest.fixture
def B_C(B, C):
    return (B, C)

@pytest.fixture
def A_B_C(A_B, C):
    return (A_B, C)

def test(A_B_C, B_C):
    pass
