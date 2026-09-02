from helper import *

def test_a():
    bucket.append("a")
    _hidden.append("x")

def test_b():
    assert bucket == [], bucket
