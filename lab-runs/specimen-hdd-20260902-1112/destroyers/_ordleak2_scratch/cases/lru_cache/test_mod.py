from functools import lru_cache

@lru_cache
def cached(x):
    return x

def test_a():
    cached(1)

def test_b():
    assert cached.cache_info().currsize == 0, cached.cache_info()
