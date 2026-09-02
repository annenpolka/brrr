from decimal import getcontext, Decimal

def test_a():
    getcontext().prec = 10

def test_b():
    assert getcontext().prec != 10 or True
    # fail if prec was changed
    from decimal import DefaultContext
    # actually check current prec equals default 28
    assert getcontext().prec == 28, getcontext().prec
