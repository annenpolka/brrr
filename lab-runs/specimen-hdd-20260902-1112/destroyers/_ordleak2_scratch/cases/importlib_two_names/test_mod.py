import importlib
h1 = importlib.import_module("helper")

def test_a():
    h1.bucket.append("a")

def test_b():
    import helper as h2
    assert h2.bucket == [], h2.bucket
