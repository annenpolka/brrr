from decimal import getcontext

def test_a():
    getcontext().prec = 10

def test_b():
    assert getcontext().prec != 10, getcontext().prec
