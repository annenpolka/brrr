import helper

def test_a():
    helper._acc.append("a")

def test_b():
    assert helper._acc == [], helper._acc
