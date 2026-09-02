import helper

def test_a():
    helper._store["n"] = 1

def test_b():
    assert helper.n == 0, helper.n
