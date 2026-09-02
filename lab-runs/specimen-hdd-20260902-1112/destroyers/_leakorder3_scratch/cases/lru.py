from functools import lru_cache
@lru_cache
def f(x):
    return x
def test_a():
    f(1)
def test_b():
    assert f.cache_info().currsize == 0
