import warnings
def test_a():
    warnings.filterwarnings("ignore")
def test_b():
    assert warnings.filters == []
