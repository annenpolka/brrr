import warnings

def test_a():
    warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_b():
    assert warnings.filters == [] or not any(f[2] is DeprecationWarning for f in warnings.filters)
