import warnings

def test_a():
    warnings.filterwarnings("ignore", category=UserWarning)

def test_b():
    assert warnings.filters[0][0] != "ignore"
